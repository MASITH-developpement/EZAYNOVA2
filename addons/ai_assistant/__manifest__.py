# -*- coding: utf-8 -*-
{
    'name': 'Assistant IA - Génération Multimédia',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Assistant IA pour génération de contenu, images, icônes et audio',
    'description': """
        Assistant IA - Génération Multimédia
        =====================================

        Module d'assistance IA intégré pour générer automatiquement :

        **Génération de contenu :**
        * Textes optimisés (descriptions, questions, pages d'accueil)
        * Suggestions intelligentes contextuelles
        * Réponses aux questions en temps réel

        **Génération d'images :**
        * Images personnalisées (bannières, illustrations)
        * Icônes sur mesure pour vos types de rendez-vous
        * Optimisation et redimensionnement automatique

        **Génération d'audio :**
        * Messages vocaux professionnels
        * Sons de notification personnalisés
        * Narration automatique

        **APIs supportées :**
        * Claude API (Anthropic) - Génération de texte
        * OpenAI GPT-4 - Génération de texte
        * DALL-E 3 - Génération d'images et icônes
        * Stable Diffusion - Alternative images
        * ElevenLabs - Génération audio haute qualité
        * OpenAI TTS - Text-to-Speech

        **Fonctionnalités :**
        * Configuration centralisée des API keys
        * Bibliothèque de médias générés
        * Historique et versioning
        * Cache intelligent pour économiser les crédits
        * Widgets réutilisables pour tous les modules
    """,
    'author': 'EAZYNOVA - S. MOREAU',
    'website': 'https://eazynova.fr',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'data': [
        # Sécurité
        'security/ir.model.access.csv',

        # Données
        'data/ai_prompt_templates.xml',

        # Vues
        'views/ai_config_views.xml',
        'views/ai_media_library_views.xml',
        'views/ai_assistant_menu.xml',

        # Wizards
        'wizard/ai_generate_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_assistant/static/src/css/ai_assistant.css',
            'ai_assistant/static/src/js/ai_assistant_widget.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
