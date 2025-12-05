# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class UnpaidReminderWizard(models.TransientModel):
    _name = 'unpaid.reminder.wizard'
    _description = 'Assistant de relance'
    
    partner_ids = fields.Many2many('res.partner', string='Clients')
    
    def action_send_reminders(self):
        invoices = self.env['account.move'].search([
            ('partner_id', 'in', self.partner_ids.ids),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('invoice_date_due', '<', fields.Date.today())
        ])
        invoices.action_send_reminder()
        return {'type': 'ir.actions.act_window_close'}
