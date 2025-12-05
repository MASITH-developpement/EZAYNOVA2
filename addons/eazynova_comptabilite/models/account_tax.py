# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _name = 'account.tax'
    _description = 'Taxe (TVA)'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la taxe'
    )

    description = fields.Char(
        string='Label sur facture',
        help='Libellé affiché sur les factures'
    )

    type_tax_use = fields.Selection([
        ('sale', 'Vente'),
        ('purchase', 'Achat'),
        ('none', 'Aucun'),
    ], string='Type de taxe', required=True, default='sale')

    amount_type = fields.Selection([
        ('percent', 'Pourcentage du prix'),
        ('fixed', 'Montant fixe'),
        ('division', 'Pourcentage du prix (division)'),
    ], string='Type de calcul', required=True, default='percent')

    amount = fields.Float(
        string='Montant',
        required=True,
        default=20.0,
        help='Taux de taxe en pourcentage ou montant fixe'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    # Comptes comptables
    invoice_repartition_line_ids = fields.One2many(
        'account.tax.repartition.line',
        'invoice_tax_id',
        string='Répartition sur facture',
        help='Comptes utilisés pour enregistrer la taxe sur les factures'
    )

    refund_repartition_line_ids = fields.One2many(
        'account.tax.repartition.line',
        'refund_tax_id',
        string='Répartition sur avoir',
        help='Comptes utilisés pour enregistrer la taxe sur les avoirs'
    )

    # TVA intracommunautaire
    is_intracom = fields.Boolean(
        string='TVA intracommunautaire',
        default=False,
        help='Utilisé pour les transactions intracommunautaires'
    )

    # Options
    price_include = fields.Boolean(
        string='Prix TTC',
        default=False,
        help='Le prix inclut cette taxe'
    )

    include_base_amount = fields.Boolean(
        string='Affecter les taxes suivantes',
        default=False,
        help='Inclure ce montant dans la base de calcul des taxes suivantes'
    )

    # Déclaration TVA
    tax_group_id = fields.Many2one(
        'account.tax.group',
        string='Groupe de taxe',
        help='Groupe pour regrouper les taxes dans les rapports'
    )

    tax_exigibility = fields.Selection([
        ('on_invoice', 'Sur la facture'),
        ('on_payment', 'Sur le paiement'),
    ], string='Exigibilité', default='on_invoice', required=True,
        help="Sur la facture: la TVA est due dès l'émission de la facture.\n"
             "Sur le paiement: la TVA est due au moment du paiement (TVA sur encaissement).")

    cash_basis_account_id = fields.Many2one(
        'account.chart',
        string='Compte transitoire TVA',
        domain=[('deprecated', '=', False)],
        help='Compte transitoire pour TVA sur encaissement'
    )

    @api.constrains('amount')
    def _check_amount(self):
        """Vérifie que le montant est valide"""
        for tax in self:
            if tax.amount_type == 'percent' and (tax.amount < 0 or tax.amount > 100):
                raise ValidationError(_('Le taux de TVA doit être entre 0 et 100%.'))

    @api.model
    def create(self, vals):
        """Création de la taxe avec répartition par défaut"""
        tax = super(AccountTax, self).create(vals)

        # Créer les lignes de répartition par défaut si non définies
        if not tax.invoice_repartition_line_ids:
            # Ligne de base (100%)
            self.env['account.tax.repartition.line'].create({
                'invoice_tax_id': tax.id,
                'factor_percent': 100,
                'repartition_type': 'base',
            })
            # Ligne de taxe (100%)
            self.env['account.tax.repartition.line'].create({
                'invoice_tax_id': tax.id,
                'factor_percent': 100,
                'repartition_type': 'tax',
                'account_id': tax._get_default_tax_account().id if tax._get_default_tax_account() else False,
            })

        if not tax.refund_repartition_line_ids:
            # Ligne de base (100%)
            self.env['account.tax.repartition.line'].create({
                'refund_tax_id': tax.id,
                'factor_percent': 100,
                'repartition_type': 'base',
            })
            # Ligne de taxe (100%)
            self.env['account.tax.repartition.line'].create({
                'refund_tax_id': tax.id,
                'factor_percent': 100,
                'repartition_type': 'tax',
                'account_id': tax._get_default_tax_account().id if tax._get_default_tax_account() else False,
            })

        return tax

    def _get_default_tax_account(self):
        """Retourne le compte de TVA par défaut selon le type"""
        if self.type_tax_use == 'sale':
            # TVA collectée - compte 4457
            return self.env['account.chart'].search([
                ('code', '=like', '4457%'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        elif self.type_tax_use == 'purchase':
            # TVA déductible - compte 4456
            return self.env['account.chart'].search([
                ('code', '=like', '4456%'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        return False

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """Calcule les montants de taxe"""
        if not currency:
            currency = self.env.company.currency_id

        taxes = self.flatten_taxes_hierarchy()

        total_excluded = total_included = base = price_unit * quantity

        res = {
            'taxes': [],
            'total_excluded': 0.0,
            'total_included': 0.0,
            'base': base,
        }

        for tax in taxes:
            if tax.amount_type == 'percent':
                if tax.price_include:
                    # Prix TTC
                    tax_amount = base - (base / (1 + tax.amount / 100))
                else:
                    # Prix HT
                    tax_amount = base * (tax.amount / 100)
            elif tax.amount_type == 'fixed':
                tax_amount = tax.amount * quantity
            else:  # division
                tax_amount = base / (1 + tax.amount / 100)

            if not tax.price_include:
                total_included += tax_amount

            res['taxes'].append({
                'id': tax.id,
                'name': tax.name,
                'amount': tax_amount,
                'base': base,
            })

        res['total_excluded'] = total_excluded
        res['total_included'] = total_included

        return res

    def flatten_taxes_hierarchy(self):
        """Retourne la liste des taxes (pour taxes groupées)"""
        # Simple pour l'instant, peut être étendu pour gérer des taxes composées
        return self


class AccountTaxRepartitionLine(models.Model):
    _name = 'account.tax.repartition.line'
    _description = 'Ligne de répartition de taxe'

    invoice_tax_id = fields.Many2one(
        'account.tax',
        string='Taxe (Facture)',
        ondelete='cascade'
    )

    refund_tax_id = fields.Many2one(
        'account.tax',
        string='Taxe (Avoir)',
        ondelete='cascade'
    )

    factor_percent = fields.Float(
        string='Facteur (%)',
        required=True,
        default=100.0,
        help='Pourcentage de la taxe à répartir'
    )

    repartition_type = fields.Selection([
        ('base', 'Base'),
        ('tax', 'Taxe'),
    ], string='Type', required=True, default='tax')

    account_id = fields.Many2one(
        'account.chart',
        string='Compte',
        domain=[('deprecated', '=', False)],
        help='Compte pour enregistrer cette portion de taxe'
    )

    tag_ids = fields.Many2many(
        'account.account.tag',
        string='Tags',
        help='Tags pour rapports fiscaux'
    )


class AccountTaxGroup(models.Model):
    _name = 'account.tax.group'
    _description = 'Groupe de taxes'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom',
        required=True
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )


class AccountAccountTag(models.Model):
    _name = 'account.account.tag'
    _description = 'Tag comptable'

    name = fields.Char(
        string='Nom',
        required=True
    )

    applicability = fields.Selection([
        ('accounts', 'Comptes'),
        ('taxes', 'Taxes'),
        ('products', 'Produits'),
    ], string='Applicabilité', required=True, default='accounts')

    color = fields.Integer(
        string='Couleur'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société'
    )
