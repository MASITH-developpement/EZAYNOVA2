# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class AccountPaymentTerm(models.Model):
    _name = 'account.payment.term'
    _description = 'Conditions de paiement'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom',
        required=True,
        translate=True
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    line_ids = fields.One2many(
        'account.payment.term.line',
        'payment_term_id',
        string='Lignes',
        copy=True
    )

    note = fields.Text(
        string='Description',
        translate=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société'
    )

    def compute_due_date(self, invoice_date):
        """Calcule la date d'échéance selon les conditions de paiement"""
        self.ensure_one()

        if not self.line_ids:
            return invoice_date

        # Pour simplifier, prendre la dernière ligne
        last_line = self.line_ids.sorted(key=lambda l: l.value)[-1]

        due_date = invoice_date

        if last_line.option == 'day_after_invoice_date':
            due_date = invoice_date + timedelta(days=last_line.nb_days)
        elif last_line.option == 'after_invoice_month':
            due_date = invoice_date + relativedelta(months=1, day=last_line.day_of_month)
        elif last_line.option == 'day_current_month':
            due_date = invoice_date.replace(day=last_line.day_of_month)

        return due_date

    def compute_due_dates(self, invoice_date, total_amount):
        """Calcule toutes les échéances avec leurs montants"""
        self.ensure_one()

        if not self.line_ids:
            return [(invoice_date, total_amount)]

        result = []
        remaining_amount = total_amount

        for line in self.line_ids.sorted(key=lambda l: l.sequence):
            # Calculer le montant
            if line.value == 'percent':
                amount = total_amount * (line.value_amount / 100.0)
            else:  # balance
                amount = remaining_amount

            remaining_amount -= amount

            # Calculer la date
            due_date = invoice_date

            if line.option == 'day_after_invoice_date':
                due_date = invoice_date + timedelta(days=line.nb_days)
            elif line.option == 'after_invoice_month':
                due_date = invoice_date + relativedelta(months=1, day=line.day_of_month)
            elif line.option == 'day_current_month':
                due_date = invoice_date.replace(day=line.day_of_month)

            result.append({
                'date': due_date,
                'amount': amount,
                'line': line
            })

        return result


class AccountPaymentTermLine(models.Model):
    _name = 'account.payment.term.line'
    _description = 'Ligne de condition de paiement'
    _order = 'sequence'

    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Condition de paiement',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    value = fields.Selection([
        ('percent', 'Pourcentage'),
        ('balance', 'Solde'),
    ], string='Type', required=True, default='percent')

    value_amount = fields.Float(
        string='Montant',
        help='Pourcentage du total pour cette ligne'
    )

    option = fields.Selection([
        ('day_after_invoice_date', 'Jours après date de facture'),
        ('after_invoice_month', 'Jours après fin de mois'),
        ('day_current_month', 'Jour du mois en cours'),
    ], string='Options', required=True, default='day_after_invoice_date')

    nb_days = fields.Integer(
        string='Nombre de jours',
        default=0,
        help='Nombre de jours à ajouter'
    )

    day_of_month = fields.Integer(
        string='Jour du mois',
        default=1,
        help='Jour du mois (1-31)'
    )

    @api.constrains('value_amount')
    def _check_value_amount(self):
        """Vérifie que le pourcentage est valide"""
        for line in self:
            if line.value == 'percent' and (line.value_amount < 0 or line.value_amount > 100):
                raise ValidationError(_('Le pourcentage doit être entre 0 et 100.'))

    @api.constrains('day_of_month')
    def _check_day_of_month(self):
        """Vérifie que le jour du mois est valide"""
        for line in self:
            if line.day_of_month < 1 or line.day_of_month > 31:
                raise ValidationError(_('Le jour du mois doit être entre 1 et 31.'))
