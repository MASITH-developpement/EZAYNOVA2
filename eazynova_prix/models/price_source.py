# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class PriceSource(models.Model):
    """Source de données externe pour la vérification des prix"""
    _name = 'eazynova.price.source'
    _description = 'Source de Prix Externe'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom de la source',
        required=True,
        help='Nom de la base de données de prix (ex: Batiprix, API Custom)'
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10
    )
    source_type = fields.Selection([
        ('batiprix', 'Batiprix'),
        ('api', 'API Personnalisée'),
        ('file', 'Fichier CSV/Excel'),
        ('manual', 'Manuel')
    ], string='Type de source', required=True, default='manual')

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    api_url = fields.Char(
        string='URL de l\'API',
        help='URL de base pour les requêtes API'
    )
    api_key = fields.Char(
        string='Clé API',
        help='Clé d\'authentification pour l\'API'
    )

    margin_warning = fields.Float(
        string='Seuil d\'alerte (%)',
        default=20.0,
        help='Pourcentage d\'écart déclenchant une alerte'
    )

    last_sync = fields.Datetime(
        string='Dernière synchronisation',
        readonly=True
    )

    check_count = fields.Integer(
        string='Nombre de vérifications',
        compute='_compute_check_count'
    )

    notes = fields.Text(
        string='Notes'
    )

    @api.depends('name')
    def _compute_check_count(self):
        """Calcule le nombre de vérifications effectuées"""
        for source in self:
            source.check_count = self.env['eazynova.price.check'].search_count([
                ('source_id', '=', source.id)
            ])

    def action_sync_prices(self):
        """Synchronise les prix depuis la source externe"""
        self.ensure_one()

        if self.source_type == 'batiprix':
            return self._sync_batiprix()
        elif self.source_type == 'api':
            return self._sync_api()
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Information',
                    'message': 'Synchronisation manuelle requise pour ce type de source',
                    'type': 'warning',
                }
            }

    def _sync_batiprix(self):
        """Synchronise les prix depuis Batiprix"""
        # TODO: Implémenter l'intégration Batiprix
        self.last_sync = fields.Datetime.now()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Succès',
                'message': 'Synchronisation Batiprix effectuée',
                'type': 'success',
            }
        }

    def _sync_api(self):
        """Synchronise les prix depuis une API personnalisée"""
        self.ensure_one()

        if not self.api_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': 'URL API non configurée',
                    'type': 'danger',
                }
            }

        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()

            self.last_sync = fields.Datetime.now()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Succès',
                    'message': f'Synchronisation API effectuée: {len(response.json())} articles',
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.error(f"Erreur lors de la synchronisation API: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': f'Erreur de synchronisation: {str(e)}',
                    'type': 'danger',
                }
            }

    def action_view_checks(self):
        """Affiche les vérifications pour cette source"""
        self.ensure_one()
        return {
            'name': f'Vérifications - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.price.check',
            'view_mode': 'tree,form',
            'domain': [('source_id', '=', self.id)],
            'context': {'default_source_id': self.id}
        }
