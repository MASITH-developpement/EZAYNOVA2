# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PlanningTask(models.Model):
    _name = 'eazynova.planning.task'
    _description = 'Tâche de planning EAZYNOVA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, priority desc, id desc'

    name = fields.Char(string="Nom de la tâche", required=True, tracking=True)
    reference = fields.Char(
        string="Référence",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Dates et durée
    date_start = fields.Datetime(string="Date de début", required=True, tracking=True)
    date_end = fields.Datetime(string="Date de fin", required=True, tracking=True)
    duration = fields.Float(
        string="Durée (heures)",
        compute='_compute_duration',
        store=True,
        help="Durée en heures"
    )
    duration_days = fields.Float(
        string="Durée (jours)",
        compute='_compute_duration',
        store=True,
        help="Durée en jours"
    )

    # Projet et chantier
    project_id = fields.Many2one(
        'project.project',
        string="Projet",
        tracking=True,
        ondelete='cascade'
    )
    project_task_id = fields.Many2one(
        'project.task',
        string="Tâche projet",
        tracking=True,
        ondelete='cascade'
    )

    # Description
    description = fields.Html(string="Description")
    notes = fields.Text(string="Notes internes")

    # Priorité et état
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente'),
    ], string="Priorité", default='1', tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifié'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', required=True, tracking=True)

    # Assignations
    assignment_ids = fields.One2many(
        'eazynova.planning.assignment',
        'task_id',
        string="Assignations de ressources"
    )
    assignment_count = fields.Integer(
        string="Nombre d'assignations",
        compute='_compute_assignment_count'
    )

    # Ressources requises
    required_resource_count = fields.Integer(
        string="Ressources requises",
        default=1,
        help="Nombre de ressources nécessaires pour cette tâche"
    )
    resource_skill_ids = fields.Many2many(
        'eazynova.planning.resource.skill',
        'task_skill_rel',
        string="Compétences requises"
    )

    # Responsable
    user_id = fields.Many2one(
        'res.users',
        string="Responsable",
        default=lambda self: self.env.user,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )

    # Localisation
    location = fields.Char(string="Localisation")
    location_latitude = fields.Float(string="Latitude", digits=(10, 7))
    location_longitude = fields.Float(string="Longitude", digits=(10, 7))

    # Planification
    is_recurring = fields.Boolean(string="Récurrent")
    recurrence_rule = fields.Char(string="Règle de récurrence")
    parent_task_id = fields.Many2one(
        'eazynova.planning.task',
        string="Tâche parente"
    )

    # Statuts calculés
    is_overdue = fields.Boolean(
        string="En retard",
        compute='_compute_is_overdue',
        store=True
    )
    progress = fields.Float(
        string="Progression (%)",
        default=0.0,
        help="Progression de la tâche (0-100)"
    )

    # Couleur pour le calendrier
    color = fields.Integer(string="Couleur", default=0)

    @api.model
    def create(self, vals):
        """Génère la référence à la création"""
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('eazynova.planning.task') or _('New')
        return super(PlanningTask, self).create(vals)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        """Calcule la durée de la tâche"""
        for task in self:
            if task.date_start and task.date_end:
                delta = task.date_end - task.date_start
                task.duration = delta.total_seconds() / 3600.0  # Heures
                task.duration_days = delta.total_seconds() / 86400.0  # Jours
            else:
                task.duration = 0.0
                task.duration_days = 0.0

    @api.depends('assignment_ids')
    def _compute_assignment_count(self):
        """Compte le nombre d'assignations"""
        for task in self:
            task.assignment_count = len(task.assignment_ids)

    @api.depends('date_end', 'state')
    def _compute_is_overdue(self):
        """Vérifie si la tâche est en retard"""
        now = fields.Datetime.now()
        for task in self:
            task.is_overdue = (
                task.date_end < now and
                task.state not in ('done', 'cancelled')
            )

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Vérifie la cohérence des dates"""
        for task in self:
            if task.date_start and task.date_end:
                if task.date_end <= task.date_start:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début."))

    def action_plan(self):
        """Passe la tâche en état planifié"""
        self.write({'state': 'planned'})

    def action_confirm(self):
        """Confirme la tâche"""
        self.write({'state': 'confirmed'})

    def action_start(self):
        """Démarre la tâche"""
        self.write({'state': 'in_progress'})

    def action_done(self):
        """Termine la tâche"""
        self.write({
            'state': 'done',
            'progress': 100.0
        })

    def action_cancel(self):
        """Annule la tâche"""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Remet en brouillon"""
        self.write({'state': 'draft'})

    def action_view_assignments(self):
        """Ouvre la vue des assignations"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignations'),
            'res_model': 'eazynova.planning.assignment',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
        }

    def action_auto_assign_resources(self):
        """Lance l'assignation automatique des ressources"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignation automatique'),
            'res_model': 'eazynova.planning.auto.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_task_id': self.id},
        }

    def check_resource_availability(self):
        """Vérifie la disponibilité des ressources assignées"""
        self.ensure_one()
        conflicts = []

        for assignment in self.assignment_ids:
            # Vérifier les autres assignations de la ressource
            overlapping = self.env['eazynova.planning.assignment'].search([
                ('resource_id', '=', assignment.resource_id.id),
                ('id', '!=', assignment.id),
                ('state', '!=', 'cancelled'),
                '|',
                '&', ('date_start', '<=', self.date_start), ('date_end', '>=', self.date_start),
                '&', ('date_start', '<=', self.date_end), ('date_end', '>=', self.date_end),
            ])

            if overlapping:
                conflicts.append({
                    'resource': assignment.resource_id.name,
                    'overlapping_count': len(overlapping)
                })

        return conflicts


class PlanningResourceSkill(models.Model):
    _name = 'eazynova.planning.resource.skill'
    _description = 'Compétence de ressource'
    _order = 'name'

    name = fields.Char(string="Nom", required=True)
    description = fields.Text(string="Description")
    level_required = fields.Selection([
        ('basic', 'Basique'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
        ('expert', 'Expert'),
    ], string="Niveau requis", default='basic')
    active = fields.Boolean(string="Actif", default=True)
