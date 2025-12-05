# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountBankStatement(models.Model):
    _name = 'account.bank.statement'
    _description = 'Relevé bancaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/',
        tracking=True
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    date_start = fields.Date(
        string='Date de début',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    date_end = fields.Date(
        string='Date de fin',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    bank_account_id = fields.Many2one(
        'eazynova.bank.account',
        string='Compte bancaire',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('type', 'in', ['bank', 'cash'])],
        tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company.currency_id
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('open', 'Ouvert'),
        ('confirm', 'Confirmé'),
    ], string='État', default='draft', required=True, tracking=True, copy=False)

    line_ids = fields.One2many(
        'account.bank.statement.line',
        'statement_id',
        string='Lignes de relevé',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True
    )

    # Soldes
    balance_start = fields.Monetary(
        string='Solde initial',
        readonly=True,
        states={'draft': [('readonly', False)]},
        currency_field='currency_id'
    )

    balance_end = fields.Monetary(
        string='Solde final',
        readonly=True,
        states={'draft': [('readonly', False)]},
        currency_field='currency_id'
    )

    balance_end_real = fields.Monetary(
        string='Solde final calculé',
        compute='_compute_balance_end_real',
        store=True,
        currency_field='currency_id'
    )

    difference = fields.Monetary(
        string='Différence',
        compute='_compute_difference',
        store=True,
        currency_field='currency_id',
        help='Différence entre solde final saisi et calculé'
    )

    # Import
    import_file_name = fields.Char(
        string='Nom du fichier'
    )

    import_date = fields.Datetime(
        string='Date d\'import'
    )

    @api.depends('balance_start', 'line_ids.amount')
    def _compute_balance_end_real(self):
        """Calcule le solde final selon les lignes"""
        for statement in self:
            statement.balance_end_real = statement.balance_start + sum(statement.line_ids.mapped('amount'))

    @api.depends('balance_end', 'balance_end_real')
    def _compute_difference(self):
        """Calcule la différence entre solde saisi et calculé"""
        for statement in self:
            statement.difference = statement.balance_end - statement.balance_end_real

    @api.model
    def create(self, vals):
        """Création avec numéro automatique"""
        if vals.get('name', '/') == '/':
            journal = self.env['account.journal'].browse(vals.get('journal_id'))
            if journal:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    f'account.bank.statement.{journal.code.lower()}'
                ) or f'BS/{journal.code}/{fields.Date.today()}'

        return super(AccountBankStatement, self).create(vals)

    def action_open(self):
        """Ouvre le relevé pour saisie"""
        for statement in self:
            statement.state = 'open'

        return True

    def action_confirm(self):
        """Confirme le relevé et crée les écritures"""
        for statement in self:
            if statement.state != 'open':
                raise UserError(_('Seuls les relevés ouverts peuvent être confirmés.'))

            # Vérifier qu'il n'y a pas de différence
            if statement.difference != 0:
                raise UserError(_(
                    'Le relevé n\'est pas équilibré.\n'
                    'Différence: %.2f\n\n'
                    'Veuillez corriger les montants avant de confirmer.'
                ) % statement.difference)

            # Vérifier que toutes les lignes sont rapprochées
            unreconciled = statement.line_ids.filtered(lambda l: not l.is_reconciled)
            if unreconciled:
                raise UserError(_(
                    'Toutes les lignes doivent être rapprochées avant confirmation.\n'
                    '%d ligne(s) non rapprochée(s).'
                ) % len(unreconciled))

            statement.state = 'confirm'

        return True

    def action_draft(self):
        """Repasse le relevé en brouillon"""
        for statement in self:
            statement.state = 'draft'

        return True

    @api.onchange('bank_account_id')
    def _onchange_bank_account_id(self):
        """Remplit automatiquement le journal"""
        if self.bank_account_id:
            self.journal_id = self.bank_account_id.journal_id
            self.currency_id = self.bank_account_id.currency_id

            # Récupérer le dernier solde
            last_statement = self.search([
                ('bank_account_id', '=', self.bank_account_id.id),
                ('state', '=', 'confirm')
            ], order='date desc', limit=1)

            if last_statement:
                self.balance_start = last_statement.balance_end
            else:
                self.balance_start = self.bank_account_id.initial_balance

    def action_view_reconciliation(self):
        """Ouvre la vue de rapprochement"""
        self.ensure_one()
        return {
            'name': _('Rapprochement bancaire'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.line',
            'view_mode': 'tree,form',
            'domain': [('statement_id', '=', self.id)],
            'context': {'default_statement_id': self.id}
        }
