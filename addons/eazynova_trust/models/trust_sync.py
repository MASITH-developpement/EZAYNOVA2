# -*- coding: utf-8 -*-

import logging
import requests
from odoo import models

_logger = logging.getLogger(__name__)


class TrustSync(models.Model):
    _name = 'eazynova.trust.sync'
    _description = 'Synchronisation Trustpilot'

    def sync_trustpilot_reviews(self):
        Config = self.env['eazynova.trust.config'].sudo()
        config = Config.search([], limit=1)
        if not config or not config.trustpilot_enabled:
            return
        buid = config.trustpilot_business_unit_id
        api_key = config.trustpilot_api_key
        if not buid or not api_key:
            _logger.warning('Trustpilot non configuré (business_unit_id/api_key)')
            return

        url = f'https://api.trustpilot.com/v1/business-units/{buid}/reviews'
        try:
            resp = requests.get(url, params={'apikey': api_key, 'perPage': 50}, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            _logger.error('Erreur sync Trustpilot: %s', e)
            return

        data = resp.json() if resp.content else {}
        reviews = data.get('reviews') or []

        Review = self.env['eazynova.customer.review'].sudo()
        for r in reviews:
            ext_id = r.get('id')
            stars = str(r.get('stars') or '5')
            text = r.get('text') or ''
            consumer = (r.get('consumer') or {}).get('displayName') or ''
            vals = {
                'name': 'Avis Trustpilot',
                'partner_id': False,
                'rating': stars if stars in ['1','2','3','4','5'] else '5',
                'review_text': text,
                'reviewer_name': consumer,
                'platform': 'trustpilot',
                'state': 'approved',
                'external_id': ext_id,
            }
            existing = Review.search([('external_id', '=', ext_id)], limit=1)
            if existing:
                existing.write(vals)
                review = existing
            else:
                review = Review.create(vals)

            # Publication selon configuration
            try:
                min_star = int((config.min_rating_publish or '3'))
            except Exception:
                min_star = 3
            if config and not config.trustpilot_dev_mode and int(review.rating) >= min_star and config.display_on_website:
                review.write({'state': 'published', 'publish_on_website': True})
