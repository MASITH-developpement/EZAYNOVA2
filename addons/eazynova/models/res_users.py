# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Reconnaissance faciale
    eazynova_facial_encoding = fields.Binary(
        string="Encodage facial",
        help="Données d'encodage pour la reconnaissance faciale (RGPD: stockage sécurisé)"
    )

    eazynova_facial_consent = fields.Boolean(
        string="Consentement reconnaissance faciale",
        default=False,
        help="L'utilisateur a donné son consentement pour la reconnaissance faciale (RGPD)"
    )

    eazynova_facial_consent_date = fields.Datetime(
        string="Date de consentement",
        help="Date à laquelle l'utilisateur a donné son consentement"
    )

    # Préférences utilisateur
    eazynova_dashboard_layout = fields.Selection([
        ('default', 'Défaut'),
        ('compact', 'Compact'),
        ('detailed', 'Détaillé'),
    ], string="Mise en page tableau de bord", default='default')

    eazynova_notification_email = fields.Boolean(
        string="Notifications par email",
        default=True,
        help="Recevoir les notifications EAZYNOVA par email"
    )

    eazynova_notification_sms = fields.Boolean(
        string="Notifications par SMS",
        default=False,
        help="Recevoir les notifications EAZYNOVA par SMS"
    )

    # Statistiques
    eazynova_last_login = fields.Datetime(
        string="Dernière connexion EAZYNOVA",
        readonly=True
    )

    eazynova_login_count = fields.Integer(
        string="Nombre de connexions",
        default=0,
        readonly=True,
        help="Nombre total de connexions à l'interface EAZYNOVA"
    )
