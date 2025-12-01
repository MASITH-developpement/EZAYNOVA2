# -*- coding: utf-8 -*-

from odoo import models, fields


class ReviewRequestWizard(models.TransientModel):
    """Assistant de création de demandes d'avis"""
    _name = 'eazynova.review.request.wizard'
    _description = 'Assistant Demande d\'Avis'

    partner_ids = fields.Many2many(
        'res.partner',
        string='Clients',
        required=True
    )

    platform = fields.Selection([
        ('trustpilot', 'Trustpilot'),
        ('google', 'Google Reviews'),
        ('internal', 'Avis Interne')
    ], string='Plateforme', default='trustpilot', required=True)

    send_immediately = fields.Boolean(
        string='Envoyer immédiatement',
        default=False
    )

    def action_create_requests(self):
        """Crée les demandes d'avis"""
        self.ensure_one()

        requests = self.env['eazynova.review.request']

        for partner in self.partner_ids:
            request = self.env['eazynova.review.request'].create({
                'partner_id': partner.id,
                'platform': self.platform,
                'state': 'draft'
            })

            if self.send_immediately:
                request.action_send_request()

            requests |= request

        return {
            'name': 'Demandes d\'Avis Créées',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.request',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', requests.ids)],
            'target': 'current',
        }
