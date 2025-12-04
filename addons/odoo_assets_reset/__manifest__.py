# -*- coding: utf-8 -*-
{
    'name': 'Odoo Assets Reset',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Force la régénération des assets au démarrage',
    'description': """
        Module technique pour forcer la régénération complète des assets Odoo.
        Ce module vide les caches d'assets au démarrage pour résoudre les problèmes de compilation.
    """,
    'author': 'EAZYNOVA',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
