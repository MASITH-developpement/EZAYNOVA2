# -*- coding: utf-8 -*-
{
    'name': 'Odoo Unlock - Module de déblocage',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Débloque les modules en attente',
    'description': """
        Module de maintenance pour débloquer les modules Odoo bloqués.

        Ce module :
        - Réinitialise les états des modules bloqués
        - Nettoie les verrous de module
        - Se désinstalle automatiquement après utilisation
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova.fr',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
