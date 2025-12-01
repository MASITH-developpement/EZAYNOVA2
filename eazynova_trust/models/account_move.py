# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    """Extension du modèle facture"""
    _inherit = 'account.move'

    review_request_id = fields.Many2one(
        'eazynova.review.request',
        string='Demande d\'avis',
        readonly=True
    )

    review_request_sent = fields.Boolean(
        string='Demande d\'avis envoyée',
        compute='_compute_review_request_sent',
        store=True
    )

    @api.depends('review_request_id')
    def _compute_review_request_sent(self):
        """Vérifie si une demande d'avis a été envoyée"""
        for move in self:
            move.review_request_sent = bool(move.review_request_id)

    def action_post(self):
        """Surcharge de la validation de facture pour créer une demande d'avis"""
        res = super().action_post()

        # Vérifier la configuration
        config = self.env['eazynova.trust.config'].sudo().search([], limit=1)

        if not config or not config.auto_send_after_invoice:
            return res

        # Créer une demande d'avis pour les factures clients validées
        for move in self:
            if (move.move_type == 'out_invoice' and
                move.partner_id.allow_review_request and
                not move.review_request_id):

                # Calculer la date d'envoi
                send_date = fields.Datetime.add(
                    fields.Datetime.now(),
                    days=config.days_after_invoice
                )

                # Créer la demande
                request = self.env['eazynova.review.request'].create({
                    'partner_id': move.partner_id.id,
                    'invoice_id': move.id,
                    'request_date': send_date,
                    'state': 'pending',
                    'platform': 'trustpilot' if config.trustpilot_enabled else 'internal'
                })

                move.review_request_id = request.id

        return res

    def action_view_review_request(self):
        """Affiche la demande d'avis associée"""
        self.ensure_one()

        if not self.review_request_id:
            return

        return {
            'name': 'Demande d\'Avis',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.request',
            'res_id': self.review_request_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_create_review_request(self):
        """Crée manuellement une demande d'avis"""
        self.ensure_one()

        if self.review_request_id:
            return self.action_view_review_request()

        return {
            'name': 'Demander un Avis',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, [self.partner_id.id])],
                'default_invoice_id': self.id
            }
        }
