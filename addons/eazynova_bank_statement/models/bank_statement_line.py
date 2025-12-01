# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BankStatementLine(models.Model):
    _name = 'eazynova.bank.statement.line'
    _description = 'Ligne de Relevé Bancaire Importée'
    _order = 'date desc, id desc'

    import_id = fields.Many2one(
        'eazynova.bank.statement.import',
        string='Import',
        required=True,
        ondelete='cascade',
        index=True
    )

    date = fields.Date(string='Date', required=True, index=True)

    name = fields.Char(string='Libellé', required=True)

    ref = fields.Char(string='Référence')

    partner_name = fields.Char(string='Nom du Partenaire')

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        help="Partenaire détecté automatiquement"
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='import_id.currency_id',
        store=True
    )

    unique_import_id = fields.Char(
        string='ID Unique Import',
        help="Identifiant unique pour éviter les doublons"
    )

    account_number = fields.Char(string='Numéro de Compte')

    note = fields.Text(string='Notes')

    reconciliation_state = fields.Selection([
        ('not_reconciled', 'Non Rapproché'),
        ('uncertain', 'Incertain'),
        ('reconciled', 'Rapproché'),
        ('manual', 'Manuel'),
    ], string='État Rapprochement', default='not_reconciled', tracking=True)

    confidence_score = fields.Float(
        string='Score de Confiance',
        default=0.0,
        help="Score de confiance du rapprochement (0-1)"
    )

    matching_move_id = fields.Many2one(
        'account.move',
        string='Écriture Correspondante',
        help="Écriture comptable correspondante trouvée"
    )

    matching_move_line_id = fields.Many2one(
        'account.move.line',
        string='Ligne d\'Écriture Correspondante',
        help="Ligne d'écriture comptable correspondante"
    )

    suggestion_ids = fields.One2many(
        'eazynova.reconciliation.suggestion',
        'line_id',
        string='Suggestions de Rapprochement'
    )

    suggestion_count = fields.Integer(
        string='Nombre de Suggestions',
        compute='_compute_suggestion_count'
    )

    statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        string='Ligne de Relevé Odoo',
        readonly=True,
        help="Ligne de relevé bancaire créée dans Odoo"
    )

    is_duplicate = fields.Boolean(
        string='Doublon Possible',
        compute='_compute_is_duplicate',
        store=True
    )

    @api.depends('suggestion_ids')
    def _compute_suggestion_count(self):
        for record in self:
            record.suggestion_count = len(record.suggestion_ids)

    @api.depends('unique_import_id', 'date', 'amount', 'name')
    def _compute_is_duplicate(self):
        for record in self:
            if not record.unique_import_id:
                record.is_duplicate = False
                continue

            # Chercher des doublons potentiels
            domain = [
                ('id', '!=', record.id),
                ('unique_import_id', '=', record.unique_import_id),
            ]

            duplicate = self.search(domain, limit=1)
            record.is_duplicate = bool(duplicate)

    def action_find_matching_entries(self, use_ai=True, confidence_threshold=0.8):
        """Trouve les écritures comptables correspondantes"""
        self.ensure_one()

        # Nettoyer les anciennes suggestions
        self.suggestion_ids.unlink()

        suggestions = []

        # 1. Recherche par référence exacte
        if self.ref:
            exact_matches = self._find_by_reference(self.ref)
            for match in exact_matches:
                suggestions.append({
                    'line_id': self.id,
                    'move_line_id': match.id,
                    'match_type': 'exact_reference',
                    'confidence_score': 1.0,
                    'match_reason': _("Correspondance exacte par référence: %s") % self.ref,
                })

        # 2. Recherche par montant et date
        amount_matches = self._find_by_amount_date(self.amount, self.date)
        for match in amount_matches:
            # Calculer un score basé sur la proximité de date
            date_diff = abs((match.date - self.date).days)
            score = max(0.5, 1.0 - (date_diff / 30.0))  # Décroissance sur 30 jours

            suggestions.append({
                'line_id': self.id,
                'move_line_id': match.id,
                'match_type': 'amount_date',
                'confidence_score': score,
                'match_reason': _("Correspondance par montant et date (±%d jours)") % date_diff,
            })

        # 3. Recherche par partenaire et montant
        if self.partner_id:
            partner_matches = self._find_by_partner_amount(self.partner_id, self.amount)
            for match in partner_matches:
                date_diff = abs((match.date - self.date).days)
                score = max(0.6, 0.9 - (date_diff / 60.0))

                suggestions.append({
                    'line_id': self.id,
                    'move_line_id': match.id,
                    'match_type': 'partner_amount',
                    'confidence_score': score,
                    'match_reason': _("Correspondance par partenaire et montant"),
                })

        # 4. Analyse sémantique par IA (si activée)
        if use_ai and self.name:
            ai_matches = self._find_by_ai_analysis(self.name, self.amount, self.date)
            suggestions.extend(ai_matches)

        # Créer les suggestions
        SuggestionModel = self.env['eazynova.reconciliation.suggestion']

        # Dédupliquer les suggestions
        seen_move_lines = set()
        unique_suggestions = []

        for sugg in sorted(suggestions, key=lambda x: x['confidence_score'], reverse=True):
            move_line_id = sugg['move_line_id']
            if move_line_id not in seen_move_lines:
                seen_move_lines.add(move_line_id)
                unique_suggestions.append(sugg)

        for sugg in unique_suggestions[:10]:  # Limiter à 10 suggestions
            SuggestionModel.create(sugg)

        # Déterminer l'état de rapprochement
        if unique_suggestions:
            best_suggestion = unique_suggestions[0]
            best_score = best_suggestion['confidence_score']

            if best_score >= confidence_threshold:
                self.reconciliation_state = 'reconciled'
                self.confidence_score = best_score
                self.matching_move_line_id = best_suggestion['move_line_id']
                self.matching_move_id = self.env['account.move.line'].browse(
                    best_suggestion['move_line_id']
                ).move_id.id
            elif best_score >= 0.5:
                self.reconciliation_state = 'uncertain'
                self.confidence_score = best_score
            else:
                self.reconciliation_state = 'not_reconciled'
                self.confidence_score = best_score
        else:
            self.reconciliation_state = 'not_reconciled'
            self.confidence_score = 0.0

    def _find_by_reference(self, reference):
        """Recherche par référence exacte"""
        if not reference:
            return self.env['account.move.line']

        domain = [
            ('ref', '=', reference),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ('reconciled', '=', False),
        ]

        return self.env['account.move.line'].search(domain, limit=5)

    def _find_by_amount_date(self, amount, date, days_range=7):
        """Recherche par montant et date proche"""
        if not amount or not date:
            return self.env['account.move.line']

        from datetime import timedelta

        date_min = date - timedelta(days=days_range)
        date_max = date + timedelta(days=days_range)

        domain = [
            ('date', '>=', date_min),
            ('date', '<=', date_max),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ('reconciled', '=', False),
            '|',
            ('debit', '=', abs(amount)) if amount > 0 else ('credit', '=', abs(amount)),
            ('credit', '=', abs(amount)) if amount > 0 else ('debit', '=', abs(amount)),
        ]

        return self.env['account.move.line'].search(domain, limit=10)

    def _find_by_partner_amount(self, partner, amount):
        """Recherche par partenaire et montant"""
        if not partner or not amount:
            return self.env['account.move.line']

        domain = [
            ('partner_id', '=', partner.id),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ('reconciled', '=', False),
            '|',
            ('debit', '=', abs(amount)) if amount > 0 else ('credit', '=', abs(amount)),
            ('credit', '=', abs(amount)) if amount > 0 else ('debit', '=', abs(amount)),
        ]

        return self.env['account.move.line'].search(domain, limit=5)

    def _find_by_ai_analysis(self, description, amount, date):
        """Analyse sémantique du libellé par IA"""
        suggestions = []

        try:
            # Chercher des écritures potentielles
            from datetime import timedelta

            date_min = date - timedelta(days=30)
            date_max = date + timedelta(days=30)

            domain = [
                ('date', '>=', date_min),
                ('date', '<=', date_max),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                ('reconciled', '=', False),
            ]

            potential_matches = self.env['account.move.line'].search(domain, limit=50)

            if not potential_matches:
                return suggestions

            # Utiliser l'IA pour analyser la similarité
            ai_service = self.env['eazynova.ai.service']

            for move_line in potential_matches:
                # Construire un contexte pour l'IA
                context = {
                    'bank_description': description,
                    'bank_amount': amount,
                    'bank_date': str(date),
                    'move_name': move_line.name or '',
                    'move_ref': move_line.ref or '',
                    'move_amount': move_line.debit or move_line.credit,
                    'move_date': str(move_line.date),
                    'partner_name': move_line.partner_id.name if move_line.partner_id else '',
                }

                # Demander à l'IA d'évaluer la correspondance
                prompt = f"""
Analyse si ces deux transactions correspondent :

Transaction bancaire :
- Libellé : {context['bank_description']}
- Montant : {context['bank_amount']}
- Date : {context['bank_date']}

Écriture comptable :
- Nom : {context['move_name']}
- Référence : {context['move_ref']}
- Montant : {context['move_amount']}
- Date : {context['move_date']}
- Partenaire : {context['partner_name']}

Réponds avec un score de confiance entre 0 et 1, et une raison courte.
Format JSON : {{"score": 0.0-1.0, "reason": "..."}}
"""

                try:
                    result = ai_service.analyze_text(prompt, format='json')

                    if result and 'score' in result:
                        score = float(result.get('score', 0))

                        if score >= 0.5:
                            suggestions.append({
                                'line_id': self.id,
                                'move_line_id': move_line.id,
                                'match_type': 'ai_semantic',
                                'confidence_score': score,
                                'match_reason': result.get('reason', _("Analyse IA")),
                            })

                except Exception as e:
                    _logger.warning("Erreur analyse IA pour ligne %s: %s", move_line.id, e)
                    continue

        except Exception as e:
            _logger.error("Erreur dans l'analyse IA: %s", e)

        return suggestions

    def action_validate_reconciliation(self):
        """Valide le rapprochement suggéré"""
        self.ensure_one()

        if not self.matching_move_line_id:
            raise UserError(_("Aucune écriture correspondante sélectionnée."))

        self.reconciliation_state = 'reconciled'
        self.confidence_score = 1.0

        self.import_id.message_post(
            body=_("Rapprochement validé pour la ligne: %s") % self.name
        )

    def action_manual_reconciliation(self):
        """Ouvre un wizard pour sélectionner manuellement l'écriture"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Sélectionner une Écriture'),
            'res_model': 'eazynova.reconciliation.suggestion.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_line_id': self.id,
            },
        }

    def action_view_suggestions(self):
        """Affiche les suggestions de rapprochement"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Suggestions de Rapprochement'),
            'res_model': 'eazynova.reconciliation.suggestion',
            'domain': [('line_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_create_bank_statement_line(self, statement):
        """Crée la ligne dans le relevé bancaire Odoo"""
        self.ensure_one()

        if self.statement_line_id:
            raise UserError(_("Cette ligne a déjà été créée dans un relevé bancaire."))

        vals = {
            'statement_id': statement.id,
            'date': self.date,
            'payment_ref': self.name,
            'ref': self.ref,
            'partner_name': self.partner_name,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'amount': self.amount,
            'unique_import_id': self.unique_import_id,
            'account_number': self.account_number,
        }

        statement_line = self.env['account.bank.statement.line'].create(vals)

        self.statement_line_id = statement_line.id

        # Si rapproché, créer la réconciliation
        if self.reconciliation_state == 'reconciled' and self.matching_move_line_id:
            try:
                statement_line.reconcile([{
                    'id': self.matching_move_line_id.id,
                }])
            except Exception as e:
                _logger.warning(
                    "Impossible de réconcilier automatiquement la ligne %s: %s",
                    self.id, e
                )

        return statement_line


class ReconciliationSuggestion(models.Model):
    _name = 'eazynova.reconciliation.suggestion'
    _description = 'Suggestion de Rapprochement'
    _order = 'confidence_score desc, id desc'

    line_id = fields.Many2one(
        'eazynova.bank.statement.line',
        string='Ligne Bancaire',
        required=True,
        ondelete='cascade',
        index=True
    )

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Ligne d\'Écriture',
        required=True,
        ondelete='cascade'
    )

    move_id = fields.Many2one(
        'account.move',
        string='Écriture',
        related='move_line_id.move_id',
        store=True
    )

    match_type = fields.Selection([
        ('exact_reference', 'Référence Exacte'),
        ('amount_date', 'Montant et Date'),
        ('partner_amount', 'Partenaire et Montant'),
        ('ai_semantic', 'Analyse Sémantique IA'),
        ('rule', 'Règle de Rapprochement'),
    ], string='Type de Correspondance', required=True)

    confidence_score = fields.Float(
        string='Score de Confiance',
        required=True,
        help="Score de confiance (0-1)"
    )

    match_reason = fields.Text(string='Raison de la Correspondance')

    def action_apply_suggestion(self):
        """Applique cette suggestion"""
        self.ensure_one()

        self.line_id.write({
            'matching_move_line_id': self.move_line_id.id,
            'matching_move_id': self.move_id.id,
            'reconciliation_state': 'reconciled',
            'confidence_score': self.confidence_score,
        })

        self.line_id.import_id.message_post(
            body=_("Suggestion de rapprochement appliquée pour: %s") % self.line_id.name
        )
