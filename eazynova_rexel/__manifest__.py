# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Factures Dématérialisées Rexel',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Purchase',
    'summary': 'Réception et traitement automatique des factures électroniques Rexel',
    'description': """
        EAZYNOVA - Module Factures Dématérialisées Rexel
        =================================================

        Automatisez la réception et le traitement des factures électroniques
        de votre fournisseur Rexel directement dans Odoo.

        **Fonctionnalités principales:**
        • Réception automatique des factures Rexel par email
        • Extraction des données de facture (PDF/XML)
        • Création automatique de factures brouillon
        • Rapprochement avec les commandes d'achat
        • Validation assistée par IA (optionnel)
        • Archivage des documents
        • Traçabilité complète

        **Processus automatisé:**
        1. Réception de l'email Rexel avec facture
        2. Extraction des données (OCR si nécessaire)
        3. Identification du fournisseur et des références
        4. Création de la facture brouillon dans Odoo
        5. Rapprochement avec commande d'achat si trouvée
        6. Notification à l'utilisateur pour validation

        **Formats supportés:**
        • PDF (avec OCR)
        • XML (Factur-X, UBL)
        • EDI (optionnel)

        **Intégrations:**
        • Comptabilité fournisseurs
        • Commandes d'achat
        • OCR (module eazynova_facture_ocr)
        • IA (analyse automatique)

        Compatible Odoo 19 Community Edition
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'purchase',
        'mail',
        'eazynova',  # Module EAZYNOVA Core
    ],
    'external_dependencies': {
        'python': ['PyPDF2', 'lxml'],
    },
    'data': [
        # Sécurité
        'security/rexel_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/rexel_data.xml',
        'data/cron_rexel.xml',

        # Vues
        'views/rexel_menu.xml',
        'views/rexel_invoice_import_views.xml',
        'views/rexel_config_views.xml',
        'views/account_move_views.xml',

        # Wizards
        'wizard/rexel_invoice_wizard_views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
