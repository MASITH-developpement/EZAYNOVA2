# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AIConfig(models.Model):
    _name = 'ai.config'
    _description = 'Configuration Assistant IA'
    _rec_name = 'provider'

    # Fournisseur IA actif
    provider = fields.Selection([
        ('claude', 'Claude (Anthropic)'),
        ('openai', 'OpenAI GPT-4'),
        ('both', 'Les deux')
    ], string='Fournisseur de texte', default='claude', required=True)

    # API Keys pour génération de texte
    claude_api_key = fields.Char(
        string='Clé API Claude',
        help="Clé API Anthropic Claude pour génération de texte"
    )
    openai_api_key = fields.Char(
        string='Clé API OpenAI',
        help="Clé API OpenAI pour génération de texte et images"
    )

    # API Keys pour génération d'images
    image_provider = fields.Selection([
        ('dalle', 'DALL-E 3 (OpenAI)'),
        ('stable_diffusion', 'Stable Diffusion'),
    ], string='Fournisseur d\'images', default='dalle')

    stable_diffusion_api_key = fields.Char(
        string='Clé API Stable Diffusion',
        help="Clé API pour Stable Diffusion (optionnel)"
    )

    # API Keys pour génération d'audio
    audio_provider = fields.Selection([
        ('elevenlabs', 'ElevenLabs'),
        ('openai_tts', 'OpenAI TTS'),
    ], string='Fournisseur d\'audio', default='elevenlabs')

    elevenlabs_api_key = fields.Char(
        string='Clé API ElevenLabs',
        help="Clé API ElevenLabs pour génération audio haute qualité"
    )

    # Paramètres de génération
    text_model = fields.Selection([
        ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet (Recommandé)'),
        ('claude-3-opus-20240229', 'Claude 3 Opus (Plus puissant)'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-4o', 'GPT-4o'),
    ], string='Modèle de texte', default='claude-3-5-sonnet-20241022')

    image_quality = fields.Selection([
        ('standard', 'Standard'),
        ('hd', 'Haute Définition'),
    ], string='Qualité images', default='hd')

    image_size = fields.Selection([
        ('1024x1024', '1024x1024 (Carré)'),
        ('1792x1024', '1792x1024 (Paysage)'),
        ('1024x1792', '1024x1792 (Portrait)'),
    ], string='Taille images', default='1024x1024')

    # Options
    enable_cache = fields.Boolean(
        string='Activer le cache',
        default=True,
        help="Mettre en cache les résultats pour économiser les crédits API"
    )
    cache_duration = fields.Integer(
        string='Durée du cache (jours)',
        default=30
    )

    max_tokens = fields.Integer(
        string='Tokens maximum',
        default=2000,
        help="Nombre maximum de tokens pour les réponses texte"
    )

    temperature = fields.Float(
        string='Température',
        default=0.7,
        help="Créativité de l'IA (0 = précis, 1 = créatif)"
    )

    # État et tests
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    last_test_date = fields.Datetime(
        string='Dernier test',
        readonly=True
    )
    last_test_result = fields.Text(
        string='Résultat du test',
        readonly=True
    )

    @api.constrains('claude_api_key', 'openai_api_key')
    def _check_api_keys(self):
        """Vérifier qu'au moins une clé API est configurée"""
        for record in self:
            if record.provider == 'claude' and not record.claude_api_key:
                raise ValidationError(_("Veuillez configurer la clé API Claude"))
            elif record.provider == 'openai' and not record.openai_api_key:
                raise ValidationError(_("Veuillez configurer la clé API OpenAI"))

    def action_test_connection(self):
        """Tester la connexion aux APIs"""
        self.ensure_one()
        try:
            # Test API de texte
            ai_service = self.env['ai.service']
            test_prompt = "Dites 'OK' si vous me recevez."

            result = ai_service.generate_text(test_prompt, max_tokens=10)

            self.last_test_date = fields.Datetime.now()
            self.last_test_result = f"✓ Test réussi!\nRéponse: {result}"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test réussi!'),
                    'message': _('La connexion à l\'API fonctionne correctement.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.last_test_date = fields.Datetime.now()
            self.last_test_result = f"✗ Erreur: {str(e)}"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test échoué'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.model
    def get_active_config(self):
        """Récupérer la configuration active"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError(_(
                "Aucune configuration IA active. "
                "Veuillez configurer l'assistant IA dans Paramètres > Assistant IA."
            ))
        return config
