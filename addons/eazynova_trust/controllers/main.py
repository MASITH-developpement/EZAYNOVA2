# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class TrustController(http.Controller):

    @http.route('/review/submit/<int:request_id>', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def submit_review(self, request_id, **kwargs):
        rr = request.env['eazynova.review.request'].sudo().browse(request_id)
        if not rr.exists():
            return request.redirect('/404')

        token = kwargs.get('token') or request.params.get('token')
        is_valid, reason = rr._check_token_valid(token)
        if not is_valid:
            return request.render('eazynova_trust.review_link_invalid', {
                'reason': reason,
            })

        if request.httprequest.method == 'POST':
            rating = request.params.get('rating')
            comment = request.params.get('review_text')
            name = request.params.get('reviewer_name') or rr.partner_id.name

            if rating not in ['1', '2', '3', '4', '5']:
                return request.render('eazynova_trust.review_submit_page', {
                    'review_request': rr,
                    'error': 'Veuillez choisir une note entre 1 et 5.'
                })

            Review = request.env['eazynova.customer.review'].sudo()
            new_review = Review.create({
                'name': 'Avis de ' + name,
                'partner_id': rr.partner_id.id,
                'request_id': rr.id,
                'rating': rating,
                'review_text': comment or '',
                'reviewer_name': name,
                'platform': 'internal',
                'state': 'pending',
                'publish_on_website': False,
            })

            rr.write({'state': 'completed', 'token_used': True, 'review_id': new_review.id})

            if rr.intervention_id:
                rr.intervention_id.write({'statut': 'termine', 'date_fin': request.env['ir.fields.converter'].get_datetime_from_string(fields.Datetime.now())})

            try:
                todo = request.env.ref('mail.mail_activity_data_todo')
                new_review.activity_schedule(activity_type_id=todo.id, summary='Valider et publier l\'avis', user_id=rr.user_id.id)
            except Exception:
                pass
            return request.render('eazynova_trust.review_thanks', {
                'review': new_review,
            })

        return request.render('eazynova_trust.review_submit_page', {
            'review_request': rr,
        })
