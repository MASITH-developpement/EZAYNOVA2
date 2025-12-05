# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import csv
from io import StringIO

class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _description = 'Import de relevé bancaire'

    bank_account_id = fields.Many2one('eazynova.bank.account', string='Compte bancaire', required=True)
    file = fields.Binary(string='Fichier', required=True)
    file_name = fields.Char(string='Nom du fichier')
    file_type = fields.Selection([('csv', 'CSV'), ('ofx', 'OFX'), ('qif', 'QIF')], string='Type', default='csv')

    def action_import(self):
        self.ensure_one()
        if self.file_type == 'csv':
            return self._import_csv()
        return True

    def _import_csv(self):
        content = base64.b64decode(self.file).decode('utf-8')
        reader = csv.DictReader(StringIO(content), delimiter=';')
        
        statement = self.env['account.bank.statement'].create({
            'name': f'Import {fields.Date.today()}',
            'bank_account_id': self.bank_account_id.id,
            'journal_id': self.bank_account_id.journal_id.id,
            'date': fields.Date.today(),
        })
        
        for row in reader:
            self.env['account.bank.statement.line'].create({
                'statement_id': statement.id,
                'date': row.get('date', fields.Date.today()),
                'name': row.get('label', '/'),
                'amount': float(row.get('amount', 0)),
                'ref': row.get('reference', ''),
            })
        
        return {'type': 'ir.actions.act_window_close'}
