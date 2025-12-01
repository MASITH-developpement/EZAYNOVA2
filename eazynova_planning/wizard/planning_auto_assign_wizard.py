# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class PlanningAutoAssignWizard(models.TransientModel):
    _name = 'eazynova.planning.auto.assign.wizard'
    _description = 'Assistant d\'assignation automatique de ressources'

    task_id = fields.Many2one(
        'eazynova.planning.task',
        string="Tâche",
        required=True
    )

    # Critères de sélection
    resource_type = fields.Selection([
        ('human', 'Humaine'),
        ('equipment', 'Équipement'),
        ('vehicle', 'Véhicule'),
        ('material', 'Matériel'),
        ('other', 'Autre'),
    ], string="Type de ressource")

    skill_ids = fields.Many2many(
        'eazynova.planning.resource.skill',
        'wiz_auto_assign_skill_rel',
        string="Compétences requises"
    )

    required_count = fields.Integer(
        string="Nombre de ressources requises",
        default=1
    )

    # Options de recherche
    check_availability = fields.Boolean(
        string="Vérifier la disponibilité",
        default=True,
        help="Vérifier que les ressources sont disponibles sur la période"
    )

    ignore_absences = fields.Boolean(
        string="Ignorer les absences",
        default=False,
        help="Ne pas tenir compte des absences planifiées"
    )

    allow_conflicts = fields.Boolean(
        string="Autoriser les conflits",
        default=False,
        help="Autoriser l'assignation même en cas de conflit"
    )

    # Résultats
    available_resource_ids = fields.Many2many(
        'eazynova.planning.resource',
        'planning_auto_assign_resource_rel',
        string="Ressources disponibles",
        readonly=True
    )

    selected_resource_ids = fields.Many2many(
        'eazynova.planning.resource',
        'planning_auto_assign_selected_rel',
        string="Ressources sélectionnées"
    )

    # État
    state = fields.Selection([
        ('select_criteria', 'Critères de sélection'),
        ('select_resources', 'Sélection des ressources'),
        ('done', 'Terminé'),
    ], string="État", default='select_criteria')

    message = fields.Text(string="Message", readonly=True)

    def action_search_resources(self):
        """Recherche les ressources disponibles"""
        self.ensure_one()

        # Construire le domaine de recherche
        domain = [('active', '=', True)]

        if self.resource_type:
            domain.append(('resource_type', '=', self.resource_type))

        if self.skill_ids:
            domain.append(('skill_ids', 'in', self.skill_ids.ids))

        # Rechercher les ressources
        resources = self.env['eazynova.planning.resource'].search(domain)

        # Filtrer par disponibilité si demandé
        if self.check_availability and not self.allow_conflicts:
            available_resources = self.env['eazynova.planning.resource']

            for resource in resources:
                availability = resource.get_availability(
                    self.task_id.date_start,
                    self.task_id.date_end
                )

                if availability['available']:
                    available_resources |= resource
                elif self.ignore_absences and availability['reason'] != 'busy':
                    # Si on ignore les absences, on garde la ressource si elle n'est pas occupée
                    available_resources |= resource

            resources = available_resources

        self.available_resource_ids = resources

        # Pré-sélectionner les ressources si le nombre requis est spécifié
        if self.required_count and len(resources) >= self.required_count:
            self.selected_resource_ids = resources[:self.required_count]
        else:
            self.selected_resource_ids = resources

        # Message
        if not resources:
            self.message = _(
                "Aucune ressource disponible ne correspond aux critères.\n"
                "Essayez de modifier les critères de recherche."
            )
        else:
            self.message = _(
                "%d ressource(s) trouvée(s) correspondant aux critères.\n"
                "Sélectionnez les ressources à assigner."
            ) % len(resources)

        # Passer à l'étape suivante
        self.state = 'select_resources'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.planning.auto.assign.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_assign_resources(self):
        """Assigne les ressources sélectionnées à la tâche"""
        self.ensure_one()

        if not self.selected_resource_ids:
            raise UserError(_("Vous devez sélectionner au moins une ressource."))

        created_assignments = self.env['eazynova.planning.assignment']

        for resource in self.selected_resource_ids:
            # Vérifier les conflits si demandé
            if not self.allow_conflicts:
                availability = resource.get_availability(
                    self.task_id.date_start,
                    self.task_id.date_end
                )

                if not availability['available']:
                    _logger.warning(
                        f"Ressource {resource.name} non disponible: {availability['reason']}"
                    )
                    if not self.ignore_absences:
                        continue

            # Créer l'assignation
            assignment = self.env['eazynova.planning.assignment'].create({
                'task_id': self.task_id.id,
                'resource_id': resource.id,
                'date_start': self.task_id.date_start,
                'date_end': self.task_id.date_end,
                'state': 'draft',
            })

            created_assignments |= assignment

        self.state = 'done'
        self.message = _("%d assignation(s) créée(s) avec succès.") % len(created_assignments)

        # Ouvrir les assignations créées
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignations créées'),
            'res_model': 'eazynova.planning.assignment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_assignments.ids)],
            'context': {'create': False},
        }

    def action_back(self):
        """Retour à l'étape précédente"""
        self.state = 'select_criteria'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.planning.auto.assign.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_cancel(self):
        """Annule et ferme le wizard"""
        return {'type': 'ir.actions.act_window_close'}
