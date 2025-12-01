# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaasSubscription(models.Model):
    """Abonnement SaaS d'un client"""
    _name = 'saas.subscription'
    _description = 'Abonnement SaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )

    # Plan et tarification
    plan_id = fields.Many2one(
        'saas.plan',
        string='Plan',
        required=True,
        tracking=True,
    )
    nb_users = fields.Integer(
        string='Nombre d\'utilisateurs',
        default=5,
        required=True,
        tracking=True,
    )
    monthly_price = fields.Monetary(
        string='Prix mensuel (HT)',
        compute='_compute_prices',
        store=True,
        currency_field='currency_id',
    )
    setup_fee = fields.Monetary(
        string='Frais de configuration (HT)',
        compute='_compute_prices',
        store=True,
        currency_field='currency_id',
    )
    total_monthly = fields.Monetary(
        string='Total mensuel (HT)',
        compute='_compute_prices',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='company_id.currency_id',
        readonly=True,
    )

    # Dates
    date_start = fields.Date(
        string='Date de début',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    date_end = fields.Date(
        string='Date de fin',
        tracking=True,
    )
    trial_end_date = fields.Date(
        string='Fin de la période d\'essai',
        compute='_compute_trial_end_date',
        store=True,
    )
    next_billing_date = fields.Date(
        string='Prochaine facturation',
        tracking=True,
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('trial', 'Essai gratuit'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('cancelled', 'Annulé'),
        ('expired', 'Expiré'),
    ], string='État', default='draft', required=True, tracking=True)

    # Instance
    instance_id = fields.Many2one(
        'saas.instance',
        string='Instance',
        readonly=True,
    )
    instance_url = fields.Char(
        string='URL de l\'instance',
        related='instance_id.url',
        readonly=True,
    )

    # Facturation
    invoice_ids = fields.One2many(
        'account.move',
        'saas_subscription_id',
        string='Factures',
        readonly=True,
    )
    invoice_count = fields.Integer(
        string='Nombre de factures',
        compute='_compute_invoice_count',
    )

    # Configuration payée
    setup_paid = fields.Boolean(
        string='Configuration payée',
        default=False,
        tracking=True,
    )

    @api.model
    def create(self, vals):
        """Générer une référence unique à la création"""
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('saas.subscription') or _('Nouveau')
        return super().create(vals)

    @api.depends('plan_id', 'nb_users')
    def _compute_prices(self):
        """Calculer les prix selon le plan et le nombre d'utilisateurs"""
        for subscription in self:
            if subscription.plan_id:
                plan = subscription.plan_id
                base_price = plan.monthly_price
                extra_users = max(0, subscription.nb_users - plan.included_users)
                extra_price = extra_users * plan.extra_user_price

                subscription.monthly_price = base_price + extra_price
                subscription.setup_fee = plan.setup_fee if not subscription.setup_paid else 0.0
                subscription.total_monthly = subscription.monthly_price
            else:
                subscription.monthly_price = 0.0
                subscription.setup_fee = 0.0
                subscription.total_monthly = 0.0

    @api.depends('date_start', 'plan_id')
    def _compute_trial_end_date(self):
        """Calculer la date de fin de période d'essai"""
        for subscription in self:
            if subscription.date_start and subscription.plan_id:
                trial_days = subscription.plan_id.trial_days or 30
                subscription.trial_end_date = subscription.date_start + timedelta(days=trial_days)
            else:
                subscription.trial_end_date = False

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        """Compter les factures"""
        for subscription in self:
            subscription.invoice_count = len(subscription.invoice_ids)

    def action_start_trial(self):
        """Démarrer la période d'essai"""
        for subscription in self:
            if subscription.state != 'draft':
                raise UserError(_('Seuls les abonnements en brouillon peuvent démarrer un essai.'))

            # Créer l'instance Odoo
            instance = self.env['saas.instance'].create({
                'name': f'{subscription.partner_id.name} - EAZYNOVA',
                'subscription_id': subscription.id,
                'partner_id': subscription.partner_id.id,
                'plan_id': subscription.plan_id.id,
                'max_users': subscription.nb_users,
            })

            # Provisionner l'instance
            instance.action_provision()

            subscription.write({
                'state': 'trial',
                'instance_id': instance.id,
            })

            # Envoyer email de bienvenue
            template = self.env.ref('eazynova_website.email_template_trial_start', raise_if_not_found=False)
            if template:
                template.send_mail(subscription.id, force_send=True)

    def action_activate(self):
        """Activer l'abonnement (fin de période d'essai ou activation directe)"""
        for subscription in self:
            if subscription.state not in ['trial', 'draft', 'suspended']:
                raise UserError(_('Impossible d\'activer cet abonnement dans l\'état actuel.'))

            # Si pas d'instance, en créer une
            if not subscription.instance_id:
                subscription.action_start_trial()

            # Générer la facture de configuration si non payée
            if not subscription.setup_paid and subscription.setup_fee > 0:
                subscription._create_setup_invoice()

            subscription.write({
                'state': 'active',
                'next_billing_date': fields.Date.today() + timedelta(days=30),
            })

            # Envoyer email de confirmation
            template = self.env.ref('eazynova_website.email_template_subscription_active', raise_if_not_found=False)
            if template:
                template.send_mail(subscription.id, force_send=True)

    def action_suspend(self):
        """Suspendre l'abonnement"""
        for subscription in self:
            subscription.state = 'suspended'
            if subscription.instance_id:
                subscription.instance_id.action_suspend()

    def action_cancel(self):
        """Annuler l'abonnement"""
        for subscription in self:
            subscription.write({
                'state': 'cancelled',
                'date_end': fields.Date.today(),
            })

    def _create_setup_invoice(self):
        """Créer la facture de configuration"""
        self.ensure_one()

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'saas_subscription_id': self.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Configuration EAZYNOVA - {self.plan_id.name}',
                'quantity': 1,
                'price_unit': self.setup_fee,
            })],
        })

        return invoice

    def _create_monthly_invoice(self):
        """Créer la facture mensuelle"""
        self.ensure_one()

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'saas_subscription_id': self.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Abonnement EAZYNOVA {self.plan_id.name} - {self.nb_users} utilisateurs',
                'quantity': 1,
                'price_unit': self.monthly_price,
            })],
        })

        # Planifier la prochaine facture
        self.next_billing_date = fields.Date.today() + timedelta(days=30)

        return invoice

    @api.model
    def _cron_check_trial_expiration(self):
        """Vérifier les périodes d'essai expirées (cron quotidien)"""
        today = fields.Date.today()
        trials = self.search([
            ('state', '=', 'trial'),
            ('trial_end_date', '<', today),
        ])

        for trial in trials:
            _logger.info(f'Période d\'essai expirée pour {trial.name}')
            # Envoyer notification
            template = self.env.ref('eazynova_website.email_template_trial_expired', raise_if_not_found=False)
            if template:
                template.send_mail(trial.id, force_send=True)

            # Marquer comme expiré
            trial.state = 'expired'

    @api.model
    def _cron_generate_invoices(self):
        """Générer les factures mensuelles (cron quotidien)"""
        today = fields.Date.today()
        subscriptions = self.search([
            ('state', '=', 'active'),
            ('next_billing_date', '<=', today),
        ])

        for subscription in subscriptions:
            try:
                subscription._create_monthly_invoice()
                _logger.info(f'Facture générée pour {subscription.name}')
            except Exception as e:
                _logger.error(f'Erreur génération facture pour {subscription.name}: {str(e)}')

    @api.model
    def _cron_check_unpaid_subscriptions(self):
        """Vérifier les abonnements impayés et supprimer les bases après 30 jours"""
        today = fields.Date.today()
        expired = self.search([
            ('state', '=', 'expired'),
            ('trial_end_date', '<', today - timedelta(days=30)),
        ])

        for subscription in expired:
            if subscription.instance_id:
                _logger.info(f'Suppression de l\'instance pour {subscription.name} (30 jours sans paiement)')
                subscription.instance_id.action_delete()

    def action_view_invoices(self):
        """Voir les factures de l'abonnement"""
        self.ensure_one()
        return {
            'name': _('Factures'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('saas_subscription_id', '=', self.id)],
            'context': {'default_saas_subscription_id': self.id},
        }


# Extension du modèle de facture
class AccountMove(models.Model):
    _inherit = 'account.move'

    saas_subscription_id = fields.Many2one(
        'saas.subscription',
        string='Abonnement SaaS',
        readonly=True,
    )
