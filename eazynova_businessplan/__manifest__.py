# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Business Plan (Simplifié)',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Gestion simple de business plans avec indicateurs',
    'description': """
        Business Plan Complet
        =====================

        Module complet pour gérer vos business plans :
        * Créer un business plan (nom, dates, objectif financier)
        * Valider pour générer des indicateurs automatiquement
        * Suivre la progression de vos indicateurs
        * Tableaux financiers prévisionnels :
          - Plan de trésorerie (36 mois)
          - Plan de financement (sources et emplois)
          - Bilan prévisionnel (actif/passif)
          - Compte de résultat prévisionnel
        * Calculs automatiques des ratios financiers
        * Assistant de génération rapide
        * Interface simple et facile à utiliser
    """,
    'author': 'EAZYNOVA - S. MOREAU',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'Other proprietary',
    'maintainer': 'S. MOREAU',
    'depends': ['base', 'mail'],
    'data': [
        'security/businessplan_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/cron_data.xml',
        'report/businessplan_reports.xml',
        'views/business_plan_views.xml',
        'views/business_plan_indicator_views.xml',
        'views/business_plan_monthly_indicator_views.xml',
        'views/business_plan_ai_assistant_views.xml',
        'views/business_plan_cash_flow_views.xml',
        'views/business_plan_financing_views.xml',
        'views/business_plan_balance_sheet_views.xml',
        'views/business_plan_income_statement_views.xml',
        'views/businessplan_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
