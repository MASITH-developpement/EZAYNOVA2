# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _description = 'Compte analytique'
    _order = 'code, name'

    name = fields.Char(
        string='Nom',
        required=True,
        index=True
    )

    code = fields.Char(
        string='Code',
        required=True,
        index=True
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

    partner_id = fields.Many2one(
        'res.partner',
        string='Client/Projet',
        help='Partenaire associé (pour suivi par projet/client)'
    )

    # Hiérarchie
    parent_id = fields.Many2one(
        'account.analytic.account',
        string='Compte parent',
        ondelete='cascade'
    )

    child_ids = fields.One2many(
        'account.analytic.account',
        'parent_id',
        string='Comptes enfants'
    )

    # Type
    account_type = fields.Selection([
        ('project', 'Projet'),
        ('department', 'Département'),
        ('product', 'Produit'),
        ('customer', 'Client'),
        ('other', 'Autre'),
    ], string='Type', default='other')

    # Responsable
    manager_id = fields.Many2one(
        'res.users',
        string='Responsable'
    )

    # Statistiques
    balance = fields.Monetary(
        string='Solde',
        compute='_compute_balance',
        currency_field='currency_id'
    )

    debit = fields.Monetary(
        string='Charges',
        compute='_compute_balance',
        currency_field='currency_id'
    )

    credit = fields.Monetary(
        string='Produits',
        compute='_compute_balance',
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Devise',
        readonly=True
    )

    line_count = fields.Integer(
        string='Nombre de lignes',
        compute='_compute_line_count'
    )

    # Notes
    description = fields.Text(
        string='Description'
    )

    def _compute_balance(self):
        """Calcule les montants analytiques"""
        for account in self:
            lines = self.env['account.analytic.line'].search([
                ('analytic_account_id', '=', account.id)
            ])
            account.debit = sum(lines.filtered(lambda l: l.amount < 0).mapped(lambda l: abs(l.amount)))
            account.credit = sum(lines.filtered(lambda l: l.amount > 0).mapped('amount'))
            account.balance = account.credit - account.debit

    def _compute_line_count(self):
        """Compte les lignes analytiques"""
        for account in self:
            account.line_count = self.env['account.analytic.line'].search_count([
                ('analytic_account_id', '=', account.id)
            ])

    def action_view_lines(self):
        """Affiche les lignes analytiques"""
        self.ensure_one()
        return {
            'name': _('Lignes analytiques'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree,form',
            'domain': [('analytic_account_id', '=', self.id)],
            'context': {'default_analytic_account_id': self.id}
        }


class AccountAnalyticTag(models.Model):
    _name = 'account.analytic.tag'
    _description = 'Tag analytique'

    name = fields.Char(
        string='Nom',
        required=True
    )

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
