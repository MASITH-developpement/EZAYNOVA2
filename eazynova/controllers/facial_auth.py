# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.exceptions import AccessDenied
import logging
import json

_logger = logging.getLogger(__name__)


class FacialAuthController(http.Controller):
    """Controller pour l'authentification faciale"""

    @http.route('/web/facial_login', type='http', auth='public', website=True, sitemap=False)
    def facial_login_page(self, **kwargs):
        """Page de connexion par reconnaissance faciale"""
        if request.session.uid:
            return request.redirect('/web')

        # Vérifier si la reconnaissance faciale est disponible
        try:
            facial_service = request.env['eazynova.facial.service'].sudo()
            availability = facial_service.check_library_availability()
            facial_available = availability.get('available', False)
        except Exception as e:
            _logger.error(f"Erreur vérification disponibilité faciale: {e}")
            facial_available = False

        values = {
            'facial_available': facial_available,
            'error': kwargs.get('error'),
            'database': request.db,
        }

        return request.render('eazynova.facial_login_page', values)

    @http.route('/web/facial_auth/identify', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def facial_identify(self, photo_data, **kwargs):
        """
        Identifie un utilisateur à partir d'une photo

        :param photo_data: Image encodée en base64
        :return: Dict avec résultat de l'identification
        """
        try:
            if not photo_data:
                return {
                    'success': False,
                    'error': _('Aucune photo fournie')
                }

            # Utiliser le service de reconnaissance faciale
            facial_service = request.env['eazynova.facial.service'].sudo()
            result = facial_service.identify_user(photo_data)

            if not result.get('success'):
                return {
                    'success': False,
                    'error': result.get('error', _('Aucun utilisateur correspondant'))
                }

            user_id = result.get('user_id')
            confidence = result.get('confidence', 0)

            # Vérifier le seuil de confiance minimum (70%)
            if confidence < 70:
                return {
                    'success': False,
                    'error': _('Confiance insuffisante (%.1f%%). Réessayez avec un meilleur éclairage.') % confidence
                }

            # Récupérer l'utilisateur
            user = request.env['res.users'].sudo().browse(user_id)
            if not user or not user.exists():
                return {
                    'success': False,
                    'error': _('Utilisateur non trouvé')
                }

            # Vérifier que l'utilisateur est actif
            if not user.active:
                return {
                    'success': False,
                    'error': _('Utilisateur désactivé')
                }

            _logger.info(
                f"Identification faciale réussie pour {user.login} "
                f"(confiance: {confidence:.1f}%)"
            )

            return {
                'success': True,
                'user_id': user_id,
                'user_login': user.login,
                'user_name': user.name,
                'confidence': confidence,
            }

        except Exception as e:
            _logger.exception("Erreur lors de l'identification faciale")
            return {
                'success': False,
                'error': _('Erreur lors de l\'identification: %s') % str(e)
            }

    @http.route('/web/facial_auth/login', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def facial_login(self, photo_data, **kwargs):
        """
        Authentifie un utilisateur via reconnaissance faciale

        :param photo_data: Image encodée en base64
        :return: Dict avec résultat de l'authentification
        """
        try:
            # Première étape: identifier l'utilisateur
            identify_result = self.facial_identify(photo_data)

            if not identify_result.get('success'):
                return identify_result

            user_login = identify_result.get('user_login')
            user_name = identify_result.get('user_name')
            confidence = identify_result.get('confidence')

            if not user_login:
                return {
                    'success': False,
                    'error': _('Impossible de récupérer les informations utilisateur')
                }

            # Deuxième étape: créer la session
            # Note: Nous devons contourner la vérification du mot de passe
            # car l'authentification se fait par reconnaissance faciale
            try:
                # Récupérer l'utilisateur
                user = request.env['res.users'].sudo().search([
                    ('login', '=', user_login),
                    ('active', '=', True)
                ], limit=1)

                if not user:
                    return {
                        'success': False,
                        'error': _('Utilisateur non trouvé')
                    }

                # Créer la session manuellement sans mot de passe
                # En reconnaissance faciale, l'authentification est déjà validée
                request.session.uid = user.id
                request.session.login = user_login
                request.session.context = dict(request.env.context)
                request.session.context.update({
                    'uid': user.id,
                    'lang': user.lang,
                    'tz': user.tz,
                })

                # Enregistrer l'événement dans le chatter de l'utilisateur
                facial_data = request.env['eazynova.facial.data'].sudo().search([
                    ('user_id', '=', user.id),
                    ('active', '=', True)
                ], limit=1)

                if facial_data:
                    facial_data.write({
                        'last_verification_date': http.fields.Datetime.now(),
                        'verification_count': facial_data.verification_count + 1
                    })
                    facial_data.message_post(
                        body=_("Connexion par reconnaissance faciale réussie (confiance: %.1f%%)") % confidence
                    )

                _logger.info(
                    f"Authentification faciale réussie pour {user_login} "
                    f"(confiance: {confidence:.1f}%)"
                )

                return {
                    'success': True,
                    'user_name': user_name,
                    'confidence': confidence,
                    'redirect': '/web',
                }

            except Exception as auth_error:
                _logger.exception(f"Erreur lors de la création de session: {auth_error}")
                return {
                    'success': False,
                    'error': _('Erreur lors de l\'authentification: %s') % str(auth_error)
                }

        except Exception as e:
            _logger.exception("Erreur lors de l'authentification faciale")
            return {
                'success': False,
                'error': _('Erreur lors de l\'authentification: %s') % str(e)
            }

    @http.route('/web/facial_auth/check_availability', type='jsonrpc', auth='public')
    def check_facial_availability(self):
        """Vérifie si la reconnaissance faciale est disponible"""
        try:
            facial_service = request.env['eazynova.facial.service'].sudo()
            result = facial_service.check_library_availability()
            return result
        except Exception as e:
            _logger.exception("Erreur vérification disponibilité")
            return {
                'available': False,
                'error': str(e)
            }


class HomeExtended(Home):
    """Extension du controller Home pour ajouter lien vers login facial"""

    @http.route()
    def web_login(self, *args, **kwargs):
        """Surcharge de la méthode web_login pour ajouter option faciale"""
        response = super(HomeExtended, self).web_login(*args, **kwargs)

        # Ajouter un flag indiquant que la reconnaissance faciale est disponible
        if hasattr(response, 'qcontext'):
            try:
                facial_service = request.env['eazynova.facial.service'].sudo()
                availability = facial_service.check_library_availability()
                response.qcontext['facial_auth_available'] = availability.get('available', False)
            except Exception:
                response.qcontext['facial_auth_available'] = False

        return response
