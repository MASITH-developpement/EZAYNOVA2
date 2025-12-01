from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    review_request_id = fields.Many2one('eazynova.review.request', string='Demande d\'avis')

    def action_post(self):
        res = super().action_post()
        config = self.env['eazynova.trust.config'].sudo().search([], limit=1)
        if config and config.auto_send_after_invoice:
            for inv in self.filtered(lambda m: m.move_type == 'out_invoice'):
                partner = inv.partner_id
                req_date = fields.Datetime.add(fields.Datetime.now(), days=config.days_after_invoice or 0)
                rr = self.env['eazynova.review.request'].create({
                    'partner_id': partner.id,
                    'invoice_id': inv.id,
                    'state': 'pending',
                    'request_date': req_date,
                })
                inv.review_request_id = rr.id
        return res
