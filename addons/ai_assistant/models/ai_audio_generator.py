# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import logging
import requests

_logger = logging.getLogger(__name__)


class AIAudioGenerator(models.AbstractModel):
    _name = 'ai.audio.generator'
    _description = 'Générateur d\'Audio IA'

    @api.model
    def generate(self, text, voice=None, speed=1.0):
        """
        Générer de l'audio avec ElevenLabs ou OpenAI TTS

        Args:
            text (str): Texte à convertir
            voice (str): Voix à utiliser
            speed (float): Vitesse

        Returns:
            dict: {'url': str, 'binary': bytes, 'filename': str, 'duration': float}
        """
        config = self.env['ai.config'].get_active_config()

        if config.audio_provider == 'elevenlabs':
            return self._generate_with_elevenlabs(text, voice, speed, config)
        else:
            return self._generate_with_openai_tts(text, voice, speed, config)

    def _generate_with_elevenlabs(self, text, voice, speed, config):
        """Générer avec ElevenLabs"""
        if not config.elevenlabs_api_key:
            raise UserError(_("Clé API ElevenLabs manquante"))

        # Voice ID par défaut (voix professionnelle)
        voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": config.elevenlabs_api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            audio_binary = response.content
            filename = f"ai_audio_{text[:30]}.mp3".replace(" ", "_")

            return {
                'url': None,  # ElevenLabs retourne direct le binary
                'binary': audio_binary,
                'filename': filename,
                'duration': len(text) / 15  # Estimation: ~15 caractères/seconde
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur API ElevenLabs: {str(e)}")
            raise UserError(_(
                "Erreur lors de la génération audio: %s"
            ) % str(e))

    def _generate_with_openai_tts(self, text, voice, speed, config):
        """Générer avec OpenAI TTS"""
        if not config.openai_api_key:
            raise UserError(_("Clé API OpenAI manquante"))

        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "tts-1-hd",
            "input": text,
            "voice": voice or "alloy",  # alloy, echo, fable, onyx, nova, shimmer
            "speed": speed
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            audio_binary = response.content
            filename = f"ai_audio_{text[:30]}.mp3".replace(" ", "_")

            return {
                'url': None,
                'binary': audio_binary,
                'filename': filename,
                'duration': len(text) / 15
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur API OpenAI TTS: {str(e)}")
            raise UserError(_(
                "Erreur lors de la génération audio: %s"
            ) % str(e))
