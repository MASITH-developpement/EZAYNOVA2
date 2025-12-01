# -*- coding: utf-8 -*-

from odoo import fields, models


class InterventionSettings(models.TransientModel):
    """Configuration des paramètres du module intervention"""
    
    _name = 'intervention.settings'
    _description = 'Paramètres Intervention'

    ors_api_key = fields.Char(
        string="Clé API OpenRouteService",
        help="Clé gratuite à obtenir sur https://openrouteservice.org/dev/#/signup "
             "(2 500 requêtes/jour). Copiez la clé ici pour activer le calcul "
             "de distance et durée par la route."
    )