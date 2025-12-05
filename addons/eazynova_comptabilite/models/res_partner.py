# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Comptes comptables
    property_account_receivable_id = fields.Many2one(
        'account.chart',
        string='Compte client',
        company_dependent=True,
        domain=[('account_type', '=', 'asset_receivable')],
        help='Compte comptable utilisé pour les créances clients'
    )

    property_account_payable_id = fields.Many2one(
        'account.chart',
        string='Compte fournisseur',
        company_dependent=True,
        domain=[('account_type', '=', 'liability_payable')],
        help='Compte comptable utilisé pour les dettes fournisseurs'
    )

    # Conditions de paiement
    property_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Conditions de paiement client',
        company_dependent=True,
        help='Conditions de paiement pour les factures clients'
    )

    property_supplier_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Conditions de paiement fournisseur',
        company_dependent=True,
        help='Conditions de paiement pour les factures fournisseurs'
    )

    # Position fiscale
    property_account_position_id = fields.Many2one(
        'account.fiscal.position',
        string='Position fiscale',
        company_dependent=True,
        help='Position fiscale utilisée pour ce partenaire'
    )

    # TVA
    vat = fields.Char(
        string='N° TVA intracommunautaire',
        help='Numéro de TVA intracommunautaire'
    )

    # Informations comptables
    total_invoiced = fields.Monetary(
        string='Total facturé',
        compute='_compute_total_invoiced',
        currency_field='currency_id'
    )

    total_due = fields.Monetary(
        string='Total dû',
        compute='_compute_total_due',
        currency_field='currency_id'
    )

    invoice_count = fields.Integer(
        string='Nombre de factures',
        compute='_compute_invoice_count'
    )

    unpaid_invoice_count = fields.Integer(
        string='Nombre de factures impayées',
        compute='_compute_unpaid_invoice_count'
    )

    last_invoice_date = fields.Date(
        string='Date dernière facture',
        compute='_compute_last_invoice_date'
    )

    # Relances
    reminder_level = fields.Integer(
        string='Niveau de relance',
        default=0,
        help='Nombre de relances envoyées'
    )

    last_reminder_date = fields.Date(
        string='Date dernière relance',
        help='Date de la dernière relance envoyée'
    )

    # Options
    invoice_sending_method = fields.Selection([
        ('email', 'Email'),
        ('post', 'Courrier'),
        ('electronic', 'Facturation électronique'),
    ], string='Méthode d\'envoi factures', default='email')

    @api.depends('currency_id')
    def _compute_total_invoiced(self):
        """Calcule le total facturé pour ce partenaire"""
        for partner in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ])
            partner.total_invoiced = sum(invoices.mapped('amount_total'))

    @api.depends('currency_id')
    def _compute_total_due(self):
        """Calcule le total dû par ce partenaire"""
        for partner in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            partner.total_due = sum(invoices.mapped('amount_residual'))

    def _compute_invoice_count(self):
        """Compte le nombre de factures"""
        for partner in self:
            partner.invoice_count = self.env['account.move'].search_count([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund'])
            ])

    def _compute_unpaid_invoice_count(self):
        """Compte le nombre de factures impayées"""
        for partner in self:
            partner.unpaid_invoice_count = self.env['account.move'].search_count([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date_due', '<', fields.Date.today())
            ])

    def _compute_last_invoice_date(self):
        """Récupère la date de la dernière facture"""
        for partner in self:
            last_invoice = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ], order='invoice_date desc', limit=1)
            partner.last_invoice_date = last_invoice.invoice_date if last_invoice else False

    def action_view_partner_invoices(self):
        """Affiche les factures du partenaire"""
        self.ensure_one()
        return {
            'name': 'Factures',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_view_partner_ledger(self):
        """Affiche le grand livre du partenaire"""
        self.ensure_one()
        return {
            'name': 'Grand livre',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
