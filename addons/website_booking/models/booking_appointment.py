# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class BookingAppointment(models.Model):
    _name = 'booking.appointment'
    _description = 'Rendez-vous'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau')
    )
    booking_type_id = fields.Many2one(
        'booking.type',
        string='Type de rendez-vous',
        required=True,
        tracking=True
    )

    # Informations temporelles
    start_datetime = fields.Datetime(
        string='Date et heure de début',
        required=True,
        tracking=True
    )
    end_datetime = fields.Datetime(
        string='Date et heure de fin',
        compute='_compute_end_datetime',
        store=True
    )
    duration = fields.Float(
        string='Durée (heures)',
        related='booking_type_id.duration',
        readonly=True
    )

    # Utilisateur assigné
    user_id = fields.Many2one(
        'res.users',
        string='Assigné à',
        required=True,
        tracking=True
    )

    # Informations client
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        tracking=True
    )
    partner_name = fields.Char(
        string='Nom',
        required=True
    )
    partner_email = fields.Char(
        string='Email'
    )
    partner_phone = fields.Char(
        string='Téléphone'
    )
    partner_company = fields.Char(
        string='Entreprise'
    )
    message = fields.Text(
        string='Message du client'
    )
    custom_answers = fields.Text(
        string='Réponses personnalisées'
    )

    # Statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Effectué'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', required=True, tracking=True)

    # Lien avec le calendrier
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Événement calendrier',
        readonly=True
    )

    # Tokens pour annulation/reprogrammation
    access_token = fields.Char(
        string='Token d\'accès',
        copy=False,
        readonly=True
    )

    # URLs
    cancel_url = fields.Char(
        string='URL d\'annulation',
        compute='_compute_urls'
    )
    reschedule_url = fields.Char(
        string='URL de reprogrammation',
        compute='_compute_urls'
    )

    # Notifications
    confirmation_sent = fields.Boolean(
        string='Confirmation envoyée',
        default=False
    )
    reminder_sent = fields.Boolean(
        string='Rappel envoyé',
        default=False
    )

    @api.model
    def create(self, vals_list):
        # Odoo 19: vals_list est maintenant une liste de dictionnaires
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('booking.appointment') or _('Nouveau')
            if not vals.get('access_token'):
                vals['access_token'] = self._generate_access_token()

        return super(BookingAppointment, self).create(vals_list)

    def _generate_access_token(self):
        import secrets
        return secrets.token_urlsafe(32)

    @api.depends('start_datetime', 'booking_type_id.duration')
    def _compute_end_datetime(self):
        for record in self:
            if record.start_datetime and record.booking_type_id:
                record.end_datetime = record.start_datetime + timedelta(hours=record.booking_type_id.duration)
            else:
                record.end_datetime = False

    @api.depends('access_token')
    def _compute_urls(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id and record.access_token:
                record.cancel_url = f"{base_url}/booking/cancel/{record.id}/{record.access_token}"
                record.reschedule_url = f"{base_url}/booking/reschedule/{record.id}/{record.access_token}"
            else:
                record.cancel_url = False
                record.reschedule_url = False

    @api.constrains('start_datetime', 'user_id', 'booking_type_id')
    def _check_availability(self):
        for record in self:
            if record.start_datetime and record.user_id:
                # Vérifier les conflits avec d'autres rendez-vous
                overlapping = self.search([
                    ('id', '!=', record.id),
                    ('user_id', '=', record.user_id.id),
                    ('state', 'in', ['confirmed', 'draft']),
                    ('start_datetime', '<', record.end_datetime),
                    ('end_datetime', '>', record.start_datetime)
                ])
                if overlapping:
                    raise ValidationError(_(
                        "Ce créneau n'est pas disponible. Il y a un conflit avec un autre rendez-vous."
                    ))

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            record._create_calendar_event()
            if record.booking_type_id.send_confirmation and not record.confirmation_sent:
                record._send_confirmation_email()

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
            if record.calendar_event_id:
                record.calendar_event_id.unlink()

    def action_draft(self):
        self.write({'state': 'draft'})

    def _create_calendar_event(self):
        self.ensure_one()
        if not self.calendar_event_id:
            event = self.env['calendar.event'].create({
                'name': f"{self.booking_type_id.name} - {self.partner_name}",
                'start': self.start_datetime,
                'stop': self.end_datetime,
                'user_id': self.user_id.id,
                'partner_ids': [(4, self.partner_id.id)] if self.partner_id else [],
                'description': self.message or '',
                'location': self.booking_type_id.location or '',
            })
            self.calendar_event_id = event.id

    def _send_confirmation_email(self):
        self.ensure_one()
        template = self.env.ref('website_booking.email_template_booking_confirmation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.confirmation_sent = True

    def _send_reminder_email(self):
        self.ensure_one()
        template = self.env.ref('website_booking.email_template_booking_reminder', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.reminder_sent = True

    @api.model
    def _cron_send_reminders(self):
        """Cron pour envoyer les rappels"""
        now = datetime.now()
        appointments = self.search([
            ('state', '=', 'confirmed'),
            ('reminder_sent', '=', False),
            ('booking_type_id.send_reminder', '=', True)
        ])
        for appointment in appointments:
            reminder_time = appointment.start_datetime - timedelta(hours=appointment.booking_type_id.reminder_hours)
            if now >= reminder_time:
                appointment._send_reminder_email()
