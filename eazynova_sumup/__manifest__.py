# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Paiements SumUp',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Intégration SumUp pour paiements par carte sur mobile',
    'description': """
        EAZYNOVA - Module Paiements SumUp
        =================================

        Intégration complète avec SumUp pour gérer les paiements par carte
        bancaire directement depuis Odoo sur mobile et desktop.

        **Fonctionnalités principales:**
        • Intégration API SumUp officielle
        • Paiement par carte depuis l'interface Odoo
        • Validation automatique des factures après paiement
        • Historique des transactions
        • Support mobile optimisé
        • Remboursements et annulations
        • Réconciliation automatique

        **Processus de paiement:**
        1. Sélection de la facture
        2. Lancement du paiement SumUp
        3. Traitement par terminal SumUp (physique ou app)
        4. Validation automatique de la facture
        5. Création du paiement dans Odoo
        6. Réconciliation comptable

        **Intégrations:**
        • Factures clients (account.move)
        • Commandes (sale.order)
        • Point de vente (POS) - optionnel
        • Comptabilité (automatic reconciliation)

        Compatible Odoo 19 Community Edition + SumUp API v0.1
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'sale_management',
        'payment',
        'eazynova',  # Module EAZYNOVA Core
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        # Sécurité
        'security/sumup_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/sumup_data.xml',

        # Vues
        'views/sumup_menu.xml',
        'views/sumup_config_views.xml',
        'views/sumup_transaction_views.xml',
        'views/account_move_views.xml',

        # Wizards
        'wizard/sumup_payment_wizard_views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
