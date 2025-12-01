# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SubscriptionUpgradeWizard(models.TransientModel):
    """Wizard pour mettre à niveau un abonnement"""
    _name = 'subscription.upgrade.wizard'
    _description = 'Assistant de mise à niveau d\'abonnement'

    subscription_id = fields.Many2one(
        'saas.subscription',
        string='Abonnement',
        required=True,
        readonly=True,
    )
    current_nb_users = fields.Integer(
        string='Utilisateurs actuels',
        related='subscription_id.nb_users',
        readonly=True,
    )
    current_price = fields.Monetary(
        string='Prix actuel',
        related='subscription_id.monthly_price',
        readonly=True,
    )
    new_nb_users = fields.Integer(
        string='Nouveau nombre d\'utilisateurs',
        required=True,
        default=lambda self: self._default_new_nb_users(),
    )
    new_price = fields.Monetary(
        string='Nouveau prix',
        compute='_compute_new_price',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='subscription_id.currency_id',
        readonly=True,
    )
    price_difference = fields.Monetary(
        string='Différence',
        compute='_compute_new_price',
        currency_field='currency_id',
    )

    def _default_new_nb_users(self):
        subscription = self.env['saas.subscription'].browse(self._context.get('active_id'))
        return subscription.nb_users if subscription else 5

    @api.depends('new_nb_users', 'subscription_id')
    def _compute_new_price(self):
        for wizard in self:
            if wizard.subscription_id and wizard.subscription_id.plan_id:
                plan = wizard.subscription_id.plan_id
                base_price = plan.monthly_price
                extra_users = max(0, wizard.new_nb_users - plan.included_users)
                extra_price = extra_users * plan.extra_user_price

                wizard.new_price = base_price + extra_price
                wizard.price_difference = wizard.new_price - wizard.current_price
            else:
                wizard.new_price = 0.0
                wizard.price_difference = 0.0

    @api.constrains('new_nb_users')
    def _check_new_nb_users(self):
        for wizard in self:
            if wizard.new_nb_users < 1:
                raise UserError(_('Le nombre d\'utilisateurs doit être au moins 1.'))
            if wizard.subscription_id.plan_id.max_users > 0 and wizard.new_nb_users > wizard.subscription_id.plan_id.max_users:
                raise UserError(_('Le nombre maximum d\'utilisateurs pour ce plan est %d.') % wizard.subscription_id.plan_id.max_users)

    def action_upgrade(self):
        """Appliquer la mise à niveau"""
        self.ensure_one()

        if self.new_nb_users == self.current_nb_users:
            raise UserError(_('Le nombre d\'utilisateurs n\'a pas changé.'))

        # Mettre à jour l'abonnement
        self.subscription_id.write({
            'nb_users': self.new_nb_users,
        })

        # Mettre à jour l'instance
        if self.subscription_id.instance_id:
            self.subscription_id.instance_id.write({
                'max_users': self.new_nb_users,
            })

        # Si augmentation et abonnement actif, générer une facture prorata
        if self.new_nb_users > self.current_nb_users and self.subscription_id.state == 'active':
            # Ici vous pourriez créer une facture au prorata
            pass

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'message': _('L\'abonnement a été mis à jour avec succès.'),
                'type': 'success',
                'sticky': False,
            }
        }
