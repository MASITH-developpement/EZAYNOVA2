# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    booking_availability_ids = fields.One2many(
        'booking.availability',
        'user_id',
        string='Disponibilités pour rendez-vous'
    )
    booking_enabled = fields.Boolean(
        string='Disponible pour les rendez-vous',
        default=False,
        help="Activer pour permettre la prise de rendez-vous avec cet utilisateur"
    )
    booking_timezone = fields.Selection(
        lambda self: self._get_timezone_list(),
        string='Fuseau horaire',
        default='Europe/Paris'
    )

    def _get_timezone_list(self):
        import pytz
        return [(tz, tz) for tz in pytz.all_timezones]
