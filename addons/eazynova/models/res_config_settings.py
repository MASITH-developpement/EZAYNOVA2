# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Fréquence de synchronisation du planning global
    eazynova_planning_sync_interval = fields.Integer(
        string="Fréquence de synchronisation du planning (heures)",
        config_parameter='eazynova.planning_sync_interval',
        default=24,
        help="Nombre d'heures entre chaque synchronisation automatique du planning global (interventions et chantiers)."
    )

    @api.model
    def set_values(self):
        res = super().set_values()
        # Mise à jour du cron de planning si le paramètre a changé
        self.env['eazynova.planning.assignment']._update_cron_interval()
        return res

    # Configuration IA
    eazynova_ai_assistance_enabled = fields.Boolean(
        string="Activer l'assistance IA",
        config_parameter='eazynova.ai_assistance_enabled',
        default=False,
        help="Activer l'intelligence artificielle pour l'analyse automatique"
    )

    eazynova_ai_provider = fields.Selection([
        ('anthropic', 'Anthropic Claude'),
        ('openai', 'OpenAI GPT-4'),
    ], string="Fournisseur IA", config_parameter='eazynova.ai_provider', default='anthropic')

    eazynova_ai_api_key = fields.Char(
        string="Clé API IA",
        config_parameter='eazynova.ai_api_key',
        help="Clé API pour le service d'intelligence artificielle"
    )

    eazynova_ai_model = fields.Char(
        string="Modèle IA",
        config_parameter='eazynova.ai_model',
        default='claude-3-5-sonnet-20241022',
        help="Nom du modèle IA à utiliser (ex: claude-3-5-sonnet-20241022 ou gpt-4)"
    )

    # Configuration OCR
    eazynova_ocr_enabled = fields.Boolean(
        string="Activer OCR",
        config_parameter='eazynova.ocr_enabled',
        default=True,
        help="Activer la reconnaissance optique de caractères pour les documents"
    )

    eazynova_ocr_language = fields.Selection([
        ('fra', 'Français'),
        ('eng', 'Anglais'),
        ('fra+eng', 'Français + Anglais'),
    ], string="Langue OCR", config_parameter='eazynova.ocr_language', default='fra+eng')

    eazynova_ocr_confidence_threshold = fields.Float(
        string="Seuil de confiance OCR (%)",
        config_parameter='eazynova.ocr_confidence_threshold',
        default=80.0,
        help="Seuil minimum de confiance pour l'OCR (0-100)"
    )

    # Paramètres généraux
    eazynova_auto_backup = fields.Boolean(
        string="Sauvegarde automatique",
        config_parameter='eazynova.auto_backup',
        default=True,
        help="Activer les sauvegardes automatiques quotidiennes"
    )

    eazynova_debug_mode = fields.Boolean(
        string="Mode debug",
        config_parameter='eazynova.debug_mode',
        default=False,
        help="Activer les logs détaillés pour le débogage"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        res.update({
            'eazynova_ai_assistance_enabled': params.get_param('eazynova.ai_assistance_enabled', False),
            'eazynova_ai_provider': params.get_param('eazynova.ai_provider', 'anthropic'),
            'eazynova_ai_api_key': params.get_param('eazynova.ai_api_key', ''),
            'eazynova_ai_model': params.get_param('eazynova.ai_model', 'claude-3-5-sonnet-20241022'),
            'eazynova_ocr_enabled': params.get_param('eazynova.ocr_enabled', True),
            'eazynova_ocr_language': params.get_param('eazynova.ocr_language', 'fra+eng'),
            'eazynova_ocr_confidence_threshold': float(params.get_param('eazynova.ocr_confidence_threshold', 80.0)),
            'eazynova_auto_backup': params.get_param('eazynova.auto_backup', True),
            'eazynova_debug_mode': params.get_param('eazynova.debug_mode', False),
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()

        params.set_param('eazynova.ai_assistance_enabled', self.eazynova_ai_assistance_enabled)
        params.set_param('eazynova.ai_provider', self.eazynova_ai_provider)
        params.set_param('eazynova.ai_api_key', self.eazynova_ai_api_key or '')
        params.set_param('eazynova.ai_model', self.eazynova_ai_model)
        params.set_param('eazynova.ocr_enabled', self.eazynova_ocr_enabled)
        params.set_param('eazynova.ocr_language', self.eazynova_ocr_language)
        params.set_param('eazynova.ocr_confidence_threshold', self.eazynova_ocr_confidence_threshold)
        params.set_param('eazynova.auto_backup', self.eazynova_auto_backup)
        params.set_param('eazynova.debug_mode', self.eazynova_debug_mode)
