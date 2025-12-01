# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import base64
import csv
import io
import logging
from datetime import datetime
from decimal import Decimal

_logger = logging.getLogger(__name__)


class BankStatementParser(models.AbstractModel):
    _name = 'eazynova.bank.statement.parser'
    _description = 'Parser de Relevés Bancaires'

    @api.model
    def parse_csv(self, file_data, file_name=None):
        """Parse un fichier CSV"""
        try:
            # Décoder le fichier
            content = base64.b64decode(file_data).decode('utf-8-sig')

            # Détecter le délimiteur
            delimiter = self._detect_csv_delimiter(content)

            # Parser le CSV
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

            # Détecter les colonnes
            column_mapping = self._detect_csv_columns(reader.fieldnames)

            transactions = []
            log_lines = []

            log_lines.append(f"Colonnes détectées: {column_mapping}")

            for row_num, row in enumerate(reader, start=2):
                try:
                    trans = self._parse_csv_row(row, column_mapping)
                    if trans:
                        transactions.append(trans)
                except Exception as e:
                    log_lines.append(f"Ligne {row_num}: Erreur - {str(e)}")
                    _logger.warning("Erreur ligne %d: %s", row_num, e)

            log_lines.append(f"Total: {len(transactions)} transactions importées")

            # Calculer les soldes si possible
            result = {
                'transactions': transactions,
                'log': '\n'.join(log_lines),
            }

            if transactions:
                result['date_start'] = min(t['date'] for t in transactions)
                result['date_end'] = max(t['date'] for t in transactions)

            return result

        except Exception as e:
            _logger.exception("Erreur parsing CSV")
            raise UserError(_("Erreur lors du parsing CSV: %s") % str(e))

    @api.model
    def parse_ofx(self, file_data):
        """Parse un fichier OFX"""
        try:
            import ofxparse
        except ImportError:
            raise UserError(_(
                "La bibliothèque 'ofxparse' n'est pas installée.\n"
                "Installez-la avec: pip install ofxparse"
            ))

        try:
            # Décoder le fichier
            content = base64.b64decode(file_data)

            # Parser OFX
            ofx = ofxparse.OfxParser.parse(io.BytesIO(content))

            transactions = []
            log_lines = []

            # Récupérer le compte
            if not ofx.accounts:
                raise UserError(_("Aucun compte trouvé dans le fichier OFX"))

            account = ofx.accounts[0]

            log_lines.append(f"Compte: {account.account_id}")
            log_lines.append(f"Institution: {account.institution.organization if account.institution else 'N/A'}")

            # Parser les transactions
            for trans in account.statement.transactions:
                try:
                    transaction = {
                        'date': trans.date.date() if hasattr(trans.date, 'date') else trans.date,
                        'name': trans.payee or trans.memo or '/',
                        'ref': trans.id or '',
                        'amount': float(trans.amount),
                        'unique_import_id': trans.id or '',
                        'description': trans.memo or '',
                        'partner_name': trans.payee or '',
                        'note': f"Type: {trans.type}",
                    }
                    transactions.append(transaction)

                except Exception as e:
                    log_lines.append(f"Transaction {trans.id}: Erreur - {str(e)}")
                    _logger.warning("Erreur transaction OFX %s: %s", trans.id, e)

            log_lines.append(f"Total: {len(transactions)} transactions importées")

            result = {
                'transactions': transactions,
                'log': '\n'.join(log_lines),
                'date_start': account.statement.start_date.date() if hasattr(account.statement.start_date, 'date') else account.statement.start_date,
                'date_end': account.statement.end_date.date() if hasattr(account.statement.end_date, 'date') else account.statement.end_date,
                'balance_start': float(account.statement.balance) if hasattr(account.statement, 'balance') else 0.0,
                'balance_end': float(account.statement.balance) if hasattr(account.statement, 'balance') else 0.0,
            }

            return result

        except Exception as e:
            _logger.exception("Erreur parsing OFX")
            raise UserError(_("Erreur lors du parsing OFX: %s") % str(e))

    @api.model
    def parse_pdf(self, file_data, use_ai=True):
        """Parse un fichier PDF avec OCR"""
        try:
            import PyPDF2
            import pytesseract
            from pdf2image import convert_from_bytes
            from PIL import Image
        except ImportError as e:
            raise UserError(_(
                "Bibliothèques manquantes pour l'OCR PDF.\n"
                "Installez-les avec: pip install PyPDF2 pytesseract pdf2image Pillow\n"
                "Erreur: %s"
            ) % str(e))

        try:
            # Décoder le fichier
            content = base64.b64decode(file_data)

            log_lines = []

            # Essayer d'extraire le texte directement du PDF
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ''

                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'

                if text.strip():
                    log_lines.append("Texte extrait directement du PDF")
                else:
                    # Si pas de texte, utiliser OCR
                    log_lines.append("Utilisation de l'OCR pour extraire le texte")
                    text = self._ocr_pdf(content)

            except Exception as e:
                log_lines.append(f"Erreur extraction texte PDF: {str(e)}")
                log_lines.append("Utilisation de l'OCR")
                text = self._ocr_pdf(content)

            if not text.strip():
                raise UserError(_("Impossible d'extraire du texte du PDF"))

            # Analyser le texte avec IA si activé
            if use_ai:
                log_lines.append("Analyse du texte avec IA")
                transactions = self._parse_pdf_text_with_ai(text)
            else:
                log_lines.append("Analyse du texte avec règles")
                transactions = self._parse_pdf_text_with_rules(text)

            log_lines.append(f"Total: {len(transactions)} transactions trouvées")

            result = {
                'transactions': transactions,
                'log': '\n'.join(log_lines),
            }

            if transactions:
                result['date_start'] = min(t['date'] for t in transactions)
                result['date_end'] = max(t['date'] for t in transactions)

            return result

        except Exception as e:
            _logger.exception("Erreur parsing PDF")
            raise UserError(_("Erreur lors du parsing PDF: %s") % str(e))

    def _ocr_pdf(self, content):
        """Effectue l'OCR sur un PDF"""
        try:
            from pdf2image import convert_from_bytes
            import pytesseract

            # Convertir PDF en images
            images = convert_from_bytes(content)

            text = ''

            for i, image in enumerate(images):
                # OCR sur chaque page
                page_text = pytesseract.image_to_string(image, lang='fra')
                text += f"\n--- Page {i+1} ---\n{page_text}\n"

            return text

        except Exception as e:
            _logger.exception("Erreur OCR")
            raise UserError(_("Erreur lors de l'OCR: %s") % str(e))

    def _parse_pdf_text_with_ai(self, text):
        """Parse le texte PDF avec IA"""
        try:
            ai_service = self.env['eazynova.ai.service']

            prompt = f"""
Analyse ce relevé bancaire et extrait les transactions.

Pour chaque transaction, fournis :
- date (format YYYY-MM-DD)
- description/libellé
- montant (nombre décimal, négatif pour débit)
- référence (si disponible)

Réponds au format JSON :
{{
  "transactions": [
    {{
      "date": "YYYY-MM-DD",
      "name": "description",
      "amount": 0.00,
      "ref": "reference"
    }},
    ...
  ]
}}

Texte du relevé :
{text[:4000]}  # Limiter la taille
"""

            result = ai_service.analyze_text(prompt, format='json')

            if result and 'transactions' in result:
                transactions = []

                for trans in result['transactions']:
                    try:
                        # Convertir la date
                        date_str = trans.get('date', '')
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()

                        transaction = {
                            'date': date,
                            'name': trans.get('name', trans.get('description', '/')),
                            'amount': float(trans.get('amount', 0)),
                            'ref': trans.get('ref', trans.get('reference', '')),
                            'description': trans.get('name', ''),
                            'partner_name': '',
                            'note': 'Extrait par IA',
                        }

                        transactions.append(transaction)

                    except Exception as e:
                        _logger.warning("Erreur parsing transaction IA: %s", e)
                        continue

                return transactions

            return []

        except Exception as e:
            _logger.exception("Erreur parsing PDF avec IA")
            # Fallback sur les règles
            return self._parse_pdf_text_with_rules(text)

    def _parse_pdf_text_with_rules(self, text):
        """Parse le texte PDF avec des règles (regex)"""
        import re

        transactions = []

        # Patterns communs pour détecter les transactions
        # Format: DD/MM/YYYY ou DD-MM-YYYY
        date_pattern = r'(\d{2}[/-]\d{2}[/-]\d{4})'

        # Montant: 1234.56 ou 1 234,56 ou -1234.56
        amount_pattern = r'(-?\d{1,3}(?:[\s,]\d{3})*[.,]\d{2})'

        # Ligne de transaction typique
        # Date + Description + Montant
        line_pattern = rf'{date_pattern}\s+(.+?)\s+{amount_pattern}'

        for match in re.finditer(line_pattern, text):
            try:
                date_str = match.group(1)
                description = match.group(2).strip()
                amount_str = match.group(3)

                # Parser la date
                for fmt in ['%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    continue

                # Parser le montant
                amount_str = amount_str.replace(' ', '').replace(',', '.')
                amount = float(amount_str)

                transaction = {
                    'date': date,
                    'name': description[:100],
                    'amount': amount,
                    'ref': '',
                    'description': description,
                    'partner_name': '',
                    'note': 'Extrait par règles',
                }

                transactions.append(transaction)

            except Exception as e:
                _logger.debug("Erreur parsing ligne: %s", e)
                continue

        return transactions

    def _detect_csv_delimiter(self, content):
        """Détecte le délimiteur CSV"""
        # Prendre les premières lignes
        first_lines = '\n'.join(content.split('\n')[:5])

        # Tester différents délimiteurs
        for delimiter in [';', ',', '\t', '|']:
            if delimiter in first_lines:
                return delimiter

        return ','

    def _detect_csv_columns(self, fieldnames):
        """Détecte les colonnes du CSV"""
        if not fieldnames:
            return {}

        # Normaliser les noms de colonnes
        fieldnames_lower = [f.lower().strip() for f in fieldnames]

        mapping = {}

        # Détecter la colonne date
        date_keywords = ['date', 'date operation', 'date valeur', 'date comptable']
        for i, field in enumerate(fieldnames_lower):
            if any(kw in field for kw in date_keywords):
                mapping['date'] = fieldnames[i]
                break

        # Détecter la colonne libellé
        desc_keywords = ['libelle', 'libellé', 'description', 'detail', 'détail', 'operation']
        for i, field in enumerate(fieldnames_lower):
            if any(kw in field for kw in desc_keywords):
                mapping['description'] = fieldnames[i]
                break

        # Détecter la colonne montant
        amount_keywords = ['montant', 'amount', 'debit', 'credit', 'valeur']
        for i, field in enumerate(fieldnames_lower):
            if any(kw in field for kw in amount_keywords):
                if 'debit' in field:
                    mapping['debit'] = fieldnames[i]
                elif 'credit' in field:
                    mapping['credit'] = fieldnames[i]
                else:
                    mapping['amount'] = fieldnames[i]

        # Détecter la colonne référence
        ref_keywords = ['reference', 'référence', 'ref', 'numero', 'numéro']
        for i, field in enumerate(fieldnames_lower):
            if any(kw in field for kw in ref_keywords):
                mapping['reference'] = fieldnames[i]
                break

        return mapping

    def _parse_csv_row(self, row, column_mapping):
        """Parse une ligne CSV"""
        if not column_mapping.get('date'):
            raise UserError(_("Impossible de détecter la colonne date"))

        # Extraire la date
        date_str = row.get(column_mapping['date'], '').strip()
        if not date_str:
            return None

        # Parser la date
        date = self._parse_date(date_str)
        if not date:
            return None

        # Extraire la description
        description = ''
        if column_mapping.get('description'):
            description = row.get(column_mapping['description'], '').strip()

        if not description:
            # Essayer de trouver une colonne non vide
            for key, value in row.items():
                if value and key not in [column_mapping.get('date'), column_mapping.get('amount'), column_mapping.get('debit'), column_mapping.get('credit')]:
                    description = value.strip()
                    break

        # Extraire le montant
        amount = 0.0

        if column_mapping.get('amount'):
            amount_str = row.get(column_mapping['amount'], '').strip()
            amount = self._parse_amount(amount_str)

        elif column_mapping.get('debit') or column_mapping.get('credit'):
            debit_str = row.get(column_mapping.get('debit', ''), '').strip()
            credit_str = row.get(column_mapping.get('credit', ''), '').strip()

            debit = self._parse_amount(debit_str) if debit_str else 0.0
            credit = self._parse_amount(credit_str) if credit_str else 0.0

            amount = credit - debit

        # Extraire la référence
        ref = ''
        if column_mapping.get('reference'):
            ref = row.get(column_mapping['reference'], '').strip()

        return {
            'date': date,
            'name': description or '/',
            'amount': amount,
            'ref': ref,
            'description': description,
            'partner_name': '',
            'note': '',
        }

    def _parse_date(self, date_str):
        """Parse une date à partir d'une chaîne"""
        if not date_str:
            return None

        # Formats communs
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%y',
            '%d-%m-%y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    def _parse_amount(self, amount_str):
        """Parse un montant à partir d'une chaîne"""
        if not amount_str:
            return 0.0

        # Nettoyer la chaîne
        amount_str = amount_str.strip()

        # Supprimer les espaces
        amount_str = amount_str.replace(' ', '')

        # Remplacer les virgules par des points
        amount_str = amount_str.replace(',', '.')

        # Supprimer les caractères non numériques (sauf . et -)
        import re
        amount_str = re.sub(r'[^\d.-]', '', amount_str)

        try:
            return float(amount_str)
        except ValueError:
            return 0.0
