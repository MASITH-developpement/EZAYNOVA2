# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChantierPhase(models.Model):
    _name = 'chantier.phase'
    _description = 'Phase de Chantier'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom de la phase',
        required=True,
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
    )

    chantier_id = fields.Many2one(
        'chantier.chantier',
        string='Chantier',
        required=True,
        ondelete='cascade',
    )

    description = fields.Html(
        string='Description',
    )

    date_debut = fields.Date(
        string='Date de début',
        required=True,
    )

    date_fin = fields.Date(
        string='Date de fin',
        required=True,
    )

    progress = fields.Float(
        string='Avancement (%)',
        default=0.0,
    )

    tache_ids = fields.One2many(
        'chantier.tache',
        'phase_id',
        string='Tâches',
    )

    state = fields.Selection([
        ('not_started', 'Non démarrée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
    ], string='État', default='not_started', tracking=True)

    color = fields.Integer(string='Couleur', default=0)
