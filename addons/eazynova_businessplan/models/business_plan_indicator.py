# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class BusinessPlanIndicator(models.Model):
    _name = 'business.plan.indicator'
    _description = 'Indicateur de Business Plan'
    _order = 'name'

    # Champs essentiels
    name = fields.Char(string='Nom', required=True)
    business_plan_id = fields.Many2one('business.plan', string='Business Plan', required=True, ondelete='cascade')

    # Valeurs
    target_value = fields.Float(string='Objectif', required=True, default=0)
    current_value = fields.Float(string='Réalisé', default=0)

    # Calcul automatique
    progress = fields.Float(string='Progression (%)', compute='_compute_progress', store=True)

    @api.depends('current_value', 'target_value')
    def _compute_progress(self):
        for indicator in self:
            if indicator.target_value:
                indicator.progress = min(100.0, (indicator.current_value / indicator.target_value) * 100)
            else:
                indicator.progress = 0.0
