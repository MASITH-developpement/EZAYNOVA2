# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReconciliationSuggestionWizard(models.TransientModel):
    _name = 'eazynova.reconciliation.suggestion.wizard'
    _description = 'Assistant de Suggestion de Rapprochement'

    line_id = fields.Many2one(
        'eazynova.bank.statement.line',
        string='Ligne Bancaire',
        required=True
    )

    suggestion_ids = fields.Many2many(
        'eazynova.reconciliation.suggestion',
        string='Suggestions',
        compute='_compute_suggestions'
    )

    selected_suggestion_id = fields.Many2one(
        'eazynova.reconciliation.suggestion',
        string='Suggestion Sélectionnée'
    )

    manual_move_line_id = fields.Many2one(
        'account.move.line',
        string='Écriture Manuelle',
        domain="[('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']), ('reconciled', '=', False)]"
    )

    mode = fields.Selection([
        ('suggestion', 'Utiliser une Suggestion'),
        ('manual', 'Sélection Manuelle'),
    ], string='Mode', default='suggestion', required=True)

    @api.depends('line_id')
    def _compute_suggestions(self):
        for record in self:
            if record.line_id:
                record.suggestion_ids = record.line_id.suggestion_ids
            else:
                record.suggestion_ids = False

    def action_apply(self):
        """Applique la suggestion ou la sélection manuelle"""
        self.ensure_one()

        if self.mode == 'suggestion':
            if not self.selected_suggestion_id:
                raise UserError(_("Veuillez sélectionner une suggestion."))

            self.selected_suggestion_id.action_apply_suggestion()

        elif self.mode == 'manual':
            if not self.manual_move_line_id:
                raise UserError(_("Veuillez sélectionner une écriture."))

            self.line_id.write({
                'matching_move_line_id': self.manual_move_line_id.id,
                'matching_move_id': self.manual_move_line_id.move_id.id,
                'reconciliation_state': 'manual',
                'confidence_score': 1.0,
            })

        return {'type': 'ir.actions.act_window_close'}

    def action_refresh_suggestions(self):
        """Rafraîchit les suggestions"""
        self.ensure_one()

        self.line_id.action_find_matching_entries(
            use_ai=self.line_id.import_id.use_ai,
            confidence_threshold=self.line_id.import_id.confidence_threshold
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.reconciliation.suggestion.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
