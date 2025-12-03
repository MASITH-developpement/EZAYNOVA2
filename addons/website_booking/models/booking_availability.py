# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BookingAvailability(models.Model):
    _name = 'booking.availability'
    _description = 'Disponibilités pour les rendez-vous'
    _order = 'user_id, weekday, hour_from'

    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        required=True,
        ondelete='cascade'
    )
    weekday = fields.Selection([
        ('0', 'Lundi'),
        ('1', 'Mardi'),
        ('2', 'Mercredi'),
        ('3', 'Jeudi'),
        ('4', 'Vendredi'),
        ('5', 'Samedi'),
        ('6', 'Dimanche')
    ], string='Jour de la semaine', required=True)

    hour_from = fields.Float(
        string='De',
        required=True,
        help="Heure de début (ex: 9.0 pour 9h00, 14.5 pour 14h30)"
    )
    hour_to = fields.Float(
        string='À',
        required=True,
        help="Heure de fin (ex: 17.0 pour 17h00, 12.5 pour 12h30)"
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    @api.constrains('hour_from', 'hour_to')
    def _check_hours(self):
        for record in self:
            if record.hour_from >= record.hour_to:
                raise ValidationError(_("L'heure de début doit être inférieure à l'heure de fin"))
            if record.hour_from < 0 or record.hour_from >= 24:
                raise ValidationError(_("L'heure de début doit être entre 0 et 24"))
            if record.hour_to < 0 or record.hour_to > 24:
                raise ValidationError(_("L'heure de fin doit être entre 0 et 24"))

    @api.constrains('user_id', 'weekday', 'hour_from', 'hour_to')
    def _check_overlap(self):
        for record in self:
            overlapping = self.search([
                ('id', '!=', record.id),
                ('user_id', '=', record.user_id.id),
                ('weekday', '=', record.weekday),
                ('active', '=', True),
                ('hour_from', '<', record.hour_to),
                ('hour_to', '>', record.hour_from)
            ])
            if overlapping:
                raise ValidationError(_(
                    "Ces horaires se chevauchent avec une autre plage de disponibilité"
                ))
