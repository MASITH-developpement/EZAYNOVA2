# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta
import json


class WebsiteBookingController(http.Controller):

    @http.route('/booking', type='http', auth='public', website=True)
    def booking_list(self, **kwargs):
        """Liste des types de rendez-vous disponibles"""
        booking_types = request.env['booking.type'].sudo().search([
            ('active', '=', True)
        ], order='sequence, name')

        return request.render('website_booking.booking_list_page', {
            'booking_types': booking_types,
        })

    @http.route('/booking/<int:booking_type_id>', type='http', auth='public', website=True)
    def booking_page(self, booking_type_id, **kwargs):
        """Page de réservation pour un type de rendez-vous"""
        booking_type = request.env['booking.type'].sudo().browse(booking_type_id)

        if not booking_type.exists() or not booking_type.active:
            return request.render('website.404')

        return request.render('website_booking.booking_page', {
            'booking_type': booking_type,
        })

    @http.route('/booking/<int:booking_type_id>/slots', type='json', auth='public')
    def get_available_slots(self, booking_type_id, date=None, user_id=None, **kwargs):
        """Retourne les créneaux disponibles pour une date donnée"""
        booking_type = request.env['booking.type'].sudo().browse(booking_type_id)

        if not booking_type.exists():
            return {'error': 'Type de rendez-vous non trouvé'}

        # Date par défaut : aujourd'hui
        if not date:
            target_date = datetime.now().date()
        else:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Vérifier les contraintes de réservation
        now = datetime.now()
        min_date = now + timedelta(hours=booking_type.min_schedule_hours)
        max_date = now + timedelta(days=booking_type.max_schedule_days)

        if target_date < min_date.date() or target_date > max_date.date():
            return {'slots': []}

        # Déterminer l'utilisateur (tous ou un spécifique)
        if user_id:
            users = request.env['res.users'].sudo().browse(user_id)
        else:
            users = booking_type.user_ids

        if not users:
            return {'slots': []}

        # Récupérer les créneaux pour chaque utilisateur
        all_slots = []
        weekday = str(target_date.weekday())

        for user in users:
            # Récupérer les disponibilités de l'utilisateur pour ce jour
            availabilities = request.env['booking.availability'].sudo().search([
                ('user_id', '=', user.id),
                ('weekday', '=', weekday),
                ('active', '=', True)
            ])

            for availability in availabilities:
                # Générer les créneaux pour cette plage de disponibilité
                slots = self._generate_slots(
                    target_date,
                    availability.hour_from,
                    availability.hour_to,
                    booking_type.duration,
                    user,
                    booking_type
                )
                all_slots.extend(slots)

        # Trier les créneaux par heure
        all_slots.sort(key=lambda x: x['datetime'])

        return {'slots': all_slots}

    def _generate_slots(self, date, hour_from, hour_to, duration, user, booking_type):
        """Génère les créneaux disponibles pour une plage horaire"""
        slots = []
        current_hour = hour_from

        while current_hour + duration <= hour_to:
            # Créer le datetime du créneau
            slot_datetime = datetime.combine(date, datetime.min.time()) + timedelta(hours=current_hour)
            slot_end = slot_datetime + timedelta(hours=duration)

            # Vérifier si le créneau n'est pas dans le passé
            if slot_datetime > datetime.now() + timedelta(hours=booking_type.min_schedule_hours):
                # Vérifier si le créneau est disponible (pas de conflit)
                conflicts = request.env['booking.appointment'].sudo().search([
                    ('user_id', '=', user.id),
                    ('state', 'in', ['confirmed', 'draft']),
                    ('start_datetime', '<', slot_end),
                    ('end_datetime', '>', slot_datetime)
                ])

                if not conflicts:
                    slots.append({
                        'datetime': slot_datetime.isoformat(),
                        'time': slot_datetime.strftime('%H:%M'),
                        'user_id': user.id,
                        'user_name': user.name
                    })

            # Passer au créneau suivant (incrément de 30 minutes)
            current_hour += 0.5

        return slots

    @http.route('/booking/<int:booking_type_id>/book', type='json', auth='public', website=True)
    def book_appointment(self, booking_type_id, **kwargs):
        """Créer un rendez-vous"""
        booking_type = request.env['booking.type'].sudo().browse(booking_type_id)

        if not booking_type.exists():
            return {'error': 'Type de rendez-vous non trouvé'}

        # Validation des données
        required_fields = ['datetime', 'user_id', 'name', 'email']
        for field in required_fields:
            if not kwargs.get(field):
                return {'error': f'Le champ {field} est requis'}

        try:
            start_datetime = datetime.fromisoformat(kwargs['datetime'].replace('Z', '+00:00'))
        except:
            return {'error': 'Format de date invalide'}

        # Créer le contact si l'email n'existe pas
        partner = request.env['res.partner'].sudo().search([
            ('email', '=', kwargs['email'])
        ], limit=1)

        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': kwargs['name'],
                'email': kwargs['email'],
                'phone': kwargs.get('phone', ''),
                'company_name': kwargs.get('company', ''),
            })

        # Créer le rendez-vous
        appointment = request.env['booking.appointment'].sudo().create({
            'booking_type_id': booking_type_id,
            'start_datetime': start_datetime,
            'user_id': int(kwargs['user_id']),
            'partner_id': partner.id,
            'partner_name': kwargs['name'],
            'partner_email': kwargs['email'],
            'partner_phone': kwargs.get('phone', ''),
            'partner_company': kwargs.get('company', ''),
            'message': kwargs.get('message', ''),
            'state': 'draft',
        })

        # Confirmer le rendez-vous
        appointment.action_confirm()

        return {
            'success': True,
            'appointment_id': appointment.id,
            'confirmation_url': f'/booking/confirmation/{appointment.id}/{appointment.access_token}'
        }

    @http.route('/booking/confirmation/<int:appointment_id>/<string:token>', type='http', auth='public', website=True)
    def booking_confirmation(self, appointment_id, token, **kwargs):
        """Page de confirmation de rendez-vous"""
        appointment = request.env['booking.appointment'].sudo().search([
            ('id', '=', appointment_id),
            ('access_token', '=', token)
        ], limit=1)

        if not appointment:
            return request.render('website.404')

        return request.render('website_booking.booking_confirmation_page', {
            'appointment': appointment,
        })

    @http.route('/booking/cancel/<int:appointment_id>/<string:token>', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def cancel_appointment(self, appointment_id, token, **kwargs):
        """Annuler un rendez-vous"""
        appointment = request.env['booking.appointment'].sudo().search([
            ('id', '=', appointment_id),
            ('access_token', '=', token)
        ], limit=1)

        if not appointment:
            return request.render('website.404')

        if not appointment.booking_type_id.allow_cancel:
            return request.render('website_booking.booking_cancel_not_allowed', {
                'appointment': appointment,
            })

        # Vérifier le délai d'annulation
        cancel_deadline = appointment.start_datetime - timedelta(hours=appointment.booking_type_id.cancel_hours)
        if datetime.now() > cancel_deadline:
            return request.render('website_booking.booking_cancel_too_late', {
                'appointment': appointment,
            })

        if request.httprequest.method == 'POST':
            appointment.action_cancel()
            return request.render('website_booking.booking_cancelled_page', {
                'appointment': appointment,
            })

        return request.render('website_booking.booking_cancel_confirm', {
            'appointment': appointment,
        })

    @http.route('/booking/reschedule/<int:appointment_id>/<string:token>', type='http', auth='public', website=True)
    def reschedule_appointment(self, appointment_id, token, **kwargs):
        """Reprogrammer un rendez-vous"""
        appointment = request.env['booking.appointment'].sudo().search([
            ('id', '=', appointment_id),
            ('access_token', '=', token)
        ], limit=1)

        if not appointment:
            return request.render('website.404')

        if not appointment.booking_type_id.allow_reschedule:
            return request.render('website_booking.booking_reschedule_not_allowed', {
                'appointment': appointment,
            })

        return request.render('website_booking.booking_reschedule_page', {
            'appointment': appointment,
            'booking_type': appointment.booking_type_id,
        })
