# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BusinessPlanMonthlyIndicator(models.Model):
    _name = 'business.plan.monthly.indicator'
    _description = 'Indicateur Mensuel de Business Plan'
    _order = 'business_plan_id, period_date desc'
    _rec_name = 'display_name'

    business_plan_id = fields.Many2one('business.plan', string='Business Plan', required=True, ondelete='cascade')
    period_date = fields.Date(string='Mois', required=True, default=fields.Date.today)
    period_month = fields.Integer(string='Mois', compute='_compute_period', store=True)
    period_year = fields.Integer(string='Année', compute='_compute_period', store=True)
    display_name = fields.Char(string='Nom', compute='_compute_display_name', store=True)

    # INDICATEURS FINANCIERS
    currency_id = fields.Many2one(related='business_plan_id.currency_id', store=True, readonly=True)

    # Chiffre d'affaires
    revenue_target = fields.Monetary(string='CA Objectif', currency_field='currency_id', default=0)
    revenue_actual = fields.Monetary(string='CA Réalisé', currency_field='currency_id', default=0)
    revenue_variance = fields.Monetary(string='Écart CA', compute='_compute_variances', store=True, currency_field='currency_id')
    revenue_variance_pct = fields.Float(string='Écart CA %', compute='_compute_variances', store=True)

    # Charges
    costs_target = fields.Monetary(string='Charges Objectif', currency_field='currency_id', default=0)
    costs_actual = fields.Monetary(string='Charges Réelles', currency_field='currency_id', default=0)
    costs_variance = fields.Monetary(string='Écart Charges', compute='_compute_variances', store=True, currency_field='currency_id')
    costs_variance_pct = fields.Float(string='Écart Charges %', compute='_compute_variances', store=True)

    # Résultat
    profit_target = fields.Monetary(string='Résultat Objectif', compute='_compute_profit', store=True, currency_field='currency_id')
    profit_actual = fields.Monetary(string='Résultat Réel', compute='_compute_profit', store=True, currency_field='currency_id')
    profit_variance = fields.Monetary(string='Écart Résultat', compute='_compute_variances', store=True, currency_field='currency_id')

    # INDICATEURS OPÉRATIONNELS
    customers_target = fields.Integer(string='Clients Objectif', default=0)
    customers_actual = fields.Integer(string='Clients Réels', default=0)
    customers_variance = fields.Integer(string='Écart Clients', compute='_compute_variances', store=True)

    orders_target = fields.Integer(string='Commandes Objectif', default=0)
    orders_actual = fields.Integer(string='Commandes Réelles', default=0)
    orders_variance = fields.Integer(string='Écart Commandes', compute='_compute_variances', store=True)

    # STATUT ET ALERTES
    status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('warning', 'Attention'),
        ('critical', 'Critique'),
    ], string='Statut', compute='_compute_status', store=True)

    performance_score = fields.Float(string='Score Performance (%)', compute='_compute_status', store=True)

    alert = fields.Text(string='Alertes', compute='_compute_status', store=True)
    notes = fields.Text(string='Notes')

    # RENSEIGNEMENT AUTOMATIQUE
    auto_filled = fields.Boolean(string='Rempli automatiquement', default=False)
    last_update = fields.Datetime(string='Dernière mise à jour', default=fields.Datetime.now)

    @api.depends('period_date')
    def _compute_period(self):
        for record in self:
            if record.period_date:
                record.period_month = record.period_date.month
                record.period_year = record.period_date.year
            else:
                record.period_month = 0
                record.period_year = 0

    @api.depends('period_date', 'business_plan_id.reference')
    def _compute_display_name(self):
        for record in self:
            if record.period_date and record.business_plan_id:
                month_name = record.period_date.strftime('%B %Y')
                record.display_name = f"{record.business_plan_id.reference} - {month_name}"
            else:
                record.display_name = "Nouvel indicateur"

    @api.depends('revenue_target', 'revenue_actual')
    def _compute_profit(self):
        for record in self:
            record.profit_target = record.revenue_target - record.costs_target
            record.profit_actual = record.revenue_actual - record.costs_actual

    @api.depends('revenue_target', 'revenue_actual', 'costs_target', 'costs_actual',
                 'customers_target', 'customers_actual', 'orders_target', 'orders_actual')
    def _compute_variances(self):
        for record in self:
            # Écart CA
            record.revenue_variance = record.revenue_actual - record.revenue_target
            if record.revenue_target:
                record.revenue_variance_pct = (record.revenue_variance / record.revenue_target) * 100
            else:
                record.revenue_variance_pct = 0

            # Écart Charges
            record.costs_variance = record.costs_actual - record.costs_target
            if record.costs_target:
                record.costs_variance_pct = (record.costs_variance / record.costs_target) * 100
            else:
                record.costs_variance_pct = 0

            # Écart Résultat
            record.profit_variance = record.profit_actual - record.profit_target

            # Écarts opérationnels
            record.customers_variance = record.customers_actual - record.customers_target
            record.orders_variance = record.orders_actual - record.orders_target

    @api.depends('revenue_variance_pct', 'profit_actual', 'profit_target', 'customers_variance')
    def _compute_status(self):
        for record in self:
            alerts = []
            score = 100

            # Analyse CA
            if record.revenue_variance_pct < -20:
                alerts.append(f"⚠️ CA en retard de {abs(record.revenue_variance_pct):.1f}%")
                score -= 30
            elif record.revenue_variance_pct < -10:
                alerts.append(f"⚠️ CA légèrement en retard ({abs(record.revenue_variance_pct):.1f}%)")
                score -= 15
            elif record.revenue_variance_pct > 20:
                alerts.append(f"✅ CA excellent (+{record.revenue_variance_pct:.1f}%)")
                score += 10

            # Analyse Résultat
            if record.profit_actual < 0:
                alerts.append("❌ Perte ce mois")
                score -= 30
            elif record.profit_target > 0 and record.profit_actual < record.profit_target * 0.7:
                alerts.append("⚠️ Résultat bien en dessous de l'objectif")
                score -= 20

            # Analyse Clients
            if record.customers_variance < -10:
                alerts.append(f"⚠️ {abs(record.customers_variance)} clients en moins que prévu")
                score -= 15
            elif record.customers_variance > 10:
                alerts.append(f"✅ +{record.customers_variance} clients bonus")
                score += 10

            # Analyse Charges
            if record.costs_variance_pct > 20:
                alerts.append(f"❌ Charges dépassées de {record.costs_variance_pct:.1f}%")
                score -= 25
            elif record.costs_variance_pct > 10:
                alerts.append(f"⚠️ Charges légèrement dépassées ({record.costs_variance_pct:.1f}%)")
                score -= 10

            # Score final
            record.performance_score = max(0, min(100, score))

            # Statut
            if record.performance_score >= 90:
                record.status = 'excellent'
            elif record.performance_score >= 70:
                record.status = 'good'
            elif record.performance_score >= 50:
                record.status = 'warning'
            else:
                record.status = 'critical'

            # Alertes
            if alerts:
                record.alert = "\n".join(alerts)
            else:
                record.alert = "✅ Tous les indicateurs sont conformes"

    def auto_fill_from_odoo_data(self):
        """Remplir automatiquement les indicateurs depuis les données Odoo"""
        self.ensure_one()

        # Récupérer les dates du mois
        start_date = self.period_date.replace(day=1)
        if self.period_month == 12:
            end_date = start_date.replace(year=self.period_year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=self.period_month + 1, day=1) - timedelta(days=1)

        # Récupérer les données de ventes si le module sale est installé
        if self.env['ir.module.module'].search([('name', '=', 'sale'), ('state', '=', 'installed')]):
            sale_orders = self.env['sale.order'].search([
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', 'in', ['sale', 'done']),
            ])

            if sale_orders:
                self.revenue_actual = sum(sale_orders.mapped('amount_total'))
                self.orders_actual = len(sale_orders)
                self.customers_actual = len(sale_orders.mapped('partner_id'))

        # Récupérer les factures si module account installé
        if self.env['ir.module.module'].search([('name', '=', 'account'), ('state', '=', 'installed')]):
            invoices = self.env['account.move'].search([
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ])

            if invoices:
                # Si on n'a pas de données de ventes, utiliser les factures
                if not self.revenue_actual:
                    self.revenue_actual = sum(invoices.mapped('amount_total'))

            # Charges (factures fournisseurs)
            bills = self.env['account.move'].search([
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
            ])

            if bills:
                self.costs_actual = sum(bills.mapped('amount_total'))

        self.auto_filled = True
        self.last_update = fields.Datetime.now()

        return True

    def action_refresh_data(self):
        """Action pour rafraîchir les données"""
        for record in self:
            record.auto_fill_from_odoo_data()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Données actualisées'),
                'message': _('Les indicateurs ont été mis à jour avec les données Odoo'),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def generate_monthly_indicators(self, business_plan_id, start_date, end_date):
        """Générer les indicateurs mensuels pour une période donnée"""
        business_plan = self.env['business.plan'].browse(business_plan_id)

        if not business_plan:
            return False

        current_date = start_date.replace(day=1)
        end_date = end_date.replace(day=1)

        # Calculer les objectifs mensuels basés sur les prévisions annuelles
        months_total = 12
        monthly_revenue_y1 = business_plan.revenue_year1 / months_total if business_plan.revenue_year1 else 0
        monthly_costs_y1 = business_plan.costs_year1 / months_total if business_plan.costs_year1 else 0

        created_indicators = []

        while current_date <= end_date:
            # Vérifier si l'indicateur existe déjà
            existing = self.search([
                ('business_plan_id', '=', business_plan_id),
                ('period_date', '=', current_date),
            ], limit=1)

            if not existing:
                # Créer le nouvel indicateur
                indicator = self.create({
                    'business_plan_id': business_plan_id,
                    'period_date': current_date,
                    'revenue_target': monthly_revenue_y1,
                    'costs_target': monthly_costs_y1,
                    'customers_target': 10,  # Valeur par défaut
                    'orders_target': 20,     # Valeur par défaut
                })
                created_indicators.append(indicator)

            # Passer au mois suivant
            current_date = current_date + relativedelta(months=1)

        return created_indicators

    @api.model
    def cron_auto_fill_indicators(self):
        """Tâche planifiée pour remplir automatiquement les indicateurs du mois en cours"""
        today = fields.Date.today()
        current_month = today.replace(day=1)

        # Chercher tous les business plans validés
        business_plans = self.env['business.plan'].search([
            ('state', 'in', ['validated', 'done']),
        ])

        for bp in business_plans:
            # Chercher ou créer l'indicateur du mois en cours
            indicator = self.search([
                ('business_plan_id', '=', bp.id),
                ('period_date', '=', current_month),
            ], limit=1)

            if not indicator:
                # Générer l'indicateur pour ce mois
                indicators = self.generate_monthly_indicators(
                    bp.id,
                    current_month,
                    current_month
                )
                if indicators:
                    indicator = indicators[0]

            # Remplir automatiquement
            if indicator:
                indicator.auto_fill_from_odoo_data()

        return True
