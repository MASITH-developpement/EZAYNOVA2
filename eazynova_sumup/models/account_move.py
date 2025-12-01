# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    """Extension du modèle facture"""
    _inherit = 'account.move'

    sumup_transaction_ids = fields.One2many(
        'eazynova.sumup.transaction',
        'invoice_id',
        string='Transactions SumUp'
    )

    sumup_transaction_count = fields.Integer(
        string='Transactions SumUp',
        compute='_compute_sumup_transaction_count'
    )

    def _compute_sumup_transaction_count(self):
        """Calcule le nombre de transactions"""
        for move in self:
            move.sumup_transaction_count = len(move.sumup_transaction_ids)

    def action_pay_with_sumup(self):
        """Ouvre le wizard de paiement SumUp"""
        self.ensure_one()

        return {
            'name': 'Paiement SumUp',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.sumup.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
                'default_amount': self.amount_residual,
                'default_partner_id': self.partner_id.id
            }
        }

    def action_view_sumup_transactions(self):
        """Affiche les transactions SumUp"""
        self.ensure_one()

        return {
            'name': f'Transactions SumUp - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.sumup.transaction',
            'view_mode': 'tree,form',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id}
        }
