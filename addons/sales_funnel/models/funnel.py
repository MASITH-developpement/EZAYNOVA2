# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Funnel(models.Model):
    _name = 'sales.funnel'
    _description = 'Tunnel de Vente'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True
    )
    active = fields.Boolean(
        string='Actif',
        default=True,
        tracking=True
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10
    )
    description = fields.Html(
        string='Description',
        help="Description interne du tunnel"
    )

    # Type et objectif
    funnel_type = fields.Selection([
        ('lead_generation', 'Génération de leads'),
        ('qualification', 'Qualification de prospects'),
        ('survey', 'Enquête/Questionnaire'),
        ('registration', 'Inscription'),
        ('quote', 'Demande de devis'),
        ('download', 'Téléchargement de ressource'),
        ('contact', 'Formulaire de contact'),
        ('other', 'Autre')
    ], string='Type de tunnel', default='lead_generation', required=True)

    # Étapes
    step_ids = fields.One2many(
        'sales.funnel.step',
        'funnel_id',
        string='Étapes',
        copy=True
    )
    step_count = fields.Integer(
        string='Nombre d\'étapes',
        compute='_compute_step_count'
    )

    # Landing page
    landing_title = fields.Char(
        string='Titre de la page',
        default='Bienvenue'
    )
    landing_subtitle = fields.Char(
        string='Sous-titre'
    )
    landing_content = fields.Html(
        string='Contenu de la page d\'accueil'
    )
    show_progress_bar = fields.Boolean(
        string='Afficher la barre de progression',
        default=True
    )

    # Page de remerciement
    thank_you_title = fields.Char(
        string='Titre de remerciement',
        default='Merci !'
    )
    thank_you_message = fields.Html(
        string='Message de remerciement',
        default='<p>Merci pour votre soumission. Nous reviendrons vers vous prochainement.</p>'
    )
    redirect_url = fields.Char(
        string='URL de redirection',
        help="URL vers laquelle rediriger après soumission (optionnel)"
    )

    # Actions automatiques
    create_lead = fields.Boolean(
        string='Créer une opportunité CRM',
        default=True,
        help="Créer automatiquement une opportunité dans le CRM"
    )
    create_contact = fields.Boolean(
        string='Créer un contact',
        default=True,
        help="Créer automatiquement un contact"
    )
    assign_to_user_id = fields.Many2one(
        'res.users',
        string='Assigner à',
        help="Utilisateur auquel assigner les leads générés"
    )
    team_id = fields.Many2one(
        'crm.team',
        string='Équipe commerciale'
    )

    # Notifications
    send_notification = fields.Boolean(
        string='Envoyer notification',
        default=True,
        help="Envoyer un email de notification lors d'une soumission"
    )
    notification_email = fields.Char(
        string='Email de notification'
    )
    send_confirmation = fields.Boolean(
        string='Envoyer email de confirmation',
        default=True,
        help="Envoyer un email de confirmation au visiteur"
    )

    # Statistiques
    submission_count = fields.Integer(
        string='Soumissions',
        compute='_compute_submission_count'
    )
    conversion_rate = fields.Float(
        string='Taux de conversion',
        compute='_compute_conversion_rate',
        help="Pourcentage de visiteurs ayant complété le tunnel"
    )
    view_count = fields.Integer(
        string='Vues',
        default=0,
        help="Nombre de fois que la page a été vue"
    )

    # URL publique
    website_url = fields.Char(
        string='URL du tunnel',
        compute='_compute_website_url'
    )

    # Options avancées
    allow_multiple_submissions = fields.Boolean(
        string='Autoriser plusieurs soumissions',
        default=True,
        help="Permettre à un même visiteur de soumettre plusieurs fois"
    )
    require_authentication = fields.Boolean(
        string='Nécessite authentification',
        default=False,
        help="Nécessite que le visiteur soit connecté"
    )

    @api.depends('step_ids')
    def _compute_step_count(self):
        for record in self:
            record.step_count = len(record.step_ids)

    def _compute_submission_count(self):
        for record in self:
            record.submission_count = self.env['sales.funnel.submission'].search_count([
                ('funnel_id', '=', record.id)
            ])

    def _compute_conversion_rate(self):
        for record in self:
            if record.view_count > 0:
                record.conversion_rate = (record.submission_count / record.view_count) * 100
            else:
                record.conversion_rate = 0

    @api.depends('id')
    def _compute_website_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.website_url = f"{base_url}/funnel/{record.id}"
            else:
                record.website_url = False

    @api.constrains('step_ids')
    def _check_steps(self):
        for record in self:
            if not record.step_ids:
                raise ValidationError(_("Un tunnel doit avoir au moins une étape"))

    def action_view_submissions(self):
        self.ensure_one()
        return {
            'name': _('Soumissions'),
            'view_mode': 'tree,form',
            'res_model': 'sales.funnel.submission',
            'type': 'ir.actions.act_window',
            'domain': [('funnel_id', '=', self.id)],
            'context': {'default_funnel_id': self.id}
        }

    def action_view_steps(self):
        self.ensure_one()
        return {
            'name': _('Étapes'),
            'view_mode': 'tree,form',
            'res_model': 'sales.funnel.step',
            'type': 'ir.actions.act_window',
            'domain': [('funnel_id', '=', self.id)],
            'context': {'default_funnel_id': self.id}
        }

    def action_preview(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }
