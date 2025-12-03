# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FunnelStep(models.Model):
    _name = 'sales.funnel.step'
    _description = 'Étape de Tunnel'
    _order = 'funnel_id, sequence, id'

    name = fields.Char(
        string='Nom',
        required=True
    )
    funnel_id = fields.Many2one(
        'sales.funnel',
        string='Tunnel',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10
    )
    description = fields.Html(
        string='Description',
        help="Texte affiché en haut de l'étape"
    )

    # Champs du formulaire
    field_ids = fields.One2many(
        'sales.funnel.field',
        'step_id',
        string='Champs',
        copy=True
    )

    # Navigation
    next_button_text = fields.Char(
        string='Texte du bouton suivant',
        default='Suivant'
    )
    previous_button_text = fields.Char(
        string='Texte du bouton précédent',
        default='Précédent'
    )
    show_previous_button = fields.Boolean(
        string='Afficher le bouton précédent',
        default=True
    )

    # Conditions
    conditional = fields.Boolean(
        string='Étape conditionnelle',
        default=False,
        help="Cette étape est affichée seulement si une condition est remplie"
    )
    condition_field_id = fields.Many2one(
        'sales.funnel.field',
        string='Champ condition',
        help="Champ dont dépend l'affichage de cette étape"
    )
    condition_operator = fields.Selection([
        ('equals', 'Égal à'),
        ('not_equals', 'Différent de'),
        ('contains', 'Contient'),
        ('greater', 'Supérieur à'),
        ('less', 'Inférieur à')
    ], string='Opérateur')
    condition_value = fields.Char(
        string='Valeur condition'
    )

    @api.constrains('field_ids')
    def _check_fields(self):
        for record in self:
            if not record.field_ids:
                raise ValidationError(_("Une étape doit avoir au moins un champ"))
