# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Prise de Rendez-vous en ligne',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Système de prise de rendez-vous en ligne type Calendly',
    'description': """
        EAZYNOVA - Prise de Rendez-vous en ligne
        ==========================================

        Module de prise de rendez-vous en ligne similaire à Calendly.

        Fonctionnalités principales :
        * Création de types de rendez-vous configurables
        * Calendrier interactif pour la sélection de créneaux
        * Gestion des disponibilités par utilisateur/ressource
        * Durée personnalisable des rendez-vous
        * Délai de réservation configurable (buffer time)
        * Intégration avec le calendrier Odoo
        * Notifications par email automatiques
        * Page de confirmation personnalisable
        * Formulaire de collecte d'informations client
        * Support multi-utilisateurs
        * Zones horaires multiples
        * Annulation et reprogrammation de rendez-vous
        * Interface publique responsive

        Configuration :
        * Définir les types de rendez-vous disponibles
        * Configurer les horaires de disponibilité
        * Personnaliser les formulaires de réservation
        * Paramétrer les notifications
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
        'calendar',
        'contacts',
        'ai_assistant',
    ],
    'data': [
        # Sécurité
        'security/website_booking_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/booking_type_data.xml',
        'data/email_template_data.xml',

        # Vues backend
        'views/booking_type_views.xml',
        'views/booking_appointment_views.xml',
        'views/booking_availability_views.xml',
        'views/website_booking_menu.xml',

        # Templates web
        'views/website_booking_templates.xml',
        'views/website_booking_page.xml',
        'views/website_booking_confirmation.xml',

        # Wizards
        'wizard/booking_reschedule_wizard_views.xml',
        'wizard/booking_type_creation_wizard_views.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'website_booking/static/src/css/booking.css',
    #         'website_booking/static/src/js/booking_calendar.js',
    #     ],
    # },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
