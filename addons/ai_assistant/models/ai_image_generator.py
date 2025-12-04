# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import logging
import requests
import base64

_logger = logging.getLogger(__name__)


class AIImageGenerator(models.AbstractModel):
    _name = 'ai.image.generator'
    _description = 'Générateur d\'Images IA'

    @api.model
    def generate(self, prompt, style=None, size='1024x1024', quality='hd'):
        """
        Générer une image avec DALL-E

        Args:
            prompt (str): Description de l'image
            style (str): Style de l'image
            size (str): Taille
            quality (str): Qualité

        Returns:
            dict: {'url': str, 'binary': bytes, 'filename': str}
        """
        config = self.env['ai.config'].get_active_config()

        if config.image_provider == 'dalle':
            return self._generate_with_dalle(prompt, style, size, quality, config)
        else:
            # Stable Diffusion à implémenter
            raise UserError(_("Stable Diffusion pas encore implémenté"))

    def _generate_with_dalle(self, prompt, style, size, quality, config):
        """Générer avec DALL-E 3"""
        if not config.openai_api_key:
            raise UserError(_("Clé API OpenAI manquante pour DALL-E"))

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }

        # Enrichir le prompt avec le style
        if style == 'icon':
            full_prompt = f"{prompt}, minimalist icon, flat design, simple shapes"
        elif style:
            full_prompt = f"{prompt}, {style} style"
        else:
            full_prompt = prompt

        payload = {
            "model": "dall-e-3",
            "prompt": full_prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "response_format": "url"  # Ou "b64_json" pour binary direct
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            data = response.json()
            image_url = data['data'][0]['url']

            # Télécharger l'image
            image_response = requests.get(image_url, timeout=30)
            image_binary = image_response.content

            # Générer un nom de fichier
            filename = f"ai_generated_{prompt[:30]}.png".replace(" ", "_")

            return {
                'url': image_url,
                'binary': image_binary,
                'filename': filename
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur API DALL-E: {str(e)}")
            raise UserError(_(
                "Erreur lors de la génération d'image: %s"
            ) % str(e))
