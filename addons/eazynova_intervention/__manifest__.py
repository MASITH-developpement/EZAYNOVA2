# -*- coding: utf-8 -*-
{
    'name': "EAZYNOVA - Interventions",
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'summary': "Gestion complète des interventions technique",
    'description': """
        EAZYNOVA - Module de gestion des interventions technique de depannage
        =====================================================================

        **Fonctionnalités principales :**
        • Planification des interventions avec calendrier intégré
        • Gestion des techniciens et équipes
        • Suivi en temps réel des interventions
        • Géolocalisation et calcul de distance automatique
        • Photos avant/après intervention
        • Génération automatique de devis et factures
        • Rapports PDF d'intervention
        • Validation client avec signature
        • Interface mobile optimisée

        **Avantages :**
        • Interface intuitive et moderne
        • Automatisation des tâches répétitives
        • Suivi complet du cycle de vie des interventions
        • Intégration avec les modules Odoo standards
        • Rapports détaillés et analyses

        Compatible Odoo 19 Community Edition SaaS
    """,
    'author': "EAZYNOVA",
    'maintainer': "EAZYNOVA",
    'website': "https://eazynova-production.up.railway.app/",
    'category': 'Services/Project',
    'depends': [
        'base', 'hr', 'mail', 'contacts', 'base_automation',
        'product', 'stock', 'calendar', 'account', 'sale_management', 'crm', 'purchase', 'web',
        'eazynova',  # Module EAZYNOVA Core
    ],
    'data': [
        'security/intervention_security.xml',
        'security/intervention_rules.xml',
        'security/ir.model.access.csv',
        'views/intervention_search_views.xml',
        'views/intervention_server_actions.xml',
        'views/intervention_views.xml',
        'views/intervention_actions.xml',
        'views/intervention_menus.xml',
        'views/intervention_mail_config_views.xml',
        'views/res_config_settings_views.xml',
        'views/intervention_config_views.xml',
        'views/intervention_config_settings.xml',
        'data/sequences_data.xml',
        'data/mail_templates_data.xml',
        'data/automation_send_report.xml',
        'data/automation_incoming_mail.xml',
        'data/cron_cleanup_geocoding.xml',
        'views/intervention_quick_create_views.xml',
        'views/settings_views.xml',
        'views/intervention_colors_template.xml',
        'report/intervention_reports.xml',
        'views/intervention_report_templates.xml',
        'wizard/intervention_validation_wizard_views.xml',
        'views/res_users_view.xml',
        'views/technician_portal_template.xml',
        'views/technician_photos_avant_template.xml',
        'views/technician_rapport_template.xml',
        'views/technician_photos_apres_template.xml',
        'views/technician_validation_client_template.xml',
        'security/intervention_user_access_rules.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eazynova_intervention/static/src/css/intervention_enhanced.css',
            'eazynova_intervention/static/src/css/intervention_override.css',
            'eazynova_intervention/static/src/js/backend/intervention_color_dynamic.js',
        ],
        'web.assets_frontend': [
            # Pas de JS Odoo custom à charger côté frontend pour le portail technicien
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'application': True,
    'live_test_url': 'https://www.masith.fr',
    # 'post_init_hook': 'post_init_hook',
}
