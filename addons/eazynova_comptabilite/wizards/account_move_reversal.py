# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveReversal(models.TransientModel):
    _name = 'account.move.reversal'
    _description = 'Assistant d\'extourne'

    move_id = fields.Many2one('account.move', string='Écriture', required=True)
    date = fields.Date(string='Date d\'extourne', required=True, default=fields.Date.context_today)
    reason = fields.Char(string='Raison')

    def action_reverse(self):
        self.ensure_one()
        reversed_move = self.move_id.copy({
            'date': self.date,
            'ref': f'Extourne de {self.move_id.name}',
            'reversed_entry_id': self.move_id.id,
        })
        for line in reversed_move.line_ids:
            line.write({
                'debit': line.credit,
                'credit': line.debit,
            })
        reversed_move.action_post()
        return {'type': 'ir.actions.act_window_close'}
