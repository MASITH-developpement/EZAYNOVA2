# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Planning',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Module de planification et gestion des ressources pour EAZYNOVA',
    'description': """
        EAZYNOVA - Module Planning
        ==========================

        Fonctionnalités principales :
        * Planification des interventions et tâches
        * Gestion des ressources (humaines, matérielles)
        * Calendriers d'équipes et équipements
        * Attribution automatique des ressources
        * Vue Gantt pour visualisation temporelle
        * Gestion des disponibilités et absences
        * Intégration avec chantiers et projets
        * Alertes de conflits de planning
        * Optimisation de l'affectation des ressources
        * Rapports de charge et disponibilité

        Compatible avec :
        * eazynova_chantier
        * eazynova_intervention
        * project
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'eazynova',
        'eazynova_gestion_chantier',
        'eazynova_intervention',
        'project',
        'hr',
        'resource',
    ],
    'data': [
        'data/planning_cron.xml',
        # Sécurité
        'security/eazynova_planning_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/planning_sequence.xml',
        'data/planning_data.xml',

        # Vues
        'views/planning_task_views.xml',
        'views/planning_resource_views.xml',
        'views/planning_calendar_views.xml',
        'views/planning_assignment_views.xml',
        'views/planning_absence_views.xml',
        'views/planning_slot_views.xml',
        'views/eazynova_planning_menu.xml',

        # Wizards
        'wizard/planning_auto_assign_wizard_views.xml',
        'wizard/planning_conflict_wizard_views.xml',

        # Rapports
        'report/planning_reports.xml',
        'report/planning_resource_report_views.xml',
    ],
    'demo': [
        'demo/planning_demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
