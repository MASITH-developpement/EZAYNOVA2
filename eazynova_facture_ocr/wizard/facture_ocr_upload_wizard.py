# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FactureOcrUploadWizard(models.TransientModel):
    _name = 'facture.ocr.upload.wizard'
    _description = 'Upload Facture OCR'

    document_ids = fields.Many2many('ir.attachment', string="Factures", required=True, help="Uploadez une ou plusieurs factures (PDF ou images)")
    auto_process = fields.Boolean(string="Traiter automatiquement", default=True, help="Lance le traitement OCR+IA immédiatement après l'upload")
    auto_validate = fields.Boolean(string="Validation automatique", default=False, help="Valide automatiquement si confiance > 90%")
    auto_create_invoice = fields.Boolean(string="Créer factures automatiquement", default=False, help="Crée les factures Odoo automatiquement après validation")

    def action_upload_and_process(self):
        if not self.document_ids:
            raise UserError(_("Veuillez sélectionner au moins une facture."))
        facture_ocr_obj = self.env['eazynova.facture.ocr']
        factures_created = self.env['eazynova.facture.ocr']
        for attachment in self.document_ids:
            facture_ocr = facture_ocr_obj.create({'document': attachment.datas, 'document_filename': attachment.name, 'needs_validation': not self.auto_validate})
            factures_created |= facture_ocr
            if self.auto_process:
                try:
                    facture_ocr.action_process()
                    if self.auto_validate and facture_ocr.ia_confidence >= 90:
                        facture_ocr.action_validate()
                        if self.auto_create_invoice:
                            facture_ocr.action_create_invoice()
                except Exception as e:
                    facture_ocr.write({'state': 'error', 'error_message': str(e)})
        return {'type': 'ir.actions.act_window', 'name': _('Factures OCR'), 'res_model': 'eazynova.facture.ocr', 'view_mode': 'tree,form', 'domain': [('id', 'in', factures_created.ids)], 'context': {'create': False}}

