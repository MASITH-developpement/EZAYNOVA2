# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Achats',
    'version': '19.0.1.0.0',
    'category': 'Purchase',
    'summary': "Gestion des achats pour EAZYNOVA (version communautaire)",
    'description': """
        EAZYNOVA - Achats (Community)
        =============================
        
        Module de gestion des achats adapté pour Odoo Community Edition.
        Fonctionnalités :
        * Gestion des demandes d'achat
        * Suivi des commandes fournisseurs
        * Réception et validation des achats
        * Rapports d'achats
        
        Ce module ne dépend que des modules Odoo Community.
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'eazynova',
        'purchase',
        'stock',
    ],
    'data': [
        'security/achat_security.xml',
        'security/ir.model.access.csv',
        'data/achat_sequence.xml',
        'views/eazynova_achat_views.xml',
        'views/achat_menu.xml',
        'report/achat_report_views.xml',
        'report/achat_report_templates.xml',
    ],
    'demo': [
        'demo/achat_demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'application': False,
    'auto_install': False,
}
