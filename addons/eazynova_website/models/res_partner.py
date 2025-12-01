# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    """Extension du partenaire pour les informations SaaS"""
    _inherit = 'res.partner'

    # Relation avec les abonnements SaaS
    saas_subscription_ids = fields.One2many(
        'saas.subscription',
        'partner_id',
        string='Abonnements SaaS',
    )
    saas_subscription_count = fields.Integer(
        string='Nombre d\'abonnements',
        compute='_compute_saas_subscription_count',
    )
    is_saas_customer = fields.Boolean(
        string='Client SaaS',
        compute='_compute_is_saas_customer',
        store=True,
    )

    # Abonnement actif principal
    active_subscription_id = fields.Many2one(
        'saas.subscription',
        string='Abonnement actif',
        compute='_compute_active_subscription',
        store=True,
    )

    @api.depends('saas_subscription_ids')
    def _compute_saas_subscription_count(self):
        for partner in self:
            partner.saas_subscription_count = len(partner.saas_subscription_ids)

    @api.depends('saas_subscription_ids')
    def _compute_is_saas_customer(self):
        for partner in self:
            partner.is_saas_customer = bool(partner.saas_subscription_ids)

    @api.depends('saas_subscription_ids', 'saas_subscription_ids.state')
    def _compute_active_subscription(self):
        for partner in self:
            active = partner.saas_subscription_ids.filtered(
                lambda s: s.state in ['trial', 'active']
            )
            partner.active_subscription_id = active[0] if active else False

    def action_view_saas_subscriptions(self):
        """Voir les abonnements SaaS du partenaire"""
        self.ensure_one()
        return {
            'name': f'Abonnements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'saas.subscription',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
