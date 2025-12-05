# -*- coding: utf-8 -*-
from odoo import models, fields

class InvoiceOcrWizard(models.TransientModel):
    _name = 'invoice.ocr.wizard'
    _description = 'Assistant OCR Facture'
    
    invoice_id = fields.Many2one('account.move', string='Facture', required=True)
    file = fields.Binary(string='Fichier', required=True)
    
    def action_extract(self):
        self.ensure_one()
        attachment = self.env['ir.attachment'].create({
            'name': f'Facture_{self.invoice_id.id}',
            'datas': self.file,
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
        })
        self.invoice_id.action_extract_ocr()
        return {'type': 'ir.actions.act_window_close'}
