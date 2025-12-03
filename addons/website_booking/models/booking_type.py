# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BookingType(models.Model):
    _name = 'booking.type'
    _description = 'Type de Rendez-vous'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
        help="Nom du type de rendez-vous (ex: Consultation, Démo produit, etc.)"
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
        help="Description affichée sur la page de réservation"
    )
    duration = fields.Float(
        string='Durée (heures)',
        required=True,
        default=1.0,
        help="Durée du rendez-vous en heures"
    )
    location = fields.Char(
        string='Lieu',
        help="Lieu du rendez-vous (physique ou en ligne)"
    )
    location_type = fields.Selection([
        ('physical', 'Lieu physique'),
        ('phone', 'Téléphone'),
        ('video', 'Visioconférence'),
        ('other', 'Autre')
    ], string='Type de lieu', default='physical')

    # Disponibilité
    user_ids = fields.Many2many(
        'res.users',
        string='Utilisateurs disponibles',
        help="Utilisateurs pouvant prendre ce type de rendez-vous"
    )
    min_schedule_hours = fields.Integer(
        string='Délai minimum de réservation (heures)',
        default=24,
        help="Nombre d'heures minimum avant le rendez-vous"
    )
    max_schedule_days = fields.Integer(
        string='Réservation possible jusqu\'à (jours)',
        default=60,
        help="Nombre de jours maximum dans le futur pour réserver"
    )
    buffer_time_before = fields.Float(
        string='Temps de battement avant (minutes)',
        default=0,
        help="Temps libre requis avant le rendez-vous"
    )
    buffer_time_after = fields.Float(
        string='Temps de battement après (minutes)',
        default=0,
        help="Temps libre requis après le rendez-vous"
    )

    # Formulaire de réservation
    ask_phone = fields.Boolean(
        string='Demander le téléphone',
        default=True
    )
    ask_email = fields.Boolean(
        string='Demander l\'email',
        default=True
    )
    ask_company = fields.Boolean(
        string='Demander l\'entreprise',
        default=False
    )
    ask_message = fields.Boolean(
        string='Demander un message',
        default=True
    )
    custom_questions = fields.Text(
        string='Questions personnalisées',
        help="Questions additionnelles (une par ligne)"
    )

    # Configuration avancée
    allow_reschedule = fields.Boolean(
        string='Autoriser la reprogrammation',
        default=True
    )
    allow_cancel = fields.Boolean(
        string='Autoriser l\'annulation',
        default=True
    )
    cancel_hours = fields.Integer(
        string='Délai d\'annulation (heures)',
        default=24,
        help="Nombre d'heures minimum avant le rendez-vous pour annuler"
    )

    # Notifications
    send_confirmation = fields.Boolean(
        string='Envoyer email de confirmation',
        default=True
    )
    send_reminder = fields.Boolean(
        string='Envoyer rappel',
        default=True
    )
    reminder_hours = fields.Integer(
        string='Rappel avant (heures)',
        default=24
    )

    # Statistiques
    appointment_count = fields.Integer(
        string='Nombre de rendez-vous',
        compute='_compute_appointment_count'
    )

    # Page web
    website_url = fields.Char(
        string='URL de réservation',
        compute='_compute_website_url'
    )

    def _compute_website_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.website_url = f"{base_url}/booking/{record.id}"
            else:
                record.website_url = False

    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['booking.appointment'].search_count([
                ('booking_type_id', '=', record.id)
            ])

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError(_("La durée doit être supérieure à 0"))

    @api.constrains('min_schedule_hours', 'max_schedule_days')
    def _check_schedule_times(self):
        for record in self:
            if record.min_schedule_hours < 0:
                raise ValidationError(_("Le délai minimum ne peut pas être négatif"))
            if record.max_schedule_days <= 0:
                raise ValidationError(_("Le délai maximum doit être supérieur à 0"))

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': _('Rendez-vous'),
            'view_mode': 'tree,form,calendar',
            'res_model': 'booking.appointment',
            'type': 'ir.actions.act_window',
            'domain': [('booking_type_id', '=', self.id)],
            'context': {'default_booking_type_id': self.id}
        }
