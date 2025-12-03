# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class FunnelSubmission(models.Model):
    _name = 'sales.funnel.submission'
    _description = 'Soumission de Tunnel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau')
    )
    funnel_id = fields.Many2one(
        'sales.funnel',
        string='Tunnel',
        required=True,
        tracking=True
    )

    # Informations de contact
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        tracking=True
    )
    partner_name = fields.Char(
        string='Nom',
        compute='_compute_partner_info',
        store=True
    )
    partner_email = fields.Char(
        string='Email',
        compute='_compute_partner_info',
        store=True
    )
    partner_phone = fields.Char(
        string='Téléphone',
        compute='_compute_partner_info',
        store=True
    )

    # Valeurs soumises
    value_ids = fields.One2many(
        'sales.funnel.submission.value',
        'submission_id',
        string='Valeurs'
    )

    # Scoring et qualification
    score = fields.Float(
        string='Score',
        help="Score de qualification du lead"
    )
    quality = fields.Selection([
        ('cold', 'Froid'),
        ('warm', 'Tiède'),
        ('hot', 'Chaud')
    ], string='Qualification', compute='_compute_quality', store=True)

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('processed', 'Traité')
    ], string='État', default='draft', tracking=True)

    # Opportunité CRM créée
    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunité',
        readonly=True
    )

    # Métadonnées
    ip_address = fields.Char(
        string='Adresse IP'
    )
    user_agent = fields.Char(
        string='User Agent'
    )
    referrer = fields.Char(
        string='Référent',
        help="Page d'où vient le visiteur"
    )
    session_id = fields.Char(
        string='Session'
    )

    # Timestamps
    started_at = fields.Datetime(
        string='Démarré le',
        default=fields.Datetime.now
    )
    completed_at = fields.Datetime(
        string='Complété le'
    )
    duration = fields.Float(
        string='Durée (minutes)',
        compute='_compute_duration',
        store=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sales.funnel.submission') or _('Nouveau')
        return super(FunnelSubmission, self).create(vals)

    @api.depends('partner_id')
    def _compute_partner_info(self):
        for record in self:
            if record.partner_id:
                record.partner_name = record.partner_id.name
                record.partner_email = record.partner_id.email
                record.partner_phone = record.partner_id.phone or record.partner_id.mobile
            else:
                # Récupérer depuis les valeurs
                record.partner_name = False
                record.partner_email = False
                record.partner_phone = False

    @api.depends('score')
    def _compute_quality(self):
        for record in self:
            if record.score >= 70:
                record.quality = 'hot'
            elif record.score >= 40:
                record.quality = 'warm'
            else:
                record.quality = 'cold'

    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = delta.total_seconds() / 60
            else:
                record.duration = 0

    def action_submit(self):
        """Marquer comme soumis et déclencher les actions automatiques"""
        for record in self:
            record.state = 'submitted'
            record.completed_at = fields.Datetime.now()

            # Créer le contact si nécessaire
            if record.funnel_id.create_contact and not record.partner_id:
                record._create_contact()

            # Créer l'opportunité si nécessaire
            if record.funnel_id.create_lead:
                record._create_lead()

            # Envoyer les notifications
            if record.funnel_id.send_confirmation:
                record._send_confirmation_email()

            if record.funnel_id.send_notification:
                record._send_notification_email()

    def _create_contact(self):
        """Créer un contact depuis les valeurs du formulaire"""
        self.ensure_one()

        # Récupérer les valeurs mappées
        contact_vals = self._get_contact_values()

        if contact_vals.get('email'):
            # Vérifier si le contact existe déjà
            partner = self.env['res.partner'].search([
                ('email', '=', contact_vals['email'])
            ], limit=1)

            if not partner:
                partner = self.env['res.partner'].create(contact_vals)

            self.partner_id = partner.id

    def _create_lead(self):
        """Créer une opportunité CRM"""
        self.ensure_one()

        lead_vals = {
            'name': self.name,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'type': 'opportunity',
            'user_id': self.funnel_id.assign_to_user_id.id if self.funnel_id.assign_to_user_id else False,
            'team_id': self.funnel_id.team_id.id if self.funnel_id.team_id else False,
            'description': self._get_description_text(),
        }

        # Ajouter les infos de contact si pas de partner
        if not self.partner_id:
            contact_vals = self._get_contact_values()
            lead_vals.update({
                'contact_name': contact_vals.get('name', ''),
                'email_from': contact_vals.get('email', ''),
                'phone': contact_vals.get('phone', ''),
            })

        lead = self.env['crm.lead'].create(lead_vals)
        self.lead_id = lead.id

    def _get_contact_values(self):
        """Récupérer les valeurs de contact depuis les champs mappés"""
        self.ensure_one()
        vals = {}

        for value in self.value_ids:
            if value.field_id.crm_field:
                field_mapping = {
                    'name': 'name',
                    'email': 'email',
                    'phone': 'phone',
                    'mobile': 'mobile',
                    'company_name': 'company_name',
                    'website': 'website',
                    'title': 'function',
                    'street': 'street',
                    'city': 'city',
                    'zip': 'zip',
                    'country': 'country_id',
                }

                field = field_mapping.get(value.field_id.crm_field)
                if field:
                    vals[field] = value.value

        return vals

    def _get_description_text(self):
        """Générer une description depuis toutes les réponses"""
        self.ensure_one()
        lines = []
        for value in self.value_ids:
            lines.append(f"{value.field_id.name}: {value.value}")
        return '\n'.join(lines)

    def _send_confirmation_email(self):
        """Envoyer email de confirmation au visiteur"""
        self.ensure_one()
        template = self.env.ref('sales_funnel.email_template_funnel_confirmation', raise_if_not_found=False)
        if template and self.partner_email:
            template.send_mail(self.id, force_send=True)

    def _send_notification_email(self):
        """Envoyer notification interne"""
        self.ensure_one()
        template = self.env.ref('sales_funnel.email_template_funnel_notification', raise_if_not_found=False)
        if template and self.funnel_id.notification_email:
            template.send_mail(self.id, force_send=True)

    def action_process(self):
        self.write({'state': 'processed'})
