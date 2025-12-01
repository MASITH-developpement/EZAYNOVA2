# -*- coding: utf-8 -*-

import base64
import hashlib
import logging
import re
from datetime import timedelta
from math import radians, sin, cos, sqrt, atan2

import requests

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError
from odoo.addons.mail.models.mail_thread import MailThread
from .intervention_access_mixin import InterventionAccessMixin

_logger = logging.getLogger(__name__)


class InterventionIntervention(models.Model, InterventionAccessMixin, MailThread):
    observations_client = fields.Text(
        string="Observations du client",
        help="Commentaires ou remarques du client lors de la validation."
    )
    _name = 'intervention.intervention'
    _inherit = ['mail.thread']
    _description = "Intervention technique"
    _rec_name = 'numero'
    _order = 'date_prevue desc, id desc'

    def action_send_report(self):
        """Envoi du rapport d'intervention par email aux destinataires concernés"""
        self.ensure_one()
        
        # Collecte des emails (dédoublonnés)
        emails = set()
        if self.donneur_ordre_id and self.donneur_ordre_id.email:
            emails.add(self.donneur_ordre_id.email)
        if self.client_final_id and self.client_final_id.email:
            emails.add(self.client_final_id.email)
        if self.company_id and self.company_id.email:
            emails.add(self.company_id.email)
        
        if not emails:
            raise UserError("Aucune adresse email trouvée pour l'envoi du rapport.")

        # Génération du rapport HTML
        rapport_html = self._generate_report_html()
        
        # Génération du PDF
        pdf_data = self.env['ir.actions.report']._render_qweb_pdf(
            'intervention.action_rapport_intervention_pdf',
            self.id,
            data={'rapport_html': rapport_html}
        )[0]
        
        # Création de la pièce jointe
        attachment = self.env['ir.attachment'].create({
            'name': f'Rapport_intervention_{self.numero}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_data).decode(),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        # Préparation du sujet
        subject = f"Rapport d'intervention {self.numero}"
        if self.numero_donneur_ordre:
            subject += f" - N° DO: {self.numero_donneur_ordre}"

        # Création et envoi de l'email
        email_from = self.env['ir.config_parameter'].sudo().get_param(
            'intervention.email_from'
        ) or self.env.company.email or False
        
        mail_values = {
            'subject': subject,
            'body_html': "<p>Veuillez trouver ci-joint le rapport d'intervention.</p>",
            'email_to': ','.join(emails),
            'email_from': email_from,
            'attachment_ids': [(6, 0, [attachment.id])],
        }
        self.env['mail.mail'].create(mail_values).send()
    
    def _generate_report_html(self):
        """Génère le HTML du rapport d'intervention (méthode réutilisable)"""
        self.ensure_one()
        client_final = self.client_final_id.name if self.client_final_id else "Identique au donneur d'ordre"
        type_label = dict(self._fields['type_intervention'].selection).get(self.type_intervention, '')
        
        return f"""
        <div style='font-family: Arial, sans-serif; margin: 20px;'>
            <h1 style='color: #2c5282;'>RAPPORT D'INTERVENTION</h1>
            <hr/>
            <h2>Informations générales</h2>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr><td><strong>N° Intervention:</strong></td><td>{self.numero}</td></tr>
                <tr><td><strong>Date:</strong></td><td>{self.date_prevue.strftime('%d/%m/%Y %H:%M') if self.date_prevue else 'N/A'}</td></tr>
                <tr><td><strong>Type:</strong></td><td>{type_label}</td></tr>
                <tr><td><strong>Technicien:</strong></td><td>{self.technicien_principal_id.name if self.technicien_principal_id else 'N/A'}</td></tr>
            </table>
            <h2>Client</h2>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr><td><strong>Donneur d'ordre:</strong></td><td>{self.donneur_ordre_id.name if self.donneur_ordre_id else 'N/A'}</td></tr>
                <tr><td><strong>Client final:</strong></td><td>{client_final}</td></tr>
                <tr><td><strong>Adresse intervention:</strong></td><td>{self.adresse_intervention or 'N/A'}</td></tr>
            </table>
            <h2>Description du problème</h2>
            <div style='background:#f7f7f7; border:1px solid #ddd; padding:10px; margin-bottom:15px;'>
                {self.description or 'Aucune description'}
            </div>
            <h2>Rapport final</h2>
            <div style='background:#f7f7f7; border:1px solid #ddd; padding:10px; margin-bottom:15px;'>
                {self.rapport_intervention or 'Aucun rapport final saisi.'}
            </div>
            <h2>Détails de l'intervention</h2>
            <p><strong>Travaux réalisés:</strong><br/>{self.travaux_realises or 'Non renseigné'}</p>
            <p><strong>Observations:</strong><br/>{self.observations or 'Aucune observation'}</p>
            <h2>Validation</h2>
            <p><strong>Signataire:</strong> {self.nom_signataire or 'Non signé'}</p>
            <p><strong>Date signature:</strong> {self.date_signature.strftime('%d/%m/%Y %H:%M') if self.date_signature else 'Non signé'}</p>
            <hr style='margin-top: 50px;'/>
            <p style='text-align: center; font-size: 12px; color: #666;'>
                Rapport généré automatiquement le {fields.Datetime.now().strftime('%d/%m/%Y à %H:%M')}
            </p>
        </div>
        """
    lien_openrouteservice = fields.Char(
        string="Lien OpenRouteService",
        compute='_compute_lien_openrouteservice',
        store=True,
        help="Lien direct vers l'itinéraire OpenRouteService pour cette intervention"
    )

    @api.depends('latitude', 'longitude')
    def _compute_lien_openrouteservice(self):
        """Générer le lien OpenRouteService pour l'itinéraire routier"""
        for record in self:
            partner = record.company_id.partner_id
            lat_soc = getattr(partner, 'partner_latitude', None)
            lon_soc = getattr(partner, 'partner_longitude', None)
            lat_cli, lon_cli = record.latitude, record.longitude
            
            if lat_soc and lon_soc and lat_cli and lon_cli:
                try:
                    lat_soc_f = float(lat_soc)
                    lon_soc_f = float(lon_soc)
                    lat_cli_f = float(lat_cli)
                    lon_cli_f = float(lon_cli)
                    record.lien_openrouteservice = (
                        f"https://maps.openrouteservice.org/directions?engine=fossilfuel&profile=driving-car"
                        f"&start={lon_soc_f},{lat_soc_f}&end={lon_cli_f},{lat_cli_f}"
                    )
                except (ValueError, TypeError):
                    record.lien_openrouteservice = False
            else:
                record.lien_openrouteservice = False
    def action_view_photos_apres(self):
        """Action pour voir les photos après intervention"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.photos_apres_ids.ids)],
            'context': {
                'default_res_model': 'intervention.intervention',
                'default_res_id': self.id,
                'default_name': f'Photo après - {self.numero}',
            }
        }
    def action_view_photos_avant(self):
        """Action pour voir les photos avant intervention"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Photos Avant Intervention',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.photos_avant_ids.ids)],
            'context': {
                'default_res_model': 'intervention.intervention',
                'default_res_id': self.id,
                'default_name': f'Photo avant - {self.numero}',
            }
        }
    def action_calculer_distance(self):
        """Calculer la distance et la durée via OpenRouteService ou vol d'oiseau"""
        self.ensure_one()
        
        if not self.adresse_intervention:
            raise UserError("Veuillez renseigner l'adresse d'intervention.")

        try:
            # Géocoder l'adresse si les coordonnées ne sont pas déjà présentes
            if not self.latitude or not self.longitude:
                _logger.info(f"Géocodage nécessaire pour intervention {self.numero}")
                try:
                    self._geocoder_adresse()
                    _logger.info(f"Géocodage réussi: lat={self.latitude}, lon={self.longitude}")
                except UserError as e:
                    # Le géocodage a échoué, afficher l'erreur à l'utilisateur
                    return self._display_notification(
                        'Erreur de géocodage',
                        str(e),
                        'warning',
                        sticky=True
                    )

            # Récupérer les coordonnées
            partner = self.company_id.partner_id
            lat_soc = getattr(partner, 'partner_latitude', None)
            lon_soc = getattr(partner, 'partner_longitude', None)
            lat_cli, lon_cli = self.latitude, self.longitude
            
            _logger.debug(f"Calcul distance - Société: lat={lat_soc} lon={lon_soc} | Client: lat={lat_cli} lon={lon_cli}")
            
            # Vérifications
            if not lat_soc or not lon_soc:
                return self._display_notification(
                    'Erreur coordonnées société',
                    f"Le point de départ (société) n'est pas géolocalisé.\n"
                    f"Valeurs lues: lat={lat_soc} lon={lon_soc}\n"
                    "Vérifiez les champs latitude/longitude sur la fiche société.",
                    'warning',
                    sticky=True
                )
            
            if not lat_cli or not lon_cli:
                return self._display_notification(
                    'Erreur coordonnées client',
                    "Le point d'arrivée (client) n'est pas géolocalisé.\n"
                    "Le géocodage automatique n'a pas fonctionné.\n"
                    "Saisissez manuellement les coordonnées GPS dans l'onglet Navigation.",
                    'warning',
                    sticky=True
                )
            
            # Tentative avec OpenRouteService
            ors_api_key = self.env['ir.config_parameter'].sudo().get_param('intervention.openroute_api_key')
            if ors_api_key:
                distance_calculated = self._calculate_distance_ors(lat_soc, lon_soc, lat_cli, lon_cli, ors_api_key)
                if distance_calculated:
                    return distance_calculated
            
            # Fallback : distance à vol d'oiseau
            self._calculer_distance_waze()
            return self._display_notification(
                'Calcul terminé (à vol d\'oiseau)',
                f'⚠️ Itinéraire routier non disponible, calcul à vol d\'oiseau\n'
                f'📏 Distance: {self.distance_km} km (distance réelle en voiture sera plus longue)\n'
                f'⏱️ Durée estimée: {self.duree_trajet_min} min\n'
                f'Point de départ (société): lat={lat_soc}, lon={lon_soc}\n'
                f'Point d\'arrivée (client): lat={lat_cli}, lon={lon_cli}\n\n'
                f'💡 Utilisez Google Maps ou Waze pour l\'itinéraire routier précis',
                'warning'
            )
            
        except Exception as e:
            _logger.error(f"Erreur calcul distance: {str(e)}", exc_info=True)
            return self._display_notification(
                'Erreur de calcul automatique',
                f'{str(e)}\n\nVous pouvez saisir manuellement les coordonnées GPS.',
                'warning'
            )
    
    def _calculate_distance_ors(self, lat_soc, lon_soc, lat_cli, lon_cli, api_key):
        """Calcul de distance via OpenRouteService API"""
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        headers = {'Authorization': api_key, 'Accept': 'application/json'}
        body = {
            "coordinates": [[lon_soc, lat_soc], [lon_cli, lat_cli]],
            "instructions": False
        }
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Nouveau format API v2 : chercher dans 'routes'
                if 'routes' in data and data['routes']:
                    route = data['routes'][0]
                    if 'summary' in route:
                        summary = route['summary']
                        self.distance_km = round(summary['distance'] / 1000.0, 2)
                        self.duree_trajet_min = int(summary['duration'] / 60)
                        
                        _logger.info(f"OpenRouteService (routes): {self.distance_km} km, {self.duree_trajet_min} min")
                        
                        if self.distance_km > 0:
                            ors_link = (
                                f"https://maps.openrouteservice.org/directions?engine=fossilfuel&profile=driving-car"
                                f"&start={lon_soc},{lat_soc}&end={lon_cli},{lat_cli}"
                            )
                            return self._display_notification(
                                'Distance calculée (OpenRouteService)',
                                f'🗺️ {self.distance_km:.1f} km - ⏱️ {self.duree_trajet_min} min\n'
                                f'Point de départ (société): lat={lat_soc}, lon={lon_soc}\n'
                                f'Point d\'arrivée (client): lat={lat_cli}, lon={lon_cli}\n'
                                f"<a href='{ors_link}' target='_blank'>Voir l'itinéraire OpenRouteService</a>",
                                'info',
                                html=True
                            )
                
                # Ancien format API : chercher dans 'features' (fallback)
                elif 'features' in data and data['features']:
                    if 'properties' in data['features'][0] and 'summary' in data['features'][0]['properties']:
                        summary = data['features'][0]['properties']['summary']
                        self.distance_km = round(summary['distance'] / 1000.0, 2)
                        self.duree_trajet_min = int(summary['duration'] / 60)
                        
                        _logger.info(f"OpenRouteService (features): {self.distance_km} km, {self.duree_trajet_min} min")
                        
                        if self.distance_km > 0:
                            ors_link = (
                                f"https://maps.openrouteservice.org/directions?engine=fossilfuel&profile=driving-car"
                                f"&start={lon_soc},{lat_soc}&end={lon_cli},{lat_cli}"
                            )
                            return self._display_notification(
                                'Distance calculée (OpenRouteService)',
                                f'🗺️ {self.distance_km:.1f} km - ⏱️ {self.duree_trajet_min} min\n'
                                f'Point de départ (société): lat={lat_soc}, lon={lon_soc}\n'
                                f'Point d\'arrivée (client): lat={lat_cli}, lon={lon_cli}\n'
                                f"<a href='{ors_link}' target='_blank'>Voir l'itinéraire OpenRouteService</a>",
                                'info',
                                html=True
                            )
                else:
                    _logger.warning(f"OpenRouteService: format de réponse non reconnu - {data}")
                    
            elif response.status_code == 404:
                error_msg = response.json().get('error', {}).get('message', 'Adresse non trouvée') if response.text else 'Adresse non trouvée'
                _logger.warning(f"OpenRouteService API 404: {error_msg}")
            else:
                _logger.warning(f"OpenRouteService API HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.RequestException as e:
            _logger.warning(f"OpenRouteService API erreur réseau: {str(e)}")
        except KeyError as e:
            _logger.warning(f"OpenRouteService API clé manquante: {str(e)}")
        except Exception as e:
            _logger.warning(f"OpenRouteService API erreur: {str(e)}")
        
        return False
    
    def _display_notification(self, title, message, notification_type='info', sticky=False, html=False):
        """Affiche une notification à l'utilisateur"""
        params = {
            'title': title,
            'message': message,
            'type': notification_type,
            'sticky': sticky,
        }
        if html:
            params['dangerouslyUseHTMLString'] = True
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': params
        }
    def action_geocoder_adresse(self):
        """Action bouton : géocoder l'adresse d'intervention"""
        self.ensure_one()
        
        if not self.adresse_intervention:
            raise UserError("Veuillez renseigner l'adresse d'intervention.")
        
        try:
            self._geocoder_adresse()
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        except Exception as e:
            _logger.error(f"Erreur géocodage: {str(e)}")
            return self._display_notification(
                'Erreur de géocodage',
                str(e),
                'warning',
                sticky=True
            )

    # ===== DÉFINITION DES CHAMPS =====
    
    numero = fields.Char(
        string="N° Intervention",
        required=True,
        default="/",
        copy=False,
        readonly=True,
        index=True,
        help="Numéro unique de l'intervention, généré automatiquement"
    )
    technicien_app_url = fields.Char(
        string="URL App Technicien",
        help="Lien d'accès à l'application mobile du technicien pour cette intervention"
    )
    def action_view_invoices(self):
        """Ouvre la/les facture(s) liée(s) à l'intervention"""
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'default_move_type': 'out_invoice'},
            'name': 'Factures',
        }
        if self.invoice_count == 1 and self.invoice_ids:
            action['res_id'] = self.invoice_ids[0].id
            action['view_mode'] = 'form'
        return action
    def action_view_sale_order(self):
        """Ouvre le(s) devis/commande(s) lié(s) à l'intervention"""
        self.ensure_one()
        if not self.sale_order_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    _name = 'intervention.intervention'
    def action_view_calendar_event(self):
        """Ouvre l'événement calendrier lié à l'intervention"""
        self.ensure_one()
        if not self.calendar_event_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'res_id': self.calendar_event_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'create': False}
        }
    def _geocoder_adresse(self):
        """Géocoder l'adresse d'intervention avec cache et gestion robuste"""
        if not self.adresse_intervention:
            return
        
        try:
            import re
            adresse = self.adresse_intervention.strip()
            
            # Normaliser l'adresse (supprimer lignes vides, fusionner)
            lignes = [l.strip() for l in adresse.splitlines() if l.strip()]
            
            # Retirer les lignes qui ne sont pas utiles pour le géocodage
            lignes_filtrees = []
            for ligne in lignes:
                # Ignorer les lignes sans chiffre (nom de société/personne)
                if not re.search(r'\d', ligne):
                    # Mais garder si c'est juste un nom de ville
                    if not any(mot in ligne.lower() for mot in ['immeuble', 'bâtiment', 'batiment', 'résidence', 'residence', 'chez', 'société', 'societe', 'sarl', 'sas', 'eurl']):
                        lignes_filtrees.append(ligne)
                else:
                    lignes_filtrees.append(ligne)
            
            # Si on a tout filtré, reprendre les lignes originales sauf la première
            if not lignes_filtrees and len(lignes) > 1:
                lignes_filtrees = lignes[1:]
            elif not lignes_filtrees:
                lignes_filtrees = lignes
            
            adresse_join = ' '.join(lignes_filtrees)
            
            _logger.info(f"Adresse normalisée pour géocodage: {adresse_join}")
            
            # Vérifier le cache avec l'adresse originale
            cache = self.env['intervention.geocoding.cache'].sudo().search([
                ('address', '=', adresse_join)
            ], limit=1)
            
            if cache:
                self.latitude = float(cache.latitude)
                self.longitude = float(cache.longitude)
                _logger.info(f"Géocodage depuis cache pour: {adresse_join}")
                return

            # Extraire rue, code postal, ville, pays
            match = re.match(
                r'(.+?)\s+(\d{5})\s+([A-Za-z\- ]+)'
                r'(?:\s+(France|Belgique|Suisse|Luxembourg|Espagne|Italie|Germany|Deutschland|Portugal|Royaume-Uni|UK|Maroc|Tunisie|Algérie))?$',
                adresse_join,
                re.I
            )
            
            # Préparer plusieurs variantes d'adresses à tester
            adresses_a_tester = []
            
            if match:
                rue = match.group(1).strip()
                code_postal = match.group(2)
                ville = match.group(3).strip()
                pays = match.group(4) if match.group(4) else 'France'
                
                # Variante 1 : Format structuré avec virgules
                adresses_a_tester.append(f"{rue}, {code_postal} {ville}, {pays}")
                # Variante 2 : Format compact
                adresses_a_tester.append(f"{rue} {code_postal} {ville} {pays}")
                # Variante 3 : Sans la rue (parfois plus fiable)
                adresses_a_tester.append(f"{code_postal} {ville}, {pays}")
            else:
                # Si le regex ne matche pas, essayer l'adresse telle quelle
                adresses_a_tester.append(adresse_join)
                if 'france' not in adresse_join.lower():
                    adresses_a_tester.append(f"{adresse_join}, France")

            # Appel API Nominatim avec plusieurs tentatives
            url = "https://nominatim.openstreetmap.org/search"
            company_email = self.env.company.email or ''
            headers = {'User-Agent': 'OdooIntervention/1.0'}
            
            result_found = False
            lat, lon = None, None
            
            for idx, adresse_test in enumerate(adresses_a_tester):
                _logger.info(f"Tentative {idx+1}/{len(adresses_a_tester)} de géocodage: {adresse_test}")
                
                params = {
                    'q': adresse_test,
                    'format': 'json',
                    'limit': 3,  # Augmenter à 3 pour avoir plus de résultats
                    'addressdetails': 1,
                    'countrycodes': 'fr',  # Priorité France
                }
                
                if company_email:
                    params['email'] = company_email
                
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data and len(data) > 0:
                            # Prendre le premier résultat
                            lat = float(data[0]['lat'])
                            lon = float(data[0]['lon'])
                            result_found = True
                            _logger.info(f"✓ Géocodage réussi: lat={lat}, lon={lon}")
                            break
                    
                    # Pause entre les requêtes pour respecter l'usage de Nominatim
                    import time
                    time.sleep(0.5)
                    
                except requests.RequestException as e:
                    _logger.warning(f"Erreur tentative {idx+1}: {str(e)}")
                    continue
            
            if result_found and lat and lon:
                self.latitude = lat
                self.longitude = lon
                
                # Sauvegarder dans le cache
                try:
                    cache_key = hashlib.sha1(adresse_join.encode('utf-8')).hexdigest()
                    self.env['intervention.geocoding.cache'].sudo().create({
                        'cache_key': cache_key,
                        'address': adresse_join,
                        'latitude': self.latitude,
                        'longitude': self.longitude,
                    })
                    _logger.info(f"Coordonnées sauvegardées dans le cache")
                except Exception as e:
                    _logger.warning(f"Erreur sauvegarde cache: {str(e)}")
            else:
                # Aucune tentative n'a réussi
                raise UserError(
                    f"Adresse non trouvée après {len(adresses_a_tester)} tentatives.\n"
                    f"Adresse recherchée: {adresse_join}\n\n"
                    f"Suggestions:\n"
                    f"• Vérifiez l'orthographe de la ville\n"
                    f"• Vérifiez le code postal\n"
                    f"• Essayez de simplifier l'adresse (retirez 'Immeuble...', 'Résidence...', etc.)\n"
                    f"• Ou saisissez manuellement les coordonnées GPS"
                )
                
        except requests.RequestException as e:
            raise UserError(f"Erreur de connexion au service de géocodage: {str(e)}")
        except ValueError as e:
            raise UserError(f"Erreur de traitement de la réponse: {str(e)}")
        except UserError:
            raise
        except Exception as e:
            raise UserError(f"Erreur lors du géocodage: {str(e)}")


    facturer_a = fields.Selection([
        ('donneur_ordre', "Donneur d'ordre"),
        ('client_final', "Client final"),
    ], string="Facturer à", default='donneur_ordre', required=True, help="Choix du partenaire à facturer")

    partner_to_invoice_id = fields.Many2one(
        'res.partner',
        string="Partenaire à facturer",
        compute='_compute_partner_to_invoice',
        store=True,
        help="Partenaire qui sera utilisé pour la facturation selon le choix 'Facturer à'"
    )


    donneur_ordre_id = fields.Many2one(
        'res.partner',
        string="Donneur d'ordre",
        required=True,
        help="Partenaire qui commande l'intervention"
    )


    client_final_id = fields.Many2one(
        'res.partner',
        string="Client final",
        required=False,
        help="Client final de l'intervention (peut être identique au donneur d'ordre)"
    )


    numero_donneur_ordre = fields.Char(
        string="N° donneur d'ordre",
        help="Numéro d'intervention du donneur d'ordre (facultatif)",
        index=True
    )

    company_id = fields.Many2one(
        'res.company',
        string="Société",
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    # Adresse d'intervention
    adresse_intervention = fields.Text(
        string="Adresse d'intervention",
        required=True
    )

    # Adresse de l'entreprise (point de départ) - depuis les paramètres société
    adresse_entreprise = fields.Text(
        string="Adresse entreprise",
        compute="_compute_adresse_entreprise",
        help="Adresse de départ pour calculer la distance et la navigation (depuis les paramètres de la société)"
    )

    # Champs pour géolocalisation et navigation
    latitude = fields.Float(string="Latitude", digits=(16, 6))
    longitude = fields.Float(string="Longitude", digits=(16, 6))
    distance_km = fields.Float(
        string="Distance (km)",
        digits=(10, 2),
        help="Distance calculée via Waze depuis la société"
    )
    duree_trajet_min = fields.Integer(
        string="Durée trajet (min)",
        help="Durée estimée du trajet via Waze"
    )
    lien_waze = fields.Char(
        string="Lien Waze",
        compute='_compute_lien_waze',
        store=True
    )
    lien_google_maps = fields.Char(
        string="Lien Google Maps",
        compute='_compute_lien_google_maps',
        store=True
    )

    @api.depends('latitude', 'longitude')
    def _compute_lien_waze(self):
        """Générer le lien Waze pour navigation"""
        for record in self:
            if record.latitude and record.longitude:
                record.lien_waze = f"https://waze.com/ul?ll={record.latitude},{record.longitude}&navigate=yes"
            else:
                record.lien_waze = False

    @api.depends('latitude', 'longitude')
    def _compute_lien_google_maps(self):
        """Générer le lien Google Maps pour navigation depuis la société vers le client"""
        for record in self:
            partner = record.company_id.partner_id
            lat_soc = getattr(partner, 'partner_latitude', None)
            lon_soc = getattr(partner, 'partner_longitude', None)
            
            if lat_soc and lon_soc and record.latitude and record.longitude:
                record.lien_google_maps = (
                    f"https://www.google.com/maps/dir/?api=1"
                    f"&origin={lat_soc},{lon_soc}"
                    f"&destination={record.latitude},{record.longitude}"
                )
            else:
                record.lien_google_maps = False

    # Planning
    date_prevue = fields.Datetime(
        string="Date prévue",
        required=True,
        default=fields.Datetime.now,
        index=True
    )
    date_debut = fields.Datetime(string="Début réel")
    date_fin = fields.Datetime(string="Fin réelle")
    duree_prevue = fields.Float(string="Durée prévue (h)", default=lambda self: self._default_duree_prevue())
    duree_reelle = fields.Float(
        string="Durée réelle (h)", compute="_compute_duree_reelle", store=True)
    date_calendar_stop = fields.Datetime(string="Fin calendrier", compute="_compute_date_calendar_stop", store=True)

    # Type et statut
    type_intervention = fields.Selection([
        ('plomberie', 'Plomberie'),
        ('electricite', 'Électricité'),
        ('mixte', 'Plomberie + Électricité')
    ], string="Type d'intervention", required=True, default='plomberie')

    statut = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ], string="Statut", required=True, default='planifie')

    # Équipe
    technicien_principal_id = fields.Many2one(
        'hr.employee',
        string="Intervenant",
        required=True
    )

    # Description
    description = fields.Text(string="Description du problème")
    travaux_realises = fields.Text(string="Travaux réalisés")
    observations = fields.Text(string="Observations")

    # Matériaux
    materiel_ids = fields.One2many(
        'intervention.materiel',
        'intervention_id',
        string="Matériaux utilisés"
    )

    @api.depends('date_fin', 'date_prevue', 'duree_prevue')
    def _compute_date_calendar_stop(self):
        for rec in self:
            if rec.date_fin:
                rec.date_calendar_stop = rec.date_fin
            elif rec.date_prevue:
                rec.date_calendar_stop = rec.date_prevue + timedelta(hours=rec.duree_prevue or 2.0)
            else:
                rec.date_calendar_stop = False

    # Liens avec les ventes et facturation
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Commande de vente",
        help="Devis/Commande liée à cette intervention"
    )
    sale_order_count = fields.Integer(
        string="Nombre de devis",
        compute='_compute_sale_order_count'
    )
    invoice_ids = fields.Many2many(
        'account.move',
        string="Factures",
        domain=[('move_type', '=', 'out_invoice')],
        help="Factures liées à cette intervention"
    )
    invoice_count = fields.Integer(
        string="Nombre de factures",
        compute='_compute_invoice_count'
    )

    # Événement calendrier
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string="Événement calendrier",
        help="Événement calendrier associé à cette intervention"
    )

    # Validation client
    signature_client = fields.Binary(string="Signature client")
    validation_client = fields.Boolean(string="Validé par le client")

    # === NOUVEAUX CHAMPS POUR AMÉLIORATIONS ===
    
    # Gestion des photos
    photos_avant_ids = fields.Many2many(
        'ir.attachment',
        'intervention_photos_avant_rel',
        'intervention_id',
        'attachment_id',
        string="Photos avant intervention",
        help="Photos prises avant le début de l'intervention"
    )
    
    photos_apres_ids = fields.Many2many(
        'ir.attachment',
        'intervention_photos_apres_rel',
        'intervention_id', 
        'attachment_id',
        string="Photos après intervention",
        help="Photos prises après la fin de l'intervention"
    )
    
    photos_apres_count = fields.Integer(
        string="Nombre photos après",
        compute='_compute_photos_count',
        store=True
    )
    
    photos_avant_count = fields.Integer(
        string="Nombre photos avant", 
        compute='_compute_photos_count',
        store=True
    )

    # Rapport d'intervention
    rapport_intervention = fields.Html(
        string="Rapport d'intervention",
        help="Rapport détaillé de l'intervention (généré automatiquement ou saisi manuellement)"
    )
    
    # Géolocalisation et suivi terrain
    heure_arrivee = fields.Datetime(
        string="Heure d'arrivée sur site",
        help="Horodatage de l'arrivée du technicien sur le site"
    )
    
    position_technicien_lat = fields.Float(
        string="Position technicien - Latitude",
        digits=(16, 6),
        help="Position GPS du technicien (mise à jour automatique)"
    )
    
    position_technicien_lng = fields.Float(
        string="Position technicien - Longitude", 
        digits=(16, 6),
        help="Position GPS du technicien (mise à jour automatique)"
    )
    
    # Amélioration signature
    nom_signataire = fields.Char(
        string="Nom du signataire",
        help="Nom de la personne qui signe (client final ou représentant)"
    )
    
    date_signature = fields.Datetime(
        string="Date de signature",
        help="Date et heure de la signature du client"
    )
    
    # Statut de l'intervention sur terrain
    statut_terrain = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_route', 'En route'),
        ('sur_site', 'Sur site'),
        ('en_cours', 'Intervention en cours'),
        ('attente_validation', 'En attente de validation client'),
        ('termine', 'Terminé'),
        ('facture', 'Facturé')
    ], string="Statut terrain", default='planifie',
       help="Statut détaillé de l'intervention pour le suivi terrain")

    # Satisfaction client
    satisfaction_client = fields.Selection([
        ('1', '⭐ Très insatisfait'),
        ('2', '⭐⭐ Insatisfait'),
        ('3', '⭐⭐⭐ Correct'),
        ('4', '⭐⭐⭐⭐ Satisfait'),
        ('5', '⭐⭐⭐⭐⭐ Très satisfait')
    ], string="Satisfaction client", default='4', help="Niveau de satisfaction du client après intervention")

    # ===== MÉTHODES DEFAULT =====

    def _default_duree_prevue(self):
        """Récupérer la durée par défaut depuis les paramètres système"""
        duree = self.env['ir.config_parameter'].sudo().get_param('intervention.duree_intervention_defaut', default='1.0')
        try:
            return float(duree)
        except (ValueError, TypeError):
            return 1.0

    # ===== MÉTHODES COMPUTE =====

    @api.depends('company_id.street', 'company_id.street2', 'company_id.zip', 'company_id.city', 'company_id.country_id')
    def _compute_adresse_entreprise(self):
        """Récupérer l'adresse de l'entreprise depuis les paramètres"""
        for record in self:
            company = record.company_id
            adresse_parts = []
            if company.street:
                adresse_parts.append(company.street)
            if company.street2:
                adresse_parts.append(company.street2)
            if company.zip:
                adresse_parts.append(company.zip)
            if company.city:
                adresse_parts.append(company.city)
            if company.country_id:
                adresse_parts.append(company.country_id.name)

            record.adresse_entreprise = ', '.join(
                adresse_parts) if adresse_parts else "Adresse non configurée"

    @api.depends('date_debut', 'date_fin')
    def _compute_duree_reelle(self):
        for record in self:
            if record.date_debut and record.date_fin:
                delta = record.date_fin - record.date_debut
                record.duree_reelle = delta.total_seconds() / 3600
            else:
                record.duree_reelle = 0.0

    @api.depends('photos_avant_ids', 'photos_apres_ids')
    def _compute_photos_count(self):
        """Calculer le nombre de photos"""
        for record in self:
            record.photos_avant_count = len(record.photos_avant_ids)
            record.photos_apres_count = len(record.photos_apres_ids)

    @api.depends('sale_order_id')
    def _compute_sale_order_count(self):
        """Calculer le nombre de devis liés"""
        for record in self:
            record.sale_order_count = 1 if record.sale_order_id else 0

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        """Calculer le nombre de factures liées"""
        for record in self:
            record.invoice_count = len(record.invoice_ids)

    @api.depends('facturer_a', 'donneur_ordre_id', 'client_final_id')
    def _compute_partner_to_invoice(self):
        """Calculer le partenaire à facturer selon le choix"""
        for record in self:
            if record.facturer_a == 'client_final' and record.client_final_id:
                record.partner_to_invoice_id = record.client_final_id
            else:
                record.partner_to_invoice_id = record.donneur_ordre_id

    @api.onchange('facturer_a', 'client_final_id')
    def _onchange_facturer_a(self):
        """Mettre à jour automatiquement quand on change le choix de facturation"""
        if self.facturer_a == 'client_final' and not self.client_final_id:
            return {
                'warning': {
                    'title': 'Attention',
                    'message': 'Vous devez sélectionner un client final pour pouvoir le facturer.'
                }
            }

    @api.onchange('client_final_id', 'company_id')
    def _onchange_adresse_intervention(self):
        """Remplit l'adresse d'intervention et calcule la distance entre la société et le client final"""
        # Remplir automatiquement l'adresse d'intervention si vide ou si client change
        if self.client_final_id:
            adresse_client = self.client_final_id.contact_address or ''
            if not self.adresse_intervention or self.adresse_intervention.strip() == '' or self._origin and self.client_final_id != self._origin.client_final_id:
                self.adresse_intervention = adresse_client

        # Calcul de la distance désactivé (méthode manquante)
        # if self.client_final_id and self.company_id:
        #     self._calculer_distance_societe_client()

    def _haversine(self, lat1, lon1, lat2, lon2):
        """Calculer la distance à vol d'oiseau entre deux points GPS (en km)"""
        R = 6371.0  # Rayon de la Terre en km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    # === NOUVELLES ACTIONS POUR AMÉLIORATIONS ===
    
    def action_arrivee_site(self):
        """Marquer l'arrivée du technicien sur site avec géolocalisation"""
        self.ensure_one()
        
        # Marquer l'heure d'arrivée
        self.write({
            'heure_arrivee': fields.Datetime.now(),
            'statut_terrain': 'sur_site'
        })
        
        # Message de confirmation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '📍 Arrivée sur site',
                'message': f'Arrivée enregistrée à {fields.Datetime.now().strftime("%H:%M")}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_demarrer_intervention(self):
        """Démarrer l'intervention (nouveau statut détaillé)"""
        self.ensure_one()
        
        if self.statut_terrain in ['planifie', 'en_route', 'sur_site']:
            self.write({
                'statut_terrain': 'en_cours',
                'statut': 'en_cours',
                'date_debut': fields.Datetime.now()
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '🔧 Intervention démarrée',
                    'message': 'L\'intervention est maintenant en cours',
                    'type': 'info',
                    'sticky': False,
                }
            }
    
    def action_generer_rapport_pdf(self):
        """Génération automatique du rapport PDF d'intervention"""
        self.ensure_one()
        rapport_html = self._generate_report_html()
        return self.env.ref('intervention.action_rapport_intervention_pdf').report_action(
            self, 
            data={'rapport_html': rapport_html}
        )
    
    def action_envoyer_rapport_donneur_ordre(self):
        """Envoi automatique du rapport au donneur d'ordre"""
        self.ensure_one()
        
        # Collecte des emails (dédoublonnés)
        emails = set()
        if self.donneur_ordre_id and self.donneur_ordre_id.email:
            emails.add(self.donneur_ordre_id.email)
        if self.client_final_id and self.client_final_id.email:
            emails.add(self.client_final_id.email)
        if self.company_id and self.company_id.email:
            emails.add(self.company_id.email)
        
        if not emails:
            return self._display_notification(
                '⚠️ Email manquant',
                'Aucune adresse email renseignée pour les destinataires',
                'warning',
                sticky=True
            )
        
        # Envoi du rapport via template email
        template = self.env.ref('intervention.email_template_rapport_intervention', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            return self._display_notification(
                '📧 Rapport envoyé',
                f'Rapport envoyé à {", ".join(emails)}',
                'success'
            )
        else:
            return self._display_notification(
                '⚠️ Template manquant',
                'Template d\'email non configuré',
                'warning',
                sticky=True
            )
    
    def action_validation_client(self):
        """Action pour validation et signature client"""
        self.ensure_one()
        # Ouvre le wizard de validation client (signature sur mobile)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Validation Client',
            'res_model': 'intervention.validation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_intervention_id': self.id,
                'default_nom_signataire': self.client_final_id.name if self.client_final_id else self.donneur_ordre_id.name,
            }
        }
        # Après validation, envoie le rapport par mail à tous les destinataires
        if self.validation_client:
            self.action_send_report()
        return action

    # Actions

    def action_commencer(self):
        """Démarrer une intervention (passer de planifié à en cours)"""
        self.ensure_one()
        for record in self:
            if record.statut == 'planifie':
                record.statut = 'en_cours'
                record.date_debut = fields.Datetime.now()
        return True

    def action_terminer(self):
        """Terminer une intervention (passer à terminé)"""
        self.ensure_one()
        for record in self:
            if record.statut == 'en_cours':
                record.statut = 'termine'
                record.date_fin = fields.Datetime.now()
        return True

    def action_annuler(self):
        """Annuler une intervention (le client ou donneur d'ordre a annulé la commande)"""
        self.ensure_one()
        
        # Vérifier qu'on peut annuler (pas déjà terminée ou facturée)
        if self.statut == 'termine':
            raise UserError(
                "Impossible d'annuler une intervention déjà terminée.\n"
                "Si vous souhaitez vraiment l'annuler, contactez un administrateur."
            )
        
        if self.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
            raise UserError(
                "Impossible d'annuler une intervention déjà facturée.\n"
                "Vous devez d'abord annuler ou créditer la facture."
            )
        
        # Passer au statut annulé
        self.write({
            'statut': 'annule',
            'statut_terrain': 'planifie',  # Réinitialiser le statut terrain
        })
        
        # Annuler l'événement calendrier s'il existe
        if self.calendar_event_id:
            self.calendar_event_id.write({
                'name': f"[ANNULÉ] {self.calendar_event_id.name}",
                'active': False
            })
        
        # Envoyer une notification
        motif_text = 'client final' if self.facturer_a == 'client_final' else "donneur d'ordre"
        self.message_post(
            body=f"<p>✖️ Intervention annulée par {self.env.user.name}</p>"
                 f"<p>Motif: Annulation par le {motif_text}</p>",
            subject=f"Annulation intervention {self.numero}",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✖️ Intervention annulée',
                'message': f'L\'intervention {self.numero} a été annulée',
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_replanifier(self):
        """Réactiver une intervention annulée et la remettre au statut planifié"""
        self.ensure_one()
        
        # Vérifier que l'intervention est bien annulée
        if self.statut != 'annule':
            raise UserError(
                "Cette action est réservée aux interventions annulées.\n"
                f"Statut actuel : {dict(self._fields['statut'].selection).get(self.statut)}"
            )
        
        # Vérifier qu'on a toujours les informations minimales
        if not self.date_prevue:
            raise UserError(
                "Veuillez d'abord définir une nouvelle date d'intervention avant de la réactiver."
            )
        
        if not self.technicien_principal_id:
            raise UserError(
                "Veuillez d'abord assigner un technicien avant de réactiver l'intervention."
            )
        
        # Remettre au statut planifié
        self.write({
            'statut': 'planifie',
            'statut_terrain': 'planifie',
            'date_debut': False,  # Réinitialiser les dates
            'date_fin': False,
            'heure_arrivee': False,
        })
        
        # Réactiver ou recréer l'événement calendrier
        if self.calendar_event_id:
            # Supprimer le préfixe [ANNULÉ] si présent
            nom_event = self.calendar_event_id.name.replace('[ANNULÉ] ', '')
            self.calendar_event_id.write({
                'name': nom_event,
                'active': True,
                'start': self.date_prevue,
                'stop': self.date_prevue + timedelta(hours=self.duree_prevue or 2.0),
            })
        else:
            # Créer un nouvel événement calendrier
            try:
                self._create_calendar_event()
            except Exception as e:
                _logger.warning(f"Impossible de créer l'événement calendrier: {str(e)}")
        
        # Envoyer une notification
        motif_text = 'client final' if self.facturer_a == 'client_final' else "donneur d'ordre"
        self.message_post(
            body=f"<p>🔄 Intervention réactivée par {self.env.user.name}</p>"
                 f"<p>Le {motif_text} a redemandé cette intervention</p>"
                 f"<p>Nouvelle date : {self.date_prevue.strftime('%d/%m/%Y %H:%M') if self.date_prevue else 'Non définie'}</p>",
            subject=f"Réactivation intervention {self.numero}",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '🔄 Intervention réactivée',
                'message': f'L\'intervention {self.numero} a été remise au statut "Planifié"',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def create(self, vals):
        # Odoo 19 : peut recevoir une liste de dicts ou un dict
        if isinstance(vals, list):
            interventions = self.browse()
            for val in vals:
                if val.get('numero', '/') in (False, '/', ''):
                    numero_genere = self.env['ir.sequence'].next_by_code('intervention.intervention') or '/'
                    _logger.warning(f"[DEBUG INTERVENTION] Génération numéro (batch): {numero_genere}")
                    val['numero'] = numero_genere
                else:
                    _logger.warning(f"[DEBUG INTERVENTION] Numéro fourni (batch): {val.get('numero')}")
                interventions += super(InterventionIntervention, self).create(val)
            return interventions

        # Contrôle d'accès global intervention
        if not self.env.user.has_group('base.group_system') and not self.check_intervention_access('create'):
            raise AccessError("Vous n'avez pas le droit de créer une intervention.")

        # Contrôle rapport
        if 'rapport_intervention' in vals and not self.check_intervention_access('create', section='rapport'):
            raise AccessError("Vous n'avez pas le droit de créer un rapport d'intervention.")

        # Création intervention
        if vals.get('numero', '/') in (False, '/', ''):
            numero_genere = self.env['ir.sequence'].next_by_code('intervention.intervention') or '/'
            _logger.warning(f"[DEBUG INTERVENTION] Génération numéro: {numero_genere}")
            vals['numero'] = numero_genere
        else:
            _logger.warning(f"[DEBUG INTERVENTION] Numéro fourni: {vals.get('numero')}")
        intervention = super(InterventionIntervention, self).create(vals)
        # Créer automatiquement l'événement calendrier si une date est prévue
        if intervention.date_prevue and intervention.technicien_principal_id:
            try:
                intervention._create_calendar_event()
            except Exception:
                pass
        return intervention

    def write(self, vals):
        """Override write pour gérer les contrôles d'accès et mises à jour automatiques"""
        # Contrôle d'accès global
        if not self.env.user.has_group('base.group_system') and not self.check_intervention_access('write'):
            raise AccessError("Vous n'avez pas le droit de modifier une intervention.")

        # Contrôle rapport
        if 'rapport_intervention' in vals and not self.check_intervention_access('write', section='rapport'):
            raise AccessError("Vous n'avez pas le droit de modifier le rapport d'intervention.")

        # Contrôle photos : modification/suppression impossible après première saisie (sauf si droit accordé)
        champs_exclus = ['adresse_intervention', 'latitude', 'longitude', 'distance_km', 'duree_trajet_min']
        
        for champ_photo in ["photos_avant_ids", "photos_apres_ids"]:
            if champ_photo in vals and champ_photo not in champs_exclus:
                for rec in self:
                    if getattr(rec, champ_photo) and not self.check_intervention_access('write', section='photo'):
                        raise AccessError("Modification ou suppression des photos impossible après la première saisie.")

        for champ in ['heure_arrivee', 'date_debut', 'date_fin']:
            if champ in vals and champ not in champs_exclus:
                for rec in self:
                    if getattr(rec, champ) and not self.check_intervention_access('write', section='heure'):
                        raise AccessError("Modification ou suppression de l'heure impossible après la première saisie.")
        
        res = super(InterventionIntervention, self).write(vals)
        
        # Gestion automatique du statut terrain si toutes les photos sont supprimées
        for rec in self:
            if (('photos_avant_ids' in vals or 'photos_apres_ids' in vals)
                and not rec.photos_avant_ids and not rec.photos_apres_ids):
                if rec.statut_terrain == 'en_cours':
                    rec.statut_terrain = 'sur_site'
        
        # Mise à jour de l'événement calendrier si nécessaire
        calendar_fields = [
            'date_prevue', 'duree_prevue', 'technicien_principal_id',
            'donneur_ordre_id', 'client_final_id', 'adresse_intervention',
            'description', 'type_intervention'
        ]
        if any(field in vals for field in calendar_fields):
            for record in self:
                if record.calendar_event_id:
                    try:
                        record._update_calendar_event()
                    except Exception as e:
                        _logger.warning(f"Erreur mise à jour calendrier: {str(e)}")
        
        # Géolocalisation automatique si adresse change
        if 'adresse_intervention' in vals:
            for record in self:
                if record.adresse_intervention and not record.latitude:
                    try:
                        record._geocoder_adresse()
                    except Exception as e:
                        _logger.warning(f"Erreur géocodage auto: {str(e)}")
        
        return res
    def unlink(self):
        # Contrôle d'accès global intervention
        if not self.env.user.has_group('base.group_system') and not self.check_intervention_access('unlink'):
            raise AccessError("Vous n'avez pas le droit de supprimer une intervention.")

        # Suppression impossible si heure ou photos déjà saisies (sauf admin)
        for rec in self:
            if (rec.heure_arrivee or rec.date_debut or rec.date_fin) and not self.check_intervention_access('unlink', section='heure'):
                raise AccessError("Suppression impossible : heure déjà saisie.")
            if (rec.photos_avant_ids or rec.photos_apres_ids) and not self.check_intervention_access('unlink', section='photo'):
                raise AccessError("Suppression impossible : photos déjà saisies.")

        # Contrôle rapport (suppression)
        if any(self.rapport_intervention for self in self) and not self.check_intervention_access('unlink', section='rapport'):
            raise AccessError("Vous n'avez pas le droit de supprimer le rapport d'intervention.")

        return super(InterventionIntervention, self).unlink()



    def action_create_sale_order(self):
        """Créer un devis/commande de vente liée à l intervention avec les bonnes pratiques Odoo"""
        self.ensure_one()
        if not self.partner_to_invoice_id:
            raise models.UserError("Veuillez d'abord sélectionner qui facturer (donneur d'ordre ou client final).")
        
        if self.facturer_a == 'client_final' and not self.client_final_id:
            raise models.UserError("Veuillez sélectionner un client final pour pouvoir le facturer.")
        
        if self.sale_order_id:
            raise models.UserError("Un devis est déjà créé pour cette intervention.")
        
        # Utiliser le partenaire à facturer
        partner_to_use = self.partner_to_invoice_id
        
        # Créer le devis avec les informations de l'intervention
        client_order_ref = f"INT-{self.numero}"
        if self.numero_donneur_ordre:
            client_order_ref = f"{self.numero_donneur_ordre} (INT-{self.numero})"
        
        sale_order_vals = {
            'partner_id': partner_to_use.id,
            'origin': self.numero,  # Référence à l'intervention
            'client_order_ref': client_order_ref,
            'note': f"Devis généré automatiquement pour l'intervention {self.numero}\n"
                   f"Donneur d'ordre: {self.donneur_ordre_id.name}\n"
                   f"Client final: {self.client_final_id.name if self.client_final_id else 'N/A'}\n"
                   f"Facturer à: {dict(self._fields['facturer_a'].selection).get(self.facturer_a)}\n"
                   + (f"N° donneur d'ordre: {self.numero_donneur_ordre}\n" if self.numero_donneur_ordre else "")
                   + f"Type: {dict(self._fields['type_intervention'].selection).get(self.type_intervention, '')}\n"
                   f"Adresse intervention: {self.adresse_intervention}\n"
                   f"Description: {self.description or ''}",
            'date_order': fields.Datetime.now(),
            'validity_date': fields.Date.today() + timedelta(days=30),  # Validité 30 jours
        }
        
        sale_order = self.env['sale.order'].create(sale_order_vals)
        
        # Ajouter une ligne de service pour l'intervention
        service_product = self._get_or_create_intervention_product()
        if service_product:
            sale_line_vals = {
                'order_id': sale_order.id,
                'product_id': service_product.id,
                'name': f"Intervention {self.type_intervention.title()} - {self.numero}",
                'product_uom_qty': self.duree_prevue or 1.0,
                'product_uom': service_product.uom_id.id,
                'price_unit': service_product.list_price,
                'tax_id': [(6, 0, service_product.taxes_id.ids)],
            }
            self.env['sale.order.line'].create(sale_line_vals)
        
        # Lier l'intervention au devis
        self.sale_order_id = sale_order.id
        
        # Retourner l'action pour ouvrir le devis
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': partner_to_use.id,
                'intervention_id': self.id,
            }
        }

    def _get_or_create_intervention_product(self):
        """Récupérer ou créer le produit service pour les interventions"""
        # Chercher d'abord un produit existant
        service_product = self.env['product.product'].search([
            ('name', 'ilike', f'Intervention {self.type_intervention}'),
            ('type', '=', 'service')
        ], limit=1)
        
        if not service_product:
            # Chercher une catégorie de services existante
            service_category = self.env['product.category'].search([
                ('name', 'ilike', 'service')
            ], limit=1)
            
            # Si pas de catégorie service, utiliser la première catégorie disponible
            if not service_category:
                service_category = self.env['product.category'].search([], limit=1)
            
            # Créer un produit service générique
            product_vals = {
                'name': f'Service Intervention {self.type_intervention.title()}',
                'type': 'service',
                'categ_id': service_category.id if service_category else False,
                'uom_id': self.env.ref('uom.product_uom_hour').id,  # Heures
                'uom_po_id': self.env.ref('uom.product_uom_hour').id,
                'list_price': 50.0,  # Prix par défaut
                'standard_price': 30.0,  # Coût par défaut
                'sale_ok': True,
                'purchase_ok': False,
                'invoice_policy': 'delivery',
                'description_sale': f'Service d\'intervention {self.type_intervention}',
            }
            service_product = self.env['product.product'].create(product_vals)
        
        return service_product

    def action_create_invoice(self):
        """Créer une facture pour l intervention en utilisant le workflow Odoo standard"""
        self.ensure_one()
        
        # Si on a un devis confirmé, créer la facture depuis le devis
        if self.sale_order_id and self.sale_order_id.state in ['sale', 'done']:
            # Utiliser le workflow standard de facturation
            if self.sale_order_id.invoice_status == 'to invoice':
                return self.sale_order_id.action_invoice_create()
            else:
                return self.action_view_invoices()
        
        # Sinon créer une facture directe
        if not self.partner_to_invoice_id:
            raise models.UserError("Veuillez d'abord sélectionner qui facturer (donneur d'ordre ou client final).")
        
        if self.facturer_a == 'client_final' and not self.client_final_id:
            raise models.UserError("Veuillez sélectionner un client final pour pouvoir le facturer.")
        
        # Utiliser le partenaire à facturer
        partner_to_use = self.partner_to_invoice_id
        
        # Construire la référence avec le numéro donneur d'ordre si disponible
        invoice_ref = f"Intervention {self.numero}"
        if self.numero_donneur_ordre:
            invoice_ref = f"{self.numero_donneur_ordre} - {invoice_ref}"
        
        # Créer la facture avec le bon workflow Odoo
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner_to_use.id,
            'ref': invoice_ref,
            'invoice_origin': self.numero,
            'narration': f"Facture pour intervention {self.numero}\n"
                        f"Donneur d'ordre: {self.donneur_ordre_id.name}\n"
                        f"Client final: {self.client_final_id.name if self.client_final_id else 'N/A'}\n"
                        f"Facturer à: {dict(self._fields['facturer_a'].selection).get(self.facturer_a)}\n"
                        + (f"N° donneur d'ordre: {self.numero_donneur_ordre}\n" if self.numero_donneur_ordre else "")
                        + f"Type: {dict(self._fields['type_intervention'].selection).get(self.type_intervention, '')}\n"
                        f"Adresse: {self.adresse_intervention}\n"
                        f"Description: {self.description or ''}",
            'invoice_date': fields.Date.today(),
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        
        # Ajouter une ligne de facture pour l'intervention
        service_product = self._get_or_create_intervention_product()
        if service_product:
            invoice_line_vals = {
                'move_id': invoice.id,
                'product_id': service_product.id,
                'name': f"Intervention {self.type_intervention.title()} - {self.numero}",
                'quantity': self.duree_reelle or self.duree_prevue or 1.0,
                'product_uom_id': service_product.uom_id.id,
                'price_unit': service_product.list_price,
                'tax_ids': [(6, 0, service_product.taxes_id.ids)],
            }
            self.env['account.move.line'].create(invoice_line_vals)
        
        # Lier la facture à l'intervention
        self.write({'invoice_ids': [(4, invoice.id)]})
        
        # Retourner l'action pour ouvrir la facture
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_move_type': 'out_invoice',
                'default_partner_id': partner_to_use.id,
                'intervention_id': self.id,
            }
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # (Suppression de la version obsolète de action_calculer_distance, doublon inutile)


    def _calculer_distance_waze(self):
        """Calcul rapide de la distance et durée (vol d'oiseau avec estimation route)"""
        if not self.latitude or not self.longitude:
            return
        
        partner = self.company_id.partner_id
        lat_soc = getattr(partner, 'partner_latitude', None)
        lon_soc = getattr(partner, 'partner_longitude', None)
        
        if not lat_soc or not lon_soc:
            # Fallback Paris si société non géocodée
            lat_soc, lon_soc = 48.8566, 2.3522
        
        # Calcul Haversine (vol d'oiseau)
        distance = self._haversine(lat_soc, lon_soc, self.latitude, self.longitude)
        self.distance_km = round(distance, 2)
        
        # Durée estimée (2 min/km, minimum 1 min)
        self.duree_trajet_min = max(int(distance * 2), 1)

    def action_create_calendar_event(self):
        """Action pour créer manuellement un événement calendrier"""
        self.ensure_one()
        if self.calendar_event_id:
            return self.action_view_calendar_event()
        
        event = self._create_calendar_event()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'res_id': event.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _create_calendar_event(self):
        """Créer un événement calendrier pour cette intervention"""
        if self.calendar_event_id:
            return self.calendar_event_id
        
        # Définir la durée (par défaut 2h si pas de durée prévue)
        from datetime import timedelta
        duree = self.duree_prevue or 2.0
        date_fin = self.date_prevue + timedelta(hours=duree)
        
        # Préparer les données de l'événement
        event_vals = {
            'name': f"[{self.numero}] {self.type_intervention}",
            'description': f"Intervention {self.numero}\n"
                          f"Client: {self.donneur_ordre_id.name}\n"
                          f"Adresse: {self.adresse_intervention or 'Non renseignée'}\n"
                          f"Type: {self.type_intervention}\n"
                          f"Description: {self.description or ''}",
            'start': self.date_prevue,
            'stop': date_fin,
            'allday': False,
            'user_id': self.technicien_principal_id.user_id.id if self.technicien_principal_id.user_id else self.env.user.id,
            'partner_ids': [(6, 0, [self.donneur_ordre_id.id] + 
                           ([self.client_final_id.id] if self.client_final_id and self.client_final_id != self.donneur_ordre_id else []))],
            'location': self.adresse_intervention,
            'categ_ids': self._get_calendar_category(),
        }
        
        # Créer l'événement
        event = self.env['calendar.event'].create(event_vals)
        self.calendar_event_id = event
        return event

    def _get_calendar_category(self):
        """Obtenir ou créer une catégorie calendrier pour les interventions"""
        category = self.env['calendar.event.type'].search([('name', '=', 'Interventions Plomberie')], limit=1)
        if not category:
            category = self.env['calendar.event.type'].create({
                'name': 'Interventions Plomberie',
                'color': 3,  # Couleur bleue
            })
        return [(6, 0, [category.id])]

    def action_view_calendar_event(self):
        """Ouvrir l'événement calendrier associé"""
        self.ensure_one()
        if not self.calendar_event_id:
            self._create_calendar_event()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'res_id': self.calendar_event_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'create': False}
        }
    
    def validate_client_signature(self, nom_signataire=None, signature_client=None, travaux_realises=None, observations_client=None, satisfaction_client=None, date_signature=None):
        """Valide la signature client et enregistre les informations transmises par le wizard"""
        self.ensure_one()
        vals = {
            'signature_client': signature_client,
            'validation_client': True,
            'nom_signataire': nom_signataire or self.client_final_id.name,
            'date_signature': date_signature or fields.Datetime.now(),
            'statut': 'termine',  # Passer le statut à terminé
            'statut_terrain': 'termine',  # Passer le statut terrain à terminé aussi
        }
        if travaux_realises:
            vals['travaux_realises'] = travaux_realises
        if observations_client:
            vals['observations'] = observations_client
        if satisfaction_client:
            vals['satisfaction_client'] = satisfaction_client
        self.write(vals)
        # Optionnel : envoyer le rapport par mail après validation
        self.action_send_report()

    def action_open_technician_portal(self):
        """Ouvre le portail technicien dans un nouvel onglet"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/intervention/technicien',
            'target': 'new',
        }

