# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class AccountMove(models.Model):
    _name = 'account.move'
    _description = 'Écriture comptable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'

    name = fields.Char(
        string='Numéro',
        copy=False,
        readonly=True,
        tracking=True,
        index=True
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True
    )

    ref = fields.Char(
        string='Référence',
        copy=False,
        tracking=True
    )

    narration = fields.Text(
        string='Notes internes'
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'Comptabilisé'),
        ('cancel', 'Annulé'),
    ], string='État', default='draft', required=True, tracking=True, copy=False)

    move_type = fields.Selection([
        ('entry', 'Écriture'),
        ('out_invoice', 'Facture client'),
        ('out_refund', 'Avoir client'),
        ('in_invoice', 'Facture fournisseur'),
        ('in_refund', 'Avoir fournisseur'),
        ('out_receipt', 'Reçu vente'),
        ('in_receipt', 'Reçu achat'),
    ], string='Type', required=True, default='entry', tracking=True)

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        domain="[('company_id', '=', company_id)]"
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company.currency_id
    )

    # Partenaire
    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    # Lignes d'écriture
    line_ids = fields.One2many(
        'account.move.line',
        'move_id',
        string='Lignes d\'écriture',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True
    )

    # Factures spécifiques
    invoice_date = fields.Date(
        string='Date de facture',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help='Date de facturation'
    )

    invoice_date_due = fields.Date(
        string='Date d\'échéance',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    invoice_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Conditions de paiement',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # Montants
    amount_untaxed = fields.Monetary(
        string='HT',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id'
    )

    amount_tax = fields.Monetary(
        string='TVA',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id'
    )

    amount_total = fields.Monetary(
        string='TTC',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id'
    )

    amount_residual = fields.Monetary(
        string='Montant dû',
        compute='_compute_amount_residual',
        store=True,
        currency_field='currency_id'
    )

    # Paiements
    payment_state = fields.Selection([
        ('not_paid', 'Non payé'),
        ('in_payment', 'En cours'),
        ('paid', 'Payé'),
        ('partial', 'Partiellement payé'),
        ('reversed', 'Annulé'),
    ], string='État de paiement', compute='_compute_payment_state', store=True, copy=False)

    payment_ids = fields.Many2many(
        'account.payment',
        string='Paiements',
        copy=False
    )

    # Position fiscale
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position',
        string='Position fiscale',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # Verrouillage
    to_check = fields.Boolean(
        string='À vérifier',
        default=False,
        help='Marque cette écriture pour vérification'
    )

    # Analytique
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Compte analytique'
    )

    # Hash pour verrouillage
    inalterable_hash = fields.Char(
        string='Hash inaltérable',
        readonly=True,
        copy=False
    )

    # Origine
    reversed_entry_id = fields.Many2one(
        'account.move',
        string='Écriture d\'origine',
        readonly=True,
        copy=False
    )

    reversal_entry_ids = fields.One2many(
        'account.move',
        'reversed_entry_id',
        string='Écritures d\'extourne'
    )

    # Pièce jointe
    attachment_count = fields.Integer(
        string='Nombre de pièces jointes',
        compute='_compute_attachment_count'
    )

    @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.tax_line_id')
    def _compute_amounts(self):
        """Calcule les montants HT, TVA et TTC"""
        for move in self:
            amount_untaxed = 0.0
            amount_tax = 0.0

            for line in move.line_ids:
                if line.tax_line_id:
                    # Ligne de taxe
                    amount_tax += line.balance
                else:
                    # Ligne de base
                    amount_untaxed += line.balance

            move.amount_untaxed = abs(amount_untaxed)
            move.amount_tax = abs(amount_tax)
            move.amount_total = move.amount_untaxed + move.amount_tax

    @api.depends('payment_ids', 'amount_total')
    def _compute_amount_residual(self):
        """Calcule le montant restant dû"""
        for move in self:
            if move.state == 'posted' and move.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
                paid_amount = sum(move.payment_ids.mapped('amount'))
                move.amount_residual = move.amount_total - paid_amount
            else:
                move.amount_residual = move.amount_total

    @api.depends('amount_residual', 'amount_total', 'state')
    def _compute_payment_state(self):
        """Calcule l'état de paiement"""
        for move in self:
            if move.state != 'posted':
                move.payment_state = 'not_paid'
            elif move.amount_residual == 0.0:
                move.payment_state = 'paid'
            elif move.amount_residual < move.amount_total:
                move.payment_state = 'partial'
            else:
                move.payment_state = 'not_paid'

    def _compute_attachment_count(self):
        """Compte les pièces jointes"""
        for move in self:
            move.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', move.id)
            ])

    @api.model
    def create(self, vals):
        """Création d'une écriture avec numéro automatique"""
        if vals.get('move_type') in ['entry'] and not vals.get('name'):
            # Générer le numéro automatiquement
            journal = self.env['account.journal'].browse(vals.get('journal_id'))
            if journal and journal.sequence_id:
                vals['name'] = journal.sequence_id.next_by_id()

        move = super(AccountMove, self).create(vals)
        return move

    def action_post(self):
        """Comptabilise l'écriture"""
        for move in self:
            # Vérifications
            if move.state != 'draft':
                raise UserError(_('Seules les écritures au brouillon peuvent être comptabilisées.'))

            if not move.line_ids:
                raise UserError(_('Vous devez ajouter au moins une ligne d\'écriture.'))

            # Vérifier l'équilibre débit/crédit
            total_debit = sum(move.line_ids.mapped('debit'))
            total_credit = sum(move.line_ids.mapped('credit'))

            if round(total_debit, 2) != round(total_credit, 2):
                raise UserError(_(
                    'L\'écriture n\'est pas équilibrée.\n'
                    'Débit: %.2f\nCrédit: %.2f\nDifférence: %.2f'
                ) % (total_debit, total_credit, total_debit - total_credit))

            # Générer le numéro si nécessaire
            if not move.name or move.name == '/':
                if move.journal_id.sequence_id:
                    move.name = move.journal_id.sequence_id.next_by_id()

            # Générer hash si verrouillage activé
            if move.journal_id.restrict_mode_hash_table:
                move._compute_hash()

            move.state = 'posted'

        return True

    def action_draft(self):
        """Repasse l'écriture en brouillon"""
        for move in self:
            if move.state == 'posted':
                # Vérifier les verrouillages
                lock_date = move.company_id.fiscalyear_lock_date
                if lock_date and move.date <= lock_date:
                    raise UserError(_(
                        'Vous ne pouvez pas modifier une écriture verrouillée. '
                        'Date de verrouillage : %s'
                    ) % lock_date)

            move.state = 'draft'

        return True

    def action_cancel(self):
        """Annule l'écriture"""
        for move in self:
            move.state = 'cancel'

        return True

    def action_reverse(self):
        """Ouvre l'assistant d'extourne"""
        return {
            'name': _('Extourner l\'écriture'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.reversal',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_date': fields.Date.today()
            }
        }

    def _compute_hash(self):
        """Calcule le hash inaltérable"""
        import hashlib
        for move in self:
            # Récupérer le hash de l'écriture précédente
            previous_move = self.search([
                ('journal_id', '=', move.journal_id.id),
                ('state', '=', 'posted'),
                ('id', '<', move.id)
            ], order='id desc', limit=1)

            previous_hash = previous_move.inalterable_hash if previous_move else ''

            # Calculer le hash
            hash_string = f"{move.name}|{move.date}|{move.amount_total}|{previous_hash}"
            move.inalterable_hash = hashlib.sha256(hash_string.encode()).hexdigest()

    def action_view_attachments(self):
        """Affiche les pièces jointes"""
        self.ensure_one()
        return {
            'name': _('Pièces jointes'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', 'account.move'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'account.move',
                'default_res_id': self.id
            }
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Remplit automatiquement les champs selon le partenaire"""
        if self.partner_id:
            # Position fiscale
            self.fiscal_position_id = self.partner_id.property_account_position_id

            # Conditions de paiement
            if self.move_type in ['out_invoice', 'out_refund']:
                self.invoice_payment_term_id = self.partner_id.property_payment_term_id
            elif self.move_type in ['in_invoice', 'in_refund']:
                self.invoice_payment_term_id = self.partner_id.property_supplier_payment_term_id

    @api.onchange('invoice_payment_term_id', 'invoice_date')
    def _onchange_payment_term(self):
        """Calcule la date d'échéance"""
        if self.invoice_payment_term_id and self.invoice_date:
            self.invoice_date_due = self.invoice_payment_term_id.compute_due_date(self.invoice_date)
