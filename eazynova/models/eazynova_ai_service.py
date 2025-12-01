# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json

_logger = logging.getLogger(__name__)


class EazynovaAIService(models.AbstractModel):
    """Service IA abstrait pour les modules EAZYNOVA"""
    _name = 'eazynova.ai.service'
    _description = 'Service IA EAZYNOVA'

    @api.model
    def analyze_text(self, text, prompt=None, format='text'):
        """
        Analyse un texte avec l'IA

        :param text: Texte à analyser
        :param prompt: Prompt optionnel pour guider l'analyse
        :param format: Format de sortie ('text' ou 'json')
        :return: Résultat de l'analyse
        """
        try:
            # Vérifier si l'IA est activée
            ai_enabled = self.env['ir.config_parameter'].sudo().get_param(
                'eazynova.ai.enabled', 'False'
            )

            if ai_enabled != 'True':
                _logger.warning("Service IA désactivé")
                return self._get_fallback_response(text, format)

            # Récupérer le provider configuré
            provider = self.env['ir.config_parameter'].sudo().get_param(
                'eazynova.ai.provider', 'openai'
            )

            if provider == 'openai':
                return self._analyze_with_openai(text, prompt, format)
            elif provider == 'claude':
                return self._analyze_with_claude(text, prompt, format)
            else:
                _logger.warning(f"Provider IA inconnu: {provider}")
                return self._get_fallback_response(text, format)

        except Exception as e:
            _logger.error(f"Erreur dans analyze_text: {str(e)}")
            return self._get_fallback_response(text, format)

    def _analyze_with_openai(self, text, prompt, format):
        """Analyse avec OpenAI (stub pour l'instant)"""
        _logger.info("Appel OpenAI (stub)")
        return self._get_fallback_response(text, format)

    def _analyze_with_claude(self, text, prompt, format):
        """Analyse avec Claude (stub pour l'instant)"""
        _logger.info("Appel Claude (stub)")
        return self._get_fallback_response(text, format)

    def _get_fallback_response(self, text, format):
        """Réponse par défaut quand l'IA n'est pas disponible"""
        if format == 'json':
            return {
                'status': 'fallback',
                'message': 'Service IA non configuré',
                'text': text[:200]
            }
        else:
            return "Service IA non configuré. Veuillez configurer les clés API."

    @api.model
    def extract_data_from_document(self, file_data, file_type='pdf'):
        """
        Extrait des données d'un document avec OCR et IA

        :param file_data: Données du fichier (base64)
        :param file_type: Type de fichier ('pdf', 'image')
        :return: Données extraites
        """
        try:
            _logger.info(f"Extraction de données depuis {file_type}")

            # Pour l'instant, retourner une structure vide
            return {
                'status': 'pending',
                'message': 'Extraction OCR à implémenter',
                'data': {}
            }

        except Exception as e:
            _logger.error(f"Erreur extraction document: {str(e)}")
            raise UserError(_("Erreur lors de l'extraction: %s") % str(e))

    @api.model
    def get_ai_suggestion(self, context, options=None):
        """
        Obtient une suggestion de l'IA basée sur un contexte

        :param context: Contexte de la demande
        :param options: Options additionnelles
        :return: Suggestion de l'IA
        """
        try:
            _logger.info("Demande de suggestion IA")

            return {
                'suggestion': 'Service IA à configurer',
                'confidence': 0.0,
                'context': context
            }

        except Exception as e:
            _logger.error(f"Erreur get_ai_suggestion: {str(e)}")
            return {
                'suggestion': '',
                'confidence': 0.0,
                'error': str(e)
            }
