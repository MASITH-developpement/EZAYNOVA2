# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PriceCheck(models.Model):
    """Historique des vérifications de prix"""
    _name = 'eazynova.price.check'
    _description = 'Vérification de Prix'
    _order = 'check_date desc, id desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default='Nouveau'
    )

    check_date = fields.Datetime(
        string='Date de vérification',
        required=True,
        default=fields.Datetime.now,
        readonly=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Article',
        required=True,
        ondelete='cascade'
    )

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Modèle d\'article',
        related='product_id.product_tmpl_id',
        store=True
    )

    source_id = fields.Many2one(
        'eazynova.price.source',
        string='Source de prix',
        required=True,
        ondelete='restrict'
    )

    # Prix actuels
    current_sale_price = fields.Float(
        string='Prix de vente actuel',
        readonly=True
    )
    current_cost_price = fields.Float(
        string='Prix de revient actuel',
        readonly=True
    )

    # Prix de référence
    reference_sale_price = fields.Float(
        string='Prix de vente référence'
    )
    reference_cost_price = fields.Float(
        string='Prix de revient référence'
    )

    # Écarts
    sale_price_diff = fields.Float(
        string='Écart vente (%)',
        compute='_compute_price_diff',
        store=True
    )
    cost_price_diff = fields.Float(
        string='Écart coût (%)',
        compute='_compute_price_diff',
        store=True
    )

    # Statut
    status = fields.Selection([
        ('ok', 'Prix Correct'),
        ('warning', 'Attention'),
        ('alert', 'Alerte')
    ], string='Statut', compute='_compute_status', store=True)

    alert_level = fields.Selection([
        ('none', 'Aucune'),
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée')
    ], string='Niveau d\'alerte', compute='_compute_status', store=True)

    notes = fields.Text(
        string='Notes'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Vérifié par',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Génère la référence automatiquement"""
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('eazynova.price.check') or 'Nouveau'
        return super().create(vals_list)

    @api.depends('current_sale_price', 'reference_sale_price', 'current_cost_price', 'reference_cost_price')
    def _compute_price_diff(self):
        """Calcule les écarts de prix en pourcentage"""
        for check in self:
            # Écart prix de vente
            if check.reference_sale_price and check.reference_sale_price > 0:
                check.sale_price_diff = (
                    (check.current_sale_price - check.reference_sale_price) /
                    check.reference_sale_price * 100
                )
            else:
                check.sale_price_diff = 0.0

            # Écart prix de revient
            if check.reference_cost_price and check.reference_cost_price > 0:
                check.cost_price_diff = (
                    (check.current_cost_price - check.reference_cost_price) /
                    check.reference_cost_price * 100
                )
            else:
                check.cost_price_diff = 0.0

    @api.depends('sale_price_diff', 'cost_price_diff', 'source_id.margin_warning')
    def _compute_status(self):
        """Détermine le statut et le niveau d'alerte"""
        for check in self:
            margin_warning = check.source_id.margin_warning or 20.0

            # Calcul du plus grand écart (en valeur absolue)
            max_diff = max(abs(check.sale_price_diff), abs(check.cost_price_diff))

            if max_diff < margin_warning / 2:
                check.status = 'ok'
                check.alert_level = 'none'
            elif max_diff < margin_warning:
                check.status = 'warning'
                check.alert_level = 'low'
            elif max_diff < margin_warning * 1.5:
                check.status = 'warning'
                check.alert_level = 'medium'
            else:
                check.status = 'alert'
                check.alert_level = 'high'

    def action_apply_reference_prices(self):
        """Applique les prix de référence au produit"""
        self.ensure_one()

        if self.reference_sale_price > 0:
            self.product_tmpl_id.list_price = self.reference_sale_price

        if self.reference_cost_price > 0:
            self.product_tmpl_id.standard_price = self.reference_cost_price

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Succès',
                'message': 'Prix mis à jour avec les prix de référence',
                'type': 'success',
            }
        }

    def action_view_product(self):
        """Affiche le produit"""
        self.ensure_one()
        return {
            'name': self.product_id.display_name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'res_id': self.product_tmpl_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
