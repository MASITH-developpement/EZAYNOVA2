# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChantierEquipe(models.Model):
    _name = 'chantier.equipe'
    _description = 'Équipe de Chantier'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Nom de l\'équipe',
        required=True,
    )

    chef_equipe_id = fields.Many2one(
        'res.users',
        string='Chef d\'équipe',
        required=True,
    )

    member_ids = fields.Many2many(
        'res.users',
        'chantier_equipe_member_rel',
        'equipe_id',
        'user_id',
        string='Membres',
    )

    specialite = fields.Selection([
        ('gros_oeuvre', 'Gros œuvre'),
        ('second_oeuvre', 'Second œuvre'),
        ('electricite', 'Électricité'),
        ('plomberie', 'Plomberie'),
        ('chauffage', 'Chauffage'),
        ('menuiserie', 'Menuiserie'),
        ('peinture', 'Peinture'),
        ('autre', 'Autre'),
    ], string='Spécialité')

    active = fields.Boolean(
        string='Actif',
        default=True,
    )

    note = fields.Text(
        string='Notes',
    )
