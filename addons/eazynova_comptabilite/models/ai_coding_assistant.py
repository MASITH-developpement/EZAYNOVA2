# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class EazynovaAccountingAiAssistant(models.AbstractModel):
    _name = 'eazynova.accounting.ai.assistant'
    _description = 'Assistant IA pour codification comptable'

    @api.model
    def suggest_account_code(self, description, amount=None, partner_name=None, context_type='expense'):
        """
        Suggère un code comptable selon la description

        Args:
            description: str - Description de l'opération
            amount: float - Montant (optionnel)
            partner_name: str - Nom du partenaire (optionnel)
            context_type: str - Type d'opération (expense, income, etc.)

        Returns:
            dict: {
                'account_id': int,
                'account_code': str,
                'account_name': str,
                'confidence': float,
                'explanation': str
            }
        """
        try:
            # Utiliser le service IA
            ai_service = self.env['eazynova.ai.service']

            # Récupérer le plan comptable
            accounts = self.env['account.chart'].search([
                ('company_id', '=', self.env.company.id),
                ('deprecated', '=', False)
            ])

            # Construire la liste des comptes disponibles
            accounts_list = '\n'.join([
                f"{acc.code} - {acc.name} ({acc.account_type})"
                for acc in accounts[:50]  # Limiter pour ne pas surcharger
            ])

            prompt = f"""Tu es un expert-comptable. Suggère le code comptable le plus approprié pour cette opération.

Opération:
- Description: {description}
- Type: {context_type}
- Montant: {amount if amount else 'Non spécifié'}
- Partenaire: {partner_name if partner_name else 'Non spécifié'}

Comptes comptables disponibles (extrait du plan comptable français):
{accounts_list}

Réponds au format JSON:
{{
    "account_code": "le code comptable suggéré",
    "confidence": un score de 0 à 100,
    "explanation": "explication courte de pourquoi ce compte"
}}

Réponds uniquement avec le JSON, sans texte supplémentaire."""

            response = ai_service.call_ai(prompt)

            if response:
                import json
                try:
                    data = json.loads(response)

                    # Trouver le compte
                    account = self.env['account.chart'].search([
                        ('code', '=like', f"{data['account_code']}%"),
                        ('company_id', '=', self.env.company.id)
                    ], limit=1)

                    if account:
                        return {
                            'success': True,
                            'account_id': account.id,
                            'account_code': account.code,
                            'account_name': account.name,
                            'confidence': float(data.get('confidence', 70)),
                            'explanation': data.get('explanation', '')
                        }
                except json.JSONDecodeError:
                    pass

            # Fallback sur règles simples
            return self._suggest_with_rules(description, context_type)

        except Exception as e:
            _logger.error(f'Erreur suggestion IA: {str(e)}')
            return self._suggest_with_rules(description, context_type)

    def _suggest_with_rules(self, description, context_type):
        """Suggestion basée sur des règles simples"""
        description_lower = description.lower() if description else ''

        # Règles simples
        rules = {
            'expense': [
                (['loyer', 'location'], '613'),
                (['assurance'], '616'),
                (['électricité', 'eau', 'gaz', 'énergie'], '606'),
                (['téléphone', 'internet'], '626'),
                (['fourniture'], '606'),
                (['transport', 'carburant', 'essence'], '625'),
                (['repas', 'restaurant'], '625'),
                (['honoraires', 'consultant'], '622'),
                (['publicité', 'marketing'], '623'),
                (['salaire', 'paie'], '641'),
            ],
            'income': [
                (['vente', 'prestation'], '707'),
                (['service'], '706'),
            ]
        }

        # Chercher une correspondance
        for keywords, code in rules.get(context_type, []):
            if any(kw in description_lower for kw in keywords):
                account = self.env['account.chart'].search([
                    ('code', '=like', f'{code}%'),
                    ('company_id', '=', self.env.company.id)
                ], limit=1)

                if account:
                    return {
                        'success': True,
                        'account_id': account.id,
                        'account_code': account.code,
                        'account_name': account.name,
                        'confidence': 70.0,
                        'explanation': 'Suggestion basée sur les mots-clés'
                    }

        # Compte par défaut
        if context_type == 'expense':
            default_account = self.env.company.default_expense_account_id
        else:
            default_account = self.env.company.default_income_account_id

        if default_account:
            return {
                'success': True,
                'account_id': default_account.id,
                'account_code': default_account.code,
                'account_name': default_account.name,
                'confidence': 50.0,
                'explanation': 'Compte par défaut'
            }

        return {
            'success': False,
            'error': 'Aucun compte trouvé'
        }

    @api.model
    def suggest_bank_line_match(self, bank_line):
        """
        Suggère un partenaire et un compte pour une ligne de relevé bancaire

        Args:
            bank_line: account.bank.statement.line

        Returns:
            dict: {
                'partner_id': int,
                'account_id': int,
                'confidence': float
            }
        """
        try:
            description = bank_line.name
            amount = bank_line.amount

            # Rechercher dans l'historique
            similar_lines = self.env['account.bank.statement.line'].search([
                ('name', 'ilike', description[:20]),
                ('is_reconciled', '=', True)
            ], limit=1)

            if similar_lines:
                return {
                    'partner_id': similar_lines.partner_id.id if similar_lines.partner_id else False,
                    'account_id': similar_lines.account_id.id if similar_lines.account_id else False,
                    'confidence': 90.0
                }

            # Utiliser l'IA
            ai_service = self.env['eazynova.ai.service']

            prompt = f"""Analyse cette ligne de relevé bancaire et suggère le partenaire et le type de compte approprié.

Ligne:
- Description: {description}
- Montant: {amount}

Réponds au format JSON:
{{
    "partner_type": "customer" ou "supplier",
    "operation_type": "expense", "income", "bank_transfer", etc.,
    "confidence": score de 0 à 100
}}"""

            response = ai_service.call_ai(prompt)

            if response:
                import json
                try:
                    data = json.loads(response)

                    # Trouver le compte approprié
                    if data.get('operation_type') == 'expense':
                        account = self.env.company.default_expense_account_id
                    elif data.get('operation_type') == 'income':
                        account = self.env.company.default_income_account_id
                    else:
                        account = False

                    return {
                        'partner_id': False,
                        'account_id': account.id if account else False,
                        'confidence': float(data.get('confidence', 60))
                    }
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            _logger.error(f'Erreur suggestion ligne bancaire: {str(e)}')

        return {
            'partner_id': False,
            'account_id': False,
            'confidence': 0.0
        }

    @api.model
    def suggest_analytic_account(self, description, partner=None):
        """Suggère un compte analytique"""
        try:
            if not self.env.company.enable_analytic_accounting:
                return {'success': False, 'error': 'Analytique non activé'}

            # Utiliser l'IA
            ai_service = self.env['eazynova.ai.service']

            # Récupérer les comptes analytiques
            analytic_accounts = self.env['account.analytic.account'].search([
                ('company_id', '=', self.env.company.id),
                ('active', '=', True)
            ])

            accounts_list = '\n'.join([
                f"{acc.code} - {acc.name} ({acc.account_type})"
                for acc in analytic_accounts
            ])

            prompt = f"""Suggère le compte analytique le plus approprié pour cette opération.

Opération: {description}
Client/Projet: {partner.name if partner else 'Non spécifié'}

Comptes analytiques disponibles:
{accounts_list}

Réponds avec le code du compte analytique le plus approprié."""

            response = ai_service.call_ai(prompt)

            if response:
                # Chercher le compte
                account = self.env['account.analytic.account'].search([
                    '|',
                    ('code', 'ilike', response),
                    ('name', 'ilike', response),
                    ('company_id', '=', self.env.company.id)
                ], limit=1)

                if account:
                    return {
                        'success': True,
                        'analytic_account_id': account.id,
                        'confidence': 75.0
                    }

        except Exception as e:
            _logger.error(f'Erreur suggestion analytique: {str(e)}')

        return {
            'success': False,
            'error': 'Aucune suggestion'
        }
