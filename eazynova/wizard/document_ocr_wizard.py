# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64
import logging
import tempfile
import os

_logger = logging.getLogger(__name__)


class DocumentOCRWizard(models.TransientModel):
    _name = 'eazynova.document.ocr.wizard'
    _description = 'OCR de documents EAZYNOVA'

    name = fields.Char(string="Nom du document", required=True)
    document = fields.Binary(string="Document", required=True, attachment=True)
    document_filename = fields.Char(string="Nom de fichier")

    # Configuration OCR
    language = fields.Selection([
        ('fra', 'Français'),
        ('eng', 'Anglais'),
        ('fra+eng', 'Français + Anglais'),
    ], string="Langue", default=lambda self: self._default_language())

    # Résultat
    extracted_text = fields.Text(string="Texte extrait", readonly=True)
    confidence = fields.Float(string="Confiance (%)", readonly=True)

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('processing', 'Traitement en cours'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ], string="État", default='draft', readonly=True)

    error_message = fields.Text(string="Message d'erreur", readonly=True)

    @api.model
    def _default_language(self):
        """Récupère la langue OCR par défaut"""
        return self.env['ir.config_parameter'].sudo().get_param('eazynova.ocr_language', 'fra+eng')

    def action_process_ocr(self):
        """Lance le traitement OCR"""
        self.ensure_one()

        # Vérifier que l'OCR est activé
        ocr_enabled = self.env['ir.config_parameter'].sudo().get_param('eazynova.ocr_enabled', True)
        if not ocr_enabled:
            raise UserError(_("L'OCR n'est pas activé. Veuillez activer l'OCR dans les paramètres EAZYNOVA."))

        self.state = 'processing'

        try:
            # Extraire le texte du document
            extracted_text, confidence = self._extract_text_from_document()

            self.extracted_text = extracted_text
            self.confidence = confidence
            self.state = 'done'

        except Exception as e:
            _logger.error(f"Erreur lors de l'OCR: {str(e)}")
            self.error_message = str(e)
            self.state = 'error'
            raise UserError(_("Erreur lors de l'OCR: %s") % str(e))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.document.ocr.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _extract_text_from_document(self):
        """Extrait le texte d'un document via OCR"""
        try:
            import pytesseract
            from PIL import Image
            from pdf2image import convert_from_bytes
            import PyPDF2
            import io
        except ImportError as e:
            raise UserError(_(
                "Dépendances OCR manquantes. Veuillez installer: "
                "pip install pytesseract Pillow pdf2image PyPDF2"
            ))

        # Décoder le document
        document_data = base64.b64decode(self.document)
        filename = self.document_filename.lower() if self.document_filename else ''

        extracted_text = ""
        confidence = 0.0

        try:
            if filename.endswith('.pdf'):
                # Traiter un PDF
                # D'abord essayer d'extraire le texte natif
                try:
                    pdf_file = io.BytesIO(document_data)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    native_text = ""

                    for page in pdf_reader.pages:
                        native_text += page.extract_text() + "\n"

                    if native_text.strip():
                        # PDF avec texte natif
                        extracted_text = native_text
                        confidence = 95.0
                    else:
                        raise Exception("PDF sans texte natif, utilisation de l'OCR")

                except Exception:
                    # PDF scanné, utiliser l'OCR
                    images = convert_from_bytes(document_data)
                    ocr_texts = []
                    ocr_confidences = []

                    for image in images:
                        # OCR sur chaque page
                        data = pytesseract.image_to_data(
                            image,
                            lang=self.language,
                            output_type=pytesseract.Output.DICT
                        )

                        page_text = " ".join([
                            text for text in data['text']
                            if text.strip()
                        ])

                        # Calculer la confiance moyenne
                        confidences = [
                            int(conf) for conf in data['conf']
                            if int(conf) > 0
                        ]
                        page_confidence = sum(confidences) / len(confidences) if confidences else 0

                        ocr_texts.append(page_text)
                        ocr_confidences.append(page_confidence)

                    extracted_text = "\n\n".join(ocr_texts)
                    confidence = sum(ocr_confidences) / len(ocr_confidences) if ocr_confidences else 0

            elif filename.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                # Traiter une image
                image = Image.open(io.BytesIO(document_data))

                # OCR
                data = pytesseract.image_to_data(
                    image,
                    lang=self.language,
                    output_type=pytesseract.Output.DICT
                )

                extracted_text = " ".join([
                    text for text in data['text']
                    if text.strip()
                ])

                # Calculer la confiance
                confidences = [
                    int(conf) for conf in data['conf']
                    if int(conf) > 0
                ]
                confidence = sum(confidences) / len(confidences) if confidences else 0

            else:
                raise ValidationError(_("Format de fichier non supporté: %s") % filename)

        except Exception as e:
            _logger.error(f"Erreur lors de l'extraction OCR: {str(e)}")
            raise

        return extracted_text, confidence

    def action_cancel(self):
        """Annule et ferme le wizard"""
        return {'type': 'ir.actions.act_window_close'}
