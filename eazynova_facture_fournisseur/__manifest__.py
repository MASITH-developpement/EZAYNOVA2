# -*- coding: utf-8 -*-
{
    'name': 'Eazynova Facture Fournisseur IA OCR',
    'version': '1.0',
    'category': 'Accounting',
    'summary': "Extraction IA+OCR des lignes de facture fournisseur (account.move)",
    'description': "Ajoute une action IA+OCR pour extraire automatiquement les lignes de facture fournisseur à partir d'une pièce jointe PDF/image.",
    'author': 'Eazynova',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_ia_ocr_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
