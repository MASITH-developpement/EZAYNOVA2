# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FunnelCreationWizard(models.TransientModel):
    _name = 'funnel.creation.wizard'
    _description = 'Assistant de Création de Tunnel de Vente avec IA'

    # ============================================
    # ÉTAPES DU WIZARD
    # ============================================

    current_step = fields.Selection([
        ('1_basic', 'Étape 1: Informations de base'),
        ('2_landing', 'Étape 2: Page d\'accueil'),
        ('3_steps', 'Étape 3: Étapes du tunnel'),
        ('4_fields', 'Étape 4: Champs du formulaire'),
        ('5_thank_you', 'Étape 5: Page de remerciement'),
        ('6_preview', 'Étape 6: Prévisualisation'),
    ], string='Étape actuelle', default='1_basic', required=True)

    # ============================================
    # ÉTAPE 1: INFORMATIONS DE BASE
    # ============================================

    # Template pré-configuré
    template_id = fields.Selection([
        ('lead_gen', 'Génération de leads (3 étapes)'),
        ('qualification', 'Qualification prospect (5 étapes)'),
        ('download', 'Téléchargement ressource (2 étapes)'),
        ('quote', 'Demande de devis (4 étapes)'),
    ], string='Template de départ')

    # Informations de base
    name = fields.Char(string='Nom du tunnel', required=True,
                      help='Ex: "Télécharger notre guide gratuit"')
    funnel_type = fields.Selection([
        ('lead_generation', 'Génération de leads'),
        ('qualification', 'Qualification de prospects'),
        ('survey', 'Enquête/Questionnaire'),
        ('registration', 'Inscription'),
        ('quote', 'Demande de devis'),
        ('download', 'Téléchargement de ressource'),
        ('contact', 'Formulaire de contact'),
        ('other', 'Autre')
    ], string='Type de tunnel', default='lead_generation', required=True)

    target_goal = fields.Char(string='Objectif cible',
                              help='Ex: "Collecter 100 emails par mois"')
    target_audience = fields.Char(string='Public cible',
                                  help='Ex: "Entrepreneurs, TPE/PME"')

    # Description avec IA
    description = fields.Html(string='Description manuelle')
    ai_generated_description = fields.Html(string='Description générée par IA', readonly=True)
    use_ai_description = fields.Boolean(string='Utiliser la description IA')

    # ============================================
    # ÉTAPE 2: PAGE D'ACCUEIL (LANDING PAGE)
    # ============================================

    landing_title = fields.Char(string='Titre principal', default='Bienvenue')
    landing_subtitle = fields.Char(string='Sous-titre')
    landing_content = fields.Html(string='Contenu de la landing page')

    # Contenu généré par IA
    ai_generated_landing = fields.Html(string='Landing page générée par IA', readonly=True)
    use_ai_landing = fields.Boolean(string='Utiliser la landing page IA')

    show_progress_bar = fields.Boolean(string='Afficher barre de progression', default=True)

    # ============================================
    # ÉTAPE 3: ÉTAPES DU TUNNEL
    # ============================================

    # Nombre d'étapes
    step_count = fields.Integer(string='Nombre d\'étapes', default=3,
                                help='Entre 1 et 10 étapes')

    # Suggestions d'étapes par IA
    ai_suggested_steps = fields.Text(string='Étapes suggérées par IA', readonly=True)

    # Configuration des étapes (stockage JSON simplifié)
    step_1_name = fields.Char(string='Nom étape 1', default='Informations de contact')
    step_1_description = fields.Text(string='Description étape 1')

    step_2_name = fields.Char(string='Nom étape 2', default='Vos besoins')
    step_2_description = fields.Text(string='Description étape 2')

    step_3_name = fields.Char(string='Nom étape 3', default='Confirmation')
    step_3_description = fields.Text(string='Description étape 3')

    step_4_name = fields.Char(string='Nom étape 4')
    step_4_description = fields.Text(string='Description étape 4')

    step_5_name = fields.Char(string='Nom étape 5')
    step_5_description = fields.Text(string='Description étape 5')

    # ============================================
    # ÉTAPE 4: CHAMPS DU FORMULAIRE
    # ============================================

    # Champs standards
    include_name = fields.Boolean(string='Nom', default=True)
    include_email = fields.Boolean(string='Email', default=True)
    include_phone = fields.Boolean(string='Téléphone', default=True)
    include_company = fields.Boolean(string='Entreprise', default=False)
    include_message = fields.Boolean(string='Message', default=True)

    # Champs personnalisés suggérés par IA
    ai_suggested_fields = fields.Text(string='Champs suggérés par IA', readonly=True)
    custom_fields = fields.Text(string='Champs personnalisés (un par ligne)')

    # ============================================
    # ÉTAPE 5: PAGE DE REMERCIEMENT
    # ============================================

    thank_you_title = fields.Char(string='Titre de remerciement',
                                  default='Merci !')
    thank_you_message = fields.Html(string='Message de remerciement')

    # Message généré par IA
    ai_generated_thank_you = fields.Html(string='Message généré par IA', readonly=True)
    use_ai_thank_you = fields.Boolean(string='Utiliser le message IA')

    redirect_url = fields.Char(string='URL de redirection (optionnel)')

    # Actions automatiques
    create_lead = fields.Boolean(string='Créer une opportunité CRM', default=True)
    create_contact = fields.Boolean(string='Créer un contact', default=True)

    # ============================================
    # ÉTAPE 6: PRÉVISUALISATION
    # ============================================

    preview_html = fields.Html(string='Aperçu du tunnel', compute='_compute_preview_html')

    # ============================================
    # MÉTHODES COMPUTE
    # ============================================

    @api.depends('name', 'landing_title', 'landing_content', 'step_count',
                 'step_1_name', 'step_2_name', 'step_3_name')
    def _compute_preview_html(self):
        """Générer l'aperçu HTML du tunnel"""
        for record in self:
            # Déterminer le contenu de la landing page
            landing = record.landing_content or record.ai_generated_landing or '<p>Pas de contenu défini</p>'

            # Construire la liste des étapes
            steps_html = ''
            for i in range(1, min(record.step_count + 1, 6)):
                step_name = getattr(record, f'step_{i}_name', None)
                if step_name:
                    steps_html += f'<li><strong>Étape {i}:</strong> {step_name}</li>'

            # Construire l'aperçu complet
            preview = f"""
            <div style="max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           color: white; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 32px;">{record.landing_title or 'Titre principal'}</h1>
                    {f'<p style="margin: 10px 0 0 0; font-size: 18px;">{record.landing_subtitle}</p>' if record.landing_subtitle else ''}
                </div>

                <!-- Barre de progression -->
                {'''<div style="background: #f8f9fa; padding: 15px;">
                    <div style="background: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: #667eea; width: 0%; height: 100%;"></div>
                    </div>
                    <p style="text-align: center; margin: 5px 0 0 0; font-size: 12px; color: #6c757d;">
                        Étape 1 sur {record.step_count}
                    </p>
                </div>''' if record.show_progress_bar else ''}

                <!-- Contenu de la landing page -->
                <div style="padding: 30px; background: white;">
                    {landing}
                </div>

                <!-- Étapes du tunnel -->
                <div style="padding: 30px; background: #f8f9fa;">
                    <h3 style="margin-top: 0; color: #495057;">🎯 Étapes du tunnel ({record.step_count} étapes)</h3>
                    <ol style="color: #6c757d;">
                        {steps_html}
                    </ol>
                </div>

                <!-- Page de remerciement -->
                <div style="padding: 30px; background: white; border-top: 3px solid #667eea;">
                    <h3 style="margin-top: 0; color: #495057;">✅ {record.thank_you_title or 'Merci !'}</h3>
                    {record.thank_you_message or record.ai_generated_thank_you or '<p>Message de remerciement</p>'}
                </div>

                <!-- Footer -->
                <div style="padding: 20px; background: #343a40; color: white; text-align: center;
                           border-radius: 0 0 10px 10px;">
                    <p style="margin: 0; font-size: 14px;">
                        🚀 Tunnel créé avec <strong>{record.name or 'EAZYNOVA'}</strong>
                    </p>
                </div>
            </div>
            """
            record.preview_html = preview

    # ============================================
    # MÉTHODES IA - ÉTAPE 1
    # ============================================

    def action_generate_description(self):
        """Générer une description avec l'IA"""
        self.ensure_one()

        if not self.name:
            raise UserError(_("Veuillez d'abord saisir le nom du tunnel."))

        try:
            ai_service = self.env['ai.text.generator']

            # Construire le prompt
            context_info = {
                'funnel_name': self.name,
                'funnel_type': dict(self._fields['funnel_type'].selection).get(self.funnel_type),
                'target_goal': self.target_goal or 'non spécifié',
                'target_audience': self.target_audience or 'grand public',
            }

            description = ai_service.generate_funnel_description(
                self.name,
                self.funnel_type,
                self.target_goal,
                self.target_audience
            )

            self.ai_generated_description = f"<p>{description}</p>"
            self.use_ai_description = True

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Description générée avec succès !'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    # ============================================
    # MÉTHODES IA - ÉTAPE 2
    # ============================================

    def action_generate_landing_page(self):
        """Générer une landing page avec l'IA"""
        self.ensure_one()

        if not self.name:
            raise UserError(_("Veuillez d'abord saisir le nom du tunnel."))

        try:
            ai_service = self.env['ai.text.generator']

            landing_html = ai_service.generate_funnel_landing_page(
                self.name,
                self.funnel_type,
                self.target_goal or 'conversion maximale'
            )

            self.ai_generated_landing = landing_html
            self.use_ai_landing = True

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Landing page générée avec succès !'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    # ============================================
    # MÉTHODES IA - ÉTAPE 3
    # ============================================

    def action_suggest_steps(self):
        """Suggérer des étapes avec l'IA"""
        self.ensure_one()

        try:
            ai_service = self.env['ai.service']

            # Construire le contexte
            context = f"""
Tunnel de vente: {self.name}
Type: {dict(self._fields['funnel_type'].selection).get(self.funnel_type)}
Objectif: {self.target_goal or 'Collecte d\'informations'}
Public cible: {self.target_audience or 'Grand public'}
Nombre d'étapes souhaité: {self.step_count}
"""

            prompt = f"""
Contexte:
{context}

Suggère {self.step_count} étapes progressives et logiques pour ce tunnel de vente.
Pour chaque étape, fournis:
- Un nom court et clair
- Une brève description de l'objectif de l'étape

Format de réponse souhaité (texte simple):
Étape 1: [Nom] - [Description]
Étape 2: [Nom] - [Description]
etc.
"""

            suggestions = ai_service.generate_text(prompt, max_tokens=500)

            self.ai_suggested_steps = suggestions

            # Parser les suggestions et remplir automatiquement (optionnel)
            lines = suggestions.strip().split('\n')
            for i, line in enumerate(lines[:self.step_count], start=1):
                if ':' in line and i <= 5:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        # Extraire le nom (après "Étape X:")
                        name_and_desc = parts[1].strip()
                        if ' - ' in name_and_desc:
                            name, desc = name_and_desc.split(' - ', 1)
                            setattr(self, f'step_{i}_name', name.strip())
                            setattr(self, f'step_{i}_description', desc.strip())

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Étapes suggérées avec succès !'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    # ============================================
    # MÉTHODES IA - ÉTAPE 4
    # ============================================

    def action_suggest_fields(self):
        """Suggérer des champs de formulaire avec l'IA"""
        self.ensure_one()

        try:
            ai_service = self.env['ai.service']

            context = f"""
Tunnel: {self.name}
Type: {dict(self._fields['funnel_type'].selection).get(self.funnel_type)}
Public cible: {self.target_audience or 'Grand public'}
"""

            prompt = f"""
Contexte:
{context}

Suggère 3-5 champs personnalisés pertinents pour ce formulaire, en plus des champs standards (nom, email, téléphone).

Réponds au format:
- [Nom du champ]: [Type] - [Pourquoi ce champ est utile]

Exemple:
- Taille de l'entreprise: Liste déroulante - Permet de qualifier le lead
- Budget disponible: Champ numérique - Aide à prioriser les opportunités
"""

            suggestions = ai_service.generate_text(prompt, max_tokens=300)

            self.ai_suggested_fields = suggestions

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Champs suggérés avec succès !'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    # ============================================
    # MÉTHODES IA - ÉTAPE 5
    # ============================================

    def action_generate_thank_you_message(self):
        """Générer un message de remerciement avec l'IA"""
        self.ensure_one()

        try:
            ai_service = self.env['ai.service']

            prompt = f"""
Crée un message de remerciement HTML engageant pour un tunnel de vente nommé "{self.name}".

Le message doit:
- Remercier l'utilisateur pour sa soumission
- Être chaleureux et professionnel
- Indiquer les prochaines étapes (ex: "Nous vous contacterons sous 24h")
- Être formaté en HTML simple (paragraphes, gras, listes)
- Faire environ 100-150 mots

Format HTML uniquement, sans balise <html> ou <body>.
"""

            message = ai_service.generate_text(prompt, max_tokens=300)

            self.ai_generated_thank_you = message
            self.use_ai_thank_you = True

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Message de remerciement généré !'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Erreur lors de la génération: %s") % str(e))

    # ============================================
    # NAVIGATION ENTRE ÉTAPES
    # ============================================

    def action_next_step(self):
        """Passer à l'étape suivante"""
        self.ensure_one()

        steps = ['1_basic', '2_landing', '3_steps', '4_fields', '5_thank_you', '6_preview']
        current_index = steps.index(self.current_step)

        if current_index < len(steps) - 1:
            self.current_step = steps[current_index + 1]

        return {
            'type': 'ir.actions.do_nothing',
        }

    def action_previous_step(self):
        """Revenir à l'étape précédente"""
        self.ensure_one()

        steps = ['1_basic', '2_landing', '3_steps', '4_fields', '5_thank_you', '6_preview']
        current_index = steps.index(self.current_step)

        if current_index > 0:
            self.current_step = steps[current_index - 1]

        return {
            'type': 'ir.actions.do_nothing',
        }

    # ============================================
    # TEMPLATES PRÉ-CONFIGURÉS
    # ============================================

    def action_apply_template(self):
        """Appliquer un template pré-configuré"""
        self.ensure_one()

        templates = {
            'lead_gen': {
                'name': 'Génération de Leads',
                'funnel_type': 'lead_generation',
                'target_goal': 'Collecter 100 emails/mois',
                'landing_title': 'Téléchargez notre guide gratuit',
                'landing_subtitle': 'Découvrez les secrets de la croissance',
                'step_count': 3,
                'step_1_name': 'Vos coordonnées',
                'step_2_name': 'Votre situation',
                'step_3_name': 'Confirmation',
                'include_name': True,
                'include_email': True,
                'include_company': True,
            },
            'qualification': {
                'name': 'Qualification de Prospects',
                'funnel_type': 'qualification',
                'target_goal': 'Qualifier 50 prospects/mois',
                'landing_title': 'Êtes-vous prêt à passer à l\'étape suivante ?',
                'landing_subtitle': 'Répondez à quelques questions',
                'step_count': 5,
                'step_1_name': 'Informations de contact',
                'step_2_name': 'Votre entreprise',
                'step_3_name': 'Vos besoins',
                'step_4_name': 'Budget et timing',
                'step_5_name': 'Confirmation',
                'include_name': True,
                'include_email': True,
                'include_phone': True,
                'include_company': True,
            },
            'download': {
                'name': 'Téléchargement Ressource',
                'funnel_type': 'download',
                'target_goal': 'Téléchargements de ressources',
                'landing_title': 'Téléchargez votre ressource gratuite',
                'landing_subtitle': 'Accédez immédiatement à votre contenu',
                'step_count': 2,
                'step_1_name': 'Vos informations',
                'step_2_name': 'Téléchargement',
                'include_name': True,
                'include_email': True,
            },
            'quote': {
                'name': 'Demande de Devis',
                'funnel_type': 'quote',
                'target_goal': 'Recevoir 20 demandes de devis/mois',
                'landing_title': 'Obtenez votre devis gratuit',
                'landing_subtitle': 'En moins de 2 minutes',
                'step_count': 4,
                'step_1_name': 'Vos coordonnées',
                'step_2_name': 'Votre projet',
                'step_3_name': 'Budget et délais',
                'step_4_name': 'Validation',
                'include_name': True,
                'include_email': True,
                'include_phone': True,
                'include_company': True,
            },
        }

        if self.template_id and self.template_id in templates:
            template_data = templates[self.template_id]
            for field, value in template_data.items():
                if hasattr(self, field):
                    setattr(self, field, value)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Template appliqué'),
                    'message': _('Le template a été appliqué avec succès !'),
                    'type': 'success',
                }
            }

    # ============================================
    # CRÉATION DU TUNNEL
    # ============================================

    def action_create_funnel(self):
        """Créer le tunnel de vente final"""
        self.ensure_one()

        # Validation
        if not self.name:
            raise UserError(_("Le nom du tunnel est obligatoire."))

        # Déterminer les contenus finaux
        final_description = self.ai_generated_description if self.use_ai_description else self.description
        final_landing = self.ai_generated_landing if self.use_ai_landing else self.landing_content
        final_thank_you = self.ai_generated_thank_you if self.use_ai_thank_you else self.thank_you_message

        # Créer le tunnel
        funnel = self.env['sales.funnel'].create([{
            'name': self.name,
            'funnel_type': self.funnel_type,
            'description': final_description,
            'landing_title': self.landing_title,
            'landing_subtitle': self.landing_subtitle,
            'landing_content': final_landing,
            'show_progress_bar': self.show_progress_bar,
            'thank_you_title': self.thank_you_title,
            'thank_you_message': final_thank_you,
            'redirect_url': self.redirect_url,
            'create_lead': self.create_lead,
            'create_contact': self.create_contact,
        }])

        # Créer les étapes du tunnel
        sequence = 10
        for i in range(1, min(self.step_count + 1, 6)):
            step_name = getattr(self, f'step_{i}_name', None)
            step_desc = getattr(self, f'step_{i}_description', None)

            if step_name:
                self.env['sales.funnel.step'].create([{
                    'funnel_id': funnel.id,
                    'name': step_name,
                    'description': step_desc,
                    'sequence': sequence,
                }])
                sequence += 10

        # Message de succès
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tunnel créé !'),
                'message': _('Votre tunnel "%s" a été créé avec succès !') % self.name,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'sales.funnel',
                    'res_id': funnel.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
            }
        }
