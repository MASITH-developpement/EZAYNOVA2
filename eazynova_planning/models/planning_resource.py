# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PlanningResource(models.Model):
    # Peut travailler le week-end ?
    work_weekend = fields.Boolean(
        string="Travaille le week-end",
        default=False,
        help="Si coché, la ressource peut être planifiée le samedi/dimanche."
    )
    # Peut travailler les jours fériés ?
    work_holidays = fields.Boolean(
        string="Travaille les jours fériés",
        default=False,
        help="Si coché, la ressource peut être planifiée les jours fériés."
    )
    _name = 'eazynova.planning.resource'
    _description = 'Ressource de planning EAZYNOVA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    def onchange(self):
        # Méthode onchange requise par Odoo, peut être personnalisée si besoin
        pass


class PlanningResource(models.Model):
    # Peut travailler le week-end ?
    work_weekend = fields.Boolean(
        string="Travaille le week-end",
        default=False,
        help="Si coché, la ressource peut être planifiée le samedi/dimanche."
    )
    # Peut travailler les jours fériés ?
    work_holidays = fields.Boolean(
        string="Travaille les jours fériés",
        default=False,
        help="Si coché, la ressource peut être planifiée les jours fériés."
    )
    _name = 'eazynova.planning.resource'
    _description = 'Ressource de planning EAZYNOVA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Nom", required=True, tracking=True)
    code = fields.Char(string="Code", required=True, copy=False)
    active = fields.Boolean(string="Actif", default=True, tracking=True)

    # Type de ressource
    resource_type = fields.Selection([
        ('human', 'Humaine'),
        ('equipment', 'Équipement'),
        ('vehicle', 'Véhicule'),
        ('material', 'Matériel'),
        ('other', 'Autre'),
    ],
        string="Type de ressource",
        required=True,
        default='human',
        tracking=True
    )

    # Lien avec employé (si ressource humaine)
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employé",
        tracking=True,
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        'res.users',
        string="Utilisateur",
        related='employee_id.user_id',
        store=True
    )

    # Compétences
    skill_ids = fields.Many2many(
        'eazynova.planning.resource.skill',
        'resource_skill_rel',
        string="Compétences"
    )

    # Disponibilité
    calendar_id = fields.Many2one(
        'eazynova.planning.calendar',
        string="Calendrier",
        help="Calendrier de disponibilité de la ressource"
    )

    # Capacité
    capacity = fields.Float(
        string="Capacité",
        default=1.0,
        help="Capacité de la ressource (ex: 1.0 = temps plein, 0.5 = mi-temps)"
    )
    cost_per_hour = fields.Float(
        string="Coût horaire",
        help="Coût horaire de la ressource"
    )

    # Assignations
    assignment_ids = fields.One2many(
        'eazynova.planning.assignment',
        'resource_id',
        string="Assignations"
    )
    assignment_count = fields.Integer(
        string="Nombre d'assignations",
        compute='_compute_assignment_count'
    )

    # Absences
    absence_ids = fields.One2many(
        'eazynova.planning.absence',
        'resource_id',
        string="Absences"
    )
    absence_count = fields.Integer(
        string="Nombre d'absences",
        compute='_compute_absence_count'
    )

    # Informations équipement
    equipment_serial = fields.Char(string="Numéro de série")
    equipment_model = fields.Char(string="Modèle")
    equipment_manufacturer = fields.Char(string="Fabricant")
    equipment_year = fields.Integer(string="Année")

    # Maintenance (pour équipements)
    last_maintenance_date = fields.Date(string="Dernière maintenance")
    next_maintenance_date = fields.Date(string="Prochaine maintenance")
    maintenance_interval_days = fields.Integer(
        string="Intervalle de maintenance (jours)",
        default=90
    )

    # Localisation
    location = fields.Char(string="Localisation actuelle")

    # Société
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company
    )

    # Description
    description = fields.Text(string="Description")
    notes = fields.Text(string="Notes")

    # Statut calculé
    availability_status = fields.Selection([
        ('available', 'Disponible'),
        ('busy', 'Occupé'),
        ('absent', 'Absent'),
        ('maintenance', 'En maintenance'),
    ], string="Statut", compute='_compute_availability_status')

    # Couleur pour visualisation
    color = fields.Integer(string="Couleur", default=0)

    @api.depends('assignment_ids')
    def _compute_assignment_count(self):
        """Compte le nombre d'assignations"""
        for resource in self:
            resource.assignment_count = len(resource.assignment_ids)

    @api.depends('absence_ids')
    def _compute_absence_count(self):
        """Compte le nombre d'absences"""
        for resource in self:
            resource.absence_count = len(resource.absence_ids)

    @api.depends('assignment_ids', 'absence_ids')
    def _compute_availability_status(self):
        """Calcule le statut de disponibilité"""
        now = fields.Datetime.now()

        for resource in self:
            # Vérifier les absences en cours
            current_absences = resource.absence_ids.filtered(
                lambda a: (
                    a.date_start <= now <= a.date_end and a.state == 'approved'
                )
            )

            if current_absences:
                # Vérifier si c'est une maintenance
                if any(
                    a.absence_type == 'maintenance' for a in current_absences
                ):
                    resource.availability_status = 'maintenance'
                else:
                    resource.availability_status = 'absent'
                continue

            # Vérifier les assignations en cours
            current_assignments = resource.assignment_ids.filtered(
                lambda a: a.date_start <= now <= a.date_end and a.state in (
                    'confirmed', 'in_progress')
            )

            if current_assignments:
                resource.availability_status = 'busy'
            else:
                resource.availability_status = 'available'

    @api.constrains('code')
    def _check_code_unique(self):
        """Vérifie l'unicité du code"""
        for resource in self:
            if self.search_count([
                ('code', '=', resource.code),
                ('id', '!=', resource.id)
            ]) > 0:
                raise ValidationError(
                    _("Le code de la ressource doit être unique.")
                )

    def action_view_assignments(self):
        """Ouvre la vue des assignations"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assignations'),
            'res_model': 'eazynova.planning.assignment',
            'view_mode': 'tree,form,calendar,gantt',
            'domain': [('resource_id', '=', self.id)],
            'context': {'default_resource_id': self.id},
        }

    def action_view_absences(self):
        """Ouvre la vue des absences"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Absences'),
            'res_model': 'eazynova.planning.absence',
            'view_mode': 'tree,form,calendar',
            'domain': [('resource_id', '=', self.id)],
            'context': {'default_resource_id': self.id},
        }

    def get_availability(self, date_start, date_end):
        """
        Retourne la disponibilité de la ressource pour une période donnée,
        en tenant compte des week-ends et jours fériés
        """
        self.ensure_one()

        # Vérifier les absences
        absences = self.env['eazynova.planning.absence'].search([
            ('resource_id', '=', self.id),
            ('state', '=', 'approved'),
            '|',
            '&',
            ('date_start', '<=', date_start),
            ('date_end', '>=', date_start),
            '&', ('date_start', '<=', date_end), ('date_end', '>=', date_end),
        ])
        if absences:
            return {
                'available': False,
                'reason': 'absence',
                'details': absences.mapped('name')
            }

        # Vérifier les assignations existantes
        assignments = self.env['eazynova.planning.assignment'].search([
            ('resource_id', '=', self.id),
            ('state', 'in', ('confirmed', 'in_progress')),
            '|',
            '&',
            ('date_start', '<=', date_start),
            ('date_end', '>=', date_start),
            '&', ('date_start', '<=', date_end), ('date_end', '>=', date_end),
        ])
        if assignments:
            return {
                'available': False,
                'reason': 'busy',
                'details': assignments.mapped('task_id.name')
            }

        # Vérifier week-end
        import datetime
        current = date_start
        while current <= date_end:
            if current.weekday() >= 5 and not self.work_weekend:
                return {
                    'available': False,
                    'reason': 'weekend',
                    'details': [
                        _(
                            "Week-end non autorisé pour cette ressource ("
                            + current.strftime('%A')
                            + ")"
                        )
                    ]
                }
            current += datetime.timedelta(days=1)

        # Vérifier jours fériés
        if (
            self.calendar_id and
            self.calendar_id.holiday_ids and
            not self.work_holidays
        ):
            holidays = self.calendar_id.holiday_ids.mapped('date')
            current = date_start.date()
            end = date_end.date()
            while current <= end:
                if current in holidays:
                    return {
                        'available': False,
                        'reason': 'holiday',
                        'details': [
                            _(
                                "Jour férié non autorisé pour cette ressource ("
                                + current.strftime('%Y-%m-%d')
                                + ")"
                            )
                        ]
                    }
                current += datetime.timedelta(days=1)

        return {
            'available': True,
            'reason': None,
            'details': []
        }

    def action_create_absence(self):
        """Crée une nouvelle absence pour la ressource"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle absence'),
            'res_model': 'eazynova.planning.absence',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_resource_id': self.id},
        }
