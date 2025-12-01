# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Gestion des Avis Clients',
    'version': '19.0.1.0.0',
    'category': 'Évaluations',
    'summary': 'Gestion des avis clients Trustpilot et publication sur site web',
    'description': """
        EAZYNOVA - Module Gestion des Avis Clients
        ===========================================

        Gérez les avis de vos clients de manière professionnelle avec intégration
        Trustpilot et publication sur votre site web Odoo.

        **Fonctionnalités principales:**
        • Création automatique de demandes d'avis après facture
        • Envoi d'emails personnalisés en français
        • Intégration API Trustpilot
        • Suivi des avis reçus
        • Publication automatique sur le site web
        • Widgets d'affichage des avis
        • Statistiques et rapports

        **Intégrations:**
        • Trustpilot (API officielle)
        • Google Reviews (optionnel)
        • Site web Odoo (publication automatique)
        • CRM (lien avec les opportunités)
        • Ventes (déclenchement après facturation)

        **Automatisations:**
        • Demande d'avis X jours après facturation
        • Relances automatiques
        • Synchronisation des avis Trustpilot
        • Modération des avis avant publication

        Compatible Odoo 19 Community Edition
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'sale_management',
        'account',
        'website',
        'web',
        'portal',
        'eazynova_intervention',
        'eazynova',  # Module EAZYNOVA Core
    ],
    'data': [
        # Sécurité
        'security/trust_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/trust_data.xml',
        'data/mail_template_data.xml',
        'data/cron_trust.xml',
        'data/cron_trust_sync.xml',

        # Vues
        'views/review_request_views.xml',
        'views/trust_menu.xml',
        'views/customer_review_views.xml',
        'views/intervention_inherit_trust.xml',
        'views/trust_config_views.xml',
        'views/res_partner_views.xml',

        # Wizards
        'wizard/review_request_wizard_views.xml',

        # Website
        'views/website_review_templates.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'assets': {
        'web.assets_frontend': [
            'eazynova_trust/static/src/css/review_widget.css',
            'eazynova_trust/static/src/js/review_widget.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
