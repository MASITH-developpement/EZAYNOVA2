# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    """Extension du modèle partenaire"""
    _inherit = 'res.partner'

    review_request_ids = fields.One2many(
        'eazynova.review.request',
        'partner_id',
        string='Demandes d\'avis'
    )

    review_ids = fields.One2many(
        'eazynova.customer.review',
        'partner_id',
        string='Avis'
    )

    review_request_count = fields.Integer(
        string='Demandes d\'avis',
        compute='_compute_review_counts'
    )

    review_count = fields.Integer(
        string='Avis reçus',
        compute='_compute_review_counts'
    )

    average_rating = fields.Float(
        string='Note moyenne',
        compute='_compute_average_rating',
        store=True
    )

    allow_review_request = fields.Boolean(
        string='Autoriser les demandes d\'avis',
        default=True,
        help='Si décoché, aucune demande d\'avis ne sera envoyée à ce client'
    )

    @api.depends('review_request_ids', 'review_ids')
    def _compute_review_counts(self):
        """Calcule le nombre de demandes et d'avis"""
        for partner in self:
            partner.review_request_count = len(partner.review_request_ids)
            partner.review_count = len(partner.review_ids)

    @api.depends('review_ids.rating_value')
    def _compute_average_rating(self):
        """Calcule la note moyenne"""
        for partner in self:
            published_reviews = partner.review_ids.filtered(
                lambda r: r.state == 'published'
            )

            if published_reviews:
                total = sum(published_reviews.mapped('rating_value'))
                partner.average_rating = round(total / len(published_reviews), 1)
            else:
                partner.average_rating = 0.0

    def action_view_review_requests(self):
        """Affiche les demandes d'avis"""
        self.ensure_one()

        return {
            'name': f'Demandes d\'avis - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.request',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_view_reviews(self):
        """Affiche les avis"""
        self.ensure_one()

        return {
            'name': f'Avis - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.customer.review',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_request_review(self):
        """Crée une demande d'avis"""
        self.ensure_one()

        return {
            'name': 'Demander un Avis',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_ids': [(6, 0, [self.id])]}
        }
