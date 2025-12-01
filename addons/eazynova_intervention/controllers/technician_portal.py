# -*- coding: utf-8 -*-

import base64
from odoo import http
from odoo.http import request

class TechnicianPortal(http.Controller):
    @http.route('/intervention/technicien/validation_client/<int:intervention_id>', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def technician_validation_client(self, intervention_id, **post):
        intervention = request.env['intervention.intervention'].sudo().browse(intervention_id)
        error = False
        if request.httprequest.method == 'POST':
            nom_signataire = post.get('nom_signataire')
            satisfaction_client = post.get('satisfaction_client')
            travaux_realises = post.get('travaux_realises')
            observations_client = post.get('observations_client')
            signature_dataurl = post.get('signature_client')
            # Validation minimale
            if not (nom_signataire and satisfaction_client and travaux_realises and signature_dataurl and signature_dataurl.startswith('data:image/png')):
                error = True
            else:
                # Enregistrer les infos sur l'intervention
                intervention.write({
                    'nom_signataire': nom_signataire,
                    'satisfaction_client': satisfaction_client,
                    'travaux_realises': travaux_realises,
                    'observations_client': observations_client,
                    'statut_terrain': 'termine',
                })
                # Enregistrer la signature en pièce jointe sécurisée
                import base64, re
                signature_b64 = re.sub('^data:image/png;base64,', '', signature_dataurl)
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': f'Signature_Client_Intervention_{intervention_id}.png',
                    'datas': signature_b64,
                    'res_model': 'intervention.intervention',
                    'res_id': intervention.id,
                    'mimetype': 'image/png',
                    'type': 'binary',
                    'public': False,
                })
                # Rediriger vers la page de confirmation ou d'envoi de rapport (à faire ensuite)
                return request.redirect(f'/intervention/technicien/rapport_envoye/{intervention_id}')
        return request.render('eazynova_intervention.technician_validation_client_template', {
            'intervention_id': intervention_id,
            'error': error,
        })
    @http.route('/intervention/technicien/photos_apres/<int:intervention_id>', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def technician_photos_apres(self, intervention_id, **post):
        intervention = request.env['intervention.intervention'].sudo().browse(intervention_id)
        error = False
        if request.httprequest.method == 'POST':
            files = request.httprequest.files
            photo1 = files.get('photo1')
            photo2 = files.get('photo2')
            if not photo1 or not photo2:
                error = True
            else:
                attachments = []
                for photo in [photo1, photo2]:
                    datas = base64.b64encode(photo.read()).decode() if hasattr(photo, 'read') else False
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': photo.filename,
                        'datas': datas,
                        'res_model': 'intervention.intervention',
                        'res_id': intervention.id,
                        'mimetype': photo.mimetype,
                    })
                    attachments.append(attachment.id)
                if attachments:
                    intervention.write({'photos_apres_ids': [(4, att_id) for att_id in attachments]})
                # Rediriger vers la validation client (à faire ensuite)
                return request.redirect(f'/intervention/technicien/validation_client/{intervention_id}')
        return request.render('eazynova_intervention.technician_photos_apres_template', {
            'intervention_id': intervention_id,
            'error': error,
        })
    @http.route('/intervention/technicien', type='http', auth='user', website=True)
    def technician_dashboard(self, **kw):
        user = request.env.user
        # Récupère les interventions assignées au technicien connecté
        # Lire uniquement les champs nécessaires côté intervention pour le dashboard
        interventions = request.env['intervention.intervention'].sudo().search_read([
            ('technicien_principal_id.user_id', '=', user.id),
            ('statut_terrain', 'in', ['planifie', 'en_route', 'sur_site', 'en_cours'])
        ], [
            'id', 'numero', 'date_prevue', 'statut_terrain', 'client_final_id', 'donneur_ordre_id',
            'adresse_intervention', 'distance_km', 'duree_trajet_min', 'lien_waze', 'lien_google_maps'
        ])
        # Récupérer les partenaires clients référencés afin d'éviter des read() multiples
        client_ids = [i['client_final_id'][0] for i in interventions if i.get('client_final_id')]
        partner_map = {}
        if client_ids:
            partners = request.env['res.partner'].sudo().search_read([('id', 'in', client_ids)], ['id', 'name', 'email', 'phone'])
            partner_map = {p['id']: p for p in partners}
        # Préparer mapping intervention_id -> client fields
        client_fields = {}
        for i in interventions:
            cid = i.get('client_final_id') and i.get('client_final_id')[0]
            if cid:
                client_fields[i['id']] = partner_map.get(cid, {})
        # Formatage date prévue pour affichage (évite format_datetime en QWeb)
        from datetime import datetime
        for i in interventions:
            date_str = i.get('date_prevue')
            if date_str:
                try:
                    # Odoo format: 'YYYY-MM-DD HH:MM:SS'
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    i['date_prevue_fmt'] = dt.strftime('%d/%m/%Y %H:%M')
                except Exception:
                    i['date_prevue_fmt'] = date_str
            else:
                i['date_prevue_fmt'] = ''
        return request.render('eazynova_intervention.technician_portal_template', {
            'interventions': interventions,
            'user': user,
            'client_fields': client_fields,
        })

    @http.route('/intervention/technicien/arrivee/<int:intervention_id>', type='http', auth='user', website=True, csrf=False, methods=['POST'])
    def technician_arrivee(self, intervention_id, **kw):
        intervention = request.env['intervention.intervention'].sudo().browse(intervention_id)
        if intervention and intervention.statut_terrain in ['planifie', 'en_route']:
            intervention.write({'statut_terrain': 'sur_site'})
        # Rediriger vers la page d'upload des photos avant intervention
        return request.redirect(f'/intervention/technicien/photos_avant/{intervention_id}')

    @http.route('/intervention/technicien/photos_avant/<int:intervention_id>', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def technician_photos_avant(self, intervention_id, **post):
        intervention = request.env['intervention.intervention'].sudo().browse(intervention_id)
        error = False
        if request.httprequest.method == 'POST':
            files = request.httprequest.files
            photo1 = files.get('photo1')
            photo2 = files.get('photo2')
            if not photo1 or not photo2:
                error = True
            else:
                attachments = []
                for photo in [photo1, photo2]:
                    datas = base64.b64encode(photo.read()).decode() if hasattr(photo, 'read') else False
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': photo.filename,
                        'datas': datas,
                        'res_model': 'intervention.intervention',
                        'res_id': intervention.id,
                        'mimetype': photo.mimetype,
                    })
                    attachments.append(attachment.id)
                if attachments:
                    intervention.write({'photos_avant_ids': [(4, att_id) for att_id in attachments]})
                # Rediriger vers la saisie du rapport après upload des photos avant
                return request.redirect(f'/intervention/technicien/rapport/{intervention_id}')
        return request.render('eazynova_intervention.technician_photos_avant_template', {
            'intervention_id': intervention_id,
            'error': error,
        })

    @http.route('/intervention/technicien/rapport/<int:intervention_id>', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def technician_rapport(self, intervention_id, **post):
        intervention = request.env['intervention.intervention'].sudo().browse(intervention_id)
        error = False
        # Charger les produits de la société et du métier de la demande
        # (ici, on prend tous les produits actifs de la société, filtrage métier possible si besoin)
        products = request.env['product.product'].sudo().search_read([
            ('active', '=', True),
            ('company_id', 'in', [intervention.company_id.id, False]),
        ], ['id', 'display_name'])
        if request.httprequest.method == 'POST':
            rapport = post.get('rapport')
            materiel_ids = request.httprequest.form.getlist('materiel')
            if not rapport or not materiel_ids:
                error = True
            elif 'none' in materiel_ids:
                # Cas : Pas de matériel utilisé
                intervention.write({
                    'rapport_intervention': rapport,
                    'materiel_ids': [(5, 0, 0)],  # Vide le champ One2many
                })
                return request.redirect(f'/intervention/technicien/photos_apres/{intervention_id}')
            else:
                # Enregistrer le rapport et le matériel utilisé
                intervention.write({
                    'rapport_intervention': rapport,
                    'materiel_ids': [(6, 0, [int(mid) for mid in materiel_ids])],
                })
                # Rediriger vers l'upload des photos après intervention
                return request.redirect(f'/intervention/technicien/photos_apres/{intervention_id}')
        return request.render('eazynova_intervention.technician_rapport_template', {
            'intervention_id': intervention_id,
            'products': products,
            'error': error,
        })
