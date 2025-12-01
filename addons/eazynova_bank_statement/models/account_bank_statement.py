# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    eazynova_import_id = fields.Many2one(
        'eazynova.bank.statement.import',
        string='Import EAZYNOVA',
        readonly=True,
        help="Import EAZYNOVA à l'origine de ce relevé"
    )

    auto_reconciled_count = fields.Integer(
        string='Lignes Auto-rapprochées',
        compute='_compute_reconciliation_stats'
    )

    manual_reconciled_count = fields.Integer(
        string='Lignes Rapprochées Manuellement',
        compute='_compute_reconciliation_stats'
    )

    @api.depends('line_ids.is_reconciled')
    def _compute_reconciliation_stats(self):
        for record in self:
            # Cette fonctionnalité peut être étendue selon les besoins
            record.auto_reconciled_count = 0
            record.manual_reconciled_count = 0

    def action_view_eazynova_import(self):
        """Ouvre l'import EAZYNOVA associé"""
        self.ensure_one()

        if not self.eazynova_import_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Bancaire EAZYNOVA'),
            'res_model': 'eazynova.bank.statement.import',
            'res_id': self.eazynova_import_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    eazynova_line_id = fields.Many2one(
        'eazynova.bank.statement.line',
        string='Ligne Import EAZYNOVA',
        readonly=True,
        help="Ligne d'import EAZYNOVA à l'origine de cette ligne"
    )

    confidence_score = fields.Float(
        string='Score de Confiance',
        related='eazynova_line_id.confidence_score',
        store=True
    )

    reconciliation_method = fields.Selection(
        related='eazynova_line_id.reconciliation_state',
        string='Méthode de Rapprochement',
        store=True
    )
