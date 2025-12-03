# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FunnelField(models.Model):
    _name = 'sales.funnel.field'
    _description = 'Champ de Formulaire'
    _order = 'step_id, sequence, id'

    name = fields.Char(
        string='Label',
        required=True
    )
    step_id = fields.Many2one(
        'sales.funnel.step',
        string='Étape',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    # Type de champ
    field_type = fields.Selection([
        ('text', 'Texte court'),
        ('textarea', 'Texte long'),
        ('email', 'Email'),
        ('phone', 'Téléphone'),
        ('number', 'Nombre'),
        ('date', 'Date'),
        ('select', 'Liste déroulante'),
        ('radio', 'Choix unique'),
        ('checkbox', 'Cases à cocher'),
        ('file', 'Fichier'),
        ('url', 'URL'),
        ('rating', 'Évaluation (étoiles)')
    ], string='Type', required=True, default='text')

    # Options
    required = fields.Boolean(
        string='Requis',
        default=True
    )
    placeholder = fields.Char(
        string='Placeholder',
        help="Texte d'exemple dans le champ"
    )
    help_text = fields.Char(
        string='Texte d\'aide',
        help="Texte d'aide affiché sous le champ"
    )
    default_value = fields.Char(
        string='Valeur par défaut'
    )

    # Pour les champs select, radio, checkbox
    option_values = fields.Text(
        string='Options',
        help="Une option par ligne (pour les listes déroulantes et choix multiples)"
    )

    # Validation
    validation_type = fields.Selection([
        ('none', 'Aucune'),
        ('email', 'Email valide'),
        ('phone', 'Téléphone valide'),
        ('url', 'URL valide'),
        ('number', 'Nombre'),
        ('regex', 'Expression régulière')
    ], string='Type de validation', default='none')
    validation_regex = fields.Char(
        string='Expression régulière',
        help="Pattern de validation personnalisé"
    )
    validation_message = fields.Char(
        string='Message d\'erreur',
        default='Valeur invalide'
    )

    # Mapping CRM
    crm_field = fields.Selection([
        ('', 'Aucun'),
        ('name', 'Nom du contact'),
        ('email', 'Email'),
        ('phone', 'Téléphone'),
        ('mobile', 'Mobile'),
        ('company_name', 'Nom de l\'entreprise'),
        ('website', 'Site web'),
        ('title', 'Fonction'),
        ('street', 'Adresse'),
        ('city', 'Ville'),
        ('zip', 'Code postal'),
        ('country', 'Pays'),
        ('lead_name', 'Nom de l\'opportunité'),
        ('lead_description', 'Description de l\'opportunité')
    ], string='Champ CRM', help="Mapper ce champ avec un champ CRM/Contact")

    # Conditions d'affichage
    conditional = fields.Boolean(
        string='Affichage conditionnel',
        default=False
    )
    condition_field_id = fields.Many2one(
        'sales.funnel.field',
        string='Dépend du champ',
        domain="[('step_id', '=', step_id)]"
    )
    condition_value = fields.Char(
        string='Valeur attendue'
    )

    @api.constrains('field_type', 'option_values')
    def _check_options(self):
        for record in self:
            if record.field_type in ['select', 'radio', 'checkbox']:
                if not record.option_values:
                    raise ValidationError(_(
                        "Les champs de type liste déroulante, choix unique ou cases à cocher nécessitent des options"
                    ))
