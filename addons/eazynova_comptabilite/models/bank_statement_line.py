# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountBankStatementLine(models.Model):
    _name = 'account.bank.statement.line'
    _description = 'Ligne de relevé bancaire'
    _order = 'statement_id, date, sequence, id'

    statement_id = fields.Many2one(
        'account.bank.statement',
        string='Relevé',
        required=True,
        ondelete='cascade',
        index=True
    )

    sequence = fields.Integer(
        string='Séquence',
        default=1
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
    )

    name = fields.Char(
        string='Libellé',
        required=True
    )

    ref = fields.Char(
        string='Référence'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire'
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
        help='Montant positif pour crédit, négatif pour débit'
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='statement_id.currency_id',
        string='Devise',
        readonly=True
    )

    # Rapprochement
    is_reconciled = fields.Boolean(
        string='Rapproché',
        default=False,
        copy=False
    )

    move_id = fields.Many2one(
        'account.move',
        string='Écriture comptable',
        readonly=True,
        copy=False
    )

    account_id = fields.Many2one(
        'account.chart',
        string='Compte',
        help='Compte de contrepartie'
    )

    # Suggestions IA
    suggested_partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire suggéré',
        help='Partenaire suggéré par IA'
    )

    suggested_account_id = fields.Many2one(
        'account.chart',
        string='Compte suggéré',
        help='Compte suggéré par IA'
    )

    suggestion_confidence = fields.Float(
        string='Confiance suggestion',
        help='Niveau de confiance de la suggestion IA (0-100)'
    )

    # Informations bancaires brutes
    bank_account_number = fields.Char(
        string='N° compte bancaire'
    )

    bank_name = fields.Char(
        string='Nom de la banque'
    )

    transaction_type = fields.Char(
        string='Type de transaction'
    )

    notes = fields.Text(
        string='Notes'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Suggère le compte selon le partenaire"""
        if self.partner_id:
            if self.amount > 0:
                # Crédit - probablement un paiement client
                self.account_id = self.partner_id.property_account_receivable_id
            else:
                # Débit - probablement un paiement fournisseur
                self.account_id = self.partner_id.property_account_payable_id

    def action_reconcile(self):
        """Rapproche la ligne avec une écriture existante ou crée une nouvelle écriture"""
        self.ensure_one()

        if not self.account_id:
            raise ValidationError(_('Veuillez sélectionner un compte de contrepartie.'))

        # Créer l'écriture comptable
        move_vals = self._prepare_move_vals()
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        self.write({
            'is_reconciled': True,
            'move_id': move.id
        })

        return True

    def _prepare_move_vals(self):
        """Prépare les valeurs de l'écriture comptable"""
        self.ensure_one()

        journal = self.statement_id.journal_id
        bank_account = journal.default_account_id

        # Lignes d'écriture
        move_lines = []

        # Ligne banque
        if self.amount > 0:
            # Crédit sur compte bancaire (encaissement)
            move_lines.append((0, 0, {
                'name': self.name,
                'account_id': bank_account.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'debit': self.amount,
                'credit': 0.0,
            }))
            # Débit sur compte de contrepartie
            move_lines.append((0, 0, {
                'name': self.name,
                'account_id': self.account_id.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'debit': 0.0,
                'credit': self.amount,
            }))
        else:
            # Débit sur compte bancaire (décaissement)
            amount = abs(self.amount)
            move_lines.append((0, 0, {
                'name': self.name,
                'account_id': bank_account.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'debit': 0.0,
                'credit': amount,
            }))
            # Crédit sur compte de contrepartie
            move_lines.append((0, 0, {
                'name': self.name,
                'account_id': self.account_id.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'debit': amount,
                'credit': 0.0,
            }))

        return {
            'date': self.date,
            'ref': self.ref or self.statement_id.name,
            'journal_id': journal.id,
            'line_ids': move_lines,
            'partner_id': self.partner_id.id if self.partner_id else False,
        }

    def action_suggest_match(self):
        """Utilise l'IA pour suggérer un partenaire et un compte"""
        self.ensure_one()

        # Utiliser le service IA pour suggérer
        ai_service = self.env['eazynova.accounting.ai.assistant']
        suggestions = ai_service.suggest_bank_line_match(self)

        if suggestions:
            self.write({
                'suggested_partner_id': suggestions.get('partner_id'),
                'suggested_account_id': suggestions.get('account_id'),
                'suggestion_confidence': suggestions.get('confidence', 0.0)
            })

        return True

    def action_apply_suggestion(self):
        """Applique la suggestion IA"""
        for line in self:
            if line.suggested_partner_id:
                line.partner_id = line.suggested_partner_id
            if line.suggested_account_id:
                line.account_id = line.suggested_account_id

        return True

    def action_unreconcile(self):
        """Annule le rapprochement"""
        for line in self:
            if line.move_id:
                line.move_id.action_cancel()

            line.write({
                'is_reconciled': False,
                'move_id': False
            })

        return True
