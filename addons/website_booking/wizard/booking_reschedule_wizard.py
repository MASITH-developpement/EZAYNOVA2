# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BookingRescheduleWizard(models.TransientModel):
    _name = 'booking.reschedule.wizard'
    _description = 'Wizard de reprogrammation de rendez-vous'

    appointment_id = fields.Many2one(
        'booking.appointment',
        string='Rendez-vous',
        required=True,
        readonly=True
    )
    old_datetime = fields.Datetime(
        string='Ancienne date',
        related='appointment_id.start_datetime',
        readonly=True
    )
    new_datetime = fields.Datetime(
        string='Nouvelle date',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Nouvel utilisateur',
        help="Laisser vide pour garder le même utilisateur"
    )

    def action_reschedule(self):
        self.ensure_one()

        if self.new_datetime <= fields.Datetime.now():
            raise ValidationError(_("La nouvelle date doit être dans le futur"))

        # Mettre à jour le rendez-vous
        vals = {
            'start_datetime': self.new_datetime,
        }
        if self.user_id:
            vals['user_id'] = self.user_id.id

        self.appointment_id.write(vals)

        # Mettre à jour l'événement calendrier
        if self.appointment_id.calendar_event_id:
            self.appointment_id.calendar_event_id.write({
                'start': self.new_datetime,
                'stop': self.appointment_id.end_datetime,
                'user_id': self.appointment_id.user_id.id,
            })

        return {'type': 'ir.actions.act_window_close'}
