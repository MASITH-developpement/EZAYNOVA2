# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
import json

_logger = logging.getLogger(__name__)


class AIAssistantWizard(models.TransientModel):
    _name = 'eazynova.ai.assistant.wizard'
    _description = 'Assistant IA EAZYNOVA'

    name = fields.Char(string="Titre de la demande", required=True)
    prompt = fields.Text(string="Question / Demande", required=True)
    context_data = fields.Text(string="Contexte", help="Données contextuelles pour l'IA")

    # Résultat
    response = fields.Text(string="Réponse de l'IA", readonly=True)
    response_json = fields.Text(string="Réponse JSON", readonly=True)

    # Configuration
    ai_provider = fields.Selection([
        ('anthropic', 'Anthropic Claude'),
        ('openai', 'OpenAI GPT-4'),
    ], string="Fournisseur IA", default=lambda self: self._default_ai_provider())

    ai_model = fields.Char(
        string="Modèle",
        default=lambda self: self._default_ai_model()
    )

    temperature = fields.Float(
        string="Température",
        default=0.7,
        help="Créativité de l'IA (0.0-1.0)"
    )

    max_tokens = fields.Integer(
        string="Tokens maximum",
        default=4096,
        help="Nombre maximum de tokens dans la réponse"
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('processing', 'Traitement en cours'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ], string="État", default='draft', readonly=True)

    error_message = fields.Text(string="Message d'erreur", readonly=True)

    @api.model
    def _default_ai_provider(self):
        """Récupère le fournisseur IA par défaut"""
        return self.env['ir.config_parameter'].sudo().get_param('eazynova.ai_provider', 'anthropic')

    @api.model
    def _default_ai_model(self):
        """Récupère le modèle IA par défaut"""
        return self.env['ir.config_parameter'].sudo().get_param('eazynova.ai_model', 'claude-3-5-sonnet-20241022')

    def action_process(self):
        """Lance le traitement par l'IA"""
        self.ensure_one()

        # Vérifier la configuration
        api_key = self.env['ir.config_parameter'].sudo().get_param('eazynova.ai_api_key')
        if not api_key:
            raise UserError(_("Clé API IA non configurée. Veuillez configurer les paramètres EAZYNOVA."))

        self.state = 'processing'

        try:
            # Appel à l'IA (à implémenter avec les bibliothèques appropriées)
            if self.ai_provider == 'anthropic':
                response = self._call_anthropic_api(api_key)
            elif self.ai_provider == 'openai':
                response = self._call_openai_api(api_key)
            else:
                raise ValidationError(_("Fournisseur IA non supporté: %s") % self.ai_provider)

            self.response = response
            self.state = 'done'

        except Exception as e:
            _logger.error(f"Erreur lors de l'appel à l'IA: {str(e)}")
            self.error_message = str(e)
            self.state = 'error'
            raise UserError(_("Erreur lors de l'appel à l'IA: %s") % str(e))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.ai.assistant.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _call_anthropic_api(self, api_key):
        """Appelle l'API Anthropic Claude"""
        try:
            import anthropic
        except ImportError:
            raise UserError(_("Le module 'anthropic' n'est pas installé. Veuillez l'installer avec: pip install anthropic"))

        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Construire le prompt complet
            full_prompt = self.prompt
            if self.context_data:
                full_prompt = f"Contexte:\n{self.context_data}\n\nQuestion:\n{self.prompt}"

            message = client.messages.create(
                model=self.ai_model or "claude-3-5-sonnet-20241022",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            _logger.error(f"Erreur Anthropic API: {str(e)}")
            raise

    def _call_openai_api(self, api_key):
        """Appelle l'API OpenAI"""
        try:
            import openai
        except ImportError:
            raise UserError(_("Le module 'openai' n'est pas installé. Veuillez l'installer avec: pip install openai"))

        try:
            client = openai.OpenAI(api_key=api_key)

            # Construire le prompt complet
            full_prompt = self.prompt
            if self.context_data:
                full_prompt = f"Contexte:\n{self.context_data}\n\nQuestion:\n{self.prompt}"

            response = client.chat.completions.create(
                model=self.ai_model or "gpt-4",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return response.choices[0].message.content

        except Exception as e:
            _logger.error(f"Erreur OpenAI API: {str(e)}")
            raise

    def action_cancel(self):
        """Annule et ferme le wizard"""
        return {'type': 'ir.actions.act_window_close'}
