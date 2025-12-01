# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BusinessPlanFinancing(models.Model):
    """Plan de Financement - Sources et emplois"""
    _name = 'business.plan.financing'
    _description = 'Plan de Financement'
    _order = 'business_plan_id, sequence, id'

    business_plan_id = fields.Many2one(
        'business.plan',
        string='Business Plan',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Séquence', default=10)
    currency_id = fields.Many2one(
        'res.currency',
        related='business_plan_id.currency_id',
        readonly=True,
    )

    # Type de ligne
    line_type = fields.Selection([
        ('source', 'Source de financement'),
        ('use', 'Emploi (Besoin)'),
    ], string='Type', required=True, default='source')

    # Catégorie
    category = fields.Selection([
        # Sources
        ('equity', 'Apport en capital'),
        ('loan', 'Emprunt bancaire'),
        ('honor_loan', 'Prêt d\'honneur'),
        ('subsidy', 'Subvention'),
        ('other_source', 'Autre source'),
        # Emplois
        ('equipment', 'Équipements et matériel'),
        ('vehicle', 'Véhicule'),
        ('furniture', 'Mobilier et agencements'),
        ('it', 'Informatique et logiciels'),
        ('stock', 'Stock initial'),
        ('working_capital', 'Besoin en fonds de roulement (BFR)'),
        ('setup_costs', 'Frais d\'établissement'),
        ('deposits', 'Dépôts et cautionnements'),
        ('other_use', 'Autre emploi'),
    ], string='Catégorie', required=True)

    name = fields.Char(string='Description', required=True)
    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
    )

    # Pour les emprunts
    is_loan = fields.Boolean(
        string='Est un emprunt',
        compute='_compute_is_loan',
        store=True,
    )
    interest_rate = fields.Float(
        string='Taux d\'intérêt (%)',
        help='Taux annuel',
    )
    duration_months = fields.Integer(
        string='Durée (mois)',
    )
    monthly_payment = fields.Monetary(
        string='Mensualité',
        compute='_compute_monthly_payment',
        store=True,
        currency_field='currency_id',
    )

    notes = fields.Text(string='Notes')

    @api.depends('category')
    def _compute_is_loan(self):
        """Déterminer si c'est un emprunt"""
        for record in self:
            record.is_loan = record.category in ('loan', 'honor_loan')

    @api.depends('amount', 'interest_rate', 'duration_months')
    def _compute_monthly_payment(self):
        """Calculer la mensualité d'un emprunt"""
        for record in self:
            if record.is_loan and record.amount and record.interest_rate and record.duration_months:
                # Formule de calcul de mensualité
                # M = C * (t / (1 - (1 + t)^(-n)))
                # où t = taux mensuel, n = nombre de mois, C = capital
                monthly_rate = (record.interest_rate / 100) / 12
                n = record.duration_months

                if monthly_rate == 0:
                    # Si taux = 0, mensualité = montant / durée
                    record.monthly_payment = record.amount / n
                else:
                    numerator = monthly_rate * record.amount
                    denominator = 1 - ((1 + monthly_rate) ** -n)
                    record.monthly_payment = numerator / denominator
            else:
                record.monthly_payment = 0.0

    @api.model
    def get_financing_summary(self, business_plan_id):
        """Obtenir un résumé du plan de financement"""
        financing_lines = self.search([('business_plan_id', '=', business_plan_id)])

        sources = financing_lines.filtered(lambda l: l.line_type == 'source')
        uses = financing_lines.filtered(lambda l: l.line_type == 'use')

        total_sources = sum(sources.mapped('amount'))
        total_uses = sum(uses.mapped('amount'))
        balance = total_sources - total_uses

        # Détail des sources
        source_detail = {}
        for source in sources:
            category_name = dict(self._fields['category'].selection).get(source.category)
            if category_name not in source_detail:
                source_detail[category_name] = 0
            source_detail[category_name] += source.amount

        # Détail des emplois
        use_detail = {}
        for use in uses:
            category_name = dict(self._fields['category'].selection).get(use.category)
            if category_name not in use_detail:
                use_detail[category_name] = 0
            use_detail[category_name] += use.amount

        return {
            'total_sources': total_sources,
            'total_uses': total_uses,
            'balance': balance,
            'is_balanced': abs(balance) < 0.01,  # Tolérance de 1 centime
            'source_detail': source_detail,
            'use_detail': use_detail,
            'loans': sources.filtered(lambda l: l.is_loan),
            'total_monthly_payments': sum(sources.filtered(lambda l: l.is_loan).mapped('monthly_payment')),
        }

    @api.constrains('amount')
    def _check_amount(self):
        """Vérifier que le montant est positif"""
        for record in self:
            if record.amount < 0:
                raise ValidationError(_('Le montant doit être positif.'))

    @api.constrains('interest_rate', 'duration_months')
    def _check_loan_fields(self):
        """Vérifier les champs d'emprunt"""
        for record in self:
            if record.is_loan:
                if not record.interest_rate or record.interest_rate < 0:
                    raise ValidationError(_('Le taux d\'intérêt doit être positif pour un emprunt.'))
                if not record.duration_months or record.duration_months <= 0:
                    raise ValidationError(_('La durée doit être positive pour un emprunt.'))


class BusinessPlanFinancingWizard(models.TransientModel):
    """Wizard pour créer rapidement un plan de financement standard"""
    _name = 'business.plan.financing.wizard'
    _description = 'Assistant Plan de Financement'

    business_plan_id = fields.Many2one('business.plan', required=True)
    currency_id = fields.Many2one('res.currency', related='business_plan_id.currency_id')

    # ========== SOURCES ==========
    equity_amount = fields.Monetary('Apport personnel', currency_field='currency_id')
    loan_amount = fields.Monetary('Emprunt bancaire', currency_field='currency_id')
    loan_rate = fields.Float('Taux emprunt (%)', default=3.5)
    loan_duration = fields.Integer('Durée emprunt (mois)', default=84)
    honor_loan_amount = fields.Monetary('Prêt d\'honneur', currency_field='currency_id')
    subsidy_amount = fields.Monetary('Subventions', currency_field='currency_id')

    # ========== EMPLOIS ==========
    equipment_amount = fields.Monetary('Équipements', currency_field='currency_id')
    vehicle_amount = fields.Monetary('Véhicule', currency_field='currency_id')
    furniture_amount = fields.Monetary('Mobilier', currency_field='currency_id')
    it_amount = fields.Monetary('Informatique', currency_field='currency_id')
    stock_amount = fields.Monetary('Stock initial', currency_field='currency_id')
    bfr_amount = fields.Monetary('BFR', currency_field='currency_id')
    setup_costs_amount = fields.Monetary('Frais d\'établissement', currency_field='currency_id')

    def action_generate(self):
        """Générer le plan de financement"""
        self.ensure_one()

        # Supprimer les anciennes lignes
        self.env['business.plan.financing'].search([
            ('business_plan_id', '=', self.business_plan_id.id)
        ]).unlink()

        FinancingLine = self.env['business.plan.financing']

        # Créer les sources
        if self.equity_amount:
            FinancingLine.create({
                'business_plan_id': self.business_plan_id.id,
                'line_type': 'source',
                'category': 'equity',
                'name': 'Apport personnel',
                'amount': self.equity_amount,
                'sequence': 10,
            })

        if self.loan_amount:
            FinancingLine.create({
                'business_plan_id': self.business_plan_id.id,
                'line_type': 'source',
                'category': 'loan',
                'name': 'Emprunt bancaire',
                'amount': self.loan_amount,
                'interest_rate': self.loan_rate,
                'duration_months': self.loan_duration,
                'sequence': 20,
            })

        if self.honor_loan_amount:
            FinancingLine.create({
                'business_plan_id': self.business_plan_id.id,
                'line_type': 'source',
                'category': 'honor_loan',
                'name': 'Prêt d\'honneur',
                'amount': self.honor_loan_amount,
                'interest_rate': 0.0,
                'duration_months': 60,
                'sequence': 30,
            })

        if self.subsidy_amount:
            FinancingLine.create({
                'business_plan_id': self.business_plan_id.id,
                'line_type': 'source',
                'category': 'subsidy',
                'name': 'Subventions',
                'amount': self.subsidy_amount,
                'sequence': 40,
            })

        # Créer les emplois
        emplois = [
            ('equipment', 'Équipements et matériel', self.equipment_amount, 10),
            ('vehicle', 'Véhicule', self.vehicle_amount, 20),
            ('furniture', 'Mobilier et agencements', self.furniture_amount, 30),
            ('it', 'Informatique et logiciels', self.it_amount, 40),
            ('stock', 'Stock initial', self.stock_amount, 50),
            ('working_capital', 'Besoin en fonds de roulement', self.bfr_amount, 60),
            ('setup_costs', 'Frais d\'établissement', self.setup_costs_amount, 70),
        ]

        for category, name, amount, sequence in emplois:
            if amount:
                FinancingLine.create({
                    'business_plan_id': self.business_plan_id.id,
                    'line_type': 'use',
                    'category': category,
                    'name': name,
                    'amount': amount,
                    'sequence': sequence,
                })

        return {'type': 'ir.actions.act_window_close'}
