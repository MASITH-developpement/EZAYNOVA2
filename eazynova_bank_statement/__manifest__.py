# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Import Relevés Bancaires Intelligent',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Import automatisé CSV/OFX/PDF avec rapprochement bancaire intelligent',
    'description': """
        EAZYNOVA - Import Relevés Bancaires Intelligent
        ================================================

        Fonctionnalités principales :
        * Import automatique des relevés bancaires (CSV, OFX, PDF)
        * OCR intelligent pour relevés PDF avec IA
        * Rapprochement bancaire automatique
        * Alertes sur rapprochements incertains ou absents
        * Détection automatique du format de fichier
        * Suggestions de rapprochement par IA
        * Apprentissage automatique des règles de rapprochement
        * Gestion des doublons
        * Statistiques et rapports de rapprochement

        Formats supportés :
        * CSV : Format personnalisable avec détection automatique
        * OFX : Format standard bancaire (OFX 1.x et 2.x)
        * PDF : Extraction OCR avec IA (Claude/OpenAI)

        Technologies :
        * ofxparse : Parser OFX
        * Tesseract OCR : Reconnaissance de caractères
        * Anthropic Claude / OpenAI : Analyse intelligente
        * pandas : Traitement CSV
        * PyPDF2 : Traitement PDF

        Rapprochement intelligent :
        * Correspondance exacte par référence
        * Correspondance par montant et date
        * Analyse sémantique du libellé (IA)
        * Score de confiance pour chaque rapprochement
        * Apprentissage des patterns de paiement
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'eazynova',
        'account',
    ],
    'external_dependencies': {
        'python': [
            'ofxparse',          # Parser OFX
            'pandas',            # CSV processing
            'PyPDF2',            # PDF processing
            'pytesseract',       # OCR
            'Pillow',            # Image processing
            'pdf2image',         # PDF to image conversion
        ],
    },
    'data': [
        # Sécurité
        'security/bank_statement_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/bank_statement_data.xml',
        'data/reconciliation_rules_data.xml',

        # Vues
        'views/bank_statement_import_views.xml',
        'views/bank_statement_line_views.xml',
        'views/reconciliation_rule_views.xml',
        'views/reconciliation_alert_views.xml',
        'views/bank_statement_menu.xml',

        # Wizards
        'wizard/bank_statement_import_wizard_views.xml',
        'wizard/bank_statement_ocr_wizard_views.xml',
        'wizard/reconciliation_suggestion_wizard_views.xml',

        # Rapports
        'views/bank_statement_report_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
