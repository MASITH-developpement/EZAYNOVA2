# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EazynovaBankAccount(models.Model):
    _name = 'eazynova.bank.account'
    _description = 'Compte bancaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nom du compte',
        required=True,
        tracking=True
    )

    acc_number = fields.Char(
        string='Numéro de compte',
        required=True,
        tracking=True,
        help='IBAN ou numéro de compte bancaire'
    )

    bank_id = fields.Many2one(
        'res.bank',
        string='Banque',
        tracking=True
    )

    bank_name = fields.Char(
        related='bank_id.name',
        string='Nom de la banque',
        readonly=True
    )

    bank_bic = fields.Char(
        related='bank_id.bic',
        string='BIC/SWIFT',
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal comptable',
        domain=[('type', '=', 'bank')],
        tracking=True,
        help='Journal comptable associé'
    )

    account_id = fields.Many2one(
        'account.chart',
        string='Compte comptable',
        domain=[('account_type', '=', 'asset_cash')],
        help='Compte comptable pour ce compte bancaire'
    )

    # Informations bancaires
    account_type = fields.Selection([
        ('checking', 'Compte courant'),
        ('savings', 'Compte épargne'),
        ('credit_card', 'Carte de crédit'),
        ('cash', 'Caisse'),
    ], string='Type de compte', default='checking', required=True)

    # Connexion bancaire
    bank_connection_type = fields.Selection([
        ('manual', 'Saisie manuelle'),
        ('file', 'Import fichier'),
        ('api', 'Connexion API'),
        ('bridge', 'Bridge API'),
    ], string='Type de connexion', default='manual', tracking=True)

    # Informations API
    api_endpoint = fields.Char(
        string='URL API',
        help='URL de l\'API bancaire'
    )

    api_key = fields.Char(
        string='Clé API',
        help='Clé d\'authentification API'
    )

    api_secret = fields.Char(
        string='Secret API',
        help='Secret d\'authentification API'
    )

    last_sync_date = fields.Datetime(
        string='Dernière synchronisation',
        readonly=True
    )

    # Soldes
    balance = fields.Monetary(
        string='Solde actuel',
        compute='_compute_balance',
        currency_field='currency_id'
    )

    initial_balance = fields.Monetary(
        string='Solde initial',
        default=0.0,
        currency_field='currency_id',
        help='Solde à l\'ouverture du compte'
    )

    # Statistiques
    statement_count = fields.Integer(
        string='Nombre de relevés',
        compute='_compute_statement_count'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    # Pays (pour comptes étrangers)
    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        help='Pays du compte bancaire'
    )

    # Notes
    note = fields.Text(
        string='Notes'
    )

    @api.depends('journal_id', 'initial_balance')
    def _compute_balance(self):
        """Calcule le solde actuel du compte"""
        for account in self:
            if account.journal_id:
                # Calculer depuis les écritures comptables
                lines = self.env['account.move.line'].search([
                    ('journal_id', '=', account.journal_id.id),
                    ('move_id.state', '=', 'posted')
                ])
                total_debit = sum(lines.mapped('debit'))
                total_credit = sum(lines.mapped('credit'))
                account.balance = account.initial_balance + total_debit - total_credit
            else:
                account.balance = account.initial_balance

    def _compute_statement_count(self):
        """Compte le nombre de relevés"""
        for account in self:
            account.statement_count = self.env['account.bank.statement'].search_count([
                ('bank_account_id', '=', account.id)
            ])

    @api.constrains('acc_number')
    def _check_acc_number(self):
        """Vérifie le format du numéro de compte"""
        for account in self:
            if account.acc_number:
                # Nettoyer les espaces
                acc_number = account.acc_number.replace(' ', '')

                # Vérification basique pour IBAN (2 lettres + 2 chiffres + max 30 caractères)
                if len(acc_number) >= 4 and acc_number[:2].isalpha() and acc_number[2:4].isdigit():
                    # C'est probablement un IBAN
                    if len(acc_number) > 34:
                        raise ValidationError(_('Le numéro IBAN est trop long (max 34 caractères).'))

    def action_view_statements(self):
        """Affiche les relevés bancaires"""
        self.ensure_one()
        return {
            'name': _('Relevés bancaires'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement',
            'view_mode': 'tree,form',
            'domain': [('bank_account_id', '=', self.id)],
            'context': {'default_bank_account_id': self.id}
        }

    def action_sync_bank(self):
        """Synchronise avec la banque via API"""
        self.ensure_one()

        if self.bank_connection_type != 'api':
            raise ValidationError(_('Ce compte n\'est pas configuré pour la synchronisation API.'))

        # TODO: Implémenter la synchronisation selon l\'API
        # Pour l'instant, retourner un message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Synchronisation'),
                'message': _('La synchronisation bancaire sera implémentée prochainement.'),
                'type': 'info',
            }
        }

    def action_import_statement(self):
        """Ouvre l'assistant d'import de relevé"""
        self.ensure_one()
        return {
            'name': _('Importer un relevé bancaire'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.import',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_bank_account_id': self.id}
        }
