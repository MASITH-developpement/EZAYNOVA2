# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _description = 'Ligne d\'écriture comptable'
    _order = 'move_id desc, sequence, id'

    move_id = fields.Many2one(
        'account.move',
        string='Écriture',
        required=True,
        ondelete='cascade',
        index=True
    )

    move_name = fields.Char(
        string='Numéro d\'écriture',
        related='move_id.name',
        store=True,
        index=True
    )

    date = fields.Date(
        string='Date',
        related='move_id.date',
        store=True,
        index=True
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    name = fields.Char(
        string='Libellé',
        required=True
    )

    ref = fields.Char(
        string='Référence'
    )

    # Compte
    account_id = fields.Many2one(
        'account.chart',
        string='Compte',
        required=True,
        index=True,
        domain=[('deprecated', '=', False)]
    )

    # Partenaire
    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        index=True
    )

    # Montants
    debit = fields.Monetary(
        string='Débit',
        default=0.0,
        currency_field='company_currency_id'
    )

    credit = fields.Monetary(
        string='Crédit',
        default=0.0,
        currency_field='company_currency_id'
    )

    balance = fields.Monetary(
        string='Solde',
        compute='_compute_balance',
        store=True,
        currency_field='company_currency_id'
    )

    # Devise
    amount_currency = fields.Monetary(
        string='Montant devise',
        default=0.0,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise'
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        related='move_id.company_id.currency_id',
        string='Devise société',
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        related='move_id.company_id',
        string='Société',
        store=True
    )

    # Taxes
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes',
        help='Taxes appliquées sur cette ligne'
    )

    tax_line_id = fields.Many2one(
        'account.tax',
        string='Taxe d\'origine',
        help='Indique que cette ligne est une ligne de taxe'
    )

    tax_base_amount = fields.Monetary(
        string='Base de taxe',
        currency_field='company_currency_id',
        help='Montant de base pour le calcul de la taxe'
    )

    # Analytique
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Compte analytique'
    )

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Tags analytiques'
    )

    # Lettrage
    full_reconcile_id = fields.Many2one(
        'account.full.reconcile',
        string='Lettrage complet',
        copy=False
    )

    matching_number = fields.Char(
        string='Numéro de lettrage',
        compute='_compute_matching_number',
        store=True
    )

    reconciled = fields.Boolean(
        string='Lettré',
        compute='_compute_reconciled',
        store=True
    )

    # Produit (pour factures)
    product_id = fields.Many2one(
        'product.product',
        string='Produit'
    )

    quantity = fields.Float(
        string='Quantité',
        default=1.0
    )

    price_unit = fields.Float(
        string='Prix unitaire'
    )

    discount = fields.Float(
        string='Remise (%)',
        default=0.0
    )

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        """Calcule le solde (débit - crédit)"""
        for line in self:
            line.balance = line.debit - line.credit

    @api.depends('full_reconcile_id')
    def _compute_matching_number(self):
        """Récupère le numéro de lettrage"""
        for line in self:
            line.matching_number = line.full_reconcile_id.name if line.full_reconcile_id else False

    @api.depends('full_reconcile_id')
    def _compute_reconciled(self):
        """Vérifie si la ligne est lettrée"""
        for line in self:
            line.reconciled = bool(line.full_reconcile_id)

    @api.constrains('debit', 'credit')
    def _check_debit_credit(self):
        """Vérifie qu'une ligne ne peut pas avoir débit ET crédit"""
        for line in self:
            if line.debit > 0 and line.credit > 0:
                raise ValidationError(_(
                    'Une ligne ne peut pas avoir à la fois un débit et un crédit.\n'
                    'Ligne : %s'
                ) % line.name)

    @api.constrains('analytic_account_id', 'account_id')
    def _check_analytic_required(self):
        """Vérifie que l'analytique est rempli si requis"""
        for line in self:
            if line.account_id.analytic_required and not line.analytic_account_id:
                raise ValidationError(_(
                    'Un compte analytique est obligatoire pour le compte %s.'
                ) % line.account_id.complete_name)

    @api.onchange('account_id')
    def _onchange_account_id(self):
        """Remplit automatiquement selon le compte"""
        if self.account_id:
            # Taxes par défaut
            if self.account_id.tax_ids and not self.tax_line_id:
                self.tax_ids = self.account_id.tax_ids

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Remplit automatiquement selon le produit"""
        if self.product_id:
            # Nom
            if not self.name:
                self.name = self.product_id.name

            # Prix
            if not self.price_unit:
                if self.move_id.move_type in ['out_invoice', 'out_refund']:
                    self.price_unit = self.product_id.lst_price
                else:
                    self.price_unit = self.product_id.standard_price

            # Taxes
            if not self.tax_ids:
                if self.move_id.move_type in ['out_invoice', 'out_refund']:
                    self.tax_ids = self.product_id.taxes_id
                else:
                    self.tax_ids = self.product_id.supplier_taxes_id

    @api.onchange('quantity', 'price_unit', 'discount', 'tax_ids')
    def _onchange_price_subtotal(self):
        """Calcule les montants selon quantité, prix et remise"""
        if self.quantity and self.price_unit:
            # Calcul du montant HT
            amount = self.quantity * self.price_unit
            if self.discount:
                amount = amount * (1 - self.discount / 100.0)

            # Calculer les taxes
            if self.tax_ids:
                taxes = self.tax_ids.compute_all(
                    self.price_unit,
                    currency=self.currency_id or self.company_currency_id,
                    quantity=self.quantity,
                    product=self.product_id,
                    partner=self.partner_id
                )
                amount = taxes['total_excluded']

            # Mettre à jour débit ou crédit selon le type
            if self.move_id.move_type in ['out_invoice', 'in_refund']:
                self.debit = amount
                self.credit = 0.0
            elif self.move_id.move_type in ['in_invoice', 'out_refund']:
                self.credit = amount
                self.debit = 0.0

    def action_reconcile(self):
        """Lettre les lignes sélectionnées"""
        # Vérifier que toutes les lignes sont sur des comptes lettrables
        for line in self:
            if not line.account_id.reconcile:
                raise ValidationError(_(
                    'Le compte %s n\'est pas lettrable.'
                ) % line.account_id.complete_name)

        # Vérifier l'équilibre
        total_debit = sum(self.mapped('debit'))
        total_credit = sum(self.mapped('credit'))

        if round(total_debit, 2) != round(total_credit, 2):
            raise ValidationError(_(
                'Les lignes ne sont pas équilibrées.\n'
                'Débit: %.2f\nCrédit: %.2f\nDifférence: %.2f'
            ) % (total_debit, total_credit, total_debit - total_credit))

        # Créer le lettrage
        reconcile = self.env['account.full.reconcile'].create({
            'name': self.env['ir.sequence'].next_by_code('account.reconcile') or 'R'
        })

        self.write({'full_reconcile_id': reconcile.id})

        return True

    def action_unreconcile(self):
        """Délettre les lignes"""
        reconciles = self.mapped('full_reconcile_id')
        self.write({'full_reconcile_id': False})
        reconciles.unlink()

        return True


class AccountFullReconcile(models.Model):
    _name = 'account.full.reconcile'
    _description = 'Lettrage complet'

    name = fields.Char(
        string='Numéro',
        required=True
    )

    reconciled_line_ids = fields.One2many(
        'account.move.line',
        'full_reconcile_id',
        string='Lignes lettrées'
    )

    create_date = fields.Datetime(
        string='Date de lettrage',
        readonly=True
    )
