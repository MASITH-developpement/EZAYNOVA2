# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AIService(models.AbstractModel):
    _name = 'ai.service'
    _description = 'Service IA Principal'

    @api.model
    def generate_text(self, prompt, context=None, max_tokens=None, temperature=None):
        """
        Générer du texte avec l'IA

        Args:
            prompt (str): Le prompt à envoyer à l'IA
            context (dict): Contexte additionnel (optionnel)
            max_tokens (int): Nombre max de tokens (optionnel)
            temperature (float): Température de génération (optionnel)

        Returns:
            str: Le texte généré
        """
        config = self.env['ai.config'].get_active_config()
        text_gen = self.env['ai.text.generator']

        return text_gen.generate(
            prompt=prompt,
            context=context,
            max_tokens=max_tokens or config.max_tokens,
            temperature=temperature or config.temperature
        )

    @api.model
    def generate_image(self, prompt, style=None, size=None):
        """
        Générer une image avec l'IA

        Args:
            prompt (str): Description de l'image à générer
            style (str): Style de l'image (optionnel)
            size (str): Taille de l'image (optionnel)

        Returns:
            dict: {'url': str, 'binary': bytes, 'filename': str}
        """
        config = self.env['ai.config'].get_active_config()
        image_gen = self.env['ai.image.generator']

        return image_gen.generate(
            prompt=prompt,
            style=style,
            size=size or config.image_size,
            quality=config.image_quality
        )

    @api.model
    def generate_icon(self, prompt, style='minimalist'):
        """
        Générer une icône avec l'IA

        Args:
            prompt (str): Description de l'icône
            style (str): Style de l'icône

        Returns:
            dict: {'url': str, 'binary': bytes, 'filename': str}
        """
        # Enrichir le prompt pour les icônes
        icon_prompt = f"{prompt}, {style} icon, simple, flat design, transparent background, vector style"

        return self.generate_image(
            prompt=icon_prompt,
            style='icon',
            size='1024x1024'
        )

    @api.model
    def generate_audio(self, text, voice=None, speed=1.0):
        """
        Générer de l'audio avec l'IA

        Args:
            text (str): Texte à convertir en audio
            voice (str): Voix à utiliser (optionnel)
            speed (float): Vitesse de lecture

        Returns:
            dict: {'url': str, 'binary': bytes, 'filename': str, 'duration': float}
        """
        audio_gen = self.env['ai.audio.generator']

        return audio_gen.generate(
            text=text,
            voice=voice,
            speed=speed
        )

    @api.model
    def suggest_improvements(self, text, type='general'):
        """
        Suggérer des améliorations pour un texte

        Args:
            text (str): Le texte à améliorer
            type (str): Type de suggestion (general, seo, sales, etc.)

        Returns:
            dict: {
                'suggestions': [str],
                'improved_text': str,
                'score': int
            }
        """
        prompts = {
            'general': f"Améliore ce texte et donne 3 suggestions:\n\n{text}",
            'seo': f"Optimise ce texte pour le SEO et donne 3 suggestions:\n\n{text}",
            'sales': f"Optimise ce texte pour la conversion et donne 3 suggestions:\n\n{text}",
        }

        prompt = prompts.get(type, prompts['general'])
        result = self.generate_text(prompt)

        # Parser le résultat (simplifié ici)
        return {
            'suggestions': result.split('\n')[:3],
            'improved_text': result,
            'score': 85  # Score factice pour l'instant
        }

    @api.model
    def generate_questions(self, context, count=5):
        """
        Générer des questions pertinentes pour un formulaire

        Args:
            context (str): Contexte (ex: "rendez-vous médical")
            count (int): Nombre de questions à générer

        Returns:
            list: [{'question': str, 'type': str, 'required': bool}]
        """
        prompt = f"""
Génère {count} questions pertinentes pour un formulaire de {context}.

Format de réponse (JSON):
[
  {{"question": "Question 1", "type": "text", "required": true}},
  {{"question": "Question 2", "type": "select", "required": false}},
  ...
]

Types possibles: text, email, phone, select, checkbox, textarea
"""

        result = self.generate_text(prompt, max_tokens=1000)

        # Parser le JSON (à améliorer avec gestion d'erreurs)
        try:
            import json
            questions = json.loads(result)
            return questions
        except:
            _logger.error("Erreur lors du parsing des questions générées")
            return []

    @api.model
    def check_grammar(self, text):
        """
        Vérifier la grammaire et l'orthographe

        Args:
            text (str): Texte à vérifier

        Returns:
            dict: {
                'corrected_text': str,
                'errors': [{'original': str, 'correction': str, 'explanation': str}]
            }
        """
        prompt = f"Corrige la grammaire et l'orthographe de ce texte, et liste les erreurs:\n\n{text}"

        result = self.generate_text(prompt)

        return {
            'corrected_text': result,
            'errors': []  # À parser depuis le résultat
        }
