# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EazynovaWebsiteController(http.Controller):
    """Contrôleur principal du site web EAZYNOVA SaaS"""

    @http.route('/', type='http', auth='public', website=True)
    def home(self, **kwargs):
        """Page d'accueil"""
        values = {
            'plans': request.env['saas.plan'].sudo().search([('active', '=', True)]),
        }
        return request.render('eazynova_website.homepage', values)

    @http.route('/saas/features', type='http', auth='public', website=True)
    def features(self, **kwargs):
        """Page des fonctionnalités"""
        values = {
            'features': request.env['saas.plan.feature'].sudo().search([]),
        }
        return request.render('eazynova_website.features', values)

    @http.route('/saas/pricing', type='http', auth='public', website=True)
    def pricing(self, **kwargs):
        """Page de tarification"""
        values = {
            'plans': request.env['saas.plan'].sudo().search([('active', '=', True)], order='sequence'),
        }
        return request.render('eazynova_website.pricing', values)

    @http.route('/saas/signup', type='http', auth='public', website=True)
    def signup(self, **kwargs):
        """Formulaire d'inscription"""
        values = {
            'plans': request.env['saas.plan'].sudo().search([('active', '=', True)], order='sequence'),
            'countries': request.env['res.country'].sudo().search([]),
        }
        return request.render('eazynova_website.signup', values)

    @http.route('/saas/signup/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def signup_submit(self, **post):
        """Traitement du formulaire d'inscription"""
        try:
            # Validation des données
            required_fields = ['company_name', 'contact_name', 'email', 'phone', 'plan_id', 'nb_users']
            for field in required_fields:
                if not post.get(field):
                    return request.render('eazynova_website.signup_error', {
                        'error': f'Le champ {field} est requis.',
                    })

            # Vérifier que l'email n'existe pas déjà
            existing_partner = request.env['res.partner'].sudo().search([
                ('email', '=', post.get('email'))
            ], limit=1)

            if existing_partner and existing_partner.saas_subscription_ids:
                return request.render('eazynova_website.signup_error', {
                    'error': 'Un compte existe déjà avec cette adresse email.',
                })

            # Créer ou mettre à jour le partenaire
            partner_values = {
                'name': post.get('company_name'),
                'contact_name': post.get('contact_name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
                'street': post.get('street'),
                'zip': post.get('zip'),
                'city': post.get('city'),
                'country_id': int(post.get('country_id')) if post.get('country_id') else False,
                'is_company': True,
            }

            if existing_partner:
                partner = existing_partner
                partner.sudo().write(partner_values)
            else:
                partner = request.env['res.partner'].sudo().create(partner_values)

            # Créer l'abonnement
            plan = request.env['saas.plan'].sudo().browse(int(post.get('plan_id')))
            nb_users = int(post.get('nb_users', 5))

            subscription = request.env['saas.subscription'].sudo().create({
                'partner_id': partner.id,
                'plan_id': plan.id,
                'nb_users': nb_users,
            })

            # Démarrer la période d'essai
            subscription.action_start_trial()

            # Rediriger vers la page de succès
            return request.redirect(f'/saas/signup/success/{subscription.id}')

        except Exception as e:
            _logger.error(f'Erreur lors de l\'inscription: {str(e)}')
            return request.render('eazynova_website.signup_error', {
                'error': 'Une erreur est survenue lors de l\'inscription. Veuillez réessayer ou nous contacter.',
            })

    @http.route('/saas/signup/success/<int:subscription_id>', type='http', auth='public', website=True)
    def signup_success(self, subscription_id, **kwargs):
        """Page de succès après inscription"""
        subscription = request.env['saas.subscription'].sudo().browse(subscription_id)

        if not subscription.exists():
            return request.redirect('/saas/signup')

        values = {
            'subscription': subscription,
        }
        return request.render('eazynova_website.signup_success', values)

    @http.route('/saas/calculate-price', type='json', auth='public', website=True)
    def calculate_price(self, plan_id, nb_users):
        """Calculer le prix pour un plan et un nombre d'utilisateurs (AJAX)"""
        plan = request.env['saas.plan'].sudo().browse(int(plan_id))

        if not plan.exists():
            return {'error': 'Plan non trouvé'}

        base_price = plan.monthly_price
        extra_users = max(0, int(nb_users) - plan.included_users)
        extra_price = extra_users * plan.extra_user_price
        total_monthly = base_price + extra_price

        return {
            'base_price': base_price,
            'extra_users': extra_users,
            'extra_price': extra_price,
            'total_monthly': total_monthly,
            'setup_fee': plan.setup_fee,
            'currency_symbol': '€',
        }
