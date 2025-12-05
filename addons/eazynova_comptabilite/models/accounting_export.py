# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)


class AccountingExport(models.TransientModel):
    _name = 'accounting.export'
    _description = 'Export comptable'

    export_type = fields.Selection([
        ('balance', 'Balance'),
        ('general_ledger', 'Grand livre'),
        ('trial_balance', 'Balance de vérification'),
        ('journal', 'Journal'),
        ('fec', 'FEC (Fichier des Écritures Comptables)'),
    ], string='Type d\'export', required=True, default='balance')

    export_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
    ], string='Format', required=True, default='xlsx')

    date_from = fields.Date(
        string='Date de début',
        required=True,
        default=fields.Date.context_today
    )

    date_to = fields.Date(
        string='Date de fin',
        required=True,
        default=fields.Date.context_today
    )

    journal_ids = fields.Many2many(
        'account.journal',
        string='Journaux',
        help='Laissez vide pour tous les journaux'
    )

    account_ids = fields.Many2many(
        'account.chart',
        string='Comptes',
        help='Laissez vide pour tous les comptes'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    # Fichier exporté
    file_data = fields.Binary(
        string='Fichier',
        readonly=True
    )

    file_name = fields.Char(
        string='Nom du fichier',
        readonly=True
    )

    def action_export(self):
        """Lance l'export"""
        self.ensure_one()

        if self.export_format == 'xlsx':
            return self._export_xlsx()
        elif self.export_format == 'pdf':
            return self._export_pdf()
        elif self.export_format == 'csv':
            return self._export_csv()

        return True

    def _export_xlsx(self):
        """Export Excel"""
        try:
            import xlsxwriter

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet(self.export_type.replace('_', ' ').title())

            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })

            money_format = workbook.add_format({'num_format': '#,##0.00'})

            # En-têtes selon le type
            if self.export_type == 'balance':
                headers = ['Code', 'Nom du compte', 'Débit', 'Crédit', 'Solde']
                data = self._get_balance_data()
            elif self.export_type == 'general_ledger':
                headers = ['Date', 'Journal', 'Compte', 'Libellé', 'Débit', 'Crédit', 'Solde']
                data = self._get_general_ledger_data()
            elif self.export_type == 'journal':
                headers = ['Date', 'Compte', 'Libellé', 'Référence', 'Débit', 'Crédit']
                data = self._get_journal_data()
            else:
                headers = []
                data = []

            # Écrire les en-têtes
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)

            # Écrire les données
            for row, line in enumerate(data, start=1):
                for col, value in enumerate(line):
                    if isinstance(value, (int, float)) and col >= len(headers) - 3:
                        worksheet.write(row, col, value, money_format)
                    else:
                        worksheet.write(row, col, value)

            # Ajuster la largeur des colonnes
            for col, header in enumerate(headers):
                worksheet.set_column(col, col, len(header) + 5)

            workbook.close()
            output.seek(0)

            # Sauvegarder le fichier
            file_name = f'{self.export_type}_{self.date_from}_{self.date_to}.xlsx'
            self.write({
                'file_data': base64.b64encode(output.read()),
                'file_name': file_name
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content?model=accounting.export&id={self.id}&field=file_data&download=true&filename={file_name}',
                'target': 'self',
            }

        except Exception as e:
            _logger.error(f'Erreur export XLSX: {str(e)}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erreur'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def _get_balance_data(self):
        """Récupère les données de balance"""
        accounts = self.env['account.chart'].search([
            ('company_id', '=', self.company_id.id),
            ('deprecated', '=', False)
        ] + ([('id', 'in', self.account_ids.ids)] if self.account_ids else []))

        data = []
        for account in accounts:
            # Récupérer les lignes d'écriture
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id),
                ('move_id.state', '=', 'posted'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ] + ([('journal_id', 'in', self.journal_ids.ids)] if self.journal_ids else []))

            if lines:
                debit = sum(lines.mapped('debit'))
                credit = sum(lines.mapped('credit'))
                balance = debit - credit

                data.append([
                    account.code,
                    account.name,
                    debit,
                    credit,
                    balance
                ])

        return data

    def _get_general_ledger_data(self):
        """Récupère les données du grand livre"""
        lines = self.env['account.move.line'].search([
            ('move_id.state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id)
        ] + ([('journal_id', 'in', self.journal_ids.ids)] if self.journal_ids else [])
          + ([('account_id', 'in', self.account_ids.ids)] if self.account_ids else []),
            order='date, id')

        data = []
        for line in lines:
            data.append([
                line.date.strftime('%d/%m/%Y') if line.date else '',
                line.move_id.journal_id.code,
                line.account_id.code,
                line.name,
                line.debit,
                line.credit,
                line.balance
            ])

        return data

    def _get_journal_data(self):
        """Récupère les données du journal"""
        lines = self.env['account.move.line'].search([
            ('move_id.state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id)
        ] + ([('journal_id', 'in', self.journal_ids.ids)] if self.journal_ids else []),
            order='date, id')

        data = []
        for line in lines:
            data.append([
                line.date.strftime('%d/%m/%Y') if line.date else '',
                line.account_id.code,
                line.name,
                line.ref or '',
                line.debit,
                line.credit
            ])

        return data

    def _export_pdf(self):
        """Export PDF"""
        # TODO: Implémenter avec reportlab ou wkhtmltopdf
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('En cours de développement'),
                'message': _('L\'export PDF sera disponible prochainement.'),
                'type': 'info',
            }
        }

    def _export_csv(self):
        """Export CSV"""
        try:
            import csv

            output = BytesIO()
            writer = csv.writer(output, delimiter=';')

            # En-têtes et données selon le type
            if self.export_type == 'balance':
                headers = ['Code', 'Nom du compte', 'Débit', 'Crédit', 'Solde']
                data = self._get_balance_data()
            elif self.export_type == 'general_ledger':
                headers = ['Date', 'Journal', 'Compte', 'Libellé', 'Débit', 'Crédit', 'Solde']
                data = self._get_general_ledger_data()
            else:
                headers = []
                data = []

            writer.writerow(headers)
            writer.writerows(data)

            output.seek(0)

            # Sauvegarder le fichier
            file_name = f'{self.export_type}_{self.date_from}_{self.date_to}.csv'
            self.write({
                'file_data': base64.b64encode(output.read()),
                'file_name': file_name
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content?model=accounting.export&id={self.id}&field=file_data&download=true&filename={file_name}',
                'target': 'self',
            }

        except Exception as e:
            _logger.error(f'Erreur export CSV: {str(e)}')
            return False
