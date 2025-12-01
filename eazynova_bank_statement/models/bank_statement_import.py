# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class BankStatementImport(models.Model):
    _name = 'eazynova.bank.statement.import'
    _description = 'Import de Relevés Bancaires'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('uploaded', 'Fichier Chargé'),
        ('parsing', 'Analyse en cours'),
        ('parsed', 'Analysé'),
        ('reconciling', 'Rapprochement en cours'),
        ('reconciled', 'Rapproché'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ], string='État', default='draft', tracking=True, required=True)

    file_type = fields.Selection([
        ('csv', 'CSV'),
        ('ofx', 'OFX'),
        ('pdf', 'PDF (OCR)'),
        ('auto', 'Détection Automatique'),
    ], string='Type de Fichier', default='auto', required=True)

    file_data = fields.Binary(
        string='Fichier',
        required=True,
        attachment=True
    )

    file_name = fields.Char(string='Nom du Fichier')

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal Bancaire',
        domain="[('type', '=', 'bank')]",
        required=True,
        tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    statement_id = fields.Many2one(
        'account.bank.statement',
        string='Relevé Bancaire',
        readonly=True,
        tracking=True
    )

    line_ids = fields.One2many(
        'eazynova.bank.statement.line',
        'import_id',
        string='Lignes Importées'
    )

    line_count = fields.Integer(
        string='Nombre de Lignes',
        compute='_compute_line_count'
    )

    reconciled_count = fields.Integer(
        string='Lignes Rapprochées',
        compute='_compute_reconciliation_stats'
    )

    uncertain_count = fields.Integer(
        string='Rapprochements Incertains',
        compute='_compute_reconciliation_stats'
    )

    unreconciled_count = fields.Integer(
        string='Lignes Non Rapprochées',
        compute='_compute_reconciliation_stats'
    )

    alert_ids = fields.One2many(
        'eazynova.reconciliation.alert',
        'import_id',
        string='Alertes'
    )

    alert_count = fields.Integer(
        string='Nombre d\'Alertes',
        compute='_compute_alert_count'
    )

    date_start = fields.Date(string='Date Début', tracking=True)
    date_end = fields.Date(string='Date Fin', tracking=True)

    balance_start = fields.Monetary(
        string='Solde Début',
        currency_field='currency_id'
    )

    balance_end = fields.Monetary(
        string='Solde Fin',
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='journal_id.currency_id',
        store=True
    )

    error_message = fields.Text(string='Message d\'Erreur', readonly=True)

    parsing_log = fields.Text(string='Log d\'Analyse', readonly=True)

    auto_reconcile = fields.Boolean(
        string='Rapprochement Automatique',
        default=True,
        help="Lancer automatiquement le rapprochement après l'import"
    )

    use_ai = fields.Boolean(
        string='Utiliser l\'IA',
        default=True,
        help="Utiliser l'IA pour améliorer le rapprochement"
    )

    confidence_threshold = fields.Float(
        string='Seuil de Confiance',
        default=0.8,
        help="Seuil minimum de confiance pour valider automatiquement un rapprochement (0-1)"
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'eazynova.bank.statement.import'
            ) or _('Nouveau')
        return super().create(vals)

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    @api.depends('line_ids.reconciliation_state')
    def _compute_reconciliation_stats(self):
        for record in self:
            lines = record.line_ids
            record.reconciled_count = len(lines.filtered(
                lambda l: l.reconciliation_state == 'reconciled'
            ))
            record.uncertain_count = len(lines.filtered(
                lambda l: l.reconciliation_state == 'uncertain'
            ))
            record.unreconciled_count = len(lines.filtered(
                lambda l: l.reconciliation_state == 'not_reconciled'
            ))

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        for record in self:
            record.alert_count = len(record.alert_ids)

    def action_detect_file_type(self):
        """Détecte automatiquement le type de fichier"""
        self.ensure_one()

        if not self.file_data:
            raise UserError(_("Veuillez d'abord charger un fichier."))

        file_content = base64.b64decode(self.file_data)
        file_name_lower = (self.file_name or '').lower()

        # Détection par extension
        if file_name_lower.endswith('.csv'):
            self.file_type = 'csv'
        elif file_name_lower.endswith('.ofx'):
            self.file_type = 'ofx'
        elif file_name_lower.endswith('.pdf'):
            self.file_type = 'pdf'
        else:
            # Détection par contenu
            try:
                content_str = file_content.decode('utf-8', errors='ignore')

                if '<OFX>' in content_str or 'OFXHEADER' in content_str:
                    self.file_type = 'ofx'
                elif '%PDF' in content_str[:10]:
                    self.file_type = 'pdf'
                else:
                    self.file_type = 'csv'
            except Exception:
                self.file_type = 'csv'

        self.state = 'uploaded'
        self.message_post(body=_("Type de fichier détecté : %s") % self.file_type.upper())

    def action_parse_file(self):
        """Parse le fichier et crée les lignes d'import"""
        self.ensure_one()

        if not self.file_data:
            raise UserError(_("Veuillez d'abord charger un fichier."))

        if self.file_type == 'auto':
            self.action_detect_file_type()

        self.state = 'parsing'

        try:
            parser = self.env['eazynova.bank.statement.parser']

            if self.file_type == 'csv':
                result = parser.parse_csv(self.file_data, self.file_name)
            elif self.file_type == 'ofx':
                result = parser.parse_ofx(self.file_data)
            elif self.file_type == 'pdf':
                result = parser.parse_pdf(self.file_data, self.use_ai)
            else:
                raise UserError(_("Type de fichier non supporté : %s") % self.file_type)

            # Créer les lignes d'import
            self._create_import_lines(result)

            # Mettre à jour les dates et soldes
            if result.get('date_start'):
                self.date_start = result['date_start']
            if result.get('date_end'):
                self.date_end = result['date_end']
            if result.get('balance_start'):
                self.balance_start = result['balance_start']
            if result.get('balance_end'):
                self.balance_end = result['balance_end']

            self.state = 'parsed'
            self.parsing_log = result.get('log', '')

            message = _("Fichier analysé avec succès. %d lignes importées.") % len(result.get('transactions', []))
            self.message_post(body=message)

            # Lancer le rapprochement automatique si activé
            if self.auto_reconcile:
                self.action_auto_reconcile()

        except Exception as e:
            _logger.exception("Erreur lors du parsing du fichier")
            self.state = 'error'
            self.error_message = str(e)
            raise UserError(_("Erreur lors de l'analyse du fichier : %s") % str(e))

    def _create_import_lines(self, parse_result):
        """Crée les lignes d'import à partir du résultat du parsing"""
        self.ensure_one()

        # Supprimer les anciennes lignes
        self.line_ids.unlink()

        transactions = parse_result.get('transactions', [])

        for trans in transactions:
            self.env['eazynova.bank.statement.line'].create({
                'import_id': self.id,
                'date': trans.get('date'),
                'name': trans.get('name', trans.get('description', '/')),
                'ref': trans.get('ref', trans.get('reference', '')),
                'partner_name': trans.get('partner_name', ''),
                'amount': trans.get('amount', 0.0),
                'unique_import_id': trans.get('unique_import_id', ''),
                'account_number': trans.get('account_number', ''),
                'note': trans.get('note', ''),
            })

    def action_auto_reconcile(self):
        """Lance le rapprochement automatique des lignes"""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_("Aucune ligne à rapprocher."))

        self.state = 'reconciling'

        try:
            reconciliation_engine = self.env['eazynova.bank.statement.line']

            for line in self.line_ids:
                line.action_find_matching_entries(
                    use_ai=self.use_ai,
                    confidence_threshold=self.confidence_threshold
                )

            self.state = 'reconciled'

            # Créer des alertes pour les lignes non rapprochées ou incertaines
            self._create_reconciliation_alerts()

            message = _(
                "Rapprochement automatique terminé.\n"
                "- Rapprochées : %d\n"
                "- Incertaines : %d\n"
                "- Non rapprochées : %d"
            ) % (self.reconciled_count, self.uncertain_count, self.unreconciled_count)

            self.message_post(body=message)

        except Exception as e:
            _logger.exception("Erreur lors du rapprochement automatique")
            self.state = 'error'
            self.error_message = str(e)
            raise UserError(_("Erreur lors du rapprochement : %s") % str(e))

    def _create_reconciliation_alerts(self):
        """Crée des alertes pour les lignes problématiques"""
        self.ensure_one()

        # Supprimer les anciennes alertes
        self.alert_ids.unlink()

        AlertModel = self.env['eazynova.reconciliation.alert']

        # Alertes pour lignes incertaines
        uncertain_lines = self.line_ids.filtered(
            lambda l: l.reconciliation_state == 'uncertain'
        )

        for line in uncertain_lines:
            AlertModel.create({
                'import_id': self.id,
                'line_id': line.id,
                'alert_type': 'uncertain',
                'severity': 'warning',
                'message': _("Rapprochement incertain (confiance: %.0f%%)") % (
                    line.confidence_score * 100
                ),
            })

        # Alertes pour lignes non rapprochées
        unreconciled_lines = self.line_ids.filtered(
            lambda l: l.reconciliation_state == 'not_reconciled'
        )

        for line in unreconciled_lines:
            AlertModel.create({
                'import_id': self.id,
                'line_id': line.id,
                'alert_type': 'not_reconciled',
                'severity': 'error',
                'message': _("Aucun rapprochement trouvé"),
            })

    def action_create_bank_statement(self):
        """Crée le relevé bancaire dans Odoo"""
        self.ensure_one()

        if self.statement_id:
            raise UserError(_("Un relevé bancaire a déjà été créé pour cet import."))

        if not self.line_ids:
            raise UserError(_("Aucune ligne à importer."))

        # Créer le relevé bancaire
        statement_vals = {
            'name': self.name,
            'journal_id': self.journal_id.id,
            'date': self.date_end or fields.Date.today(),
            'balance_start': self.balance_start,
            'balance_end_real': self.balance_end,
        }

        statement = self.env['account.bank.statement'].create(statement_vals)

        # Créer les lignes du relevé
        for line in self.line_ids:
            line.action_create_bank_statement_line(statement)

        self.statement_id = statement.id
        self.state = 'done'

        self.message_post(body=_("Relevé bancaire créé : %s") % statement.name)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_alerts(self):
        """Ouvre la vue des alertes"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Alertes de Rapprochement'),
            'res_model': 'eazynova.reconciliation.alert',
            'domain': [('import_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_lines(self):
        """Ouvre la vue des lignes d'import"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Lignes Importées'),
            'res_model': 'eazynova.bank.statement.line',
            'domain': [('import_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_reset_to_draft(self):
        """Remet l'import en brouillon"""
        self.ensure_one()

        if self.statement_id:
            raise UserError(_(
                "Impossible de remettre en brouillon : "
                "un relevé bancaire a déjà été créé."
            ))

        self.line_ids.unlink()
        self.alert_ids.unlink()

        self.write({
            'state': 'draft',
            'error_message': False,
            'parsing_log': False,
        })
