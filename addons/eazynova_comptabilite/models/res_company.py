# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Configuration comptable
    chart_template_id = fields.Many2one(
        'account.chart.template',
        string='Modèle de plan comptable',
        help='Modèle de plan comptable utilisé pour cette société'
    )

    fiscalyear_last_day = fields.Integer(
        string='Dernier jour de l\'exercice',
        default=31,
        required=True
    )

    fiscalyear_last_month = fields.Selection([
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')
    ], string='Dernier mois de l\'exercice', default=12, required=True)

    fiscalyear_lock_date = fields.Date(
        string='Date de verrouillage comptable',
        help='Aucune écriture ne peut être créée avant cette date'
    )

    tax_lock_date = fields.Date(
        string='Date de verrouillage TVA',
        help='Aucune écriture avec TVA ne peut être créée avant cette date'
    )

    # Numérotation
    invoice_sequence_prefix = fields.Char(
        string='Préfixe factures',
        default='FA',
        help='Préfixe pour la numérotation des factures'
    )

    supplier_invoice_sequence_prefix = fields.Char(
        string='Préfixe factures fournisseurs',
        default='FF',
        help='Préfixe pour la numérotation des factures fournisseurs'
    )

    # Comptes par défaut
    default_income_account_id = fields.Many2one(
        'account.chart',
        string='Compte de produit par défaut',
        domain=[('account_type', '=', 'income')]
    )

    default_expense_account_id = fields.Many2one(
        'account.chart',
        string='Compte de charge par défaut',
        domain=[('account_type', '=', 'expense')]
    )

    default_bank_account_id = fields.Many2one(
        'account.chart',
        string='Compte banque par défaut',
        domain=[('account_type', '=', 'asset_current')]
    )

    default_customer_account_id = fields.Many2one(
        'account.chart',
        string='Compte client par défaut',
        domain=[('account_type', '=', 'asset_receivable')]
    )

    default_supplier_account_id = fields.Many2one(
        'account.chart',
        string='Compte fournisseur par défaut',
        domain=[('account_type', '=', 'liability_payable')]
    )

    # TVA
    default_tax_id = fields.Many2one(
        'account.tax',
        string='TVA par défaut',
        domain=[('type_tax_use', '=', 'sale')]
    )

    default_purchase_tax_id = fields.Many2one(
        'account.tax',
        string='TVA achat par défaut',
        domain=[('type_tax_use', '=', 'purchase')]
    )

    tax_periodicity = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('yearly', 'Annuelle')
    ], string='Périodicité déclaration TVA', default='monthly')

    # Comptabilité analytique
    enable_analytic_accounting = fields.Boolean(
        string='Activer la comptabilité analytique',
        default=False,
        help='Active les axes analytiques pour cette société'
    )

    # Intégrations
    accounting_software = fields.Selection([
        ('none', 'Aucun'),
        ('pennylane', 'Pennylane'),
        ('sage', 'Sage'),
        ('axonaut', 'Axonaut'),
        ('ebp', 'EBP Compta'),
        ('ciel', 'Ciel Compta'),
        ('quadratus', 'Quadratus'),
        ('acd', 'ACD'),
    ], string='Logiciel comptable externe', default='none')

    accounting_api_key = fields.Char(
        string='Clé API comptable',
        help='Clé API pour la connexion au logiciel comptable externe'
    )

    accounting_api_url = fields.Char(
        string='URL API comptable',
        help='URL de l\'API du logiciel comptable externe'
    )

    last_sync_date = fields.Datetime(
        string='Dernière synchronisation',
        readonly=True
    )

    # OCR et IA
    enable_invoice_ocr = fields.Boolean(
        string='Activer OCR factures',
        default=True,
        help='Active la reconnaissance automatique des factures'
    )

    enable_ai_coding = fields.Boolean(
        string='Activer l\'IA pour codification',
        default=True,
        help='Active l\'IA pour suggérer les codes comptables'
    )

    # Relances
    auto_reminder = fields.Boolean(
        string='Relances automatiques',
        default=False,
        help='Active les relances automatiques pour impayés'
    )

    reminder_days = fields.Integer(
        string='Jours avant relance',
        default=7,
        help='Nombre de jours après échéance avant envoi relance'
    )

    # Devise
    enable_multi_currency = fields.Boolean(
        string='Multi-devises',
        default=False,
        help='Active la gestion multi-devises'
    )

    @api.model
    def get_fiscalyear_dates(self, date=None):
        """Retourne les dates de début et fin d'exercice fiscal"""
        if not date:
            date = fields.Date.today()

        company = self.env.company

        # Calculer la date de fin d'exercice
        year = date.year
        if date.month < company.fiscalyear_last_month or \
           (date.month == company.fiscalyear_last_month and date.day <= company.fiscalyear_last_day):
            year -= 1

        fiscalyear_end = fields.Date.from_string(
            f'{year}-{company.fiscalyear_last_month:02d}-{company.fiscalyear_last_day:02d}'
        )

        # Date de début = jour suivant la fin de l'exercice précédent
        from datetime import timedelta
        fiscalyear_start = fiscalyear_end - timedelta(days=364)  # Un an environ

        return {
            'start': fiscalyear_start,
            'end': fiscalyear_end
        }
