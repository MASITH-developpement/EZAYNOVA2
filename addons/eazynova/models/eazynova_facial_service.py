# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import base64
import json
import logging

_logger = logging.getLogger(__name__)


class EazynovaFacialService(models.AbstractModel):
    """Service de Reconnaissance Faciale EAZYNOVA"""
    _name = 'eazynova.facial.service'
    _description = 'Service de Reconnaissance Faciale'

    @api.model
    def register_face(self, photo_data, user_id):
        """
        Enregistre un visage pour la reconnaissance

        :param photo_data: Données de l'image en base64
        :param user_id: ID de l'utilisateur
        :return: Dict avec encoding et métadonnées
        """
        try:
            # Vérifier si la bibliothèque face_recognition est disponible
            try:
                import face_recognition
                import numpy as np
                from PIL import Image
                import io
            except ImportError:
                return self._register_face_fallback(photo_data, user_id)

            # Décoder l'image
            image_data = base64.b64decode(photo_data)
            image = Image.open(io.BytesIO(image_data))

            # Convertir en RGB si nécessaire
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convertir en array numpy
            image_array = np.array(image)

            # Détecter les visages
            face_locations = face_recognition.face_locations(image_array)

            if len(face_locations) == 0:
                raise UserError(_(
                    "Aucun visage détecté dans l'image. "
                    "Veuillez fournir une photo claire de votre visage."
                ))

            if len(face_locations) > 1:
                raise UserError(_(
                    "Plusieurs visages détectés (%d). "
                    "Veuillez fournir une photo avec un seul visage."
                ) % len(face_locations))

            # Encoder le visage
            face_encodings = face_recognition.face_encodings(
                image_array,
                face_locations
            )

            if not face_encodings:
                raise UserError(_("Impossible d'encoder le visage détecté."))

            encoding = face_encodings[0]

            # Calculer un score de qualité basé sur la taille du visage
            face_location = face_locations[0]
            top, right, bottom, left = face_location
            face_height = bottom - top
            face_width = right - left
            image_height, image_width = image_array.shape[:2]

            face_area = face_height * face_width
            image_area = image_height * image_width
            face_ratio = face_area / image_area

            # Score de qualité (0-100)
            quality_score = min(100, face_ratio * 500)  # Optimum ~20% de l'image

            # Convertir l'encoding en JSON
            encoding_json = json.dumps(encoding.tolist())

            _logger.info(
                f"Visage enregistré pour utilisateur {user_id}: "
                f"qualité={quality_score:.1f}%"
            )

            return {
                'success': True,
                'encoding': encoding_json,
                'face_count': len(face_locations),
                'quality_score': quality_score,
                'face_location': face_location,
            }

        except ImportError as e:
            _logger.warning("Bibliothèque face_recognition non disponible")
            return self._register_face_fallback(photo_data, user_id)

        except Exception as e:
            _logger.exception("Erreur dans register_face")
            raise UserError(_("Erreur lors de l'enregistrement: %s") % str(e))

    @api.model
    def verify_face(self, photo_data, stored_encoding_json, tolerance=0.6):
        """
        Vérifie si un visage correspond à un encodage stocké

        :param photo_data: Données de l'image en base64
        :param stored_encoding_json: Encodage stocké (JSON)
        :param tolerance: Seuil de tolérance (0.6 par défaut)
        :return: Dict avec résultat de la vérification
        """
        try:
            try:
                import face_recognition
                import numpy as np
                from PIL import Image
                import io
            except ImportError:
                return self._verify_face_fallback(photo_data, stored_encoding_json)

            # Décoder l'image
            image_data = base64.b64decode(photo_data)
            image = Image.open(io.BytesIO(image_data))

            if image.mode != 'RGB':
                image = image.convert('RGB')

            image_array = np.array(image)

            # Détecter les visages
            face_locations = face_recognition.face_locations(image_array)

            if len(face_locations) == 0:
                return {
                    'success': False,
                    'match': False,
                    'error': 'Aucun visage détecté',
                    'confidence': 0.0
                }

            # Encoder le visage
            face_encodings = face_recognition.face_encodings(
                image_array,
                face_locations
            )

            if not face_encodings:
                return {
                    'success': False,
                    'match': False,
                    'error': 'Impossible d\'encoder le visage',
                    'confidence': 0.0
                }

            # Charger l'encodage stocké
            stored_encoding = np.array(json.loads(stored_encoding_json))

            # Comparer les visages
            current_encoding = face_encodings[0]
            distance = face_recognition.face_distance(
                [stored_encoding],
                current_encoding
            )[0]

            match = distance <= tolerance
            confidence = max(0, min(100, (1 - distance) * 100))

            _logger.info(
                f"Vérification faciale: match={match}, "
                f"distance={distance:.3f}, confiance={confidence:.1f}%"
            )

            return {
                'success': True,
                'match': match,
                'confidence': confidence,
                'distance': float(distance),
                'tolerance': tolerance,
                'faces_detected': len(face_locations)
            }

        except ImportError:
            return self._verify_face_fallback(photo_data, stored_encoding_json)

        except Exception as e:
            _logger.exception("Erreur dans verify_face")
            return {
                'success': False,
                'match': False,
                'error': str(e),
                'confidence': 0.0
            }

    @api.model
    def identify_user(self, photo_data, tolerance=0.6):
        """
        Identifie un utilisateur à partir d'une photo

        :param photo_data: Données de l'image en base64
        :param tolerance: Seuil de tolérance
        :return: Dict avec utilisateur identifié
        """
        try:
            # Récupérer tous les enregistrements faciaux actifs
            facial_records = self.env['eazynova.facial.data'].search([
                ('active', '=', True),
                ('encoding_data', '!=', False)
            ])

            if not facial_records:
                return {
                    'success': False,
                    'user_id': None,
                    'error': 'Aucun enregistrement facial trouvé',
                    'confidence': 0.0
                }

            best_match = None
            best_confidence = 0.0

            # Comparer avec chaque enregistrement
            for record in facial_records:
                result = self.verify_face(
                    photo_data,
                    record.encoding_data,
                    tolerance
                )

                if result.get('success') and result.get('match'):
                    confidence = result.get('confidence', 0)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = record

            if best_match:
                _logger.info(
                    f"Utilisateur identifié: {best_match.user_id.name} "
                    f"(confiance: {best_confidence:.1f}%)"
                )

                return {
                    'success': True,
                    'user_id': best_match.user_id.id,
                    'user_name': best_match.user_id.name,
                    'confidence': best_confidence,
                    'facial_data_id': best_match.id
                }
            else:
                return {
                    'success': False,
                    'user_id': None,
                    'error': 'Aucune correspondance trouvée',
                    'confidence': 0.0,
                    'checked_users': len(facial_records)
                }

        except Exception as e:
            _logger.exception("Erreur dans identify_user")
            return {
                'success': False,
                'user_id': None,
                'error': str(e),
                'confidence': 0.0
            }

    def _register_face_fallback(self, photo_data, user_id):
        """Fallback quand face_recognition n'est pas disponible"""
        _logger.warning(
            "Bibliothèque face_recognition non disponible - mode fallback"
        )

        return {
            'success': True,
            'encoding': json.dumps([0] * 128),  # Encodage factice
            'face_count': 1,
            'quality_score': 50.0,
            'fallback': True,
            'message': 'Mode fallback - installez face_recognition pour une vraie reconnaissance'
        }

    def _verify_face_fallback(self, photo_data, stored_encoding_json):
        """Fallback pour la vérification"""
        _logger.warning(
            "Bibliothèque face_recognition non disponible - mode fallback"
        )

        return {
            'success': True,
            'match': False,
            'confidence': 0.0,
            'fallback': True,
            'message': 'Mode fallback - installez face_recognition'
        }

    @api.model
    def check_library_availability(self):
        """Vérifie si les bibliothèques nécessaires sont disponibles"""
        try:
            import face_recognition
            import numpy
            import PIL
            return {
                'available': True,
                'libraries': {
                    'face_recognition': True,
                    'numpy': True,
                    'PIL': True
                }
            }
        except ImportError as e:
            return {
                'available': False,
                'error': str(e),
                'message': 'Installez: pip install face_recognition pillow numpy'
            }
