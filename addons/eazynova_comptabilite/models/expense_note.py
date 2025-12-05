# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ExpenseNote(models.Model):
    _name = 'account.expense.note'
    _description = 'Note de frais'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default='/',
        tracking=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True,
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        tracking=True
    )

    user_id = fields.Many2one(
        'res.users',
        related='employee_id.user_id',
        string='Utilisateur',
        readonly=True
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('paid', 'Payé'),
        ('refused', 'Refusé'),
    ], string='État', default='draft', required=True, tracking=True)

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    line_ids = fields.One2many(
        'account.expense.note.line',
        'expense_note_id',
        string='Lignes de frais'
    )

    total_amount = fields.Monetary(
        string='Montant total',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    manager_id = fields.Many2one(
        'res.users',
        string='Responsable',
        tracking=True
    )

    approval_date = fields.Datetime(
        string='Date d\'approbation',
        readonly=True
    )

    payment_id = fields.Many2one(
        'account.payment',
        string='Paiement',
        readonly=True
    )

    move_id = fields.Many2one(
        'account.move',
        string='Écriture comptable',
        readonly=True
    )

    notes = fields.Text(
        string='Notes'
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        """Calcule le montant total"""
        for note in self:
            note.total_amount = sum(note.line_ids.mapped('amount'))

    @api.model
    def create(self, vals):
        """Création avec numéro automatique"""
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.expense.note') or '/'

        return super(ExpenseNote, self).create(vals)

    def action_submit(self):
        """Soumet la note de frais pour approbation"""
        for note in self:
            if not note.line_ids:
                raise UserError(_('Vous devez ajouter au moins une ligne de frais.'))

            note.state = 'submitted'

        return True

    def action_approve(self):
        """Approuve la note de frais"""
        for note in self:
            note.write({
                'state': 'approved',
                'manager_id': self.env.user.id,
                'approval_date': fields.Datetime.now()
            })

            # Créer l'écriture comptable
            note._create_accounting_entry()

        return True

    def action_refuse(self):
        """Refuse la note de frais"""
        for note in self:
            note.state = 'refused'

        return True

    def action_pay(self):
        """Marque la note de frais comme payée"""
        for note in self:
            # Créer le paiement
            payment = self.env['account.payment'].create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': note.employee_id.address_home_id.id,
                'amount': note.total_amount,
                'date': fields.Date.today(),
                'ref': note.name,
            })
            payment.action_post()

            note.write({
                'state': 'paid',
                'payment_id': payment.id
            })

        return True

    def _create_accounting_entry(self):
        """Crée l'écriture comptable"""
        self.ensure_one()

        # Journal des frais
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if not journal:
            raise UserError(_('Aucun journal d\'achat configuré.'))

        # Lignes d'écriture
        move_lines = []

        for line in self.line_ids:
            # Ligne de charge
            move_lines.append((0, 0, {
                'name': line.description,
                'account_id': line.account_id.id,
                'debit': line.amount,
                'credit': 0.0,
                'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False,
            }))

        # Ligne de contrepartie (dette envers l'employé)
        move_lines.append((0, 0, {
            'name': f'Note de frais {self.name}',
            'account_id': self.company_id.default_supplier_account_id.id,
            'partner_id': self.employee_id.address_home_id.id,
            'debit': 0.0,
            'credit': self.total_amount,
        }))

        # Créer l'écriture
        move = self.env['account.move'].create({
            'date': self.date,
            'ref': self.name,
            'journal_id': journal.id,
            'line_ids': move_lines,
        })
        move.action_post()

        self.move_id = move.id

        return True


class ExpenseNoteLine(models.Model):
    _name = 'account.expense.note.line'
    _description = 'Ligne de note de frais'

    expense_note_id = fields.Many2one(
        'account.expense.note',
        string='Note de frais',
        required=True,
        ondelete='cascade'
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
    )

    description = fields.Char(
        string='Description',
        required=True
    )

    category_id = fields.Many2one(
        'account.expense.category',
        string='Catégorie',
        required=True
    )

    account_id = fields.Many2one(
        'account.chart',
        string='Compte comptable',
        required=True,
        domain=[('account_type', '=', 'expense')]
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='expense_note_id.currency_id',
        string='Devise',
        readonly=True
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Compte analytique'
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Justificatifs',
        help='Reçus, factures, etc.'
    )

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Remplit le compte selon la catégorie"""
        if self.category_id:
            self.account_id = self.category_id.account_id


class ExpenseCategory(models.Model):
    _name = 'account.expense.category'
    _description = 'Catégorie de frais'

    name = fields.Char(
        string='Nom',
        required=True,
        translate=True
    )

    account_id = fields.Many2one(
        'account.chart',
        string='Compte par défaut',
        domain=[('account_type', '=', 'expense')]
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société'
    )
