# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import logging

_logger = logging.getLogger(__name__)


class EazynovaInvoiceOcrService(models.AbstractModel):
    _name = 'eazynova.invoice.ocr.service'
    _description = 'Service OCR pour factures'

    @api.model
    def extract_invoice_data(self, attachment):
        """
        Extrait les données d'une facture depuis un PDF ou une image

        Args:
            attachment: ir.attachment - Fichier à traiter

        Returns:
            dict: Données extraites
        """
        try:
            # Décoder le fichier
            file_content = base64.b64decode(attachment.datas)
            file_type = attachment.mimetype

            # Selon le type de fichier
            if 'pdf' in file_type:
                return self._extract_from_pdf(file_content)
            elif 'image' in file_type:
                return self._extract_from_image(file_content)
            else:
                return {
                    'success': False,
                    'error': _('Type de fichier non supporté')
                }

        except Exception as e:
            _logger.error(f'Erreur OCR: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_from_pdf(self, file_content):
        """Extrait les données d'un PDF"""
        try:
            # Utiliser PyPDF2 pour extraction texte
            import PyPDF2
            from io import BytesIO

            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extraire le texte de toutes les pages
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()

            # Utiliser l'IA pour analyser le texte
            return self._analyze_text_with_ai(text)

        except Exception as e:
            _logger.error(f'Erreur extraction PDF: {str(e)}')
            # Fallback sur OCR d'image
            try:
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(file_content, first_page=1, last_page=1)
                if images:
                    return self._extract_from_image_object(images[0])
            except:
                pass

            return {
                'success': False,
                'error': str(e)
            }

    def _extract_from_image(self, file_content):
        """Extrait les données d'une image"""
        try:
            from PIL import Image
            from io import BytesIO

            image = Image.open(BytesIO(file_content))
            return self._extract_from_image_object(image)

        except Exception as e:
            _logger.error(f'Erreur extraction image: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_from_image_object(self, image):
        """Extrait le texte d'un objet Image avec Tesseract"""
        try:
            import pytesseract

            # OCR avec Tesseract
            text = pytesseract.image_to_string(image, lang='fra')

            # Analyser avec IA
            return self._analyze_text_with_ai(text)

        except Exception as e:
            _logger.error(f'Erreur Tesseract: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_text_with_ai(self, text):
        """Analyse le texte extrait avec l'IA pour identifier les champs"""
        try:
            # Utiliser le service IA d'Eazynova
            ai_service = self.env['eazynova.ai.service']

            prompt = f"""Analyse cette facture et extrais les informations suivantes au format JSON:
- supplier_name: Nom du fournisseur
- supplier_vat: Numéro de TVA du fournisseur
- invoice_number: Numéro de facture
- invoice_date: Date de facture (format YYYY-MM-DD)
- due_date: Date d'échéance (format YYYY-MM-DD)
- total_ht: Montant HT
- total_tva: Montant TVA
- total_ttc: Montant TTC
- lines: Liste des lignes avec description, quantity, price_unit, amount

Texte de la facture:
{text}

Réponds uniquement avec le JSON, sans texte supplémentaire."""

            response = ai_service.call_ai(prompt)

            if response:
                import json
                try:
                    data = json.loads(response)

                    # Rechercher le fournisseur dans Odoo
                    partner_id = self._find_or_create_partner(
                        data.get('supplier_name'),
                        data.get('supplier_vat')
                    )

                    # Formater le résultat
                    return {
                        'success': True,
                        'partner_id': partner_id,
                        'reference': data.get('invoice_number'),
                        'invoice_date': data.get('invoice_date'),
                        'invoice_date_due': data.get('due_date'),
                        'amount_total': float(data.get('total_ttc', 0)),
                        'amount_untaxed': float(data.get('total_ht', 0)),
                        'amount_tax': float(data.get('total_tva', 0)),
                        'lines': self._format_invoice_lines(data.get('lines', [])),
                        'confidence': 85.0,
                        'raw_data': data
                    }
                except json.JSONDecodeError:
                    # Si ce n'est pas du JSON valide, extraire manuellement
                    return self._extract_manual(text)

            return {
                'success': False,
                'error': _('Aucune réponse de l\'IA')
            }

        except Exception as e:
            _logger.error(f'Erreur analyse IA: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _find_or_create_partner(self, name, vat=None):
        """Trouve ou crée un partenaire"""
        if not name:
            return False

        # Rechercher par nom ou TVA
        domain = ['|', ('name', 'ilike', name)]
        if vat:
            domain.append(('vat', '=', vat))

        partner = self.env['res.partner'].search(domain, limit=1)

        if partner:
            return partner.id

        # Créer le partenaire
        partner = self.env['res.partner'].create({
            'name': name,
            'vat': vat,
            'supplier_rank': 1,
        })

        return partner.id

    def _format_invoice_lines(self, lines):
        """Formate les lignes de facture"""
        result = []

        for line in lines:
            # Trouver le compte de charge par défaut
            account = self.env.company.default_expense_account_id

            result.append({
                'description': line.get('description', ''),
                'quantity': float(line.get('quantity', 1.0)),
                'price_unit': float(line.get('price_unit', 0.0)),
                'account_id': account.id if account else False,
                'tax_ids': [(6, 0, [self.env.company.default_purchase_tax_id.id])] if self.env.company.default_purchase_tax_id else [],
            })

        return result

    def _extract_manual(self, text):
        """Extraction manuelle basique avec regex"""
        import re

        result = {
            'success': True,
            'confidence': 60.0,
            'raw_data': {'text': text}
        }

        # Numéro de facture
        invoice_patterns = [
            r'facture\s*n[°o\s]*[:.\s]*(\S+)',
            r'invoice\s*n[°o\s]*[:.\s]*(\S+)',
            r'n[°o]\s*facture\s*[:.\s]*(\S+)',
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['reference'] = match.group(1)
                break

        # Montants
        amount_pattern = r'(\d+[,\s]\d+|\d+)[€\s]'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            # Prendre le dernier montant (souvent le total)
            result['amount_total'] = float(amounts[-1].replace(',', '.').replace(' ', ''))

        return result
