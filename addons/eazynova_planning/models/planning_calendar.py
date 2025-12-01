# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PlanningCalendar(models.Model):
    _name = 'eazynova.planning.calendar'
    _description = 'Calendrier de planning EAZYNOVA'
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    active = fields.Boolean(string="Actif", default=True)

    # Configuration
    calendar_type = fields.Selection([
        ('standard', 'Standard (5 jours)'),
        ('extended', 'Étendu (6 jours)'),
        ('continuous', 'Continu (7 jours)'),
        ('shifts', 'Postes (3x8)'),
        ('custom', 'Personnalisé'),
    ], string="Type de calendrier", default='standard', required=True)

    # Heures de travail
    work_hours_per_day = fields.Float(string="Heures par jour", default=8.0)
    work_hours_per_week = fields.Float(string="Heures par semaine", default=40.0)

    # Jours de travail
    monday = fields.Boolean(string="Lundi", default=True)
    tuesday = fields.Boolean(string="Mardi", default=True)
    wednesday = fields.Boolean(string="Mercredi", default=True)
    thursday = fields.Boolean(string="Jeudi", default=True)
    friday = fields.Boolean(string="Vendredi", default=True)
    saturday = fields.Boolean(string="Samedi", default=False)
    sunday = fields.Boolean(string="Dimanche", default=False)

    # Horaires standards
    hour_start_morning = fields.Float(string="Début matin", default=8.0)
    hour_end_morning = fields.Float(string="Fin matin", default=12.0)
    hour_start_afternoon = fields.Float(string="Début après-midi", default=14.0)
    hour_end_afternoon = fields.Float(string="Fin après-midi", default=18.0)

    # Créneaux personnalisés
    slot_ids = fields.One2many(
        'eazynova.planning.calendar.slot',
        'calendar_id',
        string="Créneaux"
    )

    # Jours fériés
    holiday_ids = fields.Many2many(
        'eazynova.planning.holiday',
        string="Jours fériés"
    )

    # Société
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )

    # Description
    description = fields.Text(string="Description")

    @api.model
    def create(self, vals):
        """Crée le calendrier avec des créneaux par défaut si nécessaire"""
        calendar = super(PlanningCalendar, self).create(vals)
        if not calendar.slot_ids and calendar.calendar_type != 'custom':
            calendar._create_default_slots()
        return calendar

    def _create_default_slots(self):
        """Crée les créneaux par défaut selon le type de calendrier"""
        self.ensure_one()

        # Supprimer les créneaux existants
        self.slot_ids.unlink()

        days = []
        if self.monday:
            days.append('monday')
        if self.tuesday:
            days.append('tuesday')
        if self.wednesday:
            days.append('wednesday')
        if self.thursday:
            days.append('thursday')
        if self.friday:
            days.append('friday')
        if self.saturday:
            days.append('saturday')
        if self.sunday:
            days.append('sunday')

        # Créer les créneaux matin et après-midi pour chaque jour
        for day in days:
            # Matin
            self.env['eazynova.planning.calendar.slot'].create({
                'calendar_id': self.id,
                'day_of_week': day,
                'hour_start': self.hour_start_morning,
                'hour_end': self.hour_end_morning,
                'name': f"{day.capitalize()} - Matin",
            })

            # Après-midi
            self.env['eazynova.planning.calendar.slot'].create({
                'calendar_id': self.id,
                'day_of_week': day,
                'hour_start': self.hour_start_afternoon,
                'hour_end': self.hour_end_afternoon,
                'name': f"{day.capitalize()} - Après-midi",
            })

    def get_working_hours(self, date_start, date_end):
        """Calcule les heures de travail entre deux dates"""
        self.ensure_one()
        # TODO: Implémenter le calcul des heures ouvrées
        return 0.0


class PlanningCalendarSlot(models.Model):
    _name = 'eazynova.planning.calendar.slot'
    _description = 'Créneau de calendrier'
    _order = 'day_of_week, hour_start'

    name = fields.Char(string="Nom", required=True)
    calendar_id = fields.Many2one(
        'eazynova.planning.calendar',
        string="Calendrier",
        required=True,
        ondelete='cascade'
    )

    day_of_week = fields.Selection([
        ('monday', 'Lundi'),
        ('tuesday', 'Mardi'),
        ('wednesday', 'Mercredi'),
        ('thursday', 'Jeudi'),
        ('friday', 'Vendredi'),
        ('saturday', 'Samedi'),
        ('sunday', 'Dimanche'),
    ], string="Jour de la semaine", required=True)

    hour_start = fields.Float(string="Heure de début", required=True)
    hour_end = fields.Float(string="Heure de fin", required=True)
    duration = fields.Float(string="Durée (heures)", compute='_compute_duration', store=True)

    active = fields.Boolean(string="Actif", default=True)

    @api.depends('hour_start', 'hour_end')
    def _compute_duration(self):
        """Calcule la durée du créneau"""
        for slot in self:
            slot.duration = slot.hour_end - slot.hour_start

    @api.constrains('hour_start', 'hour_end')
    def _check_hours(self):
        """Vérifie la cohérence des heures"""
        for slot in self:
            if slot.hour_end <= slot.hour_start:
                raise ValidationError(_("L'heure de fin doit être postérieure à l'heure de début."))
            if slot.hour_start < 0 or slot.hour_start > 24:
                raise ValidationError(_("L'heure de début doit être entre 0 et 24."))
            if slot.hour_end < 0 or slot.hour_end > 24:
                raise ValidationError(_("L'heure de fin doit être entre 0 et 24."))


class PlanningHoliday(models.Model):
    _name = 'eazynova.planning.holiday'
    _description = 'Jour férié'
    _order = 'date desc'

    name = fields.Char(string="Nom", required=True)
    date = fields.Date(string="Date", required=True)
    is_recurring = fields.Boolean(string="Récurrent annuellement", default=True)
    active = fields.Boolean(string="Actif", default=True)

    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )
