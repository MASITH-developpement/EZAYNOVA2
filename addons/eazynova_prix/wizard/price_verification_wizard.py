# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class PriceVerificationWizard(models.TransientModel):
    """Assistant de vérification des prix"""
    _name = 'eazynova.price.verification.wizard'
    _description = 'Assistant Vérification de Prix'

    product_ids = fields.Many2many(
        'product.product',
        string='Articles à vérifier',
        required=True
    )

    source_id = fields.Many2one(
        'eazynova.price.source',
        string='Source de prix',
        required=True,
        domain=[('active', '=', True)]
    )

    check_sale_price = fields.Boolean(
        string='Vérifier prix de vente',
        default=True
    )

    check_cost_price = fields.Boolean(
        string='Vérifier prix de revient',
        default=True
    )

    auto_update = fields.Boolean(
        string='Mettre à jour automatiquement',
        help='Mettre à jour les prix si l\'écart est acceptable'
    )

    max_diff_auto_update = fields.Float(
        string='Écart max pour màj auto (%)',
        default=10.0
    )

    @api.model
    def default_get(self, fields_list):
        """Définit les valeurs par défaut"""
        res = super().default_get(fields_list)

        # Source par défaut
        if 'source_id' in fields_list:
            default_source = self.env['eazynova.price.source'].search([
                ('active', '=', True)
            ], limit=1)
            if default_source:
                res['source_id'] = default_source.id

        # Produits depuis le contexte
        if 'product_ids' in fields_list and self.env.context.get('active_model') == 'product.template':
            active_ids = self.env.context.get('active_ids', [])
            if active_ids:
                templates = self.env['product.template'].browse(active_ids)
                product_ids = templates.mapped('product_variant_ids').ids
                res['product_ids'] = [(6, 0, product_ids)]

        return res

    def action_verify_prices(self):
        """Lance la vérification des prix"""
        self.ensure_one()

        if not self.product_ids:
            raise UserError('Veuillez sélectionner au moins un article.')

        if not self.check_sale_price and not self.check_cost_price:
            raise UserError('Veuillez sélectionner au moins un type de prix à vérifier.')

        # Créer les vérifications
        checks = self.env['eazynova.price.check']

        for product in self.product_ids:
            check_vals = {
                'product_id': product.id,
                'source_id': self.source_id.id,
                'current_sale_price': product.product_tmpl_id.list_price,
                'current_cost_price': product.product_tmpl_id.standard_price,
            }

            # Simuler la récupération des prix de référence
            # TODO: Implémenter la vraie récupération depuis l'API
            check_vals['reference_sale_price'] = product.product_tmpl_id.list_price
            check_vals['reference_cost_price'] = product.product_tmpl_id.standard_price

            check = self.env['eazynova.price.check'].create(check_vals)
            checks |= check

            # Mise à jour automatique si activée
            if self.auto_update:
                max_diff = max(abs(check.sale_price_diff), abs(check.cost_price_diff))
                if max_diff > 0 and max_diff <= self.max_diff_auto_update:
                    check.action_apply_reference_prices()

        # Afficher les résultats
        return {
            'name': 'Résultats de la vérification',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.price.check',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', checks.ids)],
            'target': 'current',
        }
