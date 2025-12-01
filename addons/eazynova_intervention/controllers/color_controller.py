# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class InterventionColorController(http.Controller):
    """Contrôleur pour générer le CSS dynamique avec les couleurs personnalisées"""
    
    @http.route('/intervention/colors.css', type='http', auth='public', website=True)
    def intervention_colors_css(self):
        """Génère un fichier CSS avec les couleurs personnalisées depuis les paramètres"""
        
        # Récupérer les couleurs depuis les paramètres système
        ICP = request.env['ir.config_parameter'].sudo()
        
        primary = ICP.get_param('intervention.color_primary', '#0277bd')
        primary_light = ICP.get_param('intervention.color_primary_light', '#29b6f6')
        primary_dark = ICP.get_param('intervention.color_primary_dark', '#01579b')
        secondary = ICP.get_param('intervention.color_secondary', '#4caf50')
        accent = ICP.get_param('intervention.color_accent', '#ff9800')
        
        # Calculer les couleurs de fond basées sur la couleur principale
        # Pour bg-light: version très claire de primary
        # Pour bg-medium: version claire de primary
        # Pour bg-dark: version moyennement claire de primary
        
        # Conversion simple pour les fonds (on utilise des versions alpha)
        css_content = f"""
/* Couleurs dynamiques du module Intervention */
/* Généré automatiquement depuis les paramètres */

:root {{
    /* Couleurs principales */
    --intervention-primary: {primary};
    --intervention-primary-light: {primary_light};
    --intervention-primary-dark: {primary_dark};
    --intervention-secondary: {secondary};
    --intervention-accent: {accent};

    /* Couleurs de fond dérivées */
    --intervention-bg-light: {primary}08;     /* 3% opacité */
    --intervention-bg-medium: {primary}20;    /* 12% opacité */
    --intervention-bg-dark: {primary}40;      /* 25% opacité */

    /* Couleurs de statut */
    --intervention-success: {secondary};
    --intervention-warning: {accent};
    --intervention-danger: #f44336;
    --intervention-info: {primary};

    /* Autres */
    --intervention-border: #e0e0e0;
    --intervention-shadow: {primary}26;       /* 15% opacité pour les ombres */
    --intervention-radius: 8px;
    
    /* Alias pour compatibilité */
    --plomberie-primary: {primary};
    --plomberie-primary-light: {primary_light};
    --plomberie-primary-dark: {primary_dark};
    --plomberie-secondary: {secondary};
    --plomberie-success: {secondary};
    --plomberie-info: {primary};
    --plomberie-bg-light: {primary}08;
    --plomberie-bg-medium: {primary}20;
    --plomberie-bg-dark: {primary}40;
    --plomberie-border: #e0e0e0;
    --plomberie-shadow: {primary}26;
}}

/* Notification de changement de palette */
.o_notification.o_intervention_color_changed {{
    background: linear-gradient(135deg, {primary}, {primary_light}) !important;
    color: white !important;
    border-left: 4px solid {primary_dark} !important;
}}
"""
        
        return request.make_response(
            css_content,
            headers=[
                ('Content-Type', 'text/css'),
                ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                ('Pragma', 'no-cache'),
                ('Expires', '0'),
            ]
        )
