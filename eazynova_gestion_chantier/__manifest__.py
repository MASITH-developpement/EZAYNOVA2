# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Gestion de Chantiers',
    'version': '19.0.1.0.0',
    'category': 'Construction/Project',
    'summary': 'Gestion complète des chantiers de construction et BTP',
    'description': """
        EAZYNOVA - Module Gestion de Chantiers
        ========================================

        Gestion complète pour le BTP et la construction :

        **Gestion de projet:**
        • Création et suivi des chantiers
        • Phases de construction
        • Planification des tâches
        • Affectation des équipes

        **Gestion des ressources:**
        • Gestion des équipes et techniciens
        • Suivi du matériel et équipements
        • Planning des ressources
        • Disponibilités

        **Suivi financier:**
        • Devis et facturation
        • Suivi des coûts
        • Achats et approvisionnement
        • Rentabilité par chantier

        **Fonctionnalités avancées:**
        • Photos et documents chantier
        • Rapports d'avancement
        • Planning Gantt
        • Vue calendrier
        • Alertes et notifications
        • Intégration GPS/géolocalisation

        Compatible Odoo 19 Community Edition SaaS
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'project',
        'hr',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'calendar',
        'eazynova',  # Module EAZYNOVA Core
    ],
    'data': [
        # Sécurité
        'security/chantier_security.xml',
        'security/ir.model.access.csv',

        # Données de base
        'data/chantier_sequence.xml',
        'data/chantier_data.xml',

        # Vues
        'views/chantier_views.xml',
        'views/chantier_phase_views.xml',
        'views/chantier_tache_views.xml',
        'views/chantier_equipe_views.xml',
        'views/chantier_materiel_views.xml',
        'views/chantier_depense_views.xml',
        'views/chantier_menu.xml',

        # Rapports
        'report/chantier_reports.xml',
        'report/chantier_report_templates.xml',

        # Wizards
        'wizard/chantier_close_wizard_views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
