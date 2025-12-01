# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChantierMateriel(models.Model):
    _name = 'chantier.materiel'
    _description = 'Matériel de Chantier'

    chantier_id = fields.Many2one(
        'chantier.chantier',
        string='Chantier',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Matériel/Équipement',
        required=True,
    )

    quantite = fields.Float(
        string='Quantité',
        default=1.0,
    )

    date_debut = fields.Date(
        string='Date de début',
        required=True,
    )

    date_fin = fields.Date(
        string='Date de fin',
    )

    cout_location = fields.Monetary(
        string='Coût de location',
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='chantier_id.currency_id',
    )

    note = fields.Text(
        string='Notes',
    )
