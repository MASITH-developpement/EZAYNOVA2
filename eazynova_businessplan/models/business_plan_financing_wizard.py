# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BusinessPlanFinancingWizard(models.TransientModel):
    """Assistant de génération rapide du plan de financement"""
    _name = 'business.plan.financing.wizard'
    _description = 'Assistant Plan de Financement'

    business_plan_id = fields.Many2one(
        'business.plan',
        string='Business Plan',
        required=True,
        ondelete='cascade',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='business_plan_id.currency_id',
        readonly=True,
    )

    # ===== SOURCES DE FINANCEMENT =====
    equity_amount = fields.Monetary(
        string='Apport en capital',
        currency_field='currency_id',
        help='Apport personnel ou des associés',
    )
    loan_amount = fields.Monetary(
        string='Emprunt bancaire',
        currency_field='currency_id',
    )
    loan_rate = fields.Float(
        string='Taux emprunt (%)',
        default=3.5,
        help='Taux annuel',
    )
    loan_duration = fields.Integer(
        string='Durée emprunt (mois)',
        default=84,
        help='84 mois = 7 ans',
    )
    honor_loan_amount = fields.Monetary(
        string='Prêt d\'honneur',
        currency_field='currency_id',
    )
    subsidy_amount = fields.Monetary(
        string='Subventions',
        currency_field='currency_id',
    )

    # ===== EMPLOIS (BESOINS) =====
    equipment_amount = fields.Monetary(
        string='Équipements',
        currency_field='currency_id',
    )
    vehicle_amount = fields.Monetary(
        string='Véhicule',
        currency_field='currency_id',
    )
    furniture_amount = fields.Monetary(
        string='Mobilier/Agencements',
        currency_field='currency_id',
    )
    it_amount = fields.Monetary(
        string='Informatique',
        currency_field='currency_id',
    )
    stock_amount = fields.Monetary(
        string='Stock initial',
        currency_field='currency_id',
    )
    bfr_amount = fields.Monetary(
        string='BFR',
        currency_field='currency_id',
        help='Besoin en Fonds de Roulement',
    )
    setup_costs_amount = fields.Monetary(
        string='Frais d\'établissement',
        currency_field='currency_id',
    )

    def action_generate(self):
        """Générer le plan de financement à partir du wizard"""
        self.ensure_one()

        if not self.business_plan_id:
            raise UserError(_('Aucun Business Plan sélectionné.'))

        # Supprimer les lignes existantes
        self.env['business.plan.financing'].search([
            ('business_plan_id', '=', self.business_plan_id.id)
        ]).unlink()

        # Préparer les lignes à créer
        lines_to_create = []
        sequence = 10

        # ===== SOURCES =====
        if self.equity_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'source',
                'category': 'equity',
                'name': 'Apport en capital',
                'amount': self.equity_amount,
            })
            sequence += 10

        if self.loan_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'source',
                'category': 'loan',
                'name': 'Emprunt bancaire',
                'amount': self.loan_amount,
                'interest_rate': self.loan_rate,
                'duration_months': self.loan_duration,
            })
            sequence += 10

        if self.honor_loan_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'source',
                'category': 'honor_loan',
                'name': 'Prêt d\'honneur',
                'amount': self.honor_loan_amount,
            })
            sequence += 10

        if self.subsidy_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'source',
                'category': 'subsidy',
                'name': 'Subventions',
                'amount': self.subsidy_amount,
            })
            sequence += 10

        # ===== EMPLOIS =====
        if self.equipment_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'equipment',
                'name': 'Équipements et matériel',
                'amount': self.equipment_amount,
            })
            sequence += 10

        if self.vehicle_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'vehicle',
                'name': 'Véhicule',
                'amount': self.vehicle_amount,
            })
            sequence += 10

        if self.furniture_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'furniture',
                'name': 'Mobilier et agencements',
                'amount': self.furniture_amount,
            })
            sequence += 10

        if self.it_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'it',
                'name': 'Informatique et logiciels',
                'amount': self.it_amount,
            })
            sequence += 10

        if self.stock_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'stock',
                'name': 'Stock initial',
                'amount': self.stock_amount,
            })
            sequence += 10

        if self.bfr_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'working_capital',
                'name': 'Besoin en Fonds de Roulement',
                'amount': self.bfr_amount,
            })
            sequence += 10

        if self.setup_costs_amount:
            lines_to_create.append({
                'business_plan_id': self.business_plan_id.id,
                'sequence': sequence,
                'line_type': 'use',
                'category': 'setup_costs',
                'name': 'Frais d\'établissement',
                'amount': self.setup_costs_amount,
            })
            sequence += 10

        # Créer toutes les lignes
        if lines_to_create:
            self.env['business.plan.financing'].create(lines_to_create)

        # Retourner l'action pour afficher le plan de financement
        return {
            'type': 'ir.actions.act_window',
            'name': _('Plan de Financement'),
            'res_model': 'business.plan.financing',
            'view_mode': 'list,form',
            'domain': [('business_plan_id', '=', self.business_plan_id.id)],
            'context': {'default_business_plan_id': self.business_plan_id.id},
        }
