# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PlanningSlot(models.Model):
    _name = 'eazynova.planning.slot'
    _description = 'Créneau de planning EAZYNOVA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(string="Nom", required=True)

    # Dates
    date_start = fields.Datetime(string="Date de début", required=True, tracking=True)
    date_end = fields.Datetime(string="Date de fin", required=True, tracking=True)
    duration = fields.Float(
        string="Durée (heures)",
        compute='_compute_duration',
        store=True
    )

    # Ressource
    resource_id = fields.Many2one(
        'eazynova.planning.resource',
        string="Ressource",
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # Tâche (optionnel)
    task_id = fields.Many2one(
        'eazynova.planning.task',
        string="Tâche",
        ondelete='cascade'
    )

    # Type de créneau
    slot_type = fields.Selection([
        ('work', 'Travail'),
        ('break', 'Pause'),
        ('meeting', 'Réunion'),
        ('training', 'Formation'),
        ('other', 'Autre'),
    ], string="Type de créneau", default='work', required=True)

    # État
    state = fields.Selection([
        ('available', 'Disponible'),
        ('booked', 'Réservé'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='available', required=True, tracking=True)

    # Allocation
    capacity = fields.Float(
        string="Capacité",
        default=1.0,
        help="Capacité du créneau (ex: 1.0 = 100%)"
    )
    allocated = fields.Float(
        string="Alloué",
        default=0.0,
        help="Pourcentage déjà alloué (0-1)"
    )
    remaining_capacity = fields.Float(
        string="Capacité restante",
        compute='_compute_remaining_capacity',
        store=True
    )

    # Répétition
    is_recurring = fields.Boolean(string="Récurrent")
    recurrence_rule = fields.Char(string="Règle de récurrence")

    # Notes
    description = fields.Text(string="Description")
    notes = fields.Text(string="Notes")

    # Société
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )

    # Couleur
    color = fields.Integer(string="Couleur", compute='_compute_color', store=True)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        """Calcule la durée du créneau"""
        for slot in self:
            if slot.date_start and slot.date_end:
                delta = slot.date_end - slot.date_start
                slot.duration = delta.total_seconds() / 3600.0
            else:
                slot.duration = 0.0

    @api.depends('capacity', 'allocated')
    def _compute_remaining_capacity(self):
        """Calcule la capacité restante"""
        for slot in self:
            slot.remaining_capacity = slot.capacity - slot.allocated

    @api.depends('state', 'remaining_capacity')
    def _compute_color(self):
        """Calcule la couleur selon l'état et la disponibilité"""
        for slot in self:
            if slot.state == 'cancelled':
                slot.color = 1  # Rouge
            elif slot.state == 'completed':
                slot.color = 10  # Vert
            elif slot.remaining_capacity <= 0:
                slot.color = 3  # Orange
            else:
                slot.color = 7  # Bleu

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Vérifie la cohérence des dates"""
        for slot in self:
            if slot.date_start and slot.date_end:
                if slot.date_end <= slot.date_start:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début."))

    @api.constrains('allocated', 'capacity')
    def _check_allocation(self):
        """Vérifie que l'allocation ne dépasse pas la capacité"""
        for slot in self:
            if slot.allocated > slot.capacity:
                raise ValidationError(_(
                    "L'allocation (%.2f) ne peut pas dépasser la capacité (%.2f)."
                ) % (slot.allocated, slot.capacity))

    def action_book(self):
        """Réserve le créneau"""
        self.write({
            'state': 'booked',
            'allocated': self.capacity
        })

    def action_complete(self):
        """Marque le créneau comme terminé"""
        self.write({'state': 'completed'})

    def action_cancel(self):
        """Annule le créneau"""
        self.write({'state': 'cancelled'})

    def action_reset(self):
        """Réinitialise le créneau"""
        self.write({
            'state': 'available',
            'allocated': 0.0
        })
