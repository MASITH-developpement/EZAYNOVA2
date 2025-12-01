# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChantierDepense(models.Model):
    _name = 'chantier.depense'
    _description = 'Dépense de Chantier'
    _inherit = ['mail.thread']
    _order = 'date desc'

    chantier_id = fields.Many2one(
        'chantier.chantier',
        string='Chantier',
        required=True,
        ondelete='cascade',
    )

    name = fields.Char(
        string='Description',
        required=True,
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )

    type_depense = fields.Selection([
        ('materiel', 'Matériel'),
        ('main_oeuvre', 'Main d\'œuvre'),
        ('location', 'Location'),
        ('transport', 'Transport'),
        ('autre', 'Autre'),
    ], string='Type de dépense', required=True)

    montant = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='chantier_id.currency_id',
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Fournisseur',
    )

    facture_id = fields.Many2one(
        'account.move',
        string='Facture',
    )

    note = fields.Text(
        string='Notes',
    )
