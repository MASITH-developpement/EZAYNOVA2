# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import json


class SalesFunnelController(http.Controller):

    @http.route('/funnel', type='http', auth='public', website=True)
    def funnel_list(self, **kwargs):
        """Liste des tunnels disponibles"""
        funnels = request.env['sales.funnel'].sudo().search([
            ('active', '=', True)
        ], order='sequence, name')

        return request.render('sales_funnel.funnel_list_page', {
            'funnels': funnels,
        })

    @http.route('/funnel/<int:funnel_id>', type='http', auth='public', website=True)
    def funnel_page(self, funnel_id, **kwargs):
        """Page du tunnel"""
        funnel = request.env['sales.funnel'].sudo().browse(funnel_id)

        if not funnel.exists() or not funnel.active:
            return request.render('website.404')

        # Vérifier l'authentification si nécessaire
        if funnel.require_authentication and not request.env.user._is_public():
            return request.redirect('/web/login?redirect=/funnel/%s' % funnel_id)

        # Incrémenter le compteur de vues
        funnel.sudo().write({'view_count': funnel.view_count + 1})

        # Créer une nouvelle soumission en brouillon
        submission = request.env['sales.funnel.submission'].sudo().create({
            'funnel_id': funnel.id,
            'ip_address': request.httprequest.remote_addr,
            'user_agent': request.httprequest.user_agent.string,
            'referrer': request.httprequest.referrer or '',
        })

        # Sauvegarder l'ID de soumission en session
        request.session['funnel_submission_id'] = submission.id

        return request.render('sales_funnel.funnel_page', {
            'funnel': funnel,
            'submission': submission,
        })

    @http.route('/funnel/<int:funnel_id>/submit', type='json', auth='public')
    def submit_funnel(self, funnel_id, values, **kwargs):
        """Soumettre le tunnel"""
        funnel = request.env['sales.funnel'].sudo().browse(funnel_id)

        if not funnel.exists():
            return {'error': 'Tunnel non trouvé'}

        # Récupérer la soumission en session
        submission_id = request.session.get('funnel_submission_id')
        if not submission_id:
            return {'error': 'Session expirée'}

        submission = request.env['sales.funnel.submission'].sudo().browse(submission_id)
        if not submission.exists():
            return {'error': 'Soumission non trouvée'}

        # Sauvegarder les valeurs
        for field_id, value in values.items():
            field = request.env['sales.funnel.field'].sudo().browse(int(field_id))
            if field.exists():
                request.env['sales.funnel.submission.value'].sudo().create({
                    'submission_id': submission.id,
                    'field_id': field.id,
                    'value': value,
                })

        # Soumettre
        submission.action_submit()

        # URL de remerciement
        if funnel.redirect_url:
            thank_you_url = funnel.redirect_url
        else:
            thank_you_url = f'/funnel/{funnel_id}/thank-you'

        return {
            'success': True,
            'submission_id': submission.id,
            'redirect_url': thank_you_url
        }

    @http.route('/funnel/<int:funnel_id>/thank-you', type='http', auth='public', website=True)
    def funnel_thank_you(self, funnel_id, **kwargs):
        """Page de remerciement"""
        funnel = request.env['sales.funnel'].sudo().browse(funnel_id)

        if not funnel.exists():
            return request.render('website.404')

        # Récupérer la soumission
        submission_id = request.session.get('funnel_submission_id')
        submission = False
        if submission_id:
            submission = request.env['sales.funnel.submission'].sudo().browse(submission_id)

        return request.render('sales_funnel.funnel_thank_you_page', {
            'funnel': funnel,
            'submission': submission,
        })

    @http.route('/funnel/<int:funnel_id>/validate', type='json', auth='public')
    def validate_field(self, funnel_id, field_id, value, **kwargs):
        """Valider un champ"""
        field = request.env['sales.funnel.field'].sudo().browse(field_id)

        if not field.exists():
            return {'valid': False, 'message': 'Champ non trouvé'}

        # Validation basique selon le type
        if field.required and not value:
            return {'valid': False, 'message': 'Ce champ est requis'}

        # Validation selon le type
        if field.validation_type == 'email':
            import re
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                return {'valid': False, 'message': field.validation_message}

        elif field.validation_type == 'phone':
            import re
            if not re.match(r'^[\d\s\+\-\(\)]{8,}$', value):
                return {'valid': False, 'message': field.validation_message}

        elif field.validation_type == 'url':
            import re
            if not re.match(r'^https?://[\w\.-]+\.\w+', value):
                return {'valid': False, 'message': field.validation_message}

        elif field.validation_type == 'regex' and field.validation_regex:
            import re
            if not re.match(field.validation_regex, value):
                return {'valid': False, 'message': field.validation_message}

        return {'valid': True}
