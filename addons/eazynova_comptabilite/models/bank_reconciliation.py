# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BankReconciliation(models.TransientModel):
    _name = 'bank.reconciliation.wizard'
    _description = 'Assistant de rapprochement bancaire'

    bank_account_id = fields.Many2one(
        'eazynova.bank.account',
        string='Compte bancaire',
        required=True
    )

    date_from = fields.Date(
        string='Date de début',
        required=True
    )

    date_to = fields.Date(
        string='Date de fin',
        required=True
    )

    def action_reconcile(self):
        """Lance le rapprochement automatique"""
        self.ensure_one()

        # Récupérer les lignes de relevé non rapprochées
        statement_lines = self.env['account.bank.statement.line'].search([
            ('statement_id.bank_account_id', '=', self.bank_account_id.id),
            ('is_reconciled', '=', False),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
        ])

        matched_count = 0

        for line in statement_lines:
            # Essayer de trouver une correspondance automatique
            # Chercher des écritures avec même montant et date proche
            account_lines = self.env['account.move.line'].search([
                ('account_id', '=', self.bank_account_id.account_id.id),
                ('reconciled', '=', False),
                ('balance', '=', abs(line.amount)),
                ('date', '>=', line.date - timedelta(days=3)),
                ('date', '<=', line.date + timedelta(days=3))
            ], limit=1)

            if account_lines:
                # Rapprocher automatiquement
                line.write({
                    'is_reconciled': True,
                    'partner_id': account_lines.partner_id.id,
                    'account_id': account_lines.account_id.id
                })
                line.action_reconcile()
                matched_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Rapprochement terminé'),
                'message': _('%d ligne(s) rapprochée(s) automatiquement.') % matched_count,
                'type': 'success',
            }
        }
