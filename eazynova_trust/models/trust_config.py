# -*- coding: utf-8 -*-

from odoo import models, fields


class TrustConfig(models.Model):
    """Configuration du module Trust"""
    _name = 'eazynova.trust.config'
    _description = 'Configuration Avis Clients'

    name = fields.Char(
        string='Configuration',
        default='Configuration Avis Clients',
        required=True
    )

    # Trustpilot
    trustpilot_enabled = fields.Boolean(
        string='Activer Trustpilot',
        default=False
    )

    trustpilot_dev_mode = fields.Boolean(
        string='Mode développement Trustpilot',
        default=True,
        help="Désactive la publication automatique et la vérification de signature pour les tests"
    )

    trustpilot_api_key = fields.Char(
        string='Clé API Trustpilot'
    )

    trustpilot_business_unit_id = fields.Char(
        string='Business Unit ID Trustpilot'
    )

    trustpilot_review_url = fields.Char(
        string='URL d\'avis Trustpilot',
        help='Lien vers la page d\'avis Trustpilot'
    )

    trustpilot_template_id = fields.Char(
        string='Template ID Trustpilot'
    )

    trustpilot_widget_token = fields.Char(
        string='Widget Token Trustpilot'
    )

    trustpilot_locale = fields.Char(
        string='Locale',
        default='fr-FR'
    )

    trustpilot_script_url = fields.Char(
        string='Script URL',
        default='//widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js'
    )

    # Google Reviews
    google_enabled = fields.Boolean(
        string='Activer Google Reviews',
        default=False
    )

    google_place_id = fields.Char(
        string='Google Place ID'
    )

    google_review_url = fields.Char(
        string='URL d\'avis Google'
    )

    # Paramètres généraux
    auto_send_after_invoice = fields.Boolean(
        string='Envoi automatique après facturation',
        default=True,
        help='Créer automatiquement une demande d\'avis après validation de facture'
    )

    days_after_invoice = fields.Integer(
        string='Jours après facturation',
        default=7,
        help='Nombre de jours à attendre après la facturation avant d\'envoyer la demande'
    )

    auto_reminder = fields.Boolean(
        string='Relances automatiques',
        default=True
    )

    days_before_reminder = fields.Integer(
        string='Jours avant relance',
        default=14
    )

    moderation_required = fields.Boolean(
        string='Modération requise',
        default=True,
        help='Les avis doivent être approuvés avant publication'
    )

    min_rating_publish = fields.Selection([
        ('1', '1 étoile et plus'),
        ('2', '2 étoiles et plus'),
        ('3', '3 étoiles et plus'),
        ('4', '4 étoiles et plus'),
        ('5', 'Uniquement 5 étoiles')
    ], string='Note minimale pour publication', default='3')

    display_on_website = fields.Boolean(
        string='Afficher les avis sur le site web',
        default=True
    )

    reviews_per_page = fields.Integer(
        string='Avis par page',
        default=10
    )
