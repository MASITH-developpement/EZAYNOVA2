# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InterventionMateriel(models.Model):
    _name = 'intervention.materiel'
    _description = 'Matériel utilisé dans les interventions'

    intervention_id = fields.Many2one(
        'intervention.intervention',
        string="Intervention",
        required=True,
        ondelete='cascade'
    )

    produit_id = fields.Many2one(
        'product.product',
        string="Produit",
        required=True
    )

    quantite = fields.Float(
        string="Quantité",
        required=True,
        default=1.0
    )

    prix_unitaire = fields.Float(
        string="Prix unitaire",
        related='produit_id.list_price',
        readonly=True
    )

    prix_total = fields.Float(
        string="Prix total",
        compute='_compute_prix_total',
        store=True
    )

    @api.depends('quantite', 'prix_unitaire')
    def _compute_prix_total(self):
        for record in self:
            record.prix_total = record.quantite * record.prix_unitaire
