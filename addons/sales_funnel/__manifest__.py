# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Tunnel de Vente',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Création de tunnels de vente type Calendly (sans prise de RDV)',
    'description': """
        EAZYNOVA - Tunnel de Vente
        ===========================

        Module de création de tunnels de vente progressifs similaire à Calendly mais sans la prise de rendez-vous.

        Fonctionnalités principales :
        * Création de tunnels de vente en plusieurs étapes
        * Pages de destination personnalisables (landing pages)
        * Formulaires multi-étapes avec progression visuelle
        * Collecte progressive d'informations
        * Questions conditionnelles
        * Scoring et qualification de leads
        * Intégration CRM automatique
        * Pages de remerciement personnalisées
        * Suivi de conversion par étape
        * A/B testing des pages
        * Analytiques et statistiques détaillées
        * Webhooks pour intégrations externes
        * Support multi-langues
        * Design responsive

        Types de tunnels supportés :
        * Lead generation (capture de contacts)
        * Qualification de prospects
        * Enquêtes et questionnaires
        * Inscriptions à des événements
        * Demandes de devis
        * Téléchargement de ressources
        * Formulaires de contact avancés

        Configuration :
        * Créer des tunnels avec étapes personnalisées
        * Définir les formulaires pour chaque étape
        * Paramétrer les conditions de navigation
        * Configurer les actions post-soumission
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
        'crm',
        'contacts',
    ],
    'data': [
        # Sécurité
        'security/sales_funnel_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/funnel_template_data.xml',
        'data/email_template_data.xml',

        # Vues backend
        'views/funnel_views.xml',
        'views/funnel_step_views.xml',
        'views/funnel_submission_views.xml',
        'views/funnel_field_views.xml',
        'views/sales_funnel_menu.xml',

        # Templates web
        'views/website_funnel_templates.xml',
        'views/website_funnel_page.xml',
        'views/website_funnel_thank_you.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'sales_funnel/static/src/css/funnel.css',
    #         'sales_funnel/static/src/js/funnel.js',
    #     ],
    # },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
