# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AIMediaLibrary(models.Model):
    _name = 'ai.media.library'
    _description = 'Bibliothèque de Médias IA'
    _order = 'create_date desc'

    name = fields.Char(
        string='Nom',
        required=True
    )
    media_type = fields.Selection([
        ('text', 'Texte'),
        ('image', 'Image'),
        ('icon', 'Icône'),
        ('audio', 'Audio'),
    ], string='Type', required=True)

    # Prompt utilisé
    prompt = fields.Text(
        string='Prompt',
        help="Prompt utilisé pour générer ce média"
    )

    # Contenu généré
    text_content = fields.Html(
        string='Contenu texte'
    )
    media_file = fields.Binary(
        string='Fichier'
    )
    media_filename = fields.Char(
        string='Nom du fichier'
    )
    media_url = fields.Char(
        string='URL',
        help="URL originale si disponible"
    )

    # Métadonnées
    file_size = fields.Integer(
        string='Taille (bytes)',
        compute='_compute_file_size',
        store=True
    )
    mime_type = fields.Char(
        string='Type MIME'
    )
    duration = fields.Float(
        string='Durée (secondes)',
        help="Pour les fichiers audio"
    )

    # Utilisation
    usage_count = fields.Integer(
        string='Utilisé',
        default=0,
        help="Nombre de fois que ce média a été utilisé"
    )
    last_used_date = fields.Datetime(
        string='Dernière utilisation'
    )

    # Tags et catégorisation
    tag_ids = fields.Many2many(
        'ai.media.tag',
        string='Tags'
    )
    category = fields.Selection([
        ('booking', 'Rendez-vous'),
        ('funnel', 'Tunnel de vente'),
        ('email', 'Email'),
        ('website', 'Site web'),
        ('other', 'Autre'),
    ], string='Catégorie')

    # État
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    favorite = fields.Boolean(
        string='Favori',
        default=False
    )

    @api.depends('media_file')
    def _compute_file_size(self):
        for record in self:
            if record.media_file:
                import sys
                record.file_size = sys.getsizeof(record.media_file)
            else:
                record.file_size = 0

    def action_mark_as_used(self):
        """Marquer comme utilisé"""
        for record in self:
            record.usage_count += 1
            record.last_used_date = fields.Datetime.now()

    def action_toggle_favorite(self):
        """Basculer favori"""
        for record in self:
            record.favorite = not record.favorite


class AIMediaTag(models.Model):
    _name = 'ai.media.tag'
    _description = 'Tag de Média IA'

    name = fields.Char(
        string='Tag',
        required=True
    )
    color = fields.Integer(
        string='Couleur'
    )
