# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Site Web SaaS',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Site web commercial pour la vente d\'EAZYNOVA en mode SaaS',
    'description': """
        EAZYNOVA - Site Web SaaS
        ========================

        Site web commercial pour la vente d'EAZYNOVA en mode SaaS avec :

        * Page d'accueil présentant les fonctionnalités
        * Page de tarification (250€ HT/mois pour 5 utilisateurs + 20€/utilisateur)
        * Essai gratuit de 30 jours
        * Configuration complète à 1800€ HT
        * Gestion automatique des abonnements
        * Suppression automatique des bases de données inactives après 30 jours
        * Intégration avec Railway pour le provisioning automatique
        * Tableau de bord client pour gérer son abonnement

        Fonctionnalités :
        * Inscription en ligne avec essai gratuit
        * Gestion des utilisateurs et facturation
        * Provisioning automatique des instances Odoo
        * Système de paiement intégré
        * Notifications par email
        * Tableau de bord d'administration SaaS
    """,
    'author': 'EAZYNOVA - S. MOREAU',
    'website': 'https://eazynova.fr',
    'license': 'Other proprietary',
    'maintainer': 'S. MOREAU',
    'depends': [
        'base',
        'web',
        'website',
        'portal',
        'mail',
        'payment',
        'account',
        'sale_management',
    ],
    'data': [
        # Sécurité
        'security/eazynova_website_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/saas_plan_data.xml',
        'data/email_template_data.xml',
        'data/ir_cron_data.xml',
        'data/website_menu_data.xml',

        # Vues backend
        'views/saas_subscription_views.xml',
        'views/saas_instance_views.xml',
        'views/saas_plan_views.xml',
        'views/eazynova_website_menu.xml',

        # Templates web
        'views/website_templates.xml',
        'views/website_homepage.xml',
        'views/website_pricing.xml',
        'views/website_signup.xml',
        'views/website_features.xml',
        'views/portal_templates.xml',

        # Wizards
        'wizard/subscription_upgrade_wizard_views.xml',
    ],
    'assets': {
        # Tous les assets SCSS désactivés temporairement - incompatibilité Odoo 19 avec web editor
        # Les variables $o-we-* ne sont pas définies correctement dans le core
        # 'web.assets_web': [
        #     ('prepend', 'eazynova_website/static/src/scss/variables_patch.scss'),
        # ],
        # 'web.assets_web_print': [
        #     ('prepend', 'eazynova_website/static/src/scss/variables_patch.scss'),
        # ],
        'web.assets_frontend': [
            'eazynova_website/static/src/css/website.css',
            # 'eazynova_website/static/src/js/website.js',  # Désactivé temporairement - incompatible Odoo 19
        ],
        'web.assets_backend': [
            'eazynova_website/static/src/css/backend.css',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,  # Masqué de la liste des applications clients
    'auto_install': False,
}
