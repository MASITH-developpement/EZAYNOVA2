# -*- coding: utf-8 -*-
{
    'name': 'Eazynova Comptabilité',
    'version': '1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Module de comptabilité complet avec passerelles, OCR IA et gestion avancée',
    'description': """
        Module de Comptabilité Eazynova
        ================================

        Fonctionnalités principales :
        -----------------------------
        * Plan comptable général français (PCG) modifiable
        * Comptabilité analytique optionnelle
        * Gestion multi-comptes bancaires (France et international)
        * Import bancaire automatisé
        * Gestion factures fournisseurs avec OCR/IA
        * Gestion factures clients
        * Notes de frais
        * Gestion de la TVA multi-taux
        * Passerelles vers logiciels externes :
            - Pennylane
            - Sage
            - Axonaut
            - EBP Compta
            - Et autres...

        Rapports et analyses :
        ----------------------
        * Bilan intermédiaire conforme réglementation française
        * Bilan annuel
        * Compte de résultat
        * Indicateurs de trésorerie
        * Grand livre
        * Balance comptable
        * Journaux

        Gestion client/fournisseur :
        ----------------------------
        * Comptes clients et fournisseurs
        * Suivi des impayés
        * Relances automatiques
        * Lettrage automatique

        Fonctionnalités avancées :
        --------------------------
        * OCR intelligent pour factures PDF et photos
        * IA pour aide à la saisie des codes comptables
        * Export comptable (PDF, Excel, formats d'échange)
        * Multi-devises
        * Multi-sociétés
        * Traduction FR/EN
        * Formation intégrée avec images tutoriels
    """,
    'author': 'Eazynova',
    'website': 'https://www.eazynova.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'web',
        'base_setup',
        'eazynova',  # Module core pour AI services
    ],
    'data': [
        # Security
        'security/comptabilite_security.xml',
        'security/ir.model.access.csv',

        # Data - Plan Comptable Général
        'data/account_chart_template_data.xml',
        'data/account_tax_data.xml',
        'data/account_journal_data.xml',
        'data/payment_term_data.xml',

        # Views - Menus principaux
        'views/menu_views.xml',
        'views/actions.xml',

        # Views - Configuration
        'views/company_views.xml',
        'views/account_chart_views.xml',
        'views/account_journal_views.xml',
        'views/account_tax_views.xml',
        'views/fiscal_position_views.xml',

        # Views - Opérations courantes
        'views/account_move_views.xml',
        'views/invoice_customer_views.xml',
        'views/invoice_supplier_views.xml',
        'views/expense_note_views.xml',
        'views/payment_views.xml',

        # Views - Banque
        'views/bank_account_views.xml',
        'views/bank_statement_views.xml',
        'views/bank_reconciliation_views.xml',

        # Views - Partenaires
        'views/partner_views.xml',
        'views/partner_ledger_views.xml',

        # Views - Analytique
        'views/analytic_account_views.xml',
        'views/analytic_line_views.xml',

        # Views - Rapports
        'views/report_views.xml',

        # Wizards
        'wizards/account_move_reversal_views.xml',
        'wizards/bank_import_views.xml',
        'wizards/invoice_ocr_views.xml',
        'wizards/export_comptable_views.xml',
        'wizards/unpaid_reminder_views.xml',
        'wizards/closing_wizard_views.xml',

        # Reports
        'reports/report_templates.xml',
        'reports/report_invoice.xml',
        'reports/report_balance.xml',
        'reports/report_general_ledger.xml',
        'reports/report_trial_balance.xml',
        'reports/report_bilan.xml',
        'reports/report_compte_resultat.xml',

        # Email templates
        'data/mail_template_data.xml',

        # Cron jobs
        'data/cron_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eazynova_comptabilite/static/src/js/**/*.js',
            'eazynova_comptabilite/static/src/css/**/*.css',
        ],
        'web.assets_frontend': [
            'eazynova_comptabilite/static/src/css/portal.css',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'numpy',
            'pandas',
            'openpyxl',
            'xlsxwriter',
            'pdf2image',
            'pytesseract',
            'Pillow',
        ],
    },
}
