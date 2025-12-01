# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BusinessPlanIncomeStatement(models.Model):
    """Compte de Résultat Prévisionnel Détaillé"""
    _name = 'business.plan.income.statement'
    _description = 'Compte de Résultat Prévisionnel'
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

    # ========== PRODUITS D'EXPLOITATION ==========
    sales_revenue = fields.Monetary(
        string='Ventes de marchandises',
        currency_field='currency_id',
    )
    services_revenue = fields.Monetary(
        string='Prestations de services',
        currency_field='currency_id',
    )
    production_revenue = fields.Monetary(
        string='Production vendue',
        currency_field='currency_id',
    )
    other_revenues = fields.Monetary(
        string='Autres produits d\'exploitation',
        currency_field='currency_id',
    )
    total_revenues = fields.Monetary(
        string='Chiffre d\'Affaires (HT)',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== CHARGES D'EXPLOITATION ==========
    # Achats et charges externes
    purchases_goods = fields.Monetary(
        string='Achats de marchandises',
        currency_field='currency_id',
    )
    purchases_materials = fields.Monetary(
        string='Achats de matières premières',
        currency_field='currency_id',
    )
    subcontracting = fields.Monetary(
        string='Sous-traitance',
        currency_field='currency_id',
    )
    rent = fields.Monetary(
        string='Loyers et charges locatives',
        currency_field='currency_id',
    )
    maintenance = fields.Monetary(
        string='Entretien et réparations',
        currency_field='currency_id',
    )
    utilities = fields.Monetary(
        string='Énergie et fluides',
        currency_field='currency_id',
    )
    insurance_premiums = fields.Monetary(
        string='Assurances',
        currency_field='currency_id',
    )
    documentation = fields.Monetary(
        string='Documentation et formation',
        currency_field='currency_id',
    )
    advertising = fields.Monetary(
        string='Publicité et communication',
        currency_field='currency_id',
    )
    transportation = fields.Monetary(
        string='Déplacements et transports',
        currency_field='currency_id',
    )
    banking_fees = fields.Monetary(
        string='Services bancaires',
        currency_field='currency_id',
    )
    professional_fees = fields.Monetary(
        string='Honoraires (experts, avocats...)',
        currency_field='currency_id',
    )
    other_external_charges = fields.Monetary(
        string='Autres charges externes',
        currency_field='currency_id',
    )
    total_external_charges = fields.Monetary(
        string='Total Charges Externes',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # Marge commerciale (pour le commerce)
    commercial_margin = fields.Monetary(
        string='Marge Commerciale',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='CA ventes - Achats de marchandises (pour activité commerciale)',
    )

    # Valeur ajoutée
    value_added = fields.Monetary(
        string='Valeur Ajoutée',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Production - Consommations externes',
    )

    # Impôts et taxes
    business_taxes = fields.Monetary(
        string='Taxes et impôts (hors IS)',
        currency_field='currency_id',
        help='CFE, taxe foncière, formation professionnelle...',
    )

    # Charges de personnel
    gross_salaries = fields.Monetary(
        string='Salaires bruts',
        currency_field='currency_id',
    )
    social_charges = fields.Monetary(
        string='Charges sociales',
        currency_field='currency_id',
        help='Cotisations patronales',
    )
    total_personnel_costs = fields.Monetary(
        string='Total Charges de Personnel',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # EBE
    ebitda = fields.Monetary(
        string='EBE (EBITDA)',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Excédent Brut d\'Exploitation = VA - Impôts/taxes - Charges personnel',
    )

    # Dotations aux amortissements
    depreciation = fields.Monetary(
        string='Dotations aux amortissements',
        currency_field='currency_id',
    )

    # Résultat d'exploitation
    operating_profit = fields.Monetary(
        string='Résultat d\'Exploitation',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='EBE - Amortissements',
    )

    # ========== RÉSULTAT FINANCIER ==========
    financial_income = fields.Monetary(
        string='Produits financiers',
        currency_field='currency_id',
    )
    financial_expenses = fields.Monetary(
        string='Charges financières (intérêts)',
        currency_field='currency_id',
    )
    financial_result = fields.Monetary(
        string='Résultat Financier',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== RÉSULTAT EXCEPTIONNEL ==========
    exceptional_income = fields.Monetary(
        string='Produits exceptionnels',
        currency_field='currency_id',
    )
    exceptional_expenses = fields.Monetary(
        string='Charges exceptionnelles',
        currency_field='currency_id',
    )
    exceptional_result = fields.Monetary(
        string='Résultat Exceptionnel',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== RÉSULTAT AVANT IMPÔT ==========
    profit_before_tax = fields.Monetary(
        string='Résultat Avant Impôt',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # Impôt sur les sociétés
    corporate_tax = fields.Monetary(
        string='Impôt sur les Sociétés',
        currency_field='currency_id',
    )
    corporate_tax_rate = fields.Float(
        string='Taux IS (%)',
        default=25.0,
        help='Taux d\'impôt sur les sociétés',
    )

    # ========== RÉSULTAT NET ==========
    net_profit = fields.Monetary(
        string='Résultat Net',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== RATIOS ET INDICATEURS ==========
    gross_margin_rate = fields.Float(
        string='Taux de Marge Brute (%)',
        compute='_compute_ratios',
        store=True,
        help='(Marge commerciale / CA ventes) × 100',
    )
    value_added_rate = fields.Float(
        string='Taux de Valeur Ajoutée (%)',
        compute='_compute_ratios',
        store=True,
        help='(VA / Production) × 100',
    )
    ebitda_margin = fields.Float(
        string='Marge d\'EBE (%)',
        compute='_compute_ratios',
        store=True,
        help='(EBE / CA) × 100',
    )
    operating_margin = fields.Float(
        string='Marge d\'Exploitation (%)',
        compute='_compute_ratios',
        store=True,
        help='(Résultat exploitation / CA) × 100',
    )
    net_margin = fields.Float(
        string='Marge Nette (%)',
        compute='_compute_ratios',
        store=True,
        help='(Résultat net / CA) × 100',
    )
    breakeven_point = fields.Monetary(
        string='Seuil de Rentabilité',
        compute='_compute_ratios',
        store=True,
        currency_field='currency_id',
        help='CA à partir duquel l\'entreprise est rentable',
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
        'sales_revenue', 'services_revenue', 'production_revenue', 'other_revenues',
        'purchases_goods', 'purchases_materials', 'subcontracting',
        'rent', 'maintenance', 'utilities', 'insurance_premiums',
        'documentation', 'advertising', 'transportation',
        'banking_fees', 'professional_fees', 'other_external_charges',
        'business_taxes', 'gross_salaries', 'social_charges',
        'depreciation', 'financial_income', 'financial_expenses',
        'exceptional_income', 'exceptional_expenses', 'corporate_tax'
    )
    def _compute_totals(self):
        """Calculer tous les totaux et résultats"""
        for record in self:
            # Chiffre d'affaires total
            record.total_revenues = (
                (record.sales_revenue or 0) +
                (record.services_revenue or 0) +
                (record.production_revenue or 0) +
                (record.other_revenues or 0)
            )

            # Marge commerciale (pour commerce)
            record.commercial_margin = (record.sales_revenue or 0) - (record.purchases_goods or 0)

            # Total charges externes
            record.total_external_charges = (
                (record.purchases_materials or 0) +
                (record.subcontracting or 0) +
                (record.rent or 0) +
                (record.maintenance or 0) +
                (record.utilities or 0) +
                (record.insurance_premiums or 0) +
                (record.documentation or 0) +
                (record.advertising or 0) +
                (record.transportation or 0) +
                (record.banking_fees or 0) +
                (record.professional_fees or 0) +
                (record.other_external_charges or 0)
            )

            # Valeur ajoutée
            production = (
                (record.services_revenue or 0) +
                (record.production_revenue or 0) +
                record.commercial_margin
            )
            record.value_added = production - record.total_external_charges

            # Charges de personnel
            record.total_personnel_costs = (
                (record.gross_salaries or 0) +
                (record.social_charges or 0)
            )

            # EBE (EBITDA)
            record.ebitda = (
                record.value_added -
                (record.business_taxes or 0) -
                record.total_personnel_costs
            )

            # Résultat d'exploitation
            record.operating_profit = record.ebitda - (record.depreciation or 0)

            # Résultat financier
            record.financial_result = (
                (record.financial_income or 0) -
                (record.financial_expenses or 0)
            )

            # Résultat exceptionnel
            record.exceptional_result = (
                (record.exceptional_income or 0) -
                (record.exceptional_expenses or 0)
            )

            # Résultat avant impôt
            record.profit_before_tax = (
                record.operating_profit +
                record.financial_result +
                record.exceptional_result
            )

            # Résultat net
            record.net_profit = record.profit_before_tax - (record.corporate_tax or 0)

    @api.depends(
        'commercial_margin', 'sales_revenue', 'value_added',
        'production_revenue', 'services_revenue',
        'ebitda', 'operating_profit', 'net_profit', 'total_revenues',
        'total_external_charges', 'total_personnel_costs', 'business_taxes'
    )
    def _compute_ratios(self):
        """Calculer les ratios"""
        for record in self:
            # Taux de marge brute
            if record.sales_revenue:
                record.gross_margin_rate = (record.commercial_margin / record.sales_revenue) * 100
            else:
                record.gross_margin_rate = 0.0

            # Taux de VA
            production = (
                (record.services_revenue or 0) +
                (record.production_revenue or 0) +
                record.commercial_margin
            )
            if production:
                record.value_added_rate = (record.value_added / production) * 100
            else:
                record.value_added_rate = 0.0

            # Marges
            if record.total_revenues:
                record.ebitda_margin = (record.ebitda / record.total_revenues) * 100
                record.operating_margin = (record.operating_profit / record.total_revenues) * 100
                record.net_margin = (record.net_profit / record.total_revenues) * 100
            else:
                record.ebitda_margin = 0.0
                record.operating_margin = 0.0
                record.net_margin = 0.0

            # Seuil de rentabilité (simplifié)
            # SR = Charges fixes / Taux de marge sur coût variable
            fixed_costs = (
                record.total_external_charges +
                record.total_personnel_costs +
                (record.business_taxes or 0) +
                (record.depreciation or 0)
            )
            if record.total_revenues:
                variable_costs_rate = (
                    (record.purchases_goods or 0) +
                    (record.purchases_materials or 0)
                ) / record.total_revenues if record.total_revenues else 0

                margin_rate = 1 - variable_costs_rate
                if margin_rate > 0:
                    record.breakeven_point = fixed_costs / margin_rate
                else:
                    record.breakeven_point = 0.0
            else:
                record.breakeven_point = 0.0

    @api.onchange('profit_before_tax', 'corporate_tax_rate')
    def _onchange_calculate_corporate_tax(self):
        """Calculer l'impôt sur les sociétés automatiquement"""
        if self.profit_before_tax > 0 and self.corporate_tax_rate:
            self.corporate_tax = self.profit_before_tax * (self.corporate_tax_rate / 100)
        else:
            self.corporate_tax = 0.0

    @api.constrains('year')
    def _check_year(self):
        """Vérifier que l'année est valide"""
        for record in self:
            if record.year < 1 or record.year > 10:
                raise ValidationError(_('L\'année doit être entre 1 et 10.'))

    @api.model
    def generate_income_statements(self, business_plan_id, years=3):
        """Générer les comptes de résultat pour X années"""
        # Supprimer les anciens
        self.search([('business_plan_id', '=', business_plan_id)]).unlink()

        income_statements = []
        for year in range(1, years + 1):
            income_stmt = self.create({
                'business_plan_id': business_plan_id,
                'year': year,
            })
            income_statements.append(income_stmt)

        return income_statements
