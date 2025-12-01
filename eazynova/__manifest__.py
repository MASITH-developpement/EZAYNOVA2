# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Principal',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Module de base EAZYNOVA - Infrastructure et services communs',
    'description': """
        EAZYNOVA - Module Principal
        ======================

        Module de base fournissant :
        * Infrastructure commune (IA, OCR)
        * Tableau de bord principal
        * Gestion des paramètres globaux
        * Services partagés entre modules

        Ce module est requis pour tous les autres modules EAZYNOVA.
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'portal',
    ],
    'external_dependencies': {
        'python': [
            'PIL',              # Pillow pour traitement d'images
            'numpy',            # Calculs numériques
        ],
    },
    'data': [
        # Sécurité
        'security/eazynova_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/eazynova_data.xml',

        'views/eazynova_dashboard_views.xml',
        'views/eazynova_menu.xml',
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'views/res_users_views.xml',

        # Wizards
        'wizard/ai_assistant_wizard_views.xml',
        'wizard/document_ocr_wizard_views.xml',
            'views/res_config_settings_planning.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eazynova/static/src/css/eazynova.css',
            'eazynova/static/src/js/dashboard.js',
            'eazynova/static/src/xml/dashboard.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}