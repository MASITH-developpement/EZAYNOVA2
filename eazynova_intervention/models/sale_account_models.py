# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Temporairement commenté pour éviter les erreurs de chargement
    # intervention_ids = fields.One2many(
    #     'intervention.intervention',
    #     'sale_order_id',
    #     string="Interventions liées"
    # )
    # intervention_count = fields.Integer(
    #     string="Nombre d'interventions",
    #     compute='_compute_intervention_count'
    # )

    # @api.depends('intervention_ids')
    # def _compute_intervention_count(self):
    #     """Calculer le nombre d'interventions liées"""
    #     for record in self:
    #         record.intervention_count = len(record.intervention_ids)

    # def action_view_interventions(self):
    #     """Voir les interventions liées au devis/commande"""
    #     self.ensure_one()
    #     if not self.intervention_ids:
    #         return False
    #     
    #     if len(self.intervention_ids) == 1:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'intervention.intervention',
    #             'res_id': self.intervention_ids[0].id,
    #             'view_mode': 'form',
    #             'target': 'current',
    #             'context': {'create': False}
    #         }
    #     else:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'intervention.intervention',
    #             'view_mode': 'list,form',
    #             'domain': [('id', 'in', self.intervention_ids.ids)],
    #             'context': {'create': False},
    #             'name': f'Interventions - {self.name}'
    #         }


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Temporairement commenté pour éviter les erreurs de chargement
    # intervention_ids = fields.Many2many(
    #     'intervention.intervention',
    #     'plomberie_intervention_account_move_rel',
    #     'invoice_id',
    #     'intervention_id',
    #     string="Interventions liées"
    # )
    # intervention_count = fields.Integer(
    #     string="Nombre d'interventions",
    #     compute='_compute_intervention_count'
    # )

    # @api.depends('intervention_ids')
    # def _compute_intervention_count(self):
    #     """Calculer le nombre d'interventions liées"""
    #     for record in self:
    #         record.intervention_count = len(record.intervention_ids)

    # def action_view_interventions(self):
    #     """Voir les interventions liées à la facture"""
    #     self.ensure_one()
    #     if not self.intervention_ids:
    #         return False
    #     
    #     if len(self.intervention_ids) == 1:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'intervention.intervention',
    #             'res_id': self.intervention_ids[0].id,
    #             'view_mode': 'form',
    #             'target': 'current',
    #             'context': {'create': False}
    #         }
    #     else:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'intervention.intervention',
    #             'view_mode': 'list,form',
    #             'domain': [('id', 'in', self.intervention_ids.ids)],
    #             'context': {'create': False},
    #             'name': f'Interventions - {self.name}'
    #         }
