# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import logging
import requests
import json

_logger = logging.getLogger(__name__)


class AITextGenerator(models.AbstractModel):
    _name = 'ai.text.generator'
    _description = 'Générateur de Texte IA'

    @api.model
    def generate(self, prompt, context=None, max_tokens=2000, temperature=0.7):
        """
        Générer du texte avec Claude ou OpenAI

        Args:
            prompt (str): Le prompt
            context (dict): Contexte additionnel
            max_tokens (int): Tokens maximum
            temperature (float): Température

        Returns:
            str: Texte généré
        """
        config = self.env['ai.config'].get_active_config()

        if config.provider in ['claude', 'both']:
            return self._generate_with_claude(
                prompt, context, max_tokens, temperature, config
            )
        else:
            return self._generate_with_openai(
                prompt, context, max_tokens, temperature, config
            )

    def _generate_with_claude(self, prompt, context, max_tokens, temperature, config):
        """Générer avec Claude API"""
        if not config.claude_api_key:
            raise UserError(_("Clé API Claude manquante"))

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": config.claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Construire le message
        messages = []
        if context:
            messages.append({
                "role": "user",
                "content": f"Contexte: {json.dumps(context, ensure_ascii=False)}"
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": config.text_model or "claude-3-5-sonnet-20241022",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            data = response.json()
            return data['content'][0]['text']

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur API Claude: {str(e)}")
            raise UserError(_(
                "Erreur lors de la communication avec Claude API: %s"
            ) % str(e))

    def _generate_with_openai(self, prompt, context, max_tokens, temperature, config):
        """Générer avec OpenAI API"""
        if not config.openai_api_key:
            raise UserError(_("Clé API OpenAI manquante"))

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }

        # Construire les messages
        messages = [
            {"role": "system", "content": "Tu es un assistant IA utile et professionnel."}
        ]
        if context:
            messages.append({
                "role": "system",
                "content": f"Contexte: {json.dumps(context, ensure_ascii=False)}"
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": config.text_model or "gpt-4-turbo",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            data = response.json()
            return data['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur API OpenAI: {str(e)}")
            raise UserError(_(
                "Erreur lors de la communication avec OpenAI API: %s"
            ) % str(e))

    @api.model
    def generate_booking_description(self, booking_type_name, duration, target_audience=None):
        """Générer une description optimisée pour un type de rendez-vous"""
        prompt = f"""
Génère une description professionnelle et engageante pour un type de rendez-vous nommé "{booking_type_name}".

Durée: {duration} minutes
Public cible: {target_audience or 'général'}

La description doit:
- Être claire et concise (2-3 phrases)
- Expliquer le bénéfice pour le client
- Donner envie de réserver
- Être professionnelle mais chaleureuse

Réponds uniquement avec la description, sans introduction.
"""
        return self.generate(prompt, max_tokens=200)

    @api.model
    def generate_funnel_description(self, funnel_name, funnel_type, target_goal=None, target_audience=None):
        """Générer une description de tunnel de vente"""
        prompt = f"""
Crée une description professionnelle pour un tunnel de vente nommé "{funnel_name}".

Type de tunnel: {funnel_type}
{f"Objectif: {target_goal}" if target_goal else ""}
{f"Public cible: {target_audience}" if target_audience else ""}

La description doit:
- Expliquer clairement l'objectif du tunnel
- Être concise (2-3 phrases)
- Mettre en avant les bénéfices
- Être professionnelle et engageante

Réponds uniquement avec la description, sans introduction.
"""
        return self.generate(prompt, max_tokens=200)

    @api.model
    def generate_funnel_landing_page(self, funnel_name, funnel_type, target_goal):
        """Générer le contenu d'une page d'accueil de tunnel"""
        prompt = f"""
Crée le contenu HTML d'une page d'accueil pour un tunnel de vente nommé "{funnel_name}".

Type de tunnel: {funnel_type}
Objectif: {target_goal}

Inclus:
- Un titre accrocheur (h1)
- Un sous-titre explicatif (h2)
- 3 bullet points des bénéfices
- Un appel à l'action

Format: HTML simple, pas de balises <html>, <head> ou <body>.
Style: Professionnel, persuasif, orienté conversion.
"""
        return self.generate(prompt, max_tokens=500)

    @api.model
    def generate_email_template(self, email_type, context_data):
        """Générer un template d'email"""
        prompt = f"""
Génère un template d'email professionnel pour: {email_type}

Contexte: {json.dumps(context_data, ensure_ascii=False)}

Le template doit:
- Avoir un objet accrocheur
- Être personnalisé et chaleureux
- Inclure les informations importantes
- Se terminer par un CTA clair

Format: JSON avec les clés 'subject' et 'body'
"""
        result = self.generate(prompt, max_tokens=400)

        try:
            return json.loads(result)
        except:
            return {
                'subject': 'Email généré',
                'body': result
            }
