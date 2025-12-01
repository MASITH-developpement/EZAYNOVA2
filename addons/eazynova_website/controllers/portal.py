# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import logging

_logger = logging.getLogger(__name__)


class EazynovaPortalController(CustomerPortal):
    """Contrôleur du portail client pour gérer les abonnements SaaS"""

    def _prepare_home_portal_values(self, counters):
        """Ajouter le nombre d'abonnements au portail"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        if 'subscription_count' in counters:
            subscription_count = request.env['saas.subscription'].search_count([
                ('partner_id', '=', partner.id),
            ])
            values['subscription_count'] = subscription_count

        return values

    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_subscriptions(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """Liste des abonnements du client"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaasSubscription = request.env['saas.subscription']

        domain = [('partner_id', '=', partner.id)]

        # Recherche
        searchbar_sortings = {
            'date': {'label': _('Date de création'), 'order': 'create_date desc'},
            'name': {'label': _('Référence'), 'order': 'name'},
            'state': {'label': _('État'), 'order': 'state'},
        }

        # Tri par défaut
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Pagination
        subscription_count = SaasSubscription.search_count(domain)
        pager = portal_pager(
            url='/my/subscriptions',
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=subscription_count,
            page=page,
            step=self._items_per_page
        )

        # Récupération des abonnements
        subscriptions = SaasSubscription.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'subscriptions': subscriptions,
            'page_name': 'subscription',
            'pager': pager,
            'default_url': '/my/subscriptions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render('eazynova_website.portal_my_subscriptions', values)

    @http.route(['/my/subscriptions/<int:subscription_id>'], type='http', auth='user', website=True)
    def portal_subscription_detail(self, subscription_id, access_token=None, **kw):
        """Détail d'un abonnement"""
        try:
            subscription_sudo = self._document_check_access('saas.subscription', subscription_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'subscription': subscription_sudo,
            'page_name': 'subscription',
        }

        return request.render('eazynova_website.portal_subscription_detail', values)

    @http.route(['/my/subscriptions/<int:subscription_id>/activate'], type='http', auth='user', website=True)
    def portal_subscription_activate(self, subscription_id, **kw):
        """Activer un abonnement"""
        try:
            subscription_sudo = self._document_check_access('saas.subscription', subscription_id)

            if subscription_sudo.state in ['trial', 'expired']:
                subscription_sudo.action_activate()
                return request.redirect(f'/my/subscriptions/{subscription_id}?message=activated')
            else:
                return request.redirect(f'/my/subscriptions/{subscription_id}?error=invalid_state')

        except (AccessError, MissingError):
            return request.redirect('/my')

    @http.route(['/my/subscriptions/<int:subscription_id>/cancel'], type='http', auth='user', website=True)
    def portal_subscription_cancel(self, subscription_id, **kw):
        """Annuler un abonnement"""
        try:
            subscription_sudo = self._document_check_access('saas.subscription', subscription_id)

            if subscription_sudo.state in ['trial', 'active']:
                subscription_sudo.action_cancel()
                return request.redirect(f'/my/subscriptions/{subscription_id}?message=cancelled')
            else:
                return request.redirect(f'/my/subscriptions/{subscription_id}?error=invalid_state')

        except (AccessError, MissingError):
            return request.redirect('/my')

    @http.route(['/my/subscriptions/<int:subscription_id>/upgrade'], type='http', auth='user', website=True)
    def portal_subscription_upgrade(self, subscription_id, **kw):
        """Formulaire de mise à niveau de l'abonnement"""
        try:
            subscription_sudo = self._document_check_access('saas.subscription', subscription_id)

            values = {
                'subscription': subscription_sudo,
                'plans': request.env['saas.plan'].sudo().search([('active', '=', True)]),
            }

            return request.render('eazynova_website.portal_subscription_upgrade', values)

        except (AccessError, MissingError):
            return request.redirect('/my')

    @http.route(['/my/subscriptions/<int:subscription_id>/upgrade/submit'], type='http', auth='user', website=True, methods=['POST'])
    def portal_subscription_upgrade_submit(self, subscription_id, **post):
        """Traiter la mise à niveau"""
        try:
            subscription_sudo = self._document_check_access('saas.subscription', subscription_id)

            new_nb_users = int(post.get('nb_users', subscription_sudo.nb_users))

            if new_nb_users != subscription_sudo.nb_users:
                subscription_sudo.write({'nb_users': new_nb_users})
                # Mettre à jour l'instance
                if subscription_sudo.instance_id:
                    subscription_sudo.instance_id.write({'max_users': new_nb_users})

            return request.redirect(f'/my/subscriptions/{subscription_id}?message=upgraded')

        except (AccessError, MissingError):
            return request.redirect('/my')

    def _document_check_access(self, model_name, document_id, access_token=None):
        """Vérifier l'accès à un document"""
        document = request.env[model_name].browse(document_id)

        if not document.exists():
            raise MissingError(_("Ce document n'existe pas."))

        # Vérifier que le document appartient bien à l'utilisateur
        if document.partner_id != request.env.user.partner_id:
            raise AccessError(_("Vous n'avez pas accès à ce document."))

        return document.sudo()
