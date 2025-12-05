# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InvoiceCustomer(models.Model):
    """
    Modèle hérité d'account.move pour les factures clients
    Ajoute des fonctionnalités spécifiques aux factures clients
    """
    _inherit = 'account.move'

    # Champs spécifiques factures clients
    payment_reference = fields.Char(
        string='Référence de paiement',
        help='Référence unique pour le paiement (ex: QR code)'
    )

    qr_code_image = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        help='QR code pour paiement'
    )

    invoice_origin = fields.Char(
        string='Document origine',
        help='Référence du document d\'origine (devis, commande, etc.)'
    )

    # Relances
    reminder_count = fields.Integer(
        string='Nombre de relances',
        default=0
    )

    last_reminder_date = fields.Date(
        string='Dernière relance'
    )

    next_reminder_date = fields.Date(
        string='Prochaine relance',
        compute='_compute_next_reminder_date'
    )

    # Pénalités de retard
    late_payment_penalty = fields.Monetary(
        string='Pénalités de retard',
        compute='_compute_late_payment_penalty',
        currency_field='currency_id'
    )

    @api.depends('payment_reference')
    def _compute_qr_code(self):
        """Génère le QR code pour paiement"""
        for invoice in self:
            # TODO: Générer QR code selon norme (SEPA, etc.)
            invoice.qr_code_image = False

    @api.depends('last_reminder_date', 'company_id.reminder_days')
    def _compute_next_reminder_date(self):
        """Calcule la date de prochaine relance"""
        from datetime import timedelta
        for invoice in self:
            if invoice.payment_state in ['not_paid', 'partial'] and invoice.invoice_date_due:
                if invoice.last_reminder_date:
                    invoice.next_reminder_date = invoice.last_reminder_date + timedelta(
                        days=invoice.company_id.reminder_days or 7
                    )
                elif invoice.invoice_date_due < fields.Date.today():
                    invoice.next_reminder_date = fields.Date.today() + timedelta(
                        days=invoice.company_id.reminder_days or 7
                    )
                else:
                    invoice.next_reminder_date = False
            else:
                invoice.next_reminder_date = False

    @api.depends('invoice_date_due', 'amount_residual')
    def _compute_late_payment_penalty(self):
        """Calcule les pénalités de retard"""
        for invoice in self:
            if invoice.invoice_date_due and invoice.invoice_date_due < fields.Date.today():
                # Calcul simplifié: 10% du montant dû
                days_late = (fields.Date.today() - invoice.invoice_date_due).days
                if days_late > 30:  # Après 30 jours
                    invoice.late_payment_penalty = invoice.amount_residual * 0.10
                else:
                    invoice.late_payment_penalty = 0.0
            else:
                invoice.late_payment_penalty = 0.0

    def action_send_reminder(self):
        """Envoie une relance au client"""
        for invoice in self:
            # Envoyer email de relance
            template = self.env.ref('eazynova_comptabilite.email_template_invoice_reminder', False)
            if template:
                template.send_mail(invoice.id, force_send=True)

            invoice.write({
                'reminder_count': invoice.reminder_count + 1,
                'last_reminder_date': fields.Date.today()
            })

        return True

    def action_register_payment(self):
        """Enregistre un paiement pour la facture"""
        self.ensure_one()

        return {
            'name': _('Enregistrer un paiement'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_type': 'inbound' if self.move_type == 'out_invoice' else 'outbound',
                'default_partner_type': 'customer',
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount_residual,
                'default_currency_id': self.currency_id.id,
                'default_invoice_ids': [(6, 0, self.ids)],
            }
        }
