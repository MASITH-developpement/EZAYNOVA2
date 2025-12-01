# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PlanningAbsence(models.Model):
    _name = 'eazynova.planning.absence'
    _description = 'Absence de ressource EAZYNOVA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(string="Motif", required=True, tracking=True)
    reference = fields.Char(
        string="Référence",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Ressource
    resource_id = fields.Many2one(
        'eazynova.planning.resource',
        string="Ressource",
        required=True,
        ondelete='cascade',
        tracking=True
    )
    resource_name = fields.Char(related='resource_id.name', string="Nom de la ressource", store=True)
    resource_type = fields.Selection(related='resource_id.resource_type', store=True)

    # Dates
    date_start = fields.Datetime(string="Date de début", required=True, tracking=True)
    date_end = fields.Datetime(string="Date de fin", required=True, tracking=True)
    duration = fields.Float(
        string="Durée (heures)",
        compute='_compute_duration',
        store=True
    )
    duration_days = fields.Float(
        string="Durée (jours)",
        compute='_compute_duration',
        store=True
    )

    # Type d'absence
    absence_type = fields.Selection([
        ('vacation', 'Congés payés'),
        ('sick_leave', 'Arrêt maladie'),
        ('training', 'Formation'),
        ('maintenance', 'Maintenance'),
        ('unavailable', 'Indisponibilité'),
        ('other', 'Autre'),
    ], string="Type d'absence", required=True, default='vacation', tracking=True)

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('refused', 'Refusé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', required=True, tracking=True)

    # Demandeur et validateur
    requested_by = fields.Many2one(
        'res.users',
        string="Demandé par",
        default=lambda self: self.env.user,
        readonly=True
    )
    approved_by = fields.Many2one(
        'res.users',
        string="Approuvé par",
        readonly=True,
        tracking=True
    )
    approved_date = fields.Datetime(string="Date d'approbation", readonly=True)

    refused_by = fields.Many2one(
        'res.users',
        string="Refusé par",
        readonly=True,
        tracking=True
    )
    refused_date = fields.Datetime(string="Date de refus", readonly=True)
    refused_reason = fields.Text(string="Motif de refus", readonly=True)

    # Notes
    description = fields.Text(string="Description")
    notes = fields.Text(string="Notes internes")

    # Remplacement
    replacement_resource_id = fields.Many2one(
        'eazynova.planning.resource',
        string="Ressource de remplacement",
        help="Ressource qui remplace pendant l'absence"
    )

    # Société
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )

    # Couleur pour visualisation
    color = fields.Integer(string="Couleur", default=3)  # Rouge par défaut

    @api.model
    def create(self, vals):
        """Génère la référence à la création"""
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('eazynova.planning.absence') or _('New')
        return super(PlanningAbsence, self).create(vals)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        """Calcule la durée de l'absence"""
        for absence in self:
            if absence.date_start and absence.date_end:
                delta = absence.date_end - absence.date_start
                absence.duration = delta.total_seconds() / 3600.0  # Heures
                absence.duration_days = delta.total_seconds() / 86400.0  # Jours
            else:
                absence.duration = 0.0
                absence.duration_days = 0.0

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Vérifie la cohérence des dates"""
        for absence in self:
            if absence.date_start and absence.date_end:
                if absence.date_end <= absence.date_start:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début."))

    def action_submit(self):
        """Soumet la demande d'absence"""
        self.write({'state': 'submitted'})

    def action_approve(self):
        """Approuve l'absence"""
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })

    def action_refuse(self):
        """Refuse l'absence - ouvre un wizard pour saisir le motif"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Motif de refus'),
            'res_model': 'eazynova.planning.absence.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_absence_id': self.id},
        }

    def action_cancel(self):
        """Annule l'absence"""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Remet en brouillon"""
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False,
            'refused_by': False,
            'refused_date': False,
            'refused_reason': False,
        })

    def check_assignment_conflicts(self):
        """Vérifie les conflits avec les assignations existantes"""
        self.ensure_one()

        conflicts = self.env['eazynova.planning.assignment'].search([
            ('resource_id', '=', self.resource_id.id),
            ('state', 'in', ('confirmed', 'in_progress')),
            '|',
            '&', ('date_start', '<=', self.date_start), ('date_end', '>=', self.date_start),
            '&', ('date_start', '<=', self.date_end), ('date_end', '>=', self.date_end),
        ])

        return conflicts

    def action_view_conflicts(self):
        """Affiche les conflits d'assignation"""
        self.ensure_one()
        conflicts = self.check_assignment_conflicts()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignations en conflit'),
            'res_model': 'eazynova.planning.assignment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', conflicts.ids)],
            'context': {'create': False},
        }
