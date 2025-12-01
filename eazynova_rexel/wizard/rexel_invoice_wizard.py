# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64


class RexelInvoiceWizard(models.TransientModel):
    """Assistant d'import manuel de facture Rexel"""
    _name = 'eazynova.rexel.invoice.wizard'
    _description = 'Assistant Import Facture Rexel'

    file_name = fields.Char(
        string='Nom du fichier',
        readonly=True
    )

    file_data = fields.Binary(
        string='Fichier',
        required=True,
        help='Facture au format PDF ou XML'
    )

    file_type = fields.Selection([
        ('pdf', 'PDF'),
        ('xml', 'XML')
    ], string='Type de fichier', required=True, default='pdf')

    auto_process = fields.Boolean(
        string='Traiter automatiquement',
        default=True,
        help='Extraire et créer la facture automatiquement'
    )

    def action_import_invoice(self):
        """Importe la facture"""
        self.ensure_one()

        if not self.file_data:
            raise UserError('Veuillez sélectionner un fichier.')

        # Créer l'import
        import_record = self.env['eazynova.rexel.invoice.import'].create({
            'source_type': 'upload',
            'file_name': self.file_name,
            'file_data': self.file_data,
            'file_type': self.file_type,
            'state': 'draft'
        })

        # Traiter automatiquement si demandé
        if self.auto_process:
            try:
                import_record.action_extract_data()

                if import_record.state in ['extracted', 'matched']:
                    import_record.action_create_invoice()

            except Exception as e:
                pass  # L'erreur est déjà loggée dans le modèle

        # Afficher l'import créé
        return {
            'name': 'Import Facture Rexel',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.rexel.invoice.import',
            'res_id': import_record.id,
            'view_mode': 'form',
            'target': 'current',
        }
