# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AIGenerateWizard(models.TransientModel):
    _name = 'ai.generate.wizard'
    _description = 'Assistant de Génération IA'

    generation_type = fields.Selection([
        ('text', 'Texte'),
        ('image', 'Image'),
        ('icon', 'Icône'),
        ('audio', 'Audio'),
    ], string='Type de génération', required=True, default='text')

    prompt = fields.Text(
        string='Décrivez ce que vous voulez générer',
        required=True,
        help="Soyez aussi précis que possible"
    )

    # Options pour texte
    max_tokens = fields.Integer(
        string='Longueur maximum',
        default=500
    )

    # Options pour image
    image_style = fields.Selection([
        ('realistic', 'Réaliste'),
        ('illustration', 'Illustration'),
        ('minimalist', 'Minimaliste'),
        ('icon', 'Icône'),
    ], string='Style d\'image')

    # Résultat
    result_text = fields.Html(
        string='Texte généré',
        readonly=True
    )
    result_media = fields.Binary(
        string='Fichier généré',
        readonly=True
    )
    result_filename = fields.Char(
        string='Nom du fichier',
        readonly=True
    )

    def action_generate(self):
        """Générer le contenu"""
        self.ensure_one()

        ai_service = self.env['ai.service']

        if self.generation_type == 'text':
            result = ai_service.generate_text(
                self.prompt,
                max_tokens=self.max_tokens
            )
            self.result_text = result

            # Sauvegarder dans la bibliothèque
            self.env['ai.media.library'].create({
                'name': self.prompt[:50],
                'media_type': 'text',
                'prompt': self.prompt,
                'text_content': result,
            })

        elif self.generation_type in ['image', 'icon']:
            result = ai_service.generate_image(
                self.prompt,
                style=self.image_style
            )
            self.result_media = result['binary']
            self.result_filename = result['filename']

            # Sauvegarder dans la bibliothèque
            self.env['ai.media.library'].create({
                'name': self.prompt[:50],
                'media_type': self.generation_type,
                'prompt': self.prompt,
                'media_file': result['binary'],
                'media_filename': result['filename'],
                'media_url': result.get('url'),
                'mime_type': 'image/png',
            })

        elif self.generation_type == 'audio':
            result = ai_service.generate_audio(self.prompt)
            self.result_media = result['binary']
            self.result_filename = result['filename']

            # Sauvegarder dans la bibliothèque
            self.env['ai.media.library'].create({
                'name': self.prompt[:50],
                'media_type': 'audio',
                'prompt': self.prompt,
                'media_file': result['binary'],
                'media_filename': result['filename'],
                'mime_type': 'audio/mpeg',
                'duration': result.get('duration'),
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Génération réussie!'),
                'message': _('Le contenu a été généré et ajouté à votre bibliothèque.'),
                'type': 'success',
                'sticky': False,
            }
        }
