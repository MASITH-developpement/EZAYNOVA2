# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BusinessPlanBalanceSheet(models.Model):
    """Bilan Prévisionnel - Actif et Passif"""
    _name = 'business.plan.balance.sheet'
    _description = 'Bilan Prévisionnel'
    _order = 'business_plan_id, year'

    business_plan_id = fields.Many2one(
        'business.plan',
        string='Business Plan',
        required=True,
        ondelete='cascade',
    )
    year = fields.Integer(
        string='Année',
        required=True,
        help='Année de prévision (1, 2 ou 3)',
    )
    year_label = fields.Char(
        string='Libellé',
        compute='_compute_year_label',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='business_plan_id.currency_id',
        readonly=True,
    )

    # ========== ACTIF ==========
    # Actif immobilisé
    intangible_assets = fields.Monetary(
        string='Immobilisations incorporelles',
        currency_field='currency_id',
        help='Brevets, marques, logiciels...',
    )
    tangible_assets = fields.Monetary(
        string='Immobilisations corporelles',
        currency_field='currency_id',
        help='Équipements, mobilier, véhicules...',
    )
    financial_assets = fields.Monetary(
        string='Immobilisations financières',
        currency_field='currency_id',
        help='Dépôts de garantie, cautions...',
    )
    total_fixed_assets = fields.Monetary(
        string='Total Actif Immobilisé',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # Actif circulant
    inventory = fields.Monetary(
        string='Stocks',
        currency_field='currency_id',
    )
    accounts_receivable = fields.Monetary(
        string='Créances clients',
        currency_field='currency_id',
    )
    other_receivables = fields.Monetary(
        string='Autres créances',
        currency_field='currency_id',
    )
    cash = fields.Monetary(
        string='Trésorerie',
        currency_field='currency_id',
        help='Banque + caisse',
    )
    total_current_assets = fields.Monetary(
        string='Total Actif Circulant',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # TOTAL ACTIF
    total_assets = fields.Monetary(
        string='TOTAL ACTIF',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== PASSIF ==========
    # Capitaux propres
    share_capital = fields.Monetary(
        string='Capital social',
        currency_field='currency_id',
    )
    reserves = fields.Monetary(
        string='Réserves',
        currency_field='currency_id',
    )
    retained_earnings = fields.Monetary(
        string='Résultat de l\'exercice',
        currency_field='currency_id',
    )
    total_equity = fields.Monetary(
        string='Total Capitaux Propres',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # Dettes
    long_term_debt = fields.Monetary(
        string='Emprunts à long terme',
        currency_field='currency_id',
        help='Part > 1 an',
    )
    short_term_debt = fields.Monetary(
        string='Emprunts à court terme',
        currency_field='currency_id',
        help='Part < 1 an',
    )
    accounts_payable = fields.Monetary(
        string='Dettes fournisseurs',
        currency_field='currency_id',
    )
    tax_payable = fields.Monetary(
        string='Dettes fiscales et sociales',
        currency_field='currency_id',
    )
    other_payables = fields.Monetary(
        string='Autres dettes',
        currency_field='currency_id',
    )
    total_liabilities = fields.Monetary(
        string='Total Dettes',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # TOTAL PASSIF
    total_equity_liabilities = fields.Monetary(
        string='TOTAL PASSIF',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # Vérification équilibre
    is_balanced = fields.Boolean(
        string='Équilibré',
        compute='_compute_totals',
        store=True,
    )
    balance_difference = fields.Monetary(
        string='Écart',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== RATIOS FINANCIERS ==========
    working_capital = fields.Monetary(
        string='Fonds de Roulement (FR)',
        compute='_compute_ratios',
        store=True,
        currency_field='currency_id',
        help='FR = Capitaux permanents - Actif immobilisé',
    )
    working_capital_requirement = fields.Monetary(
        string='Besoin en Fonds de Roulement (BFR)',
        compute='_compute_ratios',
        store=True,
        currency_field='currency_id',
        help='BFR = (Stocks + Créances) - Dettes court terme',
    )
    net_cash = fields.Monetary(
        string='Trésorerie Nette',
        compute='_compute_ratios',
        store=True,
        currency_field='currency_id',
        help='TN = FR - BFR',
    )
    current_ratio = fields.Float(
        string='Ratio de liquidité générale',
        compute='_compute_ratios',
        store=True,
        help='Actif circulant / Dettes court terme',
    )
    debt_to_equity_ratio = fields.Float(
        string='Ratio d\'endettement',
        compute='_compute_ratios',
        store=True,
        help='Total Dettes / Capitaux propres',
    )

    @api.depends('year')
    def _compute_year_label(self):
        """Calculer le libellé de l'année"""
        for record in self:
            if record.year:
                record.year_label = f'Année {record.year}'
            else:
                record.year_label = ''

    @api.depends(
        'intangible_assets', 'tangible_assets', 'financial_assets',
        'inventory', 'accounts_receivable', 'other_receivables', 'cash',
        'share_capital', 'reserves', 'retained_earnings',
        'long_term_debt', 'short_term_debt', 'accounts_payable',
        'tax_payable', 'other_payables'
    )
    def _compute_totals(self):
        """Calculer les totaux"""
        for record in self:
            # ACTIF
            record.total_fixed_assets = (
                (record.intangible_assets or 0) +
                (record.tangible_assets or 0) +
                (record.financial_assets or 0)
            )

            record.total_current_assets = (
                (record.inventory or 0) +
                (record.accounts_receivable or 0) +
                (record.other_receivables or 0) +
                (record.cash or 0)
            )

            record.total_assets = record.total_fixed_assets + record.total_current_assets

            # PASSIF
            record.total_equity = (
                (record.share_capital or 0) +
                (record.reserves or 0) +
                (record.retained_earnings or 0)
            )

            record.total_liabilities = (
                (record.long_term_debt or 0) +
                (record.short_term_debt or 0) +
                (record.accounts_payable or 0) +
                (record.tax_payable or 0) +
                (record.other_payables or 0)
            )

            record.total_equity_liabilities = record.total_equity + record.total_liabilities

            # Équilibre
            record.balance_difference = record.total_assets - record.total_equity_liabilities
            record.is_balanced = abs(record.balance_difference) < 0.01

    @api.depends(
        'total_fixed_assets', 'total_equity', 'long_term_debt',
        'inventory', 'accounts_receivable', 'accounts_payable',
        'tax_payable', 'short_term_debt', 'total_current_assets',
        'cash'
    )
    def _compute_ratios(self):
        """Calculer les ratios financiers"""
        for record in self:
            # Fonds de Roulement (FR)
            permanent_capital = (record.total_equity or 0) + (record.long_term_debt or 0)
            record.working_capital = permanent_capital - (record.total_fixed_assets or 0)

            # BFR
            current_assets_excl_cash = (
                (record.inventory or 0) +
                (record.accounts_receivable or 0) +
                (record.other_receivables or 0)
            )
            current_liabilities = (
                (record.accounts_payable or 0) +
                (record.tax_payable or 0) +
                (record.other_payables or 0)
            )
            record.working_capital_requirement = current_assets_excl_cash - current_liabilities

            # Trésorerie Nette
            record.net_cash = record.working_capital - record.working_capital_requirement

            # Ratio de liquidité générale
            total_short_term_debt = (
                (record.short_term_debt or 0) +
                (record.accounts_payable or 0) +
                (record.tax_payable or 0) +
                (record.other_payables or 0)
            )
            if total_short_term_debt > 0:
                record.current_ratio = (record.total_current_assets or 0) / total_short_term_debt
            else:
                record.current_ratio = 0.0

            # Ratio d'endettement
            if record.total_equity > 0:
                record.debt_to_equity_ratio = (record.total_liabilities or 0) / record.total_equity
            else:
                record.debt_to_equity_ratio = 0.0

    @api.constrains('year')
    def _check_year(self):
        """Vérifier que l'année est valide"""
        for record in self:
            if record.year < 1 or record.year > 10:
                raise ValidationError(_('L\'année doit être entre 1 et 10.'))

    @api.model
    def generate_balance_sheets(self, business_plan_id, years=3):
        """Générer les bilans prévisionnels pour X années"""
        # Supprimer les anciens
        self.search([('business_plan_id', '=', business_plan_id)]).unlink()

        balance_sheets = []
        for year in range(1, years + 1):
            bs = self.create({
                'business_plan_id': business_plan_id,
                'year': year,
            })
            balance_sheets.append(bs)

        return balance_sheets
