# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BusinessPlanCashFlow(models.Model):
    """Plan de Trésorerie - Suivi mensuel sur 36 mois"""
    _name = 'business.plan.cash.flow'
    _description = 'Plan de Trésorerie'
    _order = 'business_plan_id, date'

    business_plan_id = fields.Many2one(
        'business.plan',
        string='Business Plan',
        required=True,
        ondelete='cascade',
    )
    date = fields.Date(
        string='Date (Mois)',
        required=True,
        help='Premier jour du mois concerné',
    )
    month_name = fields.Char(
        string='Mois',
        compute='_compute_month_name',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='business_plan_id.currency_id',
        readonly=True,
    )

    # ========== ENCAISSEMENTS ==========
    sales_receipts = fields.Monetary(
        string='Encaissements sur ventes',
        currency_field='currency_id',
        help='Chiffre d\'affaires encaissé dans le mois',
    )
    capital_input = fields.Monetary(
        string='Apport en capital',
        currency_field='currency_id',
    )
    loans_received = fields.Monetary(
        string='Emprunts reçus',
        currency_field='currency_id',
    )
    subsidies = fields.Monetary(
        string='Subventions',
        currency_field='currency_id',
    )
    other_receipts = fields.Monetary(
        string='Autres encaissements',
        currency_field='currency_id',
    )
    total_receipts = fields.Monetary(
        string='Total Encaissements',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== DÉCAISSEMENTS ==========
    # Achats et charges variables
    purchases = fields.Monetary(
        string='Achats de marchandises',
        currency_field='currency_id',
    )
    variable_costs = fields.Monetary(
        string='Charges variables',
        currency_field='currency_id',
        help='Coûts proportionnels au CA (matières premières, sous-traitance...)',
    )

    # Charges fixes
    salaries = fields.Monetary(
        string='Salaires et charges sociales',
        currency_field='currency_id',
    )
    rent = fields.Monetary(
        string='Loyer',
        currency_field='currency_id',
    )
    utilities = fields.Monetary(
        string='Énergie et fluides',
        currency_field='currency_id',
        help='Électricité, eau, gaz...',
    )
    insurance = fields.Monetary(
        string='Assurances',
        currency_field='currency_id',
    )
    marketing = fields.Monetary(
        string='Marketing et communication',
        currency_field='currency_id',
    )
    maintenance = fields.Monetary(
        string='Entretien et maintenance',
        currency_field='currency_id',
    )

    # Autres charges
    taxes = fields.Monetary(
        string='Impôts et taxes',
        currency_field='currency_id',
    )
    loan_repayments = fields.Monetary(
        string='Remboursements d\'emprunts',
        currency_field='currency_id',
        help='Capital + intérêts',
    )
    investments = fields.Monetary(
        string='Investissements',
        currency_field='currency_id',
        help='Achats d\'immobilisations',
    )
    other_expenses = fields.Monetary(
        string='Autres décaissements',
        currency_field='currency_id',
    )
    total_expenses = fields.Monetary(
        string='Total Décaissements',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    # ========== SOLDES ==========
    monthly_cash_flow = fields.Monetary(
        string='Flux de trésorerie mensuel',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Encaissements - Décaissements',
    )
    opening_balance = fields.Monetary(
        string='Solde initial',
        currency_field='currency_id',
        help='Trésorerie en début de mois',
    )
    closing_balance = fields.Monetary(
        string='Solde final',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Trésorerie en fin de mois',
    )

    # Alertes
    is_negative = fields.Boolean(
        string='Trésorerie négative',
        compute='_compute_alerts',
        store=True,
    )
    alert_level = fields.Selection([
        ('ok', 'OK'),
        ('warning', 'Alerte'),
        ('danger', 'Danger'),
    ], string='Niveau d\'alerte', compute='_compute_alerts', store=True)

    @api.depends('date')
    def _compute_month_name(self):
        """Calculer le nom du mois"""
        for record in self:
            if record.date:
                record.month_name = record.date.strftime('%B %Y').capitalize()
            else:
                record.month_name = ''

    @api.depends(
        'sales_receipts', 'capital_input', 'loans_received', 'subsidies', 'other_receipts',
        'purchases', 'variable_costs', 'salaries', 'rent', 'utilities', 'insurance',
        'marketing', 'maintenance', 'taxes', 'loan_repayments', 'investments', 'other_expenses',
        'opening_balance'
    )
    def _compute_totals(self):
        """Calculer les totaux et soldes"""
        for record in self:
            # Total encaissements
            record.total_receipts = (
                (record.sales_receipts or 0) +
                (record.capital_input or 0) +
                (record.loans_received or 0) +
                (record.subsidies or 0) +
                (record.other_receipts or 0)
            )

            # Total décaissements
            record.total_expenses = (
                (record.purchases or 0) +
                (record.variable_costs or 0) +
                (record.salaries or 0) +
                (record.rent or 0) +
                (record.utilities or 0) +
                (record.insurance or 0) +
                (record.marketing or 0) +
                (record.maintenance or 0) +
                (record.taxes or 0) +
                (record.loan_repayments or 0) +
                (record.investments or 0) +
                (record.other_expenses or 0)
            )

            # Flux de trésorerie mensuel
            record.monthly_cash_flow = record.total_receipts - record.total_expenses

            # Solde final
            record.closing_balance = (record.opening_balance or 0) + record.monthly_cash_flow

    @api.depends('closing_balance')
    def _compute_alerts(self):
        """Calculer les alertes de trésorerie"""
        for record in self:
            record.is_negative = record.closing_balance < 0

            if record.closing_balance < 0:
                record.alert_level = 'danger'
            elif record.closing_balance < 5000:
                record.alert_level = 'warning'
            else:
                record.alert_level = 'ok'

    @api.model
    def generate_cash_flow_plan(self, business_plan_id, start_date, months=36, initial_balance=0):
        """Générer un plan de trésorerie sur X mois"""
        business_plan = self.env['business.plan'].browse(business_plan_id)

        # Supprimer les anciens enregistrements
        self.search([('business_plan_id', '=', business_plan_id)]).unlink()

        cash_flows = []
        current_date = start_date
        previous_balance = initial_balance

        for month in range(months):
            # Créer l'enregistrement
            cash_flow = self.create({
                'business_plan_id': business_plan_id,
                'date': current_date,
                'opening_balance': previous_balance,
            })
            cash_flows.append(cash_flow)

            # Mettre à jour le solde précédent
            previous_balance = cash_flow.closing_balance

            # Mois suivant
            current_date = current_date + relativedelta(months=1)

        return cash_flows

    def action_copy_to_next_months(self):
        """Copier les valeurs sur les mois suivants"""
        self.ensure_one()

        # Trouver tous les mois suivants
        next_months = self.search([
            ('business_plan_id', '=', self.business_plan_id.id),
            ('date', '>', self.date),
        ], order='date')

        if not next_months:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Information'),
                    'message': _('Aucun mois suivant à copier'),
                    'type': 'warning',
                }
            }

        # Copier les valeurs (sauf les soldes et encaissements exceptionnels)
        values = {
            'sales_receipts': self.sales_receipts,
            'purchases': self.purchases,
            'variable_costs': self.variable_costs,
            'salaries': self.salaries,
            'rent': self.rent,
            'utilities': self.utilities,
            'insurance': self.insurance,
            'marketing': self.marketing,
            'maintenance': self.maintenance,
            'taxes': self.taxes,
            'loan_repayments': self.loan_repayments,
            'other_expenses': self.other_expenses,
        }

        for month in next_months:
            month.write(values)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'message': _('Valeurs copiées sur %d mois') % len(next_months),
                'type': 'success',
            }
        }
