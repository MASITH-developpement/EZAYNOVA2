# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountChart(models.Model):
    _name = 'account.chart'
    _description = 'Plan comptable'
    _order = 'code'
    _rec_name = 'complete_name'

    name = fields.Char(
        string='Nom',
        required=True,
        index=True
    )

    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Code du compte (ex: 411000, 707000)'
    )

    complete_name = fields.Char(
        string='Nom complet',
        compute='_compute_complete_name',
        store=True
    )

    account_type = fields.Selection([
        # Actif
        ('asset_receivable', 'Clients (Créances)'),
        ('asset_current', 'Actif circulant'),
        ('asset_non_current', 'Actif immobilisé'),
        ('asset_prepayments', 'Charges constatées d\'avance'),
        ('asset_fixed', 'Immobilisations'),
        ('asset_cash', 'Banque et caisse'),

        # Passif
        ('liability_payable', 'Fournisseurs (Dettes)'),
        ('liability_current', 'Passif circulant'),
        ('liability_non_current', 'Passif non circulant'),
        ('liability_credit_card', 'Carte de crédit'),

        # Capitaux propres
        ('equity', 'Capitaux propres'),
        ('equity_unaffected', 'Bénéfices non affectés'),

        # Produits
        ('income', 'Produits d\'exploitation'),
        ('income_other', 'Autres produits'),

        # Charges
        ('expense', 'Charges d\'exploitation'),
        ('expense_direct_cost', 'Coût direct'),
        ('expense_depreciation', 'Dotations aux amortissements'),
        ('off_balance', 'Hors bilan'),
    ], string='Type de compte', required=True, help='Type de compte selon le plan comptable')

    internal_group = fields.Selection([
        ('asset', 'Actif'),
        ('liability', 'Passif'),
        ('equity', 'Capitaux propres'),
        ('income', 'Produits'),
        ('expense', 'Charges'),
    ], string='Groupe interne', compute='_compute_internal_group', store=True)

    reconcile = fields.Boolean(
        string='Lettrable',
        default=False,
        help='Permet le lettrage des écritures sur ce compte'
    )

    deprecated = fields.Boolean(
        string='Déprécié',
        default=False,
        help='Ce compte ne doit plus être utilisé'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        help='Force la devise pour ce compte'
    )

    # Taxes par défaut
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes par défaut',
        help='Taxes appliquées par défaut sur ce compte'
    )

    # Groupes
    group_id = fields.Many2one(
        'account.chart.group',
        string='Groupe',
        help='Groupe de comptes pour les rapports'
    )

    # Analytique
    analytic_required = fields.Boolean(
        string='Analytique obligatoire',
        default=False,
        help='Nécessite une affectation analytique sur les écritures'
    )

    # Statistiques
    balance = fields.Monetary(
        string='Solde',
        compute='_compute_balance',
        currency_field='company_currency_id'
    )

    debit = fields.Monetary(
        string='Débit',
        compute='_compute_balance',
        currency_field='company_currency_id'
    )

    credit = fields.Monetary(
        string='Crédit',
        compute='_compute_balance',
        currency_field='company_currency_id'
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Devise société',
        readonly=True
    )

    # Lignes d'écriture
    move_line_ids = fields.One2many(
        'account.move.line',
        'account_id',
        string='Écritures'
    )

    @api.depends('code', 'name')
    def _compute_complete_name(self):
        """Calcule le nom complet du compte"""
        for account in self:
            account.complete_name = f'{account.code} {account.name}' if account.code else account.name

    @api.depends('account_type')
    def _compute_internal_group(self):
        """Détermine le groupe interne selon le type"""
        for account in self:
            if account.account_type.startswith('asset'):
                account.internal_group = 'asset'
            elif account.account_type.startswith('liability'):
                account.internal_group = 'liability'
            elif account.account_type.startswith('equity'):
                account.internal_group = 'equity'
            elif account.account_type.startswith('income'):
                account.internal_group = 'income'
            elif account.account_type.startswith('expense'):
                account.internal_group = 'expense'
            else:
                account.internal_group = False

    def _compute_balance(self):
        """Calcule le solde du compte"""
        for account in self:
            lines = self.env['account.move.line'].search([
                ('account_id', '=', account.id),
                ('move_id.state', '=', 'posted')
            ])
            account.debit = sum(lines.mapped('debit'))
            account.credit = sum(lines.mapped('credit'))
            account.balance = account.debit - account.credit

    @api.constrains('code', 'company_id')
    def _check_code_unique(self):
        """Vérifie l'unicité du code par société"""
        for account in self:
            if self.search_count([
                ('code', '=', account.code),
                ('company_id', '=', account.company_id.id),
                ('id', '!=', account.id)
            ]) > 0:
                raise ValidationError(_(
                    'Le code de compte %s existe déjà pour cette société.'
                ) % account.code)

    @api.constrains('code')
    def _check_code_format(self):
        """Vérifie le format du code comptable"""
        for account in self:
            if not account.code:
                continue
            # Le code doit être numérique (plan comptable français)
            if not account.code.isdigit():
                raise ValidationError(_(
                    'Le code comptable doit être numérique (ex: 411000, 707000).'
                ))
            # Le code doit avoir au moins 3 caractères
            if len(account.code) < 3:
                raise ValidationError(_(
                    'Le code comptable doit avoir au moins 3 caractères.'
                ))

    def action_view_move_lines(self):
        """Affiche les écritures du compte"""
        self.ensure_one()
        return {
            'name': _('Écritures - %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id}
        }


class AccountChartGroup(models.Model):
    _name = 'account.chart.group'
    _description = 'Groupe de comptes'
    _order = 'code'
    _parent_name = 'parent_id'
    _parent_store = True

    name = fields.Char(
        string='Nom',
        required=True
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    parent_id = fields.Many2one(
        'account.chart.group',
        string='Groupe parent',
        ondelete='cascade'
    )

    parent_path = fields.Char(
        index=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )


class AccountChartTemplate(models.Model):
    _name = 'account.chart.template'
    _description = 'Modèle de plan comptable'

    name = fields.Char(
        string='Nom',
        required=True
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True
    )

    account_template_ids = fields.One2many(
        'account.chart.template.line',
        'template_id',
        string='Comptes'
    )

    def action_install_chart(self, company_id):
        """Installe le plan comptable pour une société"""
        self.ensure_one()
        company = self.env['res.company'].browse(company_id)

        # Créer les comptes
        for template_line in self.account_template_ids:
            self.env['account.chart'].create({
                'name': template_line.name,
                'code': template_line.code,
                'account_type': template_line.account_type,
                'reconcile': template_line.reconcile,
                'company_id': company.id,
            })

        company.chart_template_id = self.id
        return True


class AccountChartTemplateLine(models.Model):
    _name = 'account.chart.template.line'
    _description = 'Ligne de modèle de plan comptable'
    _order = 'code'

    template_id = fields.Many2one(
        'account.chart.template',
        string='Modèle',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char(
        string='Nom',
        required=True
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    account_type = fields.Selection([
        ('asset_receivable', 'Clients (Créances)'),
        ('asset_current', 'Actif circulant'),
        ('asset_non_current', 'Actif immobilisé'),
        ('asset_prepayments', 'Charges constatées d\'avance'),
        ('asset_fixed', 'Immobilisations'),
        ('asset_cash', 'Banque et caisse'),
        ('liability_payable', 'Fournisseurs (Dettes)'),
        ('liability_current', 'Passif circulant'),
        ('liability_non_current', 'Passif non circulant'),
        ('liability_credit_card', 'Carte de crédit'),
        ('equity', 'Capitaux propres'),
        ('equity_unaffected', 'Bénéfices non affectés'),
        ('income', 'Produits d\'exploitation'),
        ('income_other', 'Autres produits'),
        ('expense', 'Charges d\'exploitation'),
        ('expense_direct_cost', 'Coût direct'),
        ('expense_depreciation', 'Dotations aux amortissements'),
        ('off_balance', 'Hors bilan'),
    ], string='Type de compte', required=True)

    reconcile = fields.Boolean(
        string='Lettrable',
        default=False
    )
