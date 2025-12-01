# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - OCR Factures Intelligent',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'OCR automatisé avec IA pour extraction données factures',
    'description': """
        EAZYNOVA - OCR Factures Intelligent
        ====================================
        
        Fonctionnalités :
        * OCR automatique des factures (PDF et images)
        * Extraction intelligente par IA (Claude/OpenAI)
        * Reconnaissance multi-format de factures
        * Création automatique des factures fournisseurs
        * Validation et correction assistée
        * Apprentissage automatique des formats
        * Historique des traitements
        * Rapprochement avec commandes
        * Gestion des erreurs et doublons
        * Export des données extraites
        
        Technologies :
        * Tesseract OCR (reconnaissance caractères)
        * Anthropic Claude / OpenAI (analyse intelligente)
        * PyPDF2 (traitement PDF)
        * Pillow (traitement images)
        * pdf2image (conversion PDF vers images)
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'eazynova',              # Module CORE (IA, OCR)
        'account',               # Comptabilité Odoo
        'purchase',              # Achats (optionnel pour rapprochement)
    ],
    'data': [
        # Sécurité
        'security/facture_ocr_security.xml',
        'security/ir.model.access.csv',
        
        # Données
        'data/facture_ocr_data.xml',
        'data/facture_template_data.xml',
        
        # Vues
        'views/eazynova_facture_ocr_views.xml',
        'views/eazynova_facture_template_views.xml',
        'views/account_move_views.xml',
        'views/facture_ocr_menu.xml',
        
        # Wizards
        'wizard/facture_ocr_upload_wizard_views.xml',
        'wizard/facture_ocr_validate_wizard_views.xml',
        
        # Rapports
        'report/facture_ocr_report_views.xml',
    ],
    'demo': [
        'demo/facture_ocr_demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}