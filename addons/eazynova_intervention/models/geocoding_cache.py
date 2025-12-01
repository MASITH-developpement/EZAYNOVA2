# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InterventionGeocodingCache(models.Model):
    _name = 'intervention.geocoding.cache'
    _description = 'Cache pour le géocodage des adresses'
    _rec_name = 'address'

    cache_key = fields.Char(string="Clé de cache", required=True, index=True)
    address = fields.Text(string="Adresse", required=True)
    latitude = fields.Float(string="Latitude", digits=(16, 6), required=True)
    longitude = fields.Float(string="Longitude", digits=(16, 6), required=True)
    created_at = fields.Datetime(string="Créé le", default=fields.Datetime.now)

    _sql_constraints = [
        ('cache_key_unique', 'UNIQUE(cache_key)',
         'La clé de cache doit être unique.'),
    ]

    @api.model
    def cleanup_old_cache(self):
        """Nettoyer les anciens enregistrements de cache (plus de 30 jours)"""
        from datetime import timedelta
        cutoff_date = fields.Datetime.now() - timedelta(days=30)
        old_records = self.search([('created_at', '<', cutoff_date)])
        old_records.unlink()
        return True
