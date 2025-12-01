# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class EazynovaFacialData(models.Model):
    _name = 'eazynova.facial.data'
    _description = 'Données de Reconnaissance Faciale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', compute='_compute_name', store=True)

    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    photo = fields.Binary(
        string='Photo de Référence',
        required=True,
        attachment=True,
        help="Photo utilisée pour l'enregistrement facial"
    )

    encoding_data = fields.Text(
        string='Données d\'Encodage',
        help="Encodage facial pour la reconnaissance (format JSON)"
    )

    active = fields.Boolean(string='Actif', default=True, tracking=True)

    registration_date = fields.Datetime(
        string='Date d\'Enregistrement',
        default=fields.Datetime.now,
        readonly=True
    )

    last_verification_date = fields.Datetime(
        string='Dernière Vérification',
        readonly=True
    )

    verification_count = fields.Integer(
        string='Nombre de Vérifications',
        default=0,
        readonly=True
    )

    face_count = fields.Integer(
        string='Nombre de Visages Détectés',
        default=0,
        readonly=True,
        help="Nombre de visages détectés lors de l'enregistrement"
    )

    quality_score = fields.Float(
        string='Score de Qualité',
        readonly=True,
        help="Score de qualité de l'image (0-100)"
    )

    note = fields.Text(string='Notes')

    @api.depends('user_id')
    def _compute_name(self):
        for record in self:
            if record.user_id:
                record.name = f"Facial - {record.user_id.name}"
            else:
                record.name = "Facial Data"

    @api.constrains('user_id')
    def _check_unique_user(self):
        """Un seul enregistrement facial actif par utilisateur"""
        for record in self:
            if record.active:
                existing = self.search([
                    ('user_id', '=', record.user_id.id),
                    ('active', '=', True),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise UserError(_(
                        "L'utilisateur %s a déjà un enregistrement facial actif. "
                        "Veuillez désactiver l'ancien avant d'en créer un nouveau."
                    ) % record.user_id.name)

    def action_register_face(self):
        """Enregistre les données faciales"""
        self.ensure_one()

        if not self.photo:
            raise UserError(_("Aucune photo fournie pour l'enregistrement."))

        try:
            # Appeler le service de reconnaissance faciale
            facial_service = self.env['eazynova.facial.service']
            result = facial_service.register_face(
                self.photo,
                self.user_id.id
            )

            # Mettre à jour les données
            self.write({
                'encoding_data': result.get('encoding'),
                'face_count': result.get('face_count', 0),
                'quality_score': result.get('quality_score', 0),
                'registration_date': fields.Datetime.now()
            })

            self.message_post(
                body=_("Enregistrement facial effectué avec succès. "
                       "Visages détectés: %d, Score de qualité: %.1f%%") % (
                    self.face_count, self.quality_score
                )
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Enregistrement facial effectué avec succès !'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.exception("Erreur lors de l'enregistrement facial")
            raise UserError(_("Erreur lors de l'enregistrement facial: %s") % str(e))

    def action_verify_face(self, photo_to_verify):
        """Vérifie un visage contre les données enregistrées"""
        self.ensure_one()

        if not self.encoding_data:
            raise UserError(_("Aucune donnée d'encodage disponible. Veuillez réenregistrer."))

        try:
            facial_service = self.env['eazynova.facial.service']
            result = facial_service.verify_face(
                photo_to_verify,
                self.encoding_data
            )

            # Mettre à jour les statistiques
            self.write({
                'last_verification_date': fields.Datetime.now(),
                'verification_count': self.verification_count + 1
            })

            return result

        except Exception as e:
            _logger.exception("Erreur lors de la vérification faciale")
            raise UserError(_("Erreur lors de la vérification: %s") % str(e))

    @api.model
    def find_user_by_face(self, photo):
        """Trouve un utilisateur à partir d'une photo"""
        try:
            facial_service = self.env['eazynova.facial.service']
            return facial_service.identify_user(photo)

        except Exception as e:
            _logger.exception("Erreur lors de l'identification faciale")
            return {
                'success': False,
                'error': str(e)
            }

    def action_deactivate(self):
        """Désactive l'enregistrement facial"""
        self.active = False
        self.message_post(body=_("Enregistrement facial désactivé"))

    def action_reactivate(self):
        """Réactive l'enregistrement facial"""
        self.active = True
        self.message_post(body=_("Enregistrement facial réactivé"))
