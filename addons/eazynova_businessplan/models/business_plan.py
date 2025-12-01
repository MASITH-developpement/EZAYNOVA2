# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BusinessPlan(models.Model):
    _name = 'business.plan'
    _description = 'Business Plan'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    # ========== INFORMATIONS GÉNÉRALES ==========
    name = fields.Char(string='Nom du projet / entreprise', required=True, tracking=True)
    reference = fields.Char(string='Référence', readonly=True, copy=False, default='Nouveau')
    user_id = fields.Many2one('res.users', string='Porteur du projet', default=lambda self: self.env.user, required=True)

    date_start = fields.Date(string='Date de début', required=True, default=fields.Date.today)
    date_end = fields.Date(string='Date de fin', required=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('done', 'Terminé'),
    ], string='État', default='draft', required=True, tracking=True)

    # ========== 1. RÉSUMÉ EXÉCUTIF ==========
    executive_summary = fields.Text(
        string='Résumé exécutif',
        help='Synthèse du projet en quelques lignes (objectif, marché, avantage concurrentiel)')

    # ========== 2. PRÉSENTATION DU PROJET ==========
    project_description = fields.Text(
        string='Description du projet',
        help='Décrivez votre projet en détail : quelle est votre activité, votre vision ?')

    legal_form = fields.Selection([
        ('individual', 'Entreprise individuelle'),
        ('eurl', 'EURL'),
        ('sarl', 'SARL'),
        ('sas', 'SAS'),
        ('sa', 'SA'),
        ('other', 'Autre'),
    ], string='Forme juridique')

    location = fields.Char(string='Localisation', help='Où sera basée votre entreprise ?')

    # ========== 3. PRODUITS ET SERVICES ==========
    products_services = fields.Text(
        string='Produits et services',
        help='Décrivez vos produits/services : que vendez-vous ? Quelles sont leurs caractéristiques ?')

    value_proposition = fields.Text(
        string='Proposition de valeur',
        help='Quelle valeur apportez-vous à vos clients ? Qu\'est-ce qui vous différencie ?')

    # ========== 4. ANALYSE DE MARCHÉ ==========
    target_market = fields.Text(
        string='Marché cible',
        help='Qui sont vos clients cibles ? Quel est votre marché (taille, croissance) ?')

    competitors = fields.Text(
        string='Concurrence',
        help='Qui sont vos concurrents ? Quels sont leurs forces et faiblesses ?')

    competitive_advantage = fields.Text(
        string='Avantages concurrentiels',
        help='Pourquoi les clients vous choisiront plutôt que vos concurrents ?')

    # ========== 5. STRATÉGIE MARKETING ET COMMERCIALE ==========
    marketing_strategy = fields.Text(
        string='Stratégie marketing',
        help='Comment allez-vous vous faire connaître ? (communication, publicité, réseaux sociaux...)')

    sales_strategy = fields.Text(
        string='Stratégie commerciale',
        help='Comment allez-vous vendre ? (canaux de vente, prix, distribution...)')

    customer_acquisition = fields.Text(
        string='Acquisition clients',
        help='Comment allez-vous acquérir vos premiers clients ?')

    # ========== 6. ORGANISATION ET ÉQUIPE ==========
    team_structure = fields.Text(
        string='Structure de l\'équipe',
        help='Qui compose votre équipe ? Quels sont les rôles et compétences ?')

    team_size = fields.Integer(string='Nombre de personnes', default=1)

    key_partners = fields.Text(
        string='Partenaires clés',
        help='Quels sont vos partenaires stratégiques ? (fournisseurs, distributeurs...)')

    # ========== 7. PRÉVISIONS FINANCIÈRES ==========
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Année 1
    revenue_year1 = fields.Monetary(string='CA prévisionnel Année 1', currency_field='currency_id')
    costs_year1 = fields.Monetary(string='Charges Année 1', currency_field='currency_id')
    profit_year1 = fields.Monetary(string='Résultat Année 1', compute='_compute_profit_year1', store=True)

    # Année 2
    revenue_year2 = fields.Monetary(string='CA prévisionnel Année 2', currency_field='currency_id')
    costs_year2 = fields.Monetary(string='Charges Année 2', currency_field='currency_id')
    profit_year2 = fields.Monetary(string='Résultat Année 2', compute='_compute_profit_year2', store=True)

    # Année 3
    revenue_year3 = fields.Monetary(string='CA prévisionnel Année 3', currency_field='currency_id')
    costs_year3 = fields.Monetary(string='Charges Année 3', currency_field='currency_id')
    profit_year3 = fields.Monetary(string='Résultat Année 3', compute='_compute_profit_year3', store=True)

    breakeven_point = fields.Text(
        string='Seuil de rentabilité',
        help='À partir de quel chiffre d\'affaires êtes-vous rentable ?')

    # ========== 8. BESOINS DE FINANCEMENT ==========
    initial_investment = fields.Monetary(
        string='Investissement initial total',
        currency_field='currency_id',
        help='Total des investissements nécessaires au démarrage')

    own_contribution = fields.Monetary(
        string='Apport personnel',
        currency_field='currency_id',
        help='Montant que vous apportez personnellement')

    funding_needed = fields.Monetary(
        string='Besoin de financement',
        compute='_compute_funding_needed',
        store=True,
        currency_field='currency_id',
        help='Montant à financer (investissement - apport)')

    funding_sources = fields.Text(
        string='Sources de financement',
        help='Comment comptez-vous financer votre projet ? (prêt bancaire, levée de fonds, aides...)')

    # ========== 9. RISQUES ET OPPORTUNITÉS ==========
    risks = fields.Text(
        string='Risques identifiés',
        help='Quels sont les principaux risques de votre projet ?')

    mitigation_plan = fields.Text(
        string='Plan de mitigation',
        help='Comment comptez-vous gérer ces risques ?')

    opportunities = fields.Text(
        string='Opportunités',
        help='Quelles opportunités de développement voyez-vous ?')

    # ========== INDICATEURS ==========
    indicator_ids = fields.One2many('business.plan.indicator', 'business_plan_id', string='Indicateurs')
    indicator_count = fields.Integer(compute='_compute_indicator_count')
    progress = fields.Float(string='Progression (%)', compute='_compute_progress')

    # Indicateurs mensuels
    monthly_indicator_ids = fields.One2many('business.plan.monthly.indicator', 'business_plan_id', string='Indicateurs Mensuels')
    monthly_indicator_count = fields.Integer(compute='_compute_monthly_indicator_count')

    # ========== TABLEAUX FINANCIERS PRÉVISIONNELS ==========
    # Plan de Trésorerie
    cash_flow_ids = fields.One2many('business.plan.cash.flow', 'business_plan_id', string='Plan de Trésorerie')
    cash_flow_count = fields.Integer(compute='_compute_cash_flow_count')

    # Plan de Financement
    financing_ids = fields.One2many('business.plan.financing', 'business_plan_id', string='Plan de Financement')
    financing_count = fields.Integer(compute='_compute_financing_count')
    financing_balance = fields.Monetary(compute='_compute_financing_summary', string='Équilibre Financement', currency_field='currency_id')
    financing_is_balanced = fields.Boolean(compute='_compute_financing_summary', string='Financement équilibré')

    # Bilan Prévisionnel
    balance_sheet_ids = fields.One2many('business.plan.balance.sheet', 'business_plan_id', string='Bilans Prévisionnels')
    balance_sheet_count = fields.Integer(compute='_compute_balance_sheet_count')

    # Compte de Résultat Prévisionnel
    income_statement_ids = fields.One2many('business.plan.income.statement', 'business_plan_id', string='Comptes de Résultat')
    income_statement_count = fields.Integer(compute='_compute_income_statement_count')

    # ========== CALCULS ==========
    @api.depends('revenue_year1', 'costs_year1')
    def _compute_profit_year1(self):
        for plan in self:
            plan.profit_year1 = (plan.revenue_year1 or 0) - (plan.costs_year1 or 0)

    @api.depends('revenue_year2', 'costs_year2')
    def _compute_profit_year2(self):
        for plan in self:
            plan.profit_year2 = (plan.revenue_year2 or 0) - (plan.costs_year2 or 0)

    @api.depends('revenue_year3', 'costs_year3')
    def _compute_profit_year3(self):
        for plan in self:
            plan.profit_year3 = (plan.revenue_year3 or 0) - (plan.costs_year3 or 0)

    @api.depends('initial_investment', 'own_contribution')
    def _compute_funding_needed(self):
        for plan in self:
            plan.funding_needed = (plan.initial_investment or 0) - (plan.own_contribution or 0)

    @api.depends('indicator_ids')
    def _compute_indicator_count(self):
        for plan in self:
            plan.indicator_count = len(plan.indicator_ids)

    @api.depends('indicator_ids.progress')
    def _compute_progress(self):
        for plan in self:
            if plan.indicator_ids:
                plan.progress = sum(plan.indicator_ids.mapped('progress')) / len(plan.indicator_ids)
            else:
                plan.progress = 0.0

    @api.depends('monthly_indicator_ids')
    def _compute_monthly_indicator_count(self):
        for plan in self:
            plan.monthly_indicator_count = len(plan.monthly_indicator_ids)

    @api.depends('cash_flow_ids')
    def _compute_cash_flow_count(self):
        for plan in self:
            plan.cash_flow_count = len(plan.cash_flow_ids)

    @api.depends('financing_ids')
    def _compute_financing_count(self):
        for plan in self:
            plan.financing_count = len(plan.financing_ids)

    @api.depends('financing_ids', 'financing_ids.line_type', 'financing_ids.amount')
    def _compute_financing_summary(self):
        for plan in self:
            if plan.financing_ids:
                summary = self.env['business.plan.financing'].get_financing_summary(plan.id)
                plan.financing_balance = summary['balance']
                plan.financing_is_balanced = summary['is_balanced']
            else:
                plan.financing_balance = 0.0
                plan.financing_is_balanced = False

    @api.depends('balance_sheet_ids')
    def _compute_balance_sheet_count(self):
        for plan in self:
            plan.balance_sheet_count = len(plan.balance_sheet_ids)

    @api.depends('income_statement_ids')
    def _compute_income_statement_count(self):
        for plan in self:
            plan.income_statement_count = len(plan.income_statement_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code('business.plan') or 'Nouveau'
        return super().create(vals_list)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for plan in self:
            if plan.date_start and plan.date_end and plan.date_start > plan.date_end:
                raise ValidationError(_('La date de fin doit être après la date de début.'))

    def action_validate(self):
        """Valider et générer les indicateurs"""
        for plan in self:
            plan.state = 'validated'
            plan._generate_indicators()
            plan.message_post(body=_('Business plan validé. %d indicateurs créés.') % len(plan.indicator_ids))

    def action_done(self):
        """Terminer le business plan"""
        self.state = 'done'

    def has_active_subscription(self):
        """
        Vérifie si l'utilisateur a un abonnement actif EAZYNOVA
        Retourne True si abonnement actif, False sinon
        À connecter avec le module eazynova_website (SaaS subscriptions)
        """
        self.ensure_one()
        # TODO: Intégrer avec le module eazynova_website pour vérifier l'abonnement
        # Pour l'instant, retourne False (filigrane toujours affiché)
        # Exemple future implémentation:
        # subscription = self.env['saas.subscription'].search([
        #     ('partner_id', '=', self.user_id.partner_id.id),
        #     ('state', '=', 'active'),
        # ], limit=1)
        # return bool(subscription)
        return False


    def _generate_indicators(self):
        """Génère des indicateurs basés sur les prévisions"""
        self.ensure_one()
        self.indicator_ids.unlink()

        indicators = []

        # Indicateurs financiers année 1
        if self.revenue_year1:
            indicators.append({
                'name': 'CA Année 1',
                'business_plan_id': self.id,
                'target_value': self.revenue_year1,
            })

        if self.revenue_year2:
            indicators.append({
                'name': 'CA Année 2',
                'business_plan_id': self.id,
                'target_value': self.revenue_year2,
            })

        if self.revenue_year3:
            indicators.append({
                'name': 'CA Année 3',
                'business_plan_id': self.id,
                'target_value': self.revenue_year3,
            })

        # Indicateurs de performance
        indicators.extend([
            {'name': 'Nouveaux clients', 'business_plan_id': self.id, 'target_value': 50},
            {'name': 'Satisfaction client (%)', 'business_plan_id': self.id, 'target_value': 90},
        ])

        # Indicateur d'équipe
        if self.team_size > 1:
            indicators.append({
                'name': 'Effectif',
                'business_plan_id': self.id,
                'target_value': self.team_size,
            })

        for ind in indicators:
            self.env['business.plan.indicator'].create(ind)

    def action_view_indicators(self):
        """Voir les indicateurs"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Indicateurs',
            'res_model': 'business.plan.indicator',
            'view_mode': 'tree,form',
            'domain': [('business_plan_id', '=', self.id)],
            'context': {'default_business_plan_id': self.id},
        }

    # ========== TABLEAUX FINANCIERS - ACTIONS ==========

    def action_view_cash_flow(self):
        """Voir le plan de trésorerie"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'💰 Plan de Trésorerie - {self.reference}',
            'res_model': 'business.plan.cash.flow',
            'view_mode': 'list,form,graph,pivot',
            'domain': [('business_plan_id', '=', self.id)],
            'context': {'default_business_plan_id': self.id},
        }

    def action_generate_cash_flow(self):
        """Générer le plan de trésorerie"""
        self.ensure_one()
        if not self.date_start:
            raise ValidationError(_('Veuillez définir la date de début du business plan.'))

        # Générer 36 mois de trésorerie
        self.env['business.plan.cash.flow'].generate_cash_flow_plan(
            self.id,
            self.date_start,
            months=36,
            initial_balance=self.own_contribution or 0
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Plan de trésorerie généré'),
                'message': _('36 mois de trésorerie créés avec succès'),
                'type': 'success',
            }
        }

    def action_view_financing(self):
        """Voir le plan de financement"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'💼 Plan de Financement - {self.reference}',
            'res_model': 'business.plan.financing',
            'view_mode': 'list,form',
            'domain': [('business_plan_id', '=', self.id)],
            'context': {'default_business_plan_id': self.id},
        }

    def action_financing_wizard(self):
        """Assistant de création du plan de financement"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assistant Plan de Financement',
            'res_model': 'business.plan.financing.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_business_plan_id': self.id},
        }

    def action_view_balance_sheet(self):
        """Voir les bilans prévisionnels"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'📊 Bilan Prévisionnel - {self.reference}',
            'res_model': 'business.plan.balance.sheet',
            'view_mode': 'list,form,graph',
            'domain': [('business_plan_id', '=', self.id)],
            'context': {'default_business_plan_id': self.id},
        }

    def action_generate_balance_sheets(self):
        """Générer les bilans prévisionnels (3 ans)"""
        self.ensure_one()
        self.env['business.plan.balance.sheet'].generate_balance_sheets(self.id, years=3)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bilans générés'),
                'message': _('3 bilans prévisionnels créés'),
                'type': 'success',
            }
        }

    def action_view_income_statement(self):
        """Voir les comptes de résultat"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'📈 Compte de Résultat - {self.reference}',
            'res_model': 'business.plan.income.statement',
            'view_mode': 'list,form,graph,pivot',
            'domain': [('business_plan_id', '=', self.id)],
            'context': {'default_business_plan_id': self.id},
        }

    def action_generate_income_statements(self):
        """Générer les comptes de résultat (3 ans)"""
        self.ensure_one()
        self.env['business.plan.income.statement'].generate_income_statements(self.id, years=3)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Comptes de résultat générés'),
                'message': _('3 comptes de résultat créés'),
                'type': 'success',
            }
        }

    def action_generate_all_financial_tables(self):
        """Générer tous les tableaux financiers d'un coup"""
        self.ensure_one()

        # Plan de trésorerie
        self.action_generate_cash_flow()

        # Bilans
        self.action_generate_balance_sheets()

        # Comptes de résultat
        self.action_generate_income_statements()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tableaux financiers générés'),
                'message': _('Tous les tableaux financiers ont été créés avec succès !'),
                'type': 'success',
                'sticky': False,
            }
        }

    # ========== INDICATEURS MENSUELS ==========

    def action_view_monthly_indicators(self):
        """Voir les indicateurs mensuels (tableau de bord)"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'📊 Tableau de Bord Mensuel - {self.reference}',
            'res_model': 'business.plan.monthly.indicator',
            'view_mode': 'kanban,graph,pivot,list,form',
            'domain': [('business_plan_id', '=', self.id)],
            'context': {
                'default_business_plan_id': self.id,
                'search_default_current_year': 1,
            },
        }

    def action_generate_monthly_indicators(self):
        """Générer les indicateurs mensuels pour la période du business plan"""
        self.ensure_one()

        if not self.date_start or not self.date_end:
            raise ValidationError(_('Vous devez définir les dates de début et fin du business plan.'))

        # Générer les indicateurs mensuels
        MonthlyIndicator = self.env['business.plan.monthly.indicator']
        indicators = MonthlyIndicator.generate_monthly_indicators(
            self.id,
            self.date_start,
            self.date_end
        )

        # Message de confirmation
        self.message_post(
            body=_('%d indicateurs mensuels ont été générés pour la période %s - %s') % (
                len(indicators),
                self.date_start.strftime('%m/%Y'),
                self.date_end.strftime('%m/%Y')
            )
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Indicateurs générés'),
                'message': _('%d indicateurs mensuels créés avec succès') % len(indicators),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_refresh_all_monthly_indicators(self):
        """Actualiser tous les indicateurs mensuels depuis les données Odoo"""
        self.ensure_one()

        for indicator in self.monthly_indicator_ids:
            indicator.auto_fill_from_odoo_data()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Données actualisées'),
                'message': _('Tous les indicateurs mensuels ont été mis à jour'),
                'type': 'success',
                'sticky': False,
            }
        }

    # ========== ASSISTANT IA ==========

    def action_ai_analyze(self):
        """Lancer l'analyse IA complète du business plan"""
        self.ensure_one()

        # Créer une nouvelle analyse
        assistant = self.env['business.plan.ai.assistant'].create({
            'business_plan_id': self.id,
            'analysis_type': 'global',
        })

        # Lancer l'analyse
        result = assistant.analyze_business_plan()

        # Afficher le résultat dans un wizard
        return {
            'type': 'ir.actions.act_window',
            'name': '🤖 Assistant IA - Analyse de votre Business Plan',
            'res_model': 'business.plan.ai.assistant',
            'res_id': assistant.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_business_plan_id': self.id},
        }

    def action_ai_help_section(self, section):
        """Obtenir de l'aide IA pour une section spécifique"""
        self.ensure_one()

        assistant = self.env['business.plan.ai.assistant'].create({
            'business_plan_id': self.id,
            'analysis_type': 'suggestions',
        })

        suggestions = assistant.suggest_improvements_for_section(section)

        return {
            'type': 'ir.actions.act_window',
            'name': f'🤖 Conseils IA pour: {section}',
            'res_model': 'business.plan.ai.assistant',
            'res_id': assistant.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_business_plan_id': self.id,
                'default_suggestions': suggestions,
            },
        }

    def action_ai_check_financial(self):
        """Vérifier la cohérence financière avec l'IA"""
        self.ensure_one()

        assistant = self.env['business.plan.ai.assistant'].create({
            'business_plan_id': self.id,
            'analysis_type': 'financial',
        })

        checks = assistant.check_financial_coherence()
        assistant.result = checks

        return {
            'type': 'ir.actions.act_window',
            'name': '🤖 Vérification Financière IA',
            'res_model': 'business.plan.ai.assistant',
            'res_id': assistant.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_ai_smart_suggestions(self):
        """Obtenir des suggestions intelligentes"""
        self.ensure_one()

        assistant = self.env['business.plan.ai.assistant'].create({
            'business_plan_id': self.id,
            'analysis_type': 'suggestions',
        })

        suggestions = assistant.generate_smart_suggestions()
        assistant.suggestions = suggestions
        assistant.result = "Suggestions générées avec succès"

        return {
            'type': 'ir.actions.act_window',
            'name': '🤖 Suggestions Intelligentes IA',
            'res_model': 'business.plan.ai.assistant',
            'res_id': assistant.id,
            'view_mode': 'form',
            'target': 'new',
        }
