# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Paramètres spécifiques EAZYNOVA par société
    eazynova_enabled = fields.Boolean(
        string="Activer EAZYNOVA",
        default=True,
        help="Activer les fonctionnalités EAZYNOVA pour cette société"
    )

    eazynova_logo = fields.Binary(
        string="Logo EAZYNOVA",
        help="Logo personnalisé pour les rapports EAZYNOVA"
    )

    eazynova_color_primary = fields.Char(
        string="Couleur primaire",
        default="#1f77b4",
        help="Couleur primaire pour l'interface EAZYNOVA (format hex)"
    )

    eazynova_color_secondary = fields.Char(
        string="Couleur secondaire",
        default="#ff7f0e",
        help="Couleur secondaire pour l'interface EAZYNOVA (format hex)"
    )

    # Informations métier
    eazynova_industry_type = fields.Selection([
        ('construction', 'Construction / BTP'),
        ('services', 'Services'),
        ('commerce', 'Commerce'),
        ('industrie', 'Industrie'),
        ('other', 'Autre'),
    ], string="Type d'industrie", default='construction')

    eazynova_siret = fields.Char(
        string="SIRET",
        help="Numéro SIRET de l'entreprise"
    )

    eazynova_naf_code = fields.Char(
        string="Code NAF / APE",
        help="Code NAF ou APE de l'activité principale"
    )
