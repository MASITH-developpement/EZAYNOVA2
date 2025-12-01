# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class SumUpConfig(models.Model):
    """Configuration SumUp"""
    _name = 'eazynova.sumup.config'
    _description = 'Configuration SumUp'

    name = fields.Char(
        string='Configuration',
        default='Configuration SumUp',
        required=True
    )

    api_key = fields.Char(
        string='Clé API',
        required=True,
        help='Clé API SumUp (OAuth Access Token)'
    )

    merchant_code = fields.Char(
        string='Code Marchand',
        help='Code marchand SumUp'
    )

    api_url = fields.Char(
        string='URL API',
        default='https://api.sumup.com/v0.1',
        required=True
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    auto_validate_invoice = fields.Boolean(
        string='Validation automatique facture',
        default=True,
        help='Valider automatiquement la facture après paiement réussi'
    )

    auto_reconcile = fields.Boolean(
        string='Réconciliation automatique',
        default=True,
        help='Réconcilier automatiquement le paiement avec la facture'
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal de paiement',
        domain=[('type', 'in', ['bank', 'cash'])],
        help='Journal comptable pour enregistrer les paiements SumUp'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    transaction_count = fields.Integer(
        string='Nombre de transactions',
        compute='_compute_transaction_count'
    )

    @api.depends('name')
    def _compute_transaction_count(self):
        """Calcule le nombre de transactions"""
        for config in self:
            config.transaction_count = self.env['eazynova.sumup.transaction'].search_count([])

    def action_test_connection(self):
        """Teste la connexion à l'API SumUp"""
        self.ensure_one()

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.api_url}/me',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Succès',
                        'message': 'Connexion à SumUp réussie !',
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Erreur',
                        'message': f'Erreur de connexion: {response.status_code}',
                        'type': 'danger',
                    }
                }

        except Exception as e:
            _logger.error(f"Erreur test connexion SumUp: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': f'Erreur: {str(e)}',
                    'type': 'danger',
                }
            }

    def action_view_transactions(self):
        """Affiche les transactions"""
        self.ensure_one()

        return {
            'name': 'Transactions SumUp',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.sumup.transaction',
            'view_mode': 'tree,form',
            'target': 'current'
        }
