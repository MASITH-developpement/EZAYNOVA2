# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class PlanningConflictWizard(models.TransientModel):
    _name = 'eazynova.planning.conflict.wizard'
    _description = 'Assistant de gestion des conflits de planning'

    name = fields.Char(string="Titre", default="Conflits de planning détectés")

    # Ligne de conflit
    conflict_line_ids = fields.One2many(
        'eazynova.planning.conflict.line',
        'wizard_id',
        string="Conflits"
    )
    conflict_count = fields.Integer(
        string="Nombre de conflits",
        compute='_compute_conflict_count'
    )

    # Résolution
    resolution_action = fields.Selection([
        ('ignore', 'Ignorer les conflits'),
        ('reschedule', 'Reprogrammer'),
        ('reassign', 'Réassigner les ressources'),
        ('cancel', 'Annuler les assignations conflictuelles'),
    ], string="Action de résolution")

    message = fields.Html(string="Message")

    @api.depends('conflict_line_ids')
    def _compute_conflict_count(self):
        """Compte le nombre de conflits"""
        for wizard in self:
            wizard.conflict_count = len(wizard.conflict_line_ids)

    @api.model
    def default_get(self, fields_list):
        """Détecte automatiquement les conflits"""
        res = super().default_get(fields_list)

        # Rechercher les conflits
        conflicts = self._detect_conflicts()

        if conflicts:
            res['conflict_line_ids'] = [(0, 0, conflict) for conflict in conflicts]
            res['message'] = self._generate_conflict_message(conflicts)

        return res

    def _detect_conflicts(self):
        """Détecte tous les conflits de planning"""
        conflicts = []

        # Conflits d'assignation (ressource assignée plusieurs fois)
        assignments = self.env['eazynova.planning.assignment'].search([
            ('state', 'in', ('confirmed', 'in_progress'))
        ])

        for assignment in assignments:
            if assignment.has_conflict:
                conflicts.append({
                    'conflict_type': 'assignment',
                    'assignment_id': assignment.id,
                    'resource_id': assignment.resource_id.id,
                    'description': assignment.conflict_details,
                })

        # Conflits absence/assignation
        absences = self.env['eazynova.planning.absence'].search([
            ('state', '=', 'approved')
        ])

        for absence in absences:
            conflict_assignments = absence.check_assignment_conflicts()
            if conflict_assignments:
                for assignment in conflict_assignments:
                    conflicts.append({
                        'conflict_type': 'absence_conflict',
                        'assignment_id': assignment.id,
                        'absence_id': absence.id,
                        'resource_id': absence.resource_id.id,
                        'description': f"La ressource {absence.resource_id.name} est absente ({absence.name})",
                    })

        return conflicts

    def _generate_conflict_message(self, conflicts):
        """Génère un message HTML décrivant les conflits"""
        message = f"""
        <div style="padding: 10px;">
            <h4 style="color: #d9534f;">⚠️ {len(conflicts)} conflit(s) détecté(s)</h4>
            <p>Les conflits suivants ont été détectés dans votre planning :</p>
            <ul>
        """

        for conflict in conflicts[:10]:  # Limiter à 10 pour l'affichage
            message += f"<li>{conflict.get('description', 'Conflit non détaillé')}</li>"

        if len(conflicts) > 10:
            message += f"<li><em>... et {len(conflicts) - 10} autre(s) conflit(s)</em></li>"

        message += """
            </ul>
            <p>Veuillez choisir une action de résolution ci-dessous.</p>
        </div>
        """

        return message

    def action_resolve_conflicts(self):
        """Résout les conflits selon l'action sélectionnée"""
        self.ensure_one()

        if not self.resolution_action:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Erreur"),
                    'message': _("Veuillez sélectionner une action de résolution."),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        if self.resolution_action == 'ignore':
            return self.action_ignore_conflicts()
        elif self.resolution_action == 'reschedule':
            return self.action_reschedule()
        elif self.resolution_action == 'reassign':
            return self.action_reassign()
        elif self.resolution_action == 'cancel':
            return self.action_cancel_conflicts()

    def action_ignore_conflicts(self):
        """Ignore les conflits et continue"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Conflits ignorés"),
                'message': _("Les conflits ont été ignorés. Veuillez les résoudre manuellement."),
                'type': 'info',
                'sticky': False,
            }
        }

    def action_reschedule(self):
        """Ouvre un wizard pour reprogrammer les tâches"""
        # TODO: Implémenter la reprogrammation automatique
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Fonctionnalité en développement"),
                'message': _("La reprogrammation automatique sera bientôt disponible."),
                'type': 'info',
                'sticky': False,
            }
        }

    def action_reassign(self):
        """Réassigne automatiquement les ressources"""
        # TODO: Implémenter la réassignation automatique
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Fonctionnalité en développement"),
                'message': _("La réassignation automatique sera bientôt disponible."),
                'type': 'info',
                'sticky': False,
            }
        }

    def action_cancel_conflicts(self):
        """Annule les assignations en conflit"""
        self.ensure_one()

        cancelled_count = 0
        for line in self.conflict_line_ids:
            if line.assignment_id and line.assignment_id.state not in ('done', 'cancelled'):
                line.assignment_id.action_cancel()
                cancelled_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Conflits résolus"),
                'message': _("%d assignation(s) annulée(s).") % cancelled_count,
                'type': 'success',
                'sticky': False,
            }
        }


class PlanningConflictLine(models.TransientModel):
    _name = 'eazynova.planning.conflict.line'
    _description = 'Ligne de conflit de planning'

    wizard_id = fields.Many2one(
        'eazynova.planning.conflict.wizard',
        string="Wizard",
        required=True,
        ondelete='cascade'
    )

    conflict_type = fields.Selection([
        ('assignment', 'Assignation double'),
        ('absence_conflict', 'Conflit absence/assignation'),
        ('capacity', 'Dépassement de capacité'),
        ('skill', 'Compétence manquante'),
    ], string="Type de conflit")

    assignment_id = fields.Many2one(
        'eazynova.planning.assignment',
        string="Assignation"
    )
    absence_id = fields.Many2one(
        'eazynova.planning.absence',
        string="Absence"
    )
    resource_id = fields.Many2one(
        'eazynova.planning.resource',
        string="Ressource"
    )

    description = fields.Text(string="Description")

    def action_view_assignment(self):
        """Ouvre l'assignation"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.planning.assignment',
            'res_id': self.assignment_id.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_resource(self):
        """Ouvre la ressource"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.planning.resource',
            'res_id': self.resource_id.id,
            'view_mode': 'form',
            'target': 'new',
        }
