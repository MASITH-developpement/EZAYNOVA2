# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import requests
import json
import os

_logger = logging.getLogger(__name__)


class SaasInstance(models.Model):
    """Instance Odoo provisionnée pour un client SaaS"""
    _name = 'saas.instance'
    _description = 'Instance SaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
    )
    subscription_id = fields.Many2one(
        'saas.subscription',
        string='Abonnement',
        required=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
    )
    plan_id = fields.Many2one(
        'saas.plan',
        string='Plan',
        required=True,
    )

    # Configuration technique
    railway_project_id = fields.Char(
        string='ID Projet Railway',
        readonly=True,
    )
    railway_service_id = fields.Char(
        string='ID Service Railway',
        readonly=True,
    )
    database_name = fields.Char(
        string='Nom de la base de données',
        readonly=True,
    )
    url = fields.Char(
        string='URL',
        readonly=True,
        tracking=True,
    )
    admin_login = fields.Char(
        string='Login administrateur',
        default='admin',
    )
    admin_password = fields.Char(
        string='Mot de passe administrateur',
    )

    # Ressources
    max_users = fields.Integer(
        string='Nombre maximum d\'utilisateurs',
        required=True,
    )
    current_users = fields.Integer(
        string='Utilisateurs actuels',
        default=0,
    )
    storage_used_mb = fields.Float(
        string='Stockage utilisé (MB)',
        default=0.0,
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('provisioning', 'Provisioning en cours'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('deleted', 'Supprimé'),
        ('error', 'Erreur'),
    ], string='État', default='draft', required=True, tracking=True)

    error_message = fields.Text(
        string='Message d\'erreur',
        readonly=True,
    )

    # Dates
    provisioned_date = fields.Datetime(
        string='Date de provisioning',
        readonly=True,
    )
    last_accessed = fields.Datetime(
        string='Dernier accès',
    )

    def action_provision(self):
        """Provisionner une nouvelle instance Odoo via Railway API"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Seules les instances en brouillon peuvent être provisionnées.'))

        self.state = 'provisioning'

        try:
            # Récupérer les informations depuis les variables d'environnement
            railway_token = os.getenv('RAILWAY_API_TOKEN')
            if not railway_token:
                raise UserError(_('Le token Railway API n\'est pas configuré. Veuillez définir RAILWAY_API_TOKEN.'))

            # Préparer les données pour le provisioning
            company_name = self.partner_id.name.lower().replace(' ', '-').replace('_', '-')
            admin_email = self.partner_id.email or f'admin@{company_name}.com'

            # Utiliser le script create-instance.js existant
            # Pour l'instant, on va simuler le provisioning
            # Dans une vraie implémentation, vous appelleriez l'API Railway ou exécuteriez le script Node.js

            # Simulation pour la démo
            self.write({
                'state': 'active',
                'database_name': f'{company_name}_db',
                'url': f'https://{company_name}.eazynova.app',
                'admin_password': self._generate_password(),
                'provisioned_date': fields.Datetime.now(),
            })

            _logger.info(f'Instance provisionnée avec succès: {self.name}')

            # Envoyer les credentials par email
            self._send_credentials_email()

        except Exception as e:
            _logger.error(f'Erreur lors du provisioning de {self.name}: {str(e)}')
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise UserError(_('Erreur lors du provisioning: %s') % str(e))

    def action_suspend(self):
        """Suspendre l'instance"""
        self.ensure_one()
        # Ici vous pouvez appeler l'API Railway pour arrêter le service
        self.state = 'suspended'
        _logger.info(f'Instance suspendue: {self.name}')

    def action_resume(self):
        """Réactiver l'instance"""
        self.ensure_one()
        # Ici vous pouvez appeler l'API Railway pour redémarrer le service
        self.state = 'active'
        _logger.info(f'Instance réactivée: {self.name}')

    def action_delete(self):
        """Supprimer l'instance et sa base de données"""
        self.ensure_one()

        if self.state == 'deleted':
            return

        try:
            # Ici vous devriez appeler l'API Railway pour supprimer le projet
            # Pour l'instant, on marque juste comme supprimé
            self.write({
                'state': 'deleted',
                'url': False,
            })

            _logger.info(f'Instance supprimée: {self.name}')

            # Notifier le client
            template = self.env.ref('eazynova_website.email_template_instance_deleted', raise_if_not_found=False)
            if template and self.subscription_id:
                template.send_mail(self.subscription_id.id, force_send=True)

        except Exception as e:
            _logger.error(f'Erreur lors de la suppression de {self.name}: {str(e)}')
            raise UserError(_('Erreur lors de la suppression: %s') % str(e))

    def _generate_password(self):
        """Générer un mot de passe sécurisé"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(secrets.choice(alphabet) for i in range(16))
        return password

    def _send_credentials_email(self):
        """Envoyer les credentials par email au client"""
        template = self.env.ref('eazynova_website.email_template_instance_credentials', raise_if_not_found=False)
        if template and self.subscription_id:
            template.send_mail(self.subscription_id.id, force_send=True)

    def action_open_instance(self):
        """Ouvrir l'instance dans un nouvel onglet"""
        self.ensure_one()
        if not self.url:
            raise UserError(_('L\'instance n\'a pas encore d\'URL.'))

        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
            'target': 'new',
        }

    @api.model
    def _cron_update_usage_stats(self):
        """Mettre à jour les statistiques d'utilisation (cron quotidien)"""
        instances = self.search([('state', '=', 'active')])

        for instance in instances:
            try:
                # Ici vous devriez interroger l'API de l'instance pour récupérer les stats
                # Pour l'instant, on simule
                pass
            except Exception as e:
                _logger.error(f'Erreur mise à jour stats pour {instance.name}: {str(e)}')
