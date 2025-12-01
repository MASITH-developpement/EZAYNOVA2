# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AchatOrderOCR(models.Model):
    _inherit = 'purchase.order'

    def action_ia_extract_products(self):
        """
        Utilise OpenAI GPT pour extraire les produits du texte OCR et créer les lignes de commande.
        Nécessite une clé API OpenAI dans ir.config_parameter (key: openai_api_key).
        """
        import openai
        import json
        self.ensure_one()
        ocr_text = self.ocr_extracted_text or ''
        if not ocr_text.strip():
            return {'warning': {'title': 'OCR', 'message': "Aucun texte OCR à analyser."}}
        # Récupérer la clé API OpenAI depuis la config Odoo
        api_key = self.env['ir.config_parameter'].sudo().get_param('openai_api_key')
        _logger.error("Clé API OpenAI récupérée : %s", api_key)
        if not api_key:
            _logger.error("Aucune clé API OpenAI trouvée dans ir.config_parameter (openai_api_key)")
            return {'warning': {'title': 'OpenAI', 'message': "Clé API OpenAI non configurée (openai_api_key)."}}
        openai.api_key = api_key
        prompt = (
            "Tu es un assistant d'achat. À partir du texte OCR d'une facture ou d'un devis, "
            "extrait un objet JSON avec les champs suivants :\n"
            "- fournisseur (nom du fournisseur)\n"
            "- reference_fournisseur (numéro de référence de la commande ou facture)\n"
            "- echeance_commande (date d'échéance ou de livraison prévue, format YYYY-MM-DD si possible)\n"
            "- date_facture (date de la facture si c'est une facture, format YYYY-MM-DD)\n"
            "- produits : liste d'objets avec 'name' (désignation), 'quantite' (quantité réelle/unité de la facture), 'prix_net_unitaire_ht' (prix net unitaire H.T. de la facture, sans remise ni taxe), 'tva' (taux de TVA en pourcentage, ex: 20 pour 20%)\n"
            "Exemple de sortie : {\"fournisseur\":\"Rexel\", \"reference_fournisseur\":\"BC12345\", \"echeance_commande\":\"2025-12-10\", \"date_facture\":\"2025-12-01\", \"produits\":[{\"name\":\"Câble 3G2.5\",\"quantite\":100,\"prix_net_unitaire_ht\":0.85,\"tva\":20}]}\n"
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
            _logger.error("Réponse brute IA : %s", content)
            # Recherche du premier bloc JSON dans la réponse
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if not match:
                _logger.error("Aucun objet JSON trouvé dans la réponse IA.")
                raise ValueError("Aucun objet JSON trouvé dans la réponse IA.")
            ia_data = json.loads(match.group(0))
        except Exception as e:
            _logger.error("Erreur IA ou parsing JSON : %s", e)
            return {'warning': {'title': 'OpenAI', 'message': f"Erreur IA : {e}"}}

        # Renseigner les champs commande si présents
        vals = {}
        if ia_data.get('fournisseur'):
            partner = self.env['res.partner'].search([('name', 'ilike', ia_data['fournisseur'])], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({'name': ia_data['fournisseur']})
            vals['partner_id'] = partner.id
        if ia_data.get('reference_fournisseur'):
            vals['partner_ref'] = ia_data['reference_fournisseur']
        # Si date_facture présente et document = facture, on la prend comme échéance
        if ia_data.get('date_facture'):
            vals['date_planned'] = ia_data['date_facture']
        elif ia_data.get('echeance_commande'):
            vals['date_planned'] = ia_data['echeance_commande']
        if vals:
            self.write(vals)

        # Création des lignes de commande
        product_model = self.env['product.product']
        order_lines = []
        for prod in ia_data.get('produits', []):
            name = prod.get('name') or 'Produit inconnu'
            qty = float(prod.get('quantite') or 1)
            price = float(prod.get('prix_net_unitaire_ht') or 0)
            tva = prod.get('tva')
            # Recherche d’un produit existant par nom (sinon, produit générique)
            product = product_model.search([('name', 'ilike', name)], limit=1)
            if not product:
                product = product_model.create({'name': name})
            line_vals = {
                'product_id': product.id,
                'name': name,
                'product_qty': qty,
                'price_unit': price,
            }
            # Associer la taxe correspondant au taux extrait
            if tva is not None:
                tax = self.env['account.tax'].search([
                    ('amount', '=', float(tva)),
                    ('type_tax_use', '=', 'purchase')
                ], limit=1)
                if tax:
                    line_vals['tax_ids'] = [(6, 0, [tax.id])]
            order_lines.append((0, 0, line_vals))
        if order_lines:
            self.order_line = order_lines
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': self.id,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'tag': 'reload',
                'context': self.env.context,
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Produits IA',
                'message': 'Aucune ligne détectée.',
                'sticky': False,
            }
        }

    ocr_attachment_id = fields.Many2one('ir.attachment', string="Facture/Bon scanné (OCR)")
    ocr_extracted_text = fields.Text(string="Texte extrait (OCR)")
    ia_suggestion = fields.Text(string="Suggestion IA (commande)")
    chantier_id = fields.Many2one('project.project', string="Chantier lié")

    def action_ocr_extract(self):
        import pytesseract
        from pdf2image import convert_from_bytes
        from PIL import Image
        import base64
        import io
        import logging
        _logger = logging.getLogger(__name__)
        _logger.error("OCR : entrée dans action_ocr_extract !")
        try:
            extracted_text = ""
            for rec in self:
                attachment = rec.ocr_attachment_id
                if not attachment:
                    rec.ocr_extracted_text = "Aucune pièce jointe OCR."
                    _logger.error("OCR : aucune pièce jointe trouvée.")
                    continue
                file_data = base64.b64decode(attachment.datas)
                _logger.error(f"OCR : mimetype={attachment.mimetype}, nom={attachment.name}")
                if attachment.mimetype == 'application/pdf' or (attachment.name and attachment.name.lower().endswith('.pdf')):
                    # PDF : conversion en images puis OCR sur chaque page
                    try:
                        images = convert_from_bytes(file_data)
                        text_pages = []
                        for img in images:
                            page_text = pytesseract.image_to_string(img, lang='fra+eng')
                            text_pages.append(page_text)
                            _logger.error(f"OCR : texte page PDF = {page_text}")
                        extracted_text = "\n".join(text_pages)
                    except Exception as e:
                        extracted_text = f"Erreur OCR PDF : {e}"
                        _logger.error(f"OCR : erreur PDF = {e}")
                elif attachment.mimetype and attachment.mimetype.startswith('image'):
                    # Image : OCR direct
                    try:
                        img = Image.open(io.BytesIO(file_data))
                        extracted_text = pytesseract.image_to_string(img, lang='fra+eng')
                        _logger.error(f"OCR : texte image = {extracted_text}")
                    except Exception as e:
                        extracted_text = f"Erreur OCR image : {e}"
                        _logger.error(f"OCR : erreur image = {e}")
                else:
                    extracted_text = "Format de fichier non supporté pour l'OCR."
                    _logger.error("OCR : format non supporté")
                rec.ocr_extracted_text = extracted_text
                _logger.error(f"OCR : texte final = {extracted_text}")
        except Exception as exc:
            _logger.error(f"OCR : exception globale = {exc}")
        return True
