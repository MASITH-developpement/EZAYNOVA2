# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_latitude = fields.Float(
        string='Latitude',
        digits=(16, 6),
        help='Latitude GPS (précision 6 décimales)'
    )
    partner_longitude = fields.Float(
        string='Longitude',
        digits=(16, 6),
        help='Longitude GPS (précision 6 décimales)'
    )
    # Temporairement commenté pour éviter les erreurs de chargement
    # intervention_ids = fields.One2many(
    #     'intervention.intervention',
    #     'donneur_ordre_id',
    #     string="Interventions",
    #     help="Interventions pour ce client/donneur d'ordre"
    # )

    @api.model
    def create(self, vals_list):
        # Supporte la création en lot (batch)
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        for vals in vals_list:
            if self.env.context.get('from_intervention'):
                if not (self.env.user.has_group('eazynova_intervention.group_intervention_gestionnaire') or
                        self.env.user.has_group('eazynova_intervention.group_intervention_admin')):
                    raise AccessError(
                        "Seuls les gestionnaires et administrateurs peuvent "
                        "créer de nouveaux clients."
                    )
        return super().create(vals_list)
