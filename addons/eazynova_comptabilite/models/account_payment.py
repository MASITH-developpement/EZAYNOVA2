# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _name = 'account.payment'
    _description = 'Paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'

    name = fields.Char(
        string='Numéro',
        readonly=True,
        copy=False,
        tracking=True
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True
    )

    payment_type = fields.Selection([
        ('outbound', 'Sortant'),
        ('inbound', 'Entrant'),
    ], string='Type de paiement', required=True, tracking=True)

    partner_type = fields.Selection([
        ('customer', 'Client'),
        ('supplier', 'Fournisseur'),
    ], string='Type de partenaire', required=True, tracking=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        required=True,
        tracking=True
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    payment_method = fields.Selection([
        ('manual', 'Manuel'),
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement'),
        ('credit_card', 'Carte bancaire'),
        ('cash', 'Espèces'),
        ('direct_debit', 'Prélèvement'),
    ], string='Méthode de paiement', required=True, default='manual', tracking=True)

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain=[('type', 'in', ['bank', 'cash'])],
        tracking=True
    )

    destination_account_id = fields.Many2one(
        'account.chart',
        string='Compte de contrepartie',
        required=True,
        domain=[('deprecated', '=', False)]
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'Validé'),
        ('sent', 'Envoyé'),
        ('reconciled', 'Rapproché'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', required=True, tracking=True, copy=False)

    move_id = fields.Many2one(
        'account.move',
        string='Écriture comptable',
        readonly=True,
        copy=False
    )

    invoice_ids = fields.Many2many(
        'account.move',
        string='Factures',
        domain=[('move_type', 'in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund'])],
        copy=False
    )

    ref = fields.Char(
        string='Référence',
        copy=False
    )

    communication = fields.Char(
        string='Communication',
        help='Information pour le bénéficiaire'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    check_number = fields.Char(
        string='Numéro de chèque'
    )

    @api.model
    def create(self, vals):
        """Création avec numéro automatique"""
        if not vals.get('name'):
            if vals.get('payment_type') == 'inbound':
                vals['name'] = self.env['ir.sequence'].next_by_code('account.payment.in') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('account.payment.out') or '/'

        return super(AccountPayment, self).create(vals)

    def action_post(self):
        """Valide le paiement et crée l'écriture comptable"""
        for payment in self:
            if payment.state != 'draft':
                raise UserError(_('Seuls les paiements au brouillon peuvent être validés.'))

            # Créer l'écriture comptable
            move_vals = payment._prepare_move_vals()
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            payment.write({
                'state': 'posted',
                'move_id': move.id
            })

        return True

    def _prepare_move_vals(self):
        """Prépare les valeurs de l'écriture comptable"""
        self.ensure_one()

        move_lines = []

        # Ligne de paiement (banque)
        if self.payment_type == 'inbound':
            debit_account = self.journal_id.default_account_id.id
            credit_account = self.destination_account_id.id
            debit_amount = self.amount
            credit_amount = 0.0
            debit_amount_currency = 0.0
            credit_amount_currency = self.amount
        else:
            debit_account = self.destination_account_id.id
            credit_account = self.journal_id.default_account_id.id
            debit_amount = 0.0
            credit_amount = self.amount
            debit_amount_currency = self.amount
            credit_amount_currency = 0.0

        # Ligne débit
        move_lines.append((0, 0, {
            'name': self.communication or '/',
            'account_id': debit_account,
            'partner_id': self.partner_id.id,
            'debit': self.amount if self.payment_type == 'inbound' else 0.0,
            'credit': 0.0,
            'currency_id': self.currency_id.id,
        }))

        # Ligne crédit
        move_lines.append((0, 0, {
            'name': self.communication or '/',
            'account_id': credit_account,
            'partner_id': self.partner_id.id,
            'debit': 0.0,
            'credit': self.amount if self.payment_type == 'outbound' else 0.0,
            'currency_id': self.currency_id.id,
        }))

        return {
            'date': self.date,
            'ref': self.ref or self.name,
            'journal_id': self.journal_id.id,
            'line_ids': move_lines,
            'partner_id': self.partner_id.id,
        }

    def action_draft(self):
        """Repasse le paiement en brouillon"""
        for payment in self:
            if payment.move_id:
                payment.move_id.action_draft()

            payment.state = 'draft'

        return True

    def action_cancel(self):
        """Annule le paiement"""
        for payment in self:
            if payment.move_id:
                payment.move_id.action_cancel()

            payment.state = 'cancelled'

        return True

    @api.onchange('partner_id', 'payment_type', 'partner_type')
    def _onchange_partner_id(self):
        """Change le compte de contrepartie selon le partenaire"""
        if self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id
