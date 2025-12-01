# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMoveIAOCR(models.Model):
    _inherit = 'account.move'

    def action_ia_extract_invoice_lines(self):
        """
        Action IA+OCR pour remplir automatiquement les lignes de facture fournisseur
        à partir d'une pièce jointe PDF/image et de l'IA (OpenAI).
        """
        import openai
        import json
        import base64
        from pdf2image import convert_from_bytes
        from PIL import Image
        import pytesseract
        import io

        self.ensure_one()
        # 1. OCR sur la pièce jointe principale
        attachment = self.attachment_ids[:1]  # Prend la première pièce jointe
        if not attachment:
            return {'warning': {'title': 'OCR', 'message': "Aucune pièce jointe à analyser."}}
        file_data = base64.b64decode(attachment.datas)
        mimetype = attachment.mimetype or ''
        ocr_text = ''
        try:
            if mimetype == 'application/pdf' or (attachment.name and attachment.name.lower().endswith('.pdf')):
                images = convert_from_bytes(file_data)
                text_pages = [pytesseract.image_to_string(img, lang='fra+eng') for img in images]
                ocr_text = "\n".join(text_pages)
            elif mimetype.startswith('image'):
                img = Image.open(io.BytesIO(file_data))
                ocr_text = pytesseract.image_to_string(img, lang='fra+eng')
            else:
                ocr_text = "Format de fichier non supporté pour l'OCR."
        except Exception as e:
            ocr_text = f"Erreur OCR : {e}"
        _logger.error(f"FACTURE OCR : texte extrait = {ocr_text}")
        if not ocr_text.strip():
            return {'warning': {'title': 'OCR', 'message': "Aucun texte OCR extrait."}}

        # 2. Extraction IA (OpenAI)
        api_key = self.env['ir.config_parameter'].sudo().get_param('openai_api_key')
        if not api_key:
            return {'warning': {'title': 'OpenAI', 'message': "Clé API OpenAI non configurée (openai_api_key)."}}
        openai.api_key = api_key
        prompt = (
            "Tu es un assistant comptable. À partir du texte OCR d'une facture fournisseur, "
            "extrait un objet JSON avec les champs suivants :\n"
            "- fournisseur (nom du fournisseur)\n"
            "- reference_facture (numéro de facture)\n"
            "- date_facture (format YYYY-MM-DD)\n"
            "- lignes : liste d'objets avec 'name' (désignation), 'quantite' (quantité), 'prix_net_unitaire_ht' (prix net unitaire H.T.), 'tva' (taux de TVA en %)\n"
            "Exemple : {\"fournisseur\":\"Rexel\", \"reference_facture\":\"FAC12345\", \"date_facture\":\"2025-12-01\", \"lignes\":[{\"name\":\"Câble 3G2.5\",\"quantite\":100,\"prix_net_unitaire_ht\":0.85,\"tva\":20}]}\n"
            "Texte OCR :\n" + ocr_text
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.1,
            )
            content = response['choices'][0]['message']['content']
            _logger.error(f"FACTURE IA : réponse brute = {content}")
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if not match:
                raise ValueError("Aucun objet JSON trouvé dans la réponse IA.")
            ia_data = json.loads(match.group(0))
        except Exception as e:
            _logger.error(f"FACTURE IA : erreur = {e}")
            return {'warning': {'title': 'OpenAI', 'message': f"Erreur IA : {e}"}}

        # 3. Injection des champs dans la facture
        vals = {}
        if ia_data.get('fournisseur'):
            partner = self.env['res.partner'].search([('name', 'ilike', ia_data['fournisseur'])], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({'name': ia_data['fournisseur']})
            vals['partner_id'] = partner.id
        if ia_data.get('reference_facture'):
            vals['ref'] = ia_data['reference_facture']
        if ia_data.get('date_facture'):
            vals['invoice_date'] = ia_data['date_facture']
        if vals:
            self.write(vals)

        # 4. Injection des lignes
        product_model = self.env['product.product']
        invoice_lines = []
        prix_ttc_detecte = False
        prix_ht_detecte = False
        for prod in ia_data.get('lignes', []):
            name = prod.get('name') or 'Produit inconnu'
            qty = float(prod.get('quantite') or 1)
            # Gestion TTC/HT
            prix_ttc = prod.get('prix_net_unitaire_ttc')
            prix_ht = prod.get('prix_net_unitaire_ht')
            tva = prod.get('tva')
            if prix_ttc is not None and (prix_ht is None or prix_ht == 0):
                prix_ttc_detecte = True
                # Si pas de taux de TVA, on suppose 20%
                taux_tva = float(tva) if tva is not None else 20.0
                price = float(prix_ttc) / (1 + taux_tva / 100)
                tva = taux_tva
            elif prix_ht is not None:
                prix_ht_detecte = True
                price = float(prix_ht)
            else:
                price = 0.0
            product = product_model.search([('name', 'ilike', name)], limit=1)
            if not product:
                product = product_model.create({'name': name})
            line_vals = {
                'product_id': product.id,
                'name': name,
                'quantity': qty,
                'price_unit': price,
                'discount': 0,  # Remise forcée à 0 pour éviter l'affichage dans la colonne Prix
            }
            if tva is not None:
                tax = self.env['account.tax'].search([
                    ('amount', '=', float(tva)),
                    ('type_tax_use', '=', 'purchase')
                ], limit=1)
                if tax:
                    line_vals['tax_ids'] = [(6, 0, [tax.id])]
            invoice_lines.append((0, 0, line_vals))
        if invoice_lines:
            self.invoice_line_ids = invoice_lines
        # Message utilisateur sur la nature des prix
        if prix_ttc_detecte:
            info_prix = "Les prix extraits sont TTC. Recharge la page pour voir les lignes."
        elif prix_ht_detecte:
            info_prix = "Les prix extraits sont HT. Recharge la page pour voir les lignes."
        else:
            info_prix = "Impossible de déterminer si les prix sont HT ou TTC. Recharge la page pour voir les lignes."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Facture IA',
                'message': info_prix,
                'sticky': False,
            }
        }
