# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomerReview(models.Model):
    """Avis client"""
    _name = 'eazynova.customer.review'
    _description = 'Avis Client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'review_date desc, id desc'

    name = fields.Char(
        string='Titre',
        required=True,
        tracking=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        ondelete='restrict'
    )

    request_id = fields.Many2one(
        'eazynova.review.request',
        string='Demande associée',
        ondelete='set null'
    )

    review_date = fields.Datetime(
        string='Date de l\'avis',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )

    rating = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐')
    ], string='Note', required=True, tracking=True)

    rating_value = fields.Integer(
        string='Note (valeur)',
        compute='_compute_rating_value',
        store=True
    )

    review_text = fields.Text(
        string='Commentaire',
        tracking=True
    )

    reviewer_name = fields.Char(
        string='Nom du réviseur',
        compute='_compute_reviewer_name',
        store=True
    )

    platform = fields.Selection([
        ('trustpilot', 'Trustpilot'),
        ('google', 'Google Reviews'),
        ('internal', 'Avis Interne')
    ], string='Plateforme', required=True, default='internal', tracking=True)

    external_id = fields.Char(
        string='ID Externe',
        help='Identifiant de l\'avis sur la plateforme externe'
    )

    external_url = fields.Char(
        string='URL Externe',
        help='Lien vers l\'avis sur la plateforme'
    )

    state = fields.Selection([
        ('pending', 'En attente de modération'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('published', 'Publié')
    ], string='État', default='pending', required=True, tracking=True)

    publish_on_website = fields.Boolean(
        string='Publier sur le site web',
        default=True,
        tracking=True
    )

    is_featured = fields.Boolean(
        string='Avis mis en avant',
        help='Afficher cet avis en priorité sur le site web'
    )

    response_text = fields.Text(
        string='Réponse de l\'entreprise',
        tracking=True
    )

    response_date = fields.Datetime(
        string='Date de réponse',
        readonly=True
    )

    response_user_id = fields.Many2one(
        'res.users',
        string='Répondu par',
        readonly=True
    )

    verified = fields.Boolean(
        string='Avis vérifié',
        default=False,
        help='Avis d\'un client ayant effectué un achat'
    )

    helpful_count = fields.Integer(
        string='Votes utiles',
        default=0
    )

    @api.depends('rating')
    def _compute_rating_value(self):
        """Convertit la note en valeur numérique"""
        for review in self:
            review.rating_value = int(review.rating) if review.rating else 0

    @api.depends('partner_id')
    def _compute_reviewer_name(self):
        """Récupère le nom du client"""
        for review in self:
            review.reviewer_name = review.partner_id.name if review.partner_id else ''

    @api.constrains('rating')
    def _check_rating(self):
        """Valide la note"""
        for review in self:
            if review.rating_value < 1 or review.rating_value > 5:
                raise ValidationError('La note doit être entre 1 et 5 étoiles.')

    def action_approve(self):
        """Approuve l'avis"""
        if not self.env.user.has_group('eazynova_trust.group_trust_manager'):
            raise ValidationError("Seul un Manager Avis Clients peut approuver l'avis.")
        self.write({'state': 'approved'})

        # Marquer la demande comme complétée si elle existe
        if self.request_id and self.request_id.state != 'completed':
            self.request_id.action_mark_completed()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Succès',
                'message': 'Avis approuvé',
                'type': 'success',
            }
        }

    def action_reject(self):
        """Rejette l'avis"""
        self.write({'state': 'rejected'})

    def action_publish(self):
        """Publie l'avis sur le site web"""
        self.ensure_one()

        if self.state != 'approved':
            raise ValidationError('Seuls les avis approuvés peuvent être publiés.')

        self.write({
            'state': 'published',
            'publish_on_website': True
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Succès',
                'message': 'Avis publié sur le site web',
                'type': 'success',
            }
        }

    def action_unpublish(self):
        """Dépublie l'avis"""
        self.write({'publish_on_website': False})

    def action_add_response(self):
        """Ouvre un wizard pour ajouter une réponse"""
        self.ensure_one()

        return {
            'name': 'Répondre à l\'avis',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.response.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_review_id': self.id}
        }

    def write_response(self, response_text):
        """Enregistre la réponse de l'entreprise"""
        self.write({
            'response_text': response_text,
            'response_date': fields.Datetime.now(),
            'response_user_id': self.env.user.id
        })

    @api.model
    def get_average_rating(self, domain=None):
        """Calcule la note moyenne"""
        if domain is None:
            domain = [('state', '=', 'published')]

        reviews = self.search(domain)

        if not reviews:
            return 0.0

        total = sum(reviews.mapped('rating_value'))
        return round(total / len(reviews), 1)

    @api.model
    def get_rating_distribution(self):
        """Retourne la distribution des notes"""
        published_reviews = self.search([('state', '=', 'published')])

        distribution = {
            '5': 0,
            '4': 0,
            '3': 0,
            '2': 0,
            '1': 0
        }

        for review in published_reviews:
            distribution[review.rating] += 1

        return distribution
