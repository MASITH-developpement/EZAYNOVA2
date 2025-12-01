# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChantierTache(models.Model):
    _name = 'chantier.tache'
    _description = 'Tâche de Chantier'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom de la tâche',
        required=True,
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
    )

    phase_id = fields.Many2one(
        'chantier.phase',
        string='Phase',
        required=True,
        ondelete='cascade',
    )

    chantier_id = fields.Many2one(
        related='phase_id.chantier_id',
        string='Chantier',
        store=True,
    )

    description = fields.Html(
        string='Description',
    )

    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
    )

    date_debut = fields.Date(
        string='Date de début',
    )

    date_fin = fields.Date(
        string='Date de fin',
    )

    duree_prevue = fields.Float(
        string='Durée prévue (heures)',
    )

    duree_reelle = fields.Float(
        string='Durée réelle (heures)',
    )

    state = fields.Selection([
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
    ], string='État', default='todo', tracking=True)

    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
    ], string='Priorité', default='1')

    color = fields.Integer(string='Couleur', default=0)
