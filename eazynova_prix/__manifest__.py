# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Vérification des Prix',
    'version': '19.0.1.0.0',
    'category': 'Sales/Purchase',
    'summary': 'Vérification des prix des articles via bases de données externes (Batiprix, etc.)',
    'description': """
        EAZYNOVA - Module Vérification des Prix
        ========================================

        Vérifiez la crédibilité de vos prix d'achat et de vente en les comparant
        avec des bases de données externes du secteur BTP.

        **Fonctionnalités principales:**
        • Connexion aux bases de données externes (Batiprix, etc.)
        • Vérification automatique des prix articles
        • Alertes en cas d'écarts importants
        • Historique des vérifications
        • Suggestions de prix recommandés
        • Analyse des marges par rapport au marché

        **Sources de données supportées:**
        • Batiprix (tarifs BTP)
        • Autres bases de données gratuites
        • API personnalisées

        **Intégrations:**
        • Produits (product.template)
        • Achats (purchase.order)
        • Ventes (sale.order)
        • Chantiers (eazynova_gestion_chantier)

        Compatible Odoo 19 Community Edition
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'sale_management',
        'purchase',
        'eazynova',  # Module EAZYNOVA Core
    ],
    'data': [
        # Sécurité
        'security/prix_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/prix_data.xml',
        'data/cron_prix.xml',

        # Vues
        'views/prix_menu.xml',
        'views/price_source_views.xml',
        'views/price_check_views.xml',
        'views/product_template_views.xml',

        # Wizards
        'wizard/price_verification_wizard_views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
