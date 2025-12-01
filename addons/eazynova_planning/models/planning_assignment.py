from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class PlanningAssignment(models.Model):
    _name = 'eazynova.planning.assignment'
    _description = 'Assignation de ressource EAZYNOVA (intervention ou chantier)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    # Champs pour filtres avancés
    client_id = fields.Many2one('res.partner', string='Client')
    donneur_ordre_id = fields.Many2one('res.partner', string="Donneur d'ordre")

    # Champs centraux pour la vue globale
    type = fields.Selection([
        ('intervention', 'Intervention'),
        ('chantier', 'Chantier'),
    ], string='Type', required=True, tracking=True)
    intervention_id = fields.Many2one('intervention.intervention', string='Intervention')
    chantier_id = fields.Many2one('chantier.chantier', string='Chantier')
    color = fields.Integer('Couleur')

    @api.model
    def create_from_interventions(self):
        """Crée des assignments à partir des interventions en cours."""
        interventions = self.env['eazynova_intervention.intervention'].search([('state', '=', 'in_progress')])
        for inter in interventions:
            self.create({
                'name': inter.name,
                'date_start': inter.date_start,
                'date_end': inter.date_end,
                'resource_id': inter.technician_id.id,
                'type': 'intervention',
                'intervention_id': inter.id,
                'client_id': inter.client_id.id if hasattr(inter, 'client_id') else False,
                'donneur_ordre_id': inter.donneur_ordre_id.id if hasattr(inter, 'donneur_ordre_id') else False,
            })

    @api.model
    def create_from_chantiers(self):
        """Crée des assignments à partir des chantiers en cours."""
        chantiers = self.env['eazynova_gestion_chantier.chantier'].search([('state', '=', 'in_progress')])
        for ch in chantiers:
            self.create({
                'name': ch.name,
                'date_start': ch.date_start,
                'date_end': ch.date_end,
                'resource_id': ch.responsible_id.id,
                'type': 'chantier',
                'chantier_id': ch.id,
                'client_id': ch.client_id.id if hasattr(ch, 'client_id') else False,
                'donneur_ordre_id': ch.donneur_ordre_id.id if hasattr(ch, 'donneur_ordre_id') else False,
            })

    @api.model
    def cron_sync_assignments(self):
        """Synchronisation automatique quotidienne du planning global."""
        self.env['eazynova.planning.assignment'].search([]).unlink()  # Reset pour éviter doublons
        self.create_from_interventions()
        self.create_from_chantiers()

    def action_view_calendar_event(self):
        """Ouvre l'événement calendrier lié à l'assignation"""
        self.ensure_one()
        if not self.calendar_event_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'res_id': self.calendar_event_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'create': False}
        }

    # Lien avec un événement calendrier Odoo
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string="Événement calendrier",
        ondelete='set null',
        help="Synchronisation automatique avec le calendrier Odoo."
    )

    def _sync_calendar_event(self):
        """Crée ou met à jour l'événement calendar.event lié à l'assignation."""
        CalendarEvent = self.env['calendar.event']
        for assignment in self:
            vals = {
                'name': assignment.name or _('Assignation'),
                'start': assignment.date_start,
                'stop': assignment.date_end,
                'user_id': assignment.resource_id.user_id.id if assignment.resource_id.user_id else self.env.user.id,
                'allday': False,
                'description': assignment.notes or '',
                'active': True,
            }
            if assignment.calendar_event_id:
                assignment.calendar_event_id.write(vals)
            else:
                event = CalendarEvent.create(vals)
                assignment.calendar_event_id = event.id

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._sync_calendar_event()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._sync_calendar_event()
        return res

    def unlink(self):
        # Supprimer l'événement calendrier lié si présent
        for assignment in self:
            if assignment.calendar_event_id:
                assignment.calendar_event_id.unlink()
        return super().unlink()

    name = fields.Char(string="Nom", compute='_compute_name', store=True)
    reference = fields.Char(
        string="Référence",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Tâche et ressource
    task_id = fields.Many2one(
        'eazynova.planning.task',
        string="Tâche",
        required=True,
        ondelete='cascade',
        tracking=True
    )
    resource_id = fields.Many2one(
        'eazynova.planning.resource',
        string="Ressource",
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # Dates (héritées de la tâche par défaut)
    date_start = fields.Datetime(
        string="Date de début", required=True, tracking=True)
    date_end = fields.Datetime(
        string="Date de fin", required=True, tracking=True)
    duration = fields.Float(
        string="Durée (heures)",
        compute='_compute_duration',
        store=True
    )

    # Allocation
    allocation_percentage = fields.Float(
        string="Allocation (%)",
        default=100.0,
        help="Pourcentage d'allocation de la ressource (0-100)"
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', required=True, tracking=True)

    # Informations de la tâche (fields related pour faciliter les recherches)
    task_name = fields.Char(related='task_id.name',
                            string="Nom de la tâche", store=True)
    task_priority = fields.Selection(related='task_id.priority', store=True)
    task_state = fields.Selection(related='task_id.state', store=True)

    # Informations de la ressource
    resource_name = fields.Char(
        related='resource_id.name', string="Nom de la ressource", store=True)
    resource_type = fields.Selection(
        related='resource_id.resource_type', store=True)

    # Temps et coûts
    planned_hours = fields.Float(string="Heures planifiées")
    actual_hours = fields.Float(string="Heures réelles")
    cost = fields.Float(string="Coût", compute='_compute_cost', store=True)

    # Responsable
    user_id = fields.Many2one(
        'res.users',
        string="Responsable",
        default=lambda self: self.env.user,
        tracking=True
    )

    # Notes
    notes = fields.Text(string="Notes")

    # Conflit
    has_conflict = fields.Boolean(
        string="Conflit détecté",
        compute='_compute_has_conflict',
        store=False
    )
    conflict_details = fields.Text(
        string="Détails du conflit",
        compute='_compute_has_conflict',
        store=False
    )

    # Société
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )

    # Couleur
    color = fields.Integer(string="Couleur", default=0)

    @api.model
    def create(self, vals):
        """Génère la référence à la création"""
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'eazynova.planning.assignment') or _('New')

        # Si les dates ne sont pas fournies, prendre celles de la tâche
        if 'task_id' in vals and not ('date_start' in vals and 'date_end' in vals):
            task = self.env['eazynova.planning.task'].browse(vals['task_id'])
            if task:
                vals.setdefault('date_start', task.date_start)
                vals.setdefault('date_end', task.date_end)

        return super(PlanningAssignment, self).create(vals)

    @api.depends('task_id', 'resource_id')
    def _compute_name(self):
        """Génère le nom de l'assignation"""
        for assignment in self:
            if assignment.task_id and assignment.resource_id:
                assignment.name = f"{assignment.task_id.name} - {assignment.resource_id.name}"
            else:
                assignment.name = _("Nouvelle assignation")

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        """Calcule la durée de l'assignation"""
        for assignment in self:
            if assignment.date_start and assignment.date_end:
                delta = assignment.date_end - assignment.date_start
                assignment.duration = delta.total_seconds() / 3600.0
            else:
                assignment.duration = 0.0

    @api.depends('duration', 'resource_id.cost_per_hour', 'allocation_percentage')
    def _compute_cost(self):
        """Calcule le coût de l'assignation"""
        for assignment in self:
            if assignment.resource_id and assignment.resource_id.cost_per_hour:
                hours = assignment.duration * \
                    (assignment.allocation_percentage / 100.0)
                assignment.cost = hours * assignment.resource_id.cost_per_hour
            else:
                assignment.cost = 0.0

    @api.depends('resource_id', 'date_start', 'date_end', 'state')
    def _compute_has_conflict(self):
        """Détecte les conflits d'assignation, y compris week-end et jours fériés selon la ressource"""
        import datetime
        for assignment in self:
            if not assignment.resource_id or not assignment.date_start or not assignment.date_end:
                assignment.has_conflict = False
                assignment.conflict_details = ""
                continue

            # Conflits d'assignation
            overlapping = self.search([
                ('resource_id', '=', assignment.resource_id.id),
                ('id', '!=', assignment.id),
                ('state', 'not in', ('cancelled', 'done')),
                '|',
                '&', ('date_start', '<=', assignment.date_start), ('date_end',
                                                                   '>=', assignment.date_start),
                '&', ('date_start', '<=', assignment.date_end), ('date_end',
                                                                 '>=', assignment.date_end),
            ])

            # Conflits d'absence
            absences = self.env['eazynova.planning.absence'].search([
                ('resource_id', '=', assignment.resource_id.id),
                ('state', '=', 'approved'),
                '|',
                '&', ('date_start', '<=', assignment.date_start), ('date_end',
                                                                   '>=', assignment.date_start),
                '&', ('date_start', '<=', assignment.date_end), ('date_end',
                                                                 '>=', assignment.date_end),
            ])

            conflicts = []
            if overlapping:
                conflicts.append(
                    f"Chevauche {len(overlapping)} autre(s) assignation(s)")
            if absences:
                conflicts.append(
                    f"La ressource est absente ({', '.join(absences.mapped('name'))})")

            # Vérification week-end
            current = assignment.date_start
            while current <= assignment.date_end:
                if current.weekday() >= 5 and not assignment.resource_id.work_weekend:
                    conflicts.append(_(
                        "Week-end non autorisé pour cette ressource (%s)" % current.strftime(
                            '%A')
                    ))
                    break
                current += datetime.timedelta(days=1)

            # Vérification jours fériés
            calendar = assignment.resource_id.calendar_id
            if calendar and calendar.holiday_ids and not assignment.resource_id.work_holidays:
                holidays = calendar.holiday_ids.mapped('date')
                current = assignment.date_start.date()
                end = assignment.date_end.date()
                while current <= end:
                    if current in holidays:
                        conflicts.append(_(
                            "Jour férié non autorisé pour cette ressource (%s)" % current.strftime(
                                '%Y-%m-%d')
                        ))
                        break
                    current += datetime.timedelta(days=1)

            assignment.has_conflict = bool(conflicts)
            assignment.conflict_details = "\n".join(
                conflicts) if conflicts else ""

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Vérifie la cohérence des dates"""
        for assignment in self:
            if assignment.date_start and assignment.date_end:
                if assignment.date_end <= assignment.date_start:
                    raise ValidationError(
                        _(
                            "La date de fin doit être postérieure à la date de début."
                        )
                    )

    @api.constrains('allocation_percentage')
    def _check_allocation(self):
        """Vérifie que l'allocation est valide"""
        for assignment in self:
            if (
                assignment.allocation_percentage < 0 or assignment.allocation_percentage > 100
            ):
                raise ValidationError(
                    _(
                        "L'allocation doit être entre 0 et 100%."
                    )
                )

    def action_confirm(self):
        """Confirme l'assignation"""
        # Vérifier les conflits
        for assignment in self:
            if assignment.has_conflict:
                raise UserError(
                    _(
                        "Impossible de confirmer l'assignation : conflit détecté.\n\n%s"
                    ) % assignment.conflict_details
                )

        self.write({'state': 'confirmed'})

    def action_start(self):
        """Démarre l'assignation"""
        self.write({'state': 'in_progress'})

    def action_done(self):
        """Termine l'assignation"""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Annule l'assignation"""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Remet en brouillon"""
        self.write({'state': 'draft'})

    def action_view_task(self):
        """Ouvre la tâche liée"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tâche'),
            'res_model': 'eazynova.planning.task',
            'res_id': self.task_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_resource(self):
        """Ouvre la ressource liée"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ressource'),
            'res_model': 'eazynova.planning.resource',
            'res_id': self.resource_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
