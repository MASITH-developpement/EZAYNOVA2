# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BookingTypeCreationWizard(models.TransientModel):
    _name = 'booking.type.creation.wizard'
    _description = 'Assistant de Création de Type de Rendez-vous avec IA'

    # Navigation
    current_step = fields.Selection([
        ('1_basic', 'Étape 1: Informations de base'),
        ('2_availability', 'Étape 2: Disponibilités'),
        ('3_questions', 'Étape 3: Questions personnalisées'),
        ('4_landing', 'Étape 4: Page d\'accueil'),
        ('5_notifications', 'Étape 5: Notifications'),
        ('6_preview', 'Étape 6: Prévisualisation'),
    ], string='Étape actuelle', default='1_basic', required=True)

    # Étape 1: Informations de base
    name = fields.Char(
        string='Nom du type de rendez-vous',
        required=True,
        help="Ex: Consultation 30 minutes"
    )
    duration = fields.Float(
        string='Durée (heures)',
        default=0.5,
        required=True
    )
    target_audience = fields.Char(
        string='Public cible',
        help="Ex: Particuliers, Professionnels, Étudiants..."
    )
    description = fields.Html(
        string='Description'
    )
    ai_generated_description = fields.Html(
        string='Description générée par IA',
        readonly=True
    )
    use_ai_description = fields.Boolean(
        string='Utiliser la description IA',
        default=False
    )

    # Étape 2: Disponibilités
    allow_monday = fields.Boolean('Lundi', default=True)
    allow_tuesday = fields.Boolean('Mardi', default=True)
    allow_wednesday = fields.Boolean('Mercredi', default=True)
    allow_thursday = fields.Boolean('Jeudi', default=True)
    allow_friday = fields.Boolean('Vendredi', default=True)
    allow_saturday = fields.Boolean('Samedi', default=False)
    allow_sunday = fields.Boolean('Dimanche', default=False)

    start_time = fields.Float(
        string='Heure de début',
        default=9.0,
        help="Format 24h (ex: 9.0 = 9h00, 13.5 = 13h30)"
    )
    end_time = fields.Float(
        string='Heure de fin',
        default=17.0
    )
    buffer_time = fields.Float(
        string='Temps de battement (minutes)',
        default=0,
        help="Temps entre deux rendez-vous"
    )

    # Étape 3: Questions personnalisées
    ask_phone = fields.Boolean('Demander le téléphone', default=True)
    ask_company = fields.Boolean('Demander l\'entreprise', default=False)
    ask_message = fields.Boolean('Demander un message', default=True)
    custom_questions = fields.Text(
        string='Questions personnalisées (une par ligne)'
    )
    ai_generated_questions = fields.Text(
        string='Questions générées par IA',
        readonly=True
    )

    # Étape 4: Page d'accueil
    landing_title = fields.Char(
        string='Titre de la page',
        default=lambda self: "Réserver un rendez-vous"
    )
    landing_content = fields.Html(
        string='Contenu de la page d\'accueil'
    )
    ai_generated_landing = fields.Html(
        string='Page générée par IA',
        readonly=True
    )
    generate_icon = fields.Boolean(
        string='Générer une icône avec l\'IA',
        default=False
    )
    icon_data = fields.Binary(
        string='Icône personnalisée'
    )

    # Étape 5: Notifications
    send_confirmation = fields.Boolean(
        string='Envoyer email de confirmation',
        default=True
    )
    send_reminder = fields.Boolean(
        string='Envoyer rappel avant RDV',
        default=True
    )
    reminder_hours = fields.Integer(
        string='Heures avant le RDV',
        default=24
    )
    confirmation_email_subject = fields.Char(
        string='Sujet email confirmation'
    )
    confirmation_email_body = fields.Html(
        string='Corps email confirmation'
    )
    ai_generated_email = fields.Html(
        string='Email généré par IA',
        readonly=True
    )

    # Étape 6: Prévisualisation
    preview_html = fields.Html(
        string='Aperçu',
        compute='_compute_preview_html'
    )

    # Template sélectionné
    template_id = fields.Selection([
        ('meeting_15', 'Réunion Express 15 min'),
        ('consultation_30', 'Consultation 30 min'),
        ('discovery_60', 'Rendez-vous Découverte 1h'),
        ('workshop_120', 'Workshop 2h'),
    ], string='Template pré-configuré')

    def action_apply_template(self):
        """Appliquer un template pré-configuré"""
        self.ensure_one()

        templates = {
            'meeting_15': {
                'name': 'Réunion Express',
                'duration': 0.25,
                'target_audience': 'Professionnels',
                'description': '<p>Réunion rapide de 15 minutes pour échanger sur un sujet précis.</p>',
                'ask_company': True,
                'landing_title': 'Réservez une réunion express de 15 minutes',
            },
            'consultation_30': {
                'name': 'Consultation',
                'duration': 0.5,
                'target_audience': 'Général',
                'description': '<p>Consultation personnalisée de 30 minutes.</p>',
                'landing_title': 'Réservez votre consultation de 30 minutes',
            },
            'discovery_60': {
                'name': 'Rendez-vous Découverte',
                'duration': 1.0,
                'target_audience': 'Nouveaux clients',
                'description': '<p>Rendez-vous d\'une heure pour mieux vous connaître et comprendre vos besoins.</p>',
                'landing_title': 'Découvrons comment nous pouvons vous aider',
            },
            'workshop_120': {
                'name': 'Workshop',
                'duration': 2.0,
                'target_audience': 'Groupes',
                'description': '<p>Atelier de 2 heures pour approfondir un sujet.</p>',
                'landing_title': 'Participez à notre workshop',
            },
        }

        if self.template_id and self.template_id in templates:
            template = templates[self.template_id]
            for key, value in template.items():
                setattr(self, key, value)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Template appliqué!'),
                    'message': _('Le template a été chargé. Vous pouvez maintenant le personnaliser.'),
                    'type': 'success',
                }
            }

    def action_generate_description(self):
        """Générer une description avec l'IA"""
        self.ensure_one()

        if not self.name:
            raise UserError(_("Veuillez d'abord entrer un nom pour le type de rendez-vous"))

        try:
            ai_service = self.env['ai.text.generator']
            description = ai_service.generate_booking_description(
                self.name,
                self.duration * 60,  # Convertir en minutes
                self.target_audience
            )

            self.ai_generated_description = f"<p>{description}</p>"
            self.use_ai_description = True

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Description générée!'),
                    'message': _('L\'IA a généré une description optimisée.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(
                "Erreur lors de la génération: %s\n\n"
                "Vérifiez que le module AI Assistant est installé et configuré."
            ) % str(e))

    def action_generate_questions(self):
        """Générer des questions avec l'IA"""
        self.ensure_one()

        if not self.name:
            raise UserError(_("Veuillez d'abord entrer un nom pour le type de rendez-vous"))

        try:
            ai_service = self.env['ai.service']
            context = f"{self.name} - {self.target_audience or 'général'}"
            questions_list = ai_service.generate_questions(context, count=3)

            # Convertir en texte simple
            questions_text = "\n".join([q['question'] for q in questions_list])
            self.ai_generated_questions = questions_text

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Questions générées!'),
                    'message': _('L\'IA a suggéré 3 questions pertinentes.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    def action_generate_landing_page(self):
        """Générer une page d'accueil avec l'IA"""
        self.ensure_one()

        if not self.name:
            raise UserError(_("Veuillez d'abord entrer un nom"))

        try:
            ai_service = self.env['ai.text.generator']
            # Utiliser une méthode générique
            prompt = f"""
Crée le contenu HTML d'une page d'accueil engageante pour un type de rendez-vous nommé "{self.name}".

Durée: {self.duration * 60} minutes
Public: {self.target_audience or 'général'}

Inclus:
- Un paragraphe d'introduction chaleureux
- 3 bullet points des bénéfices
- Un appel à l'action

Format: HTML simple, professionnel et persuasif.
"""
            content = ai_service.generate(prompt, max_tokens=400)
            self.ai_generated_landing = content

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Page générée!'),
                    'message': _('L\'IA a créé une page d\'accueil optimisée.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    def action_generate_email_template(self):
        """Générer un template d'email avec l'IA"""
        self.ensure_one()

        if not self.name:
            raise UserError(_("Veuillez d'abord entrer un nom"))

        try:
            ai_service = self.env['ai.text.generator']
            context_data = {
                'booking_type': self.name,
                'duration': f"{self.duration * 60} minutes",
            }

            email_data = ai_service.generate_email_template(
                'confirmation de rendez-vous',
                context_data
            )

            self.confirmation_email_subject = email_data.get('subject', 'Confirmation de votre rendez-vous')
            self.ai_generated_email = f"<p>{email_data.get('body', '')}</p>"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Email généré!'),
                    'message': _('L\'IA a créé un template d\'email professionnel.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    @api.depends('name', 'duration', 'description', 'landing_content')
    def _compute_preview_html(self):
        """Générer l'aperçu HTML"""
        for record in self:
            preview = f"""
            <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
                <h1 style="color: #333;">{record.name or 'Votre rendez-vous'}</h1>
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0;">
                    <p><strong>⏱ Durée:</strong> {int(record.duration * 60)} minutes</p>
                    <p><strong>📅 Disponibilités:</strong> {', '.join([d for d, enabled in [
                        ('Lun', record.allow_monday), ('Mar', record.allow_tuesday),
                        ('Mer', record.allow_wednesday), ('Jeu', record.allow_thursday),
                        ('Ven', record.allow_friday), ('Sam', record.allow_saturday),
                        ('Dim', record.allow_sunday)
                    ] if enabled])}</p>
                    <p><strong>🕐 Horaires:</strong> {int(record.start_time)}h - {int(record.end_time)}h</p>
                </div>
                <div style="margin: 20px 0;">
                    {record.description or record.ai_generated_description or '<p>Aucune description</p>'}
                </div>
                <div style="margin: 20px 0;">
                    {record.landing_content or record.ai_generated_landing or ''}
                </div>
            </div>
            """
            record.preview_html = preview

    def action_next_step(self):
        """Passer à l'étape suivante"""
        self.ensure_one()

        steps = ['1_basic', '2_availability', '3_questions', '4_landing', '5_notifications', '6_preview']
        current_index = steps.index(self.current_step)

        if current_index < len(steps) - 1:
            self.current_step = steps[current_index + 1]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'booking.type.creation.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_previous_step(self):
        """Revenir à l'étape précédente"""
        self.ensure_one()

        steps = ['1_basic', '2_availability', '3_questions', '4_landing', '5_notifications', '6_preview']
        current_index = steps.index(self.current_step)

        if current_index > 0:
            self.current_step = steps[current_index - 1]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'booking.type.creation.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_booking_type(self):
        """Créer le type de rendez-vous"""
        self.ensure_one()

        # Utiliser la description IA si cochée
        final_description = self.ai_generated_description if self.use_ai_description else self.description

        # Créer le type de rendez-vous
        booking_type = self.env['booking.type'].create({
            'name': self.name,
            'duration': self.duration,
            'description': final_description,
            'allow_monday': self.allow_monday,
            'allow_tuesday': self.allow_tuesday,
            'allow_wednesday': self.allow_wednesday,
            'allow_thursday': self.allow_thursday,
            'allow_friday': self.allow_friday,
            'allow_saturday': self.allow_saturday,
            'allow_sunday': self.allow_sunday,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'buffer_time': self.buffer_time,
            'ask_phone': self.ask_phone,
            'ask_company': self.ask_company,
            'ask_message': self.ask_message,
            'send_confirmation': self.send_confirmation,
            'send_reminder': self.send_reminder,
            'reminder_hours': self.reminder_hours,
            'landing_title': self.landing_title,
            'landing_content': self.landing_content or self.ai_generated_landing,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Type de Rendez-vous Créé'),
            'res_model': 'booking.type',
            'res_id': booking_type.id,
            'view_mode': 'form',
            'target': 'current',
        }
