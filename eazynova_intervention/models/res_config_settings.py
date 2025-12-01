# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_intervention = fields.Boolean(string="Module Interventions", default=True)
    
    # ===== CONFIGURATION DES COULEURS =====
    
    intervention_color_palette = fields.Selection([
        ('blue_professional', 'Bleu Professionnel'),
        ('green_energy', 'Vert Énergie'),
        ('red_dynamic', 'Rouge Dynamique'),
        ('purple_modern', 'Violet Moderne'),
        ('orange_plumbing', 'Orange Plomberie'),
        ('grey_elegant', 'Gris Élégant'),
        ('custom', 'Personnalisée'),
    ], string="Palette de couleurs", 
       default='blue_professional',
       config_parameter='intervention.color_palette',
       help="Choisissez une palette de couleurs prédéfinie ou créez la vôtre")
    
    # Couleurs personnalisées (visibles si palette = custom)
    intervention_color_primary = fields.Char(
        string="Couleur principale",
        config_parameter='intervention.color_primary',
        default='#0277bd',
        help="Couleur principale du module (format: #RRGGBB)"
    )
    
    intervention_color_primary_light = fields.Char(
        string="Couleur principale (claire)",
        config_parameter='intervention.color_primary_light',
        default='#29b6f6',
        help="Variante claire de la couleur principale"
    )
    
    intervention_color_primary_dark = fields.Char(
        string="Couleur principale (foncée)",
        config_parameter='intervention.color_primary_dark',
        default='#01579b',
        help="Variante foncée de la couleur principale"
    )
    
    intervention_color_secondary = fields.Char(
        string="Couleur secondaire",
        config_parameter='intervention.color_secondary',
        default='#4caf50',
        help="Couleur secondaire pour les accents"
    )
    
    intervention_color_accent = fields.Char(
        string="Couleur d'accent",
        config_parameter='intervention.color_accent',
        default='#ff9800',
        help="Couleur d'accent pour les éléments importants"
    )

    # Configuration API OpenRouteService
    openroute_api_key = fields.Char(
        string="Clé API OpenRouteService",
        config_parameter='intervention.openroute_api_key',
        help="Clé API gratuite pour le calcul précis des distances via OpenRouteService"
    )
    
    # Coordonnées de l'entreprise
    company_latitude = fields.Float(
        string="Latitude entreprise",
        config_parameter='intervention.company_latitude',
        help="Latitude du point de départ des interventions (siège de l'entreprise)"
    )
    
    company_longitude = fields.Float(
        string="Longitude entreprise", 
        config_parameter='intervention.company_longitude',
        help="Longitude du point de départ des interventions (siège de l'entreprise)"
    )
    
    # Durée par défaut des interventions
    duree_intervention_defaut = fields.Float(
        string="Durée intervention par défaut (heures)",
        config_parameter='intervention.duree_intervention_defaut',
        default=1.0,
        help="Durée par défaut en heures pour les nouvelles interventions"
    )

    @api.model
    def get_values(self):
        """Récupérer les valeurs de configuration"""
        res = super(ResConfigSettings, self).get_values()
        
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        res.update(
            openroute_api_key=ICPSudo.get_param('intervention.openroute_api_key', ''),
            company_latitude=float(ICPSudo.get_param('intervention.company_latitude', 0.0)),
            company_longitude=float(ICPSudo.get_param('intervention.company_longitude', 0.0)),
            duree_intervention_defaut=float(ICPSudo.get_param('intervention.duree_intervention_defaut', 1.0)),
            intervention_color_palette=ICPSudo.get_param('intervention.color_palette', 'blue_professional'),
            intervention_color_primary=ICPSudo.get_param('intervention.color_primary', '#0277bd'),
            intervention_color_primary_light=ICPSudo.get_param('intervention.color_primary_light', '#29b6f6'),
            intervention_color_primary_dark=ICPSudo.get_param('intervention.color_primary_dark', '#01579b'),
            intervention_color_secondary=ICPSudo.get_param('intervention.color_secondary', '#4caf50'),
            intervention_color_accent=ICPSudo.get_param('intervention.color_accent', '#ff9800'),
        )
        
        return res

    def set_values(self):
        """Sauvegarder les valeurs de configuration"""
        super(ResConfigSettings, self).set_values()
        
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        ICPSudo.set_param('intervention.openroute_api_key', self.openroute_api_key or '')
        ICPSudo.set_param('intervention.company_latitude', self.company_latitude or 0.0)
        ICPSudo.set_param('intervention.company_longitude', self.company_longitude or 0.0)
        ICPSudo.set_param('intervention.duree_intervention_defaut', self.duree_intervention_defaut or 1.0)
        ICPSudo.set_param('intervention.color_palette', self.intervention_color_palette or 'blue_professional')
        
        # Si une palette prédéfinie est sélectionnée, appliquer les couleurs
        if self.intervention_color_palette != 'custom':
            colors = self._get_palette_colors(self.intervention_color_palette)
            ICPSudo.set_param('intervention.color_primary', colors['primary'])
            ICPSudo.set_param('intervention.color_primary_light', colors['primary_light'])
            ICPSudo.set_param('intervention.color_primary_dark', colors['primary_dark'])
            ICPSudo.set_param('intervention.color_secondary', colors['secondary'])
            ICPSudo.set_param('intervention.color_accent', colors['accent'])
        else:
            # Palette personnalisée : sauvegarder les couleurs saisies
            ICPSudo.set_param('intervention.color_primary', self.intervention_color_primary or '#0277bd')
            ICPSudo.set_param('intervention.color_primary_light', self.intervention_color_primary_light or '#29b6f6')
            ICPSudo.set_param('intervention.color_primary_dark', self.intervention_color_primary_dark or '#01579b')
            ICPSudo.set_param('intervention.color_secondary', self.intervention_color_secondary or '#4caf50')
            ICPSudo.set_param('intervention.color_accent', self.intervention_color_accent or '#ff9800')
        
        # Message de confirmation avec invitation à recharger la page
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Configuration enregistrée',
                'message': 'Les couleurs ont été mises à jour. Veuillez recharger la page (F5) pour voir les changements.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
    
    @api.model
    def _get_palette_colors(self, palette):
        """Retourne les couleurs d'une palette prédéfinie"""
        palettes = {
            'blue_professional': {
                'primary': '#0277bd',
                'primary_light': '#29b6f6',
                'primary_dark': '#01579b',
                'secondary': '#4caf50',
                'accent': '#ff9800',
            },
            'green_energy': {
                'primary': '#2e7d32',
                'primary_light': '#66bb6a',
                'primary_dark': '#1b5e20',
                'secondary': '#8bc34a',
                'accent': '#ff9800',
            },
            'red_dynamic': {
                'primary': '#d32f2f',
                'primary_light': '#ef5350',
                'primary_dark': '#c62828',
                'secondary': '#ff5722',
                'accent': '#ffc107',
            },
            'purple_modern': {
                'primary': '#7b1fa2',
                'primary_light': '#9c27b0',
                'primary_dark': '#6a1b9a',
                'secondary': '#ab47bc',
                'accent': '#ff9800',
            },
            'orange_plumbing': {
                'primary': '#f57c00',
                'primary_light': '#ff9800',
                'primary_dark': '#e65100',
                'secondary': '#ff5722',
                'accent': '#4caf50',
            },
            'grey_elegant': {
                'primary': '#546e7a',
                'primary_light': '#78909c',
                'primary_dark': '#455a64',
                'secondary': '#90a4ae',
                'accent': '#ff9800',
            },
        }
        return palettes.get(palette, palettes['blue_professional'])
