# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaasPlan(models.Model):
    """Plan d'abonnement SaaS EAZYNOVA"""
    _name = 'saas.plan'
    _description = 'Plan d\'abonnement SaaS'
    _order = 'sequence, id'

    name = fields.Char(
        string='Nom du plan',
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10,
    )
    description = fields.Html(
        string='Description',
        translate=True,
    )
    active = fields.Boolean(
        string='Actif',
        default=True,
    )

    # Tarification
    monthly_price = fields.Monetary(
        string='Prix mensuel (HT)',
        required=True,
        currency_field='currency_id',
        help='Prix de base pour le nombre d\'utilisateurs inclus',
    )
    setup_fee = fields.Monetary(
        string='Frais de configuration (HT)',
        currency_field='currency_id',
        help='Frais uniques de configuration et mise en place',
    )
    included_users = fields.Integer(
        string='Utilisateurs inclus',
        required=True,
        default=5,
        help='Nombre d\'utilisateurs inclus dans le prix de base',
    )
    extra_user_price = fields.Monetary(
        string='Prix par utilisateur supplémentaire (HT)',
        currency_field='currency_id',
        help='Prix mensuel par utilisateur au-delà du nombre inclus',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # Essai gratuit
    trial_days = fields.Integer(
        string='Jours d\'essai gratuit',
        default=30,
        help='Durée de la période d\'essai en jours',
    )

    # Fonctionnalités
    feature_ids = fields.Many2many(
        'saas.plan.feature',
        string='Fonctionnalités',
    )

    # Modules Odoo à installer
    module_ids = fields.Many2many(
        'ir.module.module',
        string='Modules à installer',
        domain=[('state', '=', 'installed')],
        help='Modules Odoo à installer automatiquement lors du provisioning',
    )

    # Limitations
    max_users = fields.Integer(
        string='Nombre maximum d\'utilisateurs',
        help='0 = illimité',
    )
    max_storage_gb = fields.Integer(
        string='Stockage maximum (GB)',
        default=10,
        help='Espace de stockage maximum autorisé',
    )

    # Statistiques
    subscription_count = fields.Integer(
        string='Nombre d\'abonnements',
        compute='_compute_subscription_count',
    )

    @api.depends('name')
    def _compute_subscription_count(self):
        for plan in self:
            plan.subscription_count = self.env['saas.subscription'].search_count([
                ('plan_id', '=', plan.id),
                ('state', 'in', ['trial', 'active']),
            ])

    def action_view_subscriptions(self):
        """Afficher les abonnements du plan"""
        self.ensure_one()
        return {
            'name': f'Abonnements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'saas.subscription',
            'view_mode': 'tree,form',
            'domain': [('plan_id', '=', self.id)],
            'context': {'default_plan_id': self.id},
        }


class SaasPlanFeature(models.Model):
    """Fonctionnalité d'un plan SaaS"""
    _name = 'saas.plan.feature'
    _description = 'Fonctionnalité de plan SaaS'
    _order = 'sequence, id'

    name = fields.Char(
        string='Fonctionnalité',
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10,
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    icon = fields.Char(
        string='Icône',
        help='Classe CSS de l\'icône (ex: fa-check, fa-star)',
        default='fa-check',
    )
