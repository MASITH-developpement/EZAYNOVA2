# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Lien avec planning
    planning_task_ids = fields.One2many(
        'eazynova.planning.task',
        'project_task_id',
        string="Tâches de planning"
    )
    planning_task_count = fields.Integer(
        string="Nombre de tâches de planning",
        compute='_compute_planning_task_count'
    )

    # Assignations de ressources
    planning_assignment_ids = fields.One2many(
        'eazynova.planning.assignment',
        compute='_compute_planning_assignments',
        string="Assignations de ressources"
    )
    planning_assignment_count = fields.Integer(
        string="Nombre d'assignations",
        compute='_compute_planning_assignment_count'
    )

    # Statistiques de planning
    planned_hours_total = fields.Float(
        string="Heures planifiées totales",
        compute='_compute_planning_stats',
        help="Total des heures planifiées pour toutes les tâches de planning"
    )
    actual_hours_total = fields.Float(
        string="Heures réelles totales",
        compute='_compute_planning_stats',
        help="Total des heures réelles pour toutes les tâches de planning"
    )

    @api.depends('planning_task_ids')
    def _compute_planning_task_count(self):
        """Compte le nombre de tâches de planning"""
        for task in self:
            task.planning_task_count = len(task.planning_task_ids)

    @api.depends('planning_task_ids')
    def _compute_planning_assignments(self):
        """Récupère toutes les assignations des tâches de planning"""
        for task in self:
            assignments = self.env['eazynova.planning.assignment'].search([
                ('task_id', 'in', task.planning_task_ids.ids)
            ])
            task.planning_assignment_ids = assignments

    @api.depends('planning_assignment_ids')
    def _compute_planning_assignment_count(self):
        """Compte le nombre d'assignations"""
        for task in self:
            task.planning_assignment_count = len(task.planning_assignment_ids)

    @api.depends('planning_assignment_ids')
    def _compute_planning_stats(self):
        """Calcule les statistiques de planning"""
        for task in self:
            task.planned_hours_total = sum(task.planning_assignment_ids.mapped('planned_hours'))
            task.actual_hours_total = sum(task.planning_assignment_ids.mapped('actual_hours'))

    def action_create_planning_task(self):
        """Crée une nouvelle tâche de planning à partir de cette tâche projet"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle tâche de planning'),
            'res_model': 'eazynova.planning.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': self.name,
                'default_project_id': self.project_id.id,
                'default_project_task_id': self.id,
                'default_description': self.description,
                'default_user_id': self.user_ids[0].id if self.user_ids else self.env.user.id,
            },
        }

    def action_view_planning_tasks(self):
        """Ouvre la vue des tâches de planning"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Tâches de planning'),
            'res_model': 'eazynova.planning.task',
            'view_mode': 'tree,form,calendar,gantt',
            'domain': [('project_task_id', '=', self.id)],
            'context': {
                'default_project_id': self.project_id.id,
                'default_project_task_id': self.id,
            },
        }

    def action_view_planning_assignments(self):
        """Ouvre la vue des assignations de ressources"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignations de ressources'),
            'res_model': 'eazynova.planning.assignment',
            'view_mode': 'tree,form,calendar,gantt',
            'domain': [('task_id', 'in', self.planning_task_ids.ids)],
            'context': {'create': False},
        }
