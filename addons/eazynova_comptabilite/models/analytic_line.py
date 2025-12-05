# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _description = 'Ligne analytique'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Description',
        required=True
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        index=True
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Compte analytique',
        required=True,
        index=True
    )

    tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Tags analytiques'
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
        help='Positif pour produit, négatif pour charge'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.user
    )

    # Origine
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Ligne d\'écriture',
        help='Ligne d\'écriture comptable d\'origine'
    )

    move_id = fields.Many2one(
        'account.move',
        related='move_line_id.move_id',
        string='Écriture',
        readonly=True
    )

    account_id = fields.Many2one(
        'account.chart',
        related='move_line_id.account_id',
        string='Compte',
        readonly=True
    )

    ref = fields.Char(
        string='Référence'
    )
