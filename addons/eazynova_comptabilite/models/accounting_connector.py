# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class AccountingConnector(models.Model):
    _name = 'accounting.connector'
    _description = 'Connecteur logiciel comptable'

    name = fields.Char(
        string='Nom',
        required=True
    )

    software = fields.Selection([
        ('pennylane', 'Pennylane'),
        ('sage', 'Sage'),
        ('axonaut', 'Axonaut'),
        ('ebp', 'EBP Compta'),
        ('ciel', 'Ciel Compta'),
        ('quadratus', 'Quadratus'),
        ('acd', 'ACD'),
    ], string='Logiciel', required=True)

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    # Paramètres de connexion
    api_url = fields.Char(
        string='URL API',
        required=True
    )

    api_key = fields.Char(
        string='Clé API',
        required=True
    )

    api_secret = fields.Char(
        string='Secret API'
    )

    # Synchronisation
    last_sync_date = fields.Datetime(
        string='Dernière synchronisation',
        readonly=True
    )

    auto_sync = fields.Boolean(
        string='Synchronisation automatique',
        default=False
    )

    sync_frequency = fields.Selection([
        ('hourly', 'Toutes les heures'),
        ('daily', 'Quotidienne'),
        ('weekly', 'Hebdomadaire'),
    ], string='Fréquence', default='daily')

    # Mapping des comptes
    account_mapping_ids = fields.One2many(
        'accounting.connector.mapping',
        'connector_id',
        string='Mapping des comptes'
    )

    # Logs
    log_ids = fields.One2many(
        'accounting.connector.log',
        'connector_id',
        string='Logs'
    )

    def action_test_connection(self):
        """Teste la connexion à l'API"""
        self.ensure_one()

        try:
            if self.software == 'pennylane':
                result = self._test_pennylane()
            elif self.software == 'sage':
                result = self._test_sage()
            elif self.software == 'axonaut':
                result = self._test_axonaut()
            else:
                result = {'success': False, 'message': 'Connecteur non implémenté'}

            if result.get('success'):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connexion réussie'),
                        'message': _('La connexion à %s est opérationnelle.') % self.software,
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Erreur de connexion'),
                        'message': result.get('message', _('Erreur inconnue')),
                        'type': 'danger',
                    }
                }

        except Exception as e:
            _logger.error(f'Erreur test connexion: {str(e)}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erreur'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def _test_pennylane(self):
        """Teste la connexion Pennylane"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.api_url}/api/external/v1/customer_invoices',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'message': f'Code HTTP: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _test_sage(self):
        """Teste la connexion Sage"""
        # TODO: Implémenter selon API Sage
        return {'success': False, 'message': 'À implémenter'}

    def _test_axonaut(self):
        """Teste la connexion Axonaut"""
        try:
            headers = {
                'userApiKey': self.api_key,
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.api_url}/api/v2/companies',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'message': f'Code HTTP: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'message': str(e)}

    def action_sync_data(self):
        """Synchronise les données avec le logiciel externe"""
        self.ensure_one()

        if self.software == 'pennylane':
            return self._sync_pennylane()
        elif self.software == 'sage':
            return self._sync_sage()
        elif self.software == 'axonaut':
            return self._sync_axonaut()

        return True

    def _sync_pennylane(self):
        """Synchronise avec Pennylane"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # Exporter les factures
            invoices = self.env['account.move'].search([
                ('company_id', '=', self.company_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('date', '>=', self.last_sync_date or '2024-01-01')
            ])

            for invoice in invoices:
                data = self._prepare_pennylane_invoice(invoice)

                response = requests.post(
                    f'{self.api_url}/api/external/v1/customer_invoices',
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if response.status_code == 201:
                    self._log_sync('success', f'Facture {invoice.name} exportée')
                else:
                    self._log_sync('error', f'Erreur facture {invoice.name}: {response.text}')

            self.last_sync_date = fields.Datetime.now()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Synchronisation terminée'),
                    'message': _('%d facture(s) synchronisée(s)') % len(invoices),
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.error(f'Erreur sync Pennylane: {str(e)}')
            self._log_sync('error', str(e))
            return False

    def _prepare_pennylane_invoice(self, invoice):
        """Prépare les données d'une facture pour Pennylane"""
        return {
            'invoice_number': invoice.name,
            'date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            'deadline': invoice.invoice_date_due.isoformat() if invoice.invoice_date_due else None,
            'customer': {
                'name': invoice.partner_id.name,
                'address': invoice.partner_id.street or '',
                'postal_code': invoice.partner_id.zip or '',
                'city': invoice.partner_id.city or '',
            },
            'line_items': [
                {
                    'label': line.name,
                    'quantity': line.quantity,
                    'unit_price': line.price_unit,
                    'vat_rate': line.tax_ids[0].amount if line.tax_ids else 20.0,
                }
                for line in invoice.line_ids.filtered(lambda l: not l.tax_line_id)
            ],
            'amount': invoice.amount_total,
            'currency': invoice.currency_id.name,
        }

    def _sync_sage(self):
        """Synchronise avec Sage"""
        # TODO: Implémenter
        return True

    def _sync_axonaut(self):
        """Synchronise avec Axonaut"""
        # TODO: Implémenter
        return True

    def _log_sync(self, status, message):
        """Enregistre un log de synchronisation"""
        self.env['accounting.connector.log'].create({
            'connector_id': self.id,
            'status': status,
            'message': message,
            'date': fields.Datetime.now()
        })


class AccountingConnectorMapping(models.Model):
    _name = 'accounting.connector.mapping'
    _description = 'Mapping compte comptable'

    connector_id = fields.Many2one(
        'accounting.connector',
        string='Connecteur',
        required=True,
        ondelete='cascade'
    )

    account_id = fields.Many2one(
        'account.chart',
        string='Compte Eazynova',
        required=True
    )

    external_account_code = fields.Char(
        string='Code compte externe',
        required=True
    )


class AccountingConnectorLog(models.Model):
    _name = 'accounting.connector.log'
    _description = 'Log connecteur'
    _order = 'date desc'

    connector_id = fields.Many2one(
        'accounting.connector',
        string='Connecteur',
        required=True,
        ondelete='cascade'
    )

    date = fields.Datetime(
        string='Date',
        required=True
    )

    status = fields.Selection([
        ('success', 'Succès'),
        ('error', 'Erreur'),
        ('warning', 'Avertissement'),
    ], string='Statut', required=True)

    message = fields.Text(
        string='Message'
    )
