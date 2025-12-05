# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountFiscalPosition(models.Model):
    _name = 'account.fiscal.position'
    _description = 'Position fiscale'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la position fiscale'
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    # Application automatique
    auto_apply = fields.Boolean(
        string='Détection automatique',
        default=False,
        help='Applique automatiquement cette position selon les critères'
    )

    vat_required = fields.Boolean(
        string='N° TVA requis',
        default=False,
        help='Le partenaire doit avoir un numéro de TVA'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        help='Pays du partenaire pour application automatique'
    )

    country_group_id = fields.Many2one(
        'res.country.group',
        string='Groupe de pays',
        help='Groupe de pays pour application automatique (ex: UE)'
    )

    # Mappings
    account_ids = fields.One2many(
        'account.fiscal.position.account',
        'position_id',
        string='Correspondances de comptes',
        help='Remplace un compte par un autre selon la position fiscale'
    )

    tax_ids = fields.One2many(
        'account.fiscal.position.tax',
        'position_id',
        string='Correspondances de taxes',
        help='Remplace une taxe par une autre selon la position fiscale'
    )

    note = fields.Text(
        string='Notes',
        help='Description de la position fiscale'
    )

    def map_tax(self, taxes):
        """Mappe les taxes selon la position fiscale"""
        if not self:
            return taxes

        result = self.env['account.tax']
        for tax in taxes:
            # Chercher une correspondance
            tax_mapping = self.tax_ids.filtered(lambda m: m.tax_src_id == tax)
            if tax_mapping:
                result |= tax_mapping[0].tax_dest_id
            else:
                result |= tax

        return result

    def map_account(self, account):
        """Mappe le compte selon la position fiscale"""
        if not self:
            return account

        # Chercher une correspondance
        account_mapping = self.account_ids.filtered(lambda m: m.account_src_id == account)
        if account_mapping:
            return account_mapping[0].account_dest_id

        return account


class AccountFiscalPositionAccount(models.Model):
    _name = 'account.fiscal.position.account'
    _description = 'Correspondance de compte selon position fiscale'

    position_id = fields.Many2one(
        'account.fiscal.position',
        string='Position fiscale',
        required=True,
        ondelete='cascade'
    )

    account_src_id = fields.Many2one(
        'account.chart',
        string='Compte source',
        required=True,
        domain=[('deprecated', '=', False)]
    )

    account_dest_id = fields.Many2one(
        'account.chart',
        string='Compte de remplacement',
        required=True,
        domain=[('deprecated', '=', False)]
    )

    _sql_constraints = [
        ('account_src_unique',
         'unique(position_id, account_src_id)',
         'Un compte source ne peut être mappé qu\'une seule fois par position fiscale.')
    ]


class AccountFiscalPositionTax(models.Model):
    _name = 'account.fiscal.position.tax'
    _description = 'Correspondance de taxe selon position fiscale'

    position_id = fields.Many2one(
        'account.fiscal.position',
        string='Position fiscale',
        required=True,
        ondelete='cascade'
    )

    tax_src_id = fields.Many2one(
        'account.tax',
        string='Taxe source',
        required=True
    )

    tax_dest_id = fields.Many2one(
        'account.tax',
        string='Taxe de remplacement',
        help='Laissez vide pour retirer la taxe'
    )

    _sql_constraints = [
        ('tax_src_unique',
         'unique(position_id, tax_src_id)',
         'Une taxe source ne peut être mappée qu\'une seule fois par position fiscale.')
    ]
