# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import request


class TrustpilotWebhookController(http.Controller):

    @http.route('/trustpilot/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def trustpilot_webhook(self):
        payload = request.jsonrequest or {}
        data = payload.get('data') or payload

        ext_id = data.get('reviewId') or data.get('id')
        stars = str(data.get('stars') or data.get('rating') or '')
        text = data.get('text') or data.get('reviewText') or ''
        consumer = data.get('consumerName') or data.get('name') or ''

        Review = request.env['eazynova.customer.review'].sudo()

        existing = Review.search([('external_id', '=', ext_id)], limit=1)
        vals = {
            'name': 'Avis Trustpilot',
            'partner_id': False,
            'rating': stars if stars in ['1', '2', '3', '4', '5'] else '5',
            'review_text': text,
            'reviewer_name': consumer,
            'platform': 'trustpilot',
            'state': 'approved',
            'external_id': ext_id,
        }

        if existing:
            existing.write(vals)
            review = existing
        else:
            review = Review.create(vals)

        # Publication automatique selon configuration (désactivée en mode dev)
        config = request.env['eazynova.trust.config'].sudo().search([], limit=1)
        try:
            min_star = int((config.min_rating_publish or '3'))
        except Exception:
            min_star = 3
        if config and not config.trustpilot_dev_mode and int(review.rating) >= min_star and config.display_on_website:
            review.write({'state': 'published', 'publish_on_website': True})

        return {'status': 'ok', 'review_id': review.id}
