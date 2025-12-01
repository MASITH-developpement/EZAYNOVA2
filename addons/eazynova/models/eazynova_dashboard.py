# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EazynovaDashboard(models.Model):
    _name = 'eazynova.dashboard'
    _description = 'Tableau de bord EAZYNOVA'
    _order = 'sequence, id'

    name = fields.Char(string="Nom", required=True)
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(string="Actif", default=True)

    # Configuration
    dashboard_type = fields.Selection([
        ('kpi', 'KPI / Indicateurs'),
        ('chart', 'Graphique'),
        ('list', 'Liste'),
        ('custom', 'Personnalisé'),
    ], string="Type de tableau de bord", required=True, default='kpi')

    model_id = fields.Many2one(
        'ir.model',
        string="Modèle",
        help="Modèle Odoo source des données"
    )

    domain = fields.Char(
        string="Domaine",
        default='[]',
        help="Filtre de domaine Odoo pour les données"
    )

    # Données calculées
    value = fields.Float(string="Valeur", compute='_compute_value', store=False)
    label = fields.Char(string="Libellé", compute='_compute_value', store=False)

    # Permissions
    group_ids = fields.Many2many(
        'res.groups',
        string="Groupes autorisés",
        help="Groupes pouvant voir ce tableau de bord"
    )

    user_ids = fields.Many2many(
        'res.users',
        string="Utilisateurs autorisés",
        help="Utilisateurs spécifiques pouvant voir ce tableau de bord"
    )

    # Personnalisation
    color = fields.Char(
        string="Couleur",
        default="#1f77b4",
        help="Couleur du tableau de bord (format hex)"
    )

    icon = fields.Char(
        string="Icône",
        default="fa-dashboard",
        help="Classe d'icône Font Awesome"
    )

    @api.depends('model_id', 'domain', 'dashboard_type')
    def _compute_value(self):
        """Calcule les valeurs du tableau de bord"""
        for dashboard in self:
            try:
                if not dashboard.model_id:
                    dashboard.value = 0
                    dashboard.label = _("Non configuré")
                    continue

                model = self.env[dashboard.model_id.model]
                domain = eval(dashboard.domain) if dashboard.domain else []

                if dashboard.dashboard_type == 'kpi':
                    # Compte le nombre d'enregistrements
                    dashboard.value = model.search_count(domain)
                    dashboard.label = dashboard.name
                else:
                    dashboard.value = 0
                    dashboard.label = dashboard.name

            except Exception as e:
                _logger.error(f"Erreur lors du calcul du tableau de bord {dashboard.name}: {str(e)}")
                dashboard.value = 0
                dashboard.label = _("Erreur")

    def action_view_records(self):
        """Ouvre la vue des enregistrements associés"""
        self.ensure_one()

        if not self.model_id:
            raise UserError(_("Aucun modèle configuré pour ce tableau de bord"))

        domain = eval(self.domain) if self.domain else []

        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': self.model_id.model,
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'create': False},
        }


class EazynovaDashboardWidget(models.Model):
    _name = 'eazynova.dashboard.widget'
    _description = 'Widget de tableau de bord EAZYNOVA'
    _order = 'sequence, id'

    name = fields.Char(string="Nom", required=True)
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(string="Actif", default=True)

    widget_type = fields.Selection([
        ('stat', 'Statistique'),
        ('chart_line', 'Graphique linéaire'),
        ('chart_bar', 'Graphique en barres'),
        ('chart_pie', 'Graphique circulaire'),
        ('table', 'Tableau'),
        ('activity', 'Activités récentes'),
    ], string="Type de widget", required=True, default='stat')

    # Configuration
    config = fields.Text(
        string="Configuration JSON",
        help="Configuration du widget au format JSON"
    )

    # Permissions
    group_ids = fields.Many2many(
        'res.groups',
        relation='eazynova_widget_group_rel',
        string="Groupes autorisés"
    )
