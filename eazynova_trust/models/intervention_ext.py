from odoo import models, fields


class InterventionIntervention(models.Model):
    _inherit = 'intervention.intervention'

    trust_request_id = fields.Many2one('eazynova.review.request', string='Demande d\'avis')

    def action_create_review_request(self):
        self.ensure_one()
        partner = self.client_final_id or self.partner_to_invoice_id or self.donneur_ordre_id
        rr = self.env['eazynova.review.request'].create({
            'partner_id': partner.id,
            'invoice_id': False,
            'sale_order_id': False,
            'intervention_id': self.id,
            'state': 'pending',
        })
        self.trust_request_id = rr.id
        rr.action_send_request()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.review.request',
            'res_id': rr.id,
            'view_mode': 'form',
            'target': 'current',
        }
