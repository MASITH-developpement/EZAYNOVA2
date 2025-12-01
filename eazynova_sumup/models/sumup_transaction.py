# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SumUpTransaction(models.Model):
    """Transaction SumUp"""
    _name = 'eazynova.sumup.transaction'
    _description = 'Transaction SumUp'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'transaction_date desc, id desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default='Nouveau'
    )

    transaction_date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )

    invoice_id = fields.Many2one(
        'account.move',
        string='Facture',
        domain=[('move_type', '=', 'out_invoice')],
        tracking=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='invoice_id.partner_id',
        store=True
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    sumup_transaction_id = fields.Char(
        string='ID Transaction SumUp',
        readonly=True
    )

    sumup_transaction_code = fields.Char(
        string='Code Transaction',
        readonly=True
    )

    state = fields.Selection([
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('successful', 'Réussie'),
        ('failed', 'Échouée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée')
    ], string='État', default='pending', required=True, tracking=True)

    payment_id = fields.Many2one(
        'account.payment',
        string='Paiement Odoo',
        readonly=True
    )

    error_message = fields.Text(
        string='Message d\'erreur',
        readonly=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Génère la référence automatiquement"""
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('eazynova.sumup.transaction') or 'Nouveau'
        return super().create(vals_list)

    def action_create_payment(self):
        """Crée le paiement Odoo"""
        self.ensure_one()

        if self.state != 'successful':
            return

        if self.payment_id:
            return self.payment_id

        config = self.env['eazynova.sumup.config'].sudo().search([], limit=1)

        if not config or not config.journal_id:
            return

        # Créer le paiement
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': config.journal_id.id,
            'date': self.transaction_date.date(),
            'ref': f'SumUp {self.name}',
        })

        payment.action_post()

        self.payment_id = payment.id

        # Réconcilier avec la facture
        if self.invoice_id and config.auto_reconcile:
            (payment.line_ids + self.invoice_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled
            ).reconcile()

        return payment
