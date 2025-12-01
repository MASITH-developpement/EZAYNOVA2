# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class SumUpPaymentWizard(models.TransientModel):
    """Assistant de paiement SumUp"""
    _name = 'eazynova.sumup.payment.wizard'
    _description = 'Assistant Paiement SumUp'

    invoice_id = fields.Many2one(
        'account.move',
        string='Facture',
        required=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='invoice_id.partner_id'
    )

    amount = fields.Monetary(
        string='Montant',
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    description = fields.Char(
        string='Description',
        compute='_compute_description'
    )

    @api.depends('invoice_id')
    def _compute_description(self):
        """Génère la description"""
        for wizard in self:
            if wizard.invoice_id:
                wizard.description = f'Paiement {wizard.invoice_id.name}'
            else:
                wizard.description = 'Paiement'

    def action_process_payment(self):
        """Traite le paiement via SumUp"""
        self.ensure_one()

        config = self.env['eazynova.sumup.config'].sudo().search([('active', '=', True)], limit=1)

        if not config:
            raise UserError('Configuration SumUp non trouvée.')

        if not config.api_key:
            raise UserError('Clé API SumUp non configurée.')

        # Créer la transaction
        transaction = self.env['eazynova.sumup.transaction'].create({
            'invoice_id': self.invoice_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'state': 'processing'
        })

        try:
            # Appeler l'API SumUp
            headers = {
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'amount': self.amount,
                'currency': self.currency_id.name,
                'description': self.description,
                'merchant_code': config.merchant_code
            }

            response = requests.post(
                f'{config.api_url}/checkouts',
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201]:
                response_data = response.json()

                transaction.write({
                    'state': 'successful',
                    'sumup_transaction_id': response_data.get('id'),
                    'sumup_transaction_code': response_data.get('transaction_code')
                })

                # Créer le paiement
                payment = transaction.action_create_payment()

                # Valider la facture si configuré
                if config.auto_validate_invoice and self.invoice_id.state == 'draft':
                    self.invoice_id.action_post()

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Succès',
                        'message': 'Paiement SumUp réussi !',
                        'type': 'success',
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }

            else:
                error_msg = f'Erreur API SumUp: {response.status_code}'
                transaction.write({
                    'state': 'failed',
                    'error_message': error_msg
                })

                raise UserError(error_msg)

        except Exception as e:
            _logger.error(f"Erreur paiement SumUp: {str(e)}")
            transaction.write({
                'state': 'failed',
                'error_message': str(e)
            })

            raise UserError(f'Erreur lors du paiement: {str(e)}')
