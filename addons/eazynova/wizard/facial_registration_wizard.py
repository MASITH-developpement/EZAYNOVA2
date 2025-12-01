# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)


class FacialRegistrationWizard(models.TransientModel):
    _name = 'eazynova.facial.registration.wizard'
    _description = 'Enregistrement reconnaissance faciale EAZYNOVA'

    user_id = fields.Many2one(
        'res.users',
        string="Utilisateur",
        required=True,
        default=lambda self: self.env.user
    )

    photo = fields.Binary(string="Photo", required=True, attachment=True)
    photo_filename = fields.Char(string="Nom de fichier")

    # Consentement RGPD
    consent = fields.Boolean(
        string="Je consens au traitement de mes données biométriques",
        required=True,
        help="Conformément au RGPD, votre consentement explicite est requis pour le traitement de données biométriques"
    )

    consent_text = fields.Html(
        string="Texte de consentement",
        readonly=True,
        default=lambda self: self._default_consent_text()
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('processing', 'Traitement en cours'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ], string="État", default='draft', readonly=True)

    error_message = fields.Text(string="Message d'erreur", readonly=True)

    @api.model
    def _default_consent_text(self):
        """Génère le texte de consentement RGPD"""
        return """
        <div style="padding: 10px; background: #f9f9f9; border: 1px solid #ddd;">
            <h4>Consentement au traitement de données biométriques</h4>
            <p>
                En cochant cette case, vous consentez explicitement au traitement de vos données biométriques
                (encodage facial) pour les finalités suivantes :
            </p>
            <ul>
                <li>Authentification sécurisée à l'application EAZYNOVA</li>
                <li>Contrôle d'accès aux zones sensibles</li>
            </ul>
            <p><strong>Vos droits :</strong></p>
            <ul>
                <li>Vous pouvez retirer votre consentement à tout moment</li>
                <li>Vous avez un droit d'accès, de rectification et de suppression de vos données</li>
                <li>Vos données sont stockées de manière sécurisée et chiffrée</li>
                <li>Vos données ne seront jamais partagées avec des tiers</li>
            </ul>
            <p>
                Pour plus d'informations, consultez notre politique de confidentialité ou contactez
                notre délégué à la protection des données.
            </p>
        </div>
        """

    @api.constrains('consent')
    def _check_consent(self):
        """Vérifie que le consentement est donné"""
        for wizard in self:
            if wizard.state != 'draft' and not wizard.consent:
                raise ValidationError(_("Vous devez donner votre consentement explicite pour continuer."))

    def action_register_face(self):
        """Enregistre l'encodage facial de l'utilisateur"""
        self.ensure_one()

        if not self.consent:
            raise UserError(_("Vous devez donner votre consentement explicite pour continuer."))

        # Vérifier que la reconnaissance faciale est activée
        facial_enabled = self.env['ir.config_parameter'].sudo().get_param('eazynova.facial_enabled', False)
        if not facial_enabled:
            raise UserError(_(
                "La reconnaissance faciale n'est pas activée. "
                "Veuillez l'activer dans les paramètres EAZYNOVA."
            ))

        self.state = 'processing'

        try:
            # Générer l'encodage facial
            facial_encoding = self._generate_facial_encoding()

            # Mettre à jour l'utilisateur
            self.user_id.write({
                'eazynova_facial_encoding': facial_encoding,
                'eazynova_facial_consent': True,
                'eazynova_facial_consent_date': fields.Datetime.now(),
            })

            self.state = 'done'

        except Exception as e:
            _logger.error(f"Erreur lors de l'enregistrement facial: {str(e)}")
            self.error_message = str(e)
            self.state = 'error'
            raise UserError(_("Erreur lors de l'enregistrement facial: %s") % str(e))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Succès"),
                'message': _("Votre visage a été enregistré avec succès."),
                'type': 'success',
                'sticky': False,
            }
        }

    def _generate_facial_encoding(self):
        """Génère l'encodage facial à partir de la photo"""
        try:
            import face_recognition
            import numpy as np
            from PIL import Image
            import io
        except ImportError:
            raise UserError(_(
                "Dépendances reconnaissance faciale manquantes. Veuillez installer: "
                "pip install face-recognition"
            ))

        # Décoder la photo
        photo_data = base64.b64decode(self.photo)
        image = Image.open(io.BytesIO(photo_data))

        # Convertir en array numpy
        image_array = np.array(image)

        # Détecter les visages
        face_locations = face_recognition.face_locations(image_array)

        if not face_locations:
            raise UserError(_("Aucun visage détecté sur la photo. Veuillez fournir une photo claire de votre visage."))

        if len(face_locations) > 1:
            raise UserError(_("Plusieurs visages détectés. Veuillez fournir une photo avec un seul visage."))

        # Générer l'encodage facial
        face_encodings = face_recognition.face_encodings(image_array, face_locations)

        if not face_encodings:
            raise UserError(_("Impossible de générer l'encodage facial. Veuillez fournir une photo de meilleure qualité."))

        # Encoder en base64 pour stockage
        encoding_bytes = face_encodings[0].tobytes()
        encoding_base64 = base64.b64encode(encoding_bytes)

        return encoding_base64

    def action_cancel(self):
        """Annule et ferme le wizard"""
        return {'type': 'ir.actions.act_window_close'}

    def action_revoke_consent(self):
        """Révoque le consentement et supprime les données biométriques"""
        self.ensure_one()

        self.user_id.write({
            'eazynova_facial_encoding': False,
            'eazynova_facial_consent': False,
            'eazynova_facial_consent_date': False,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Succès"),
                'message': _("Votre consentement a été révoqué et vos données biométriques supprimées."),
                'type': 'success',
                'sticky': False,
            }
        }
