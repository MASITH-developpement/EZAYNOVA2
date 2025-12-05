# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ClosingWizard(models.TransientModel):
    _name = 'closing.wizard'
    _description = 'Assistant de clôture'
    
    date = fields.Date(string='Date de clôture', required=True)
    
    def action_close(self):
        self.ensure_one()
        self.env.company.fiscalyear_lock_date = self.date
        return {'type': 'ir.actions.act_window_close'}
