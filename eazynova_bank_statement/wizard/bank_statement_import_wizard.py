# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BankStatementImportWizard(models.TransientModel):
    _name = 'eazynova.bank.statement.import.wizard'
    _description = 'Assistant d\'Import de Relevé Bancaire'

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal Bancaire',
        domain="[('type', '=', 'bank')]",
        required=True
    )

    file_type = fields.Selection([
        ('auto', 'Détection Automatique'),
        ('csv', 'CSV'),
        ('ofx', 'OFX'),
        ('pdf', 'PDF (OCR)'),
    ], string='Type de Fichier', default='auto', required=True)

    file_data = fields.Binary(
        string='Fichier',
        required=True,
        attachment=False
    )

    file_name = fields.Char(string='Nom du Fichier')

    auto_reconcile = fields.Boolean(
        string='Rapprochement Automatique',
        default=True,
        help="Lancer automatiquement le rapprochement après l'import"
    )

    use_ai = fields.Boolean(
        string='Utiliser l\'IA',
        default=True,
        help="Utiliser l'IA pour améliorer le rapprochement et l'extraction (PDF)"
    )

    confidence_threshold = fields.Float(
        string='Seuil de Confiance',
        default=0.8,
        help="Seuil minimum de confiance pour valider automatiquement un rapprochement (0-1)"
    )

    create_statement = fields.Boolean(
        string='Créer le Relevé Bancaire',
        default=True,
        help="Créer automatiquement le relevé bancaire dans Odoo après l'import"
    )

    def action_import(self):
        """Lance l'import du relevé bancaire"""
        self.ensure_one()

        if not self.file_data:
            raise UserError(_("Veuillez charger un fichier."))

        # Créer l'import
        import_vals = {
            'journal_id': self.journal_id.id,
            'file_type': self.file_type,
            'file_data': self.file_data,
            'file_name': self.file_name,
            'auto_reconcile': self.auto_reconcile,
            'use_ai': self.use_ai,
            'confidence_threshold': self.confidence_threshold,
        }

        import_record = self.env['eazynova.bank.statement.import'].create(import_vals)

        # Parser le fichier
        import_record.action_parse_file()

        # Créer le relevé bancaire si demandé
        if self.create_statement and import_record.state in ['parsed', 'reconciled']:
            import_record.action_create_bank_statement()

        # Retourner l'action pour afficher l'import
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Relevé Bancaire'),
            'res_model': 'eazynova.bank.statement.import',
            'res_id': import_record.id,
            'view_mode': 'form',
            'target': 'current',
        }


class BankStatementOcrWizard(models.TransientModel):
    _name = 'eazynova.bank.statement.ocr.wizard'
    _description = 'Assistant OCR de Relevé Bancaire'

    import_id = fields.Many2one(
        'eazynova.bank.statement.import',
        string='Import',
        required=True
    )

    file_data = fields.Binary(
        string='Fichier PDF',
        required=True,
        attachment=False
    )

    file_name = fields.Char(string='Nom du Fichier')

    use_ai = fields.Boolean(
        string='Utiliser l\'IA',
        default=True,
        help="Utiliser l'IA pour améliorer l'extraction"
    )

    extracted_text = fields.Text(
        string='Texte Extrait',
        readonly=True
    )

    def action_extract_text(self):
        """Extrait le texte du PDF"""
        self.ensure_one()

        if not self.file_data:
            raise UserError(_("Veuillez charger un fichier PDF."))

        parser = self.env['eazynova.bank.statement.parser']

        try:
            # Parser le PDF
            result = parser.parse_pdf(self.file_data, self.use_ai)

            self.extracted_text = result.get('log', '')

            # Mettre à jour l'import avec les transactions
            self.import_id._create_import_lines(result)

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'eazynova.bank.statement.ocr.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

        except Exception as e:
            raise UserError(_("Erreur lors de l'extraction: %s") % str(e))

    def action_validate(self):
        """Valide l'extraction et ferme le wizard"""
        self.ensure_one()

        return {'type': 'ir.actions.act_window_close'}
