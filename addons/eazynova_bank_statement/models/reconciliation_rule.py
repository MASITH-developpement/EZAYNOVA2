# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re
import logging

_logger = logging.getLogger(__name__)


class ReconciliationRule(models.Model):
    _name = 'eazynova.reconciliation.rule'
    _description = 'Règle de Rapprochement Bancaire'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True)

    active = fields.Boolean(string='Actif', default=True)

    sequence = fields.Integer(string='Séquence', default=10)

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    journal_ids = fields.Many2many(
        'account.journal',
        string='Journaux',
        domain="[('type', '=', 'bank')]",
        help="Journaux auxquels cette règle s'applique. Vide = tous les journaux"
    )

    rule_type = fields.Selection([
        ('reference_pattern', 'Pattern de Référence'),
        ('amount_range', 'Plage de Montant'),
        ('partner_keyword', 'Mot-clé Partenaire'),
        ('description_keyword', 'Mot-clé Description'),
        ('combined', 'Règle Combinée'),
    ], string='Type de Règle', required=True, default='description_keyword')

    # Critères de correspondance
    reference_pattern = fields.Char(
        string='Pattern de Référence',
        help="Expression régulière pour correspondre à la référence"
    )

    description_keywords = fields.Char(
        string='Mots-clés Description',
        help="Mots-clés séparés par des virgules"
    )

    partner_keywords = fields.Char(
        string='Mots-clés Partenaire',
        help="Mots-clés séparés par des virgules"
    )

    amount_min = fields.Float(string='Montant Minimum')
    amount_max = fields.Float(string='Montant Maximum')

    # Actions
    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire à Assigner',
        help="Partenaire à assigner automatiquement si la règle correspond"
    )

    account_id = fields.Many2one(
        'account.account',
        string='Compte Comptable',
        help="Compte à utiliser pour la contrepartie"
    )

    confidence_boost = fields.Float(
        string='Boost de Confiance',
        default=0.2,
        help="Augmentation du score de confiance si cette règle correspond (0-1)"
    )

    note = fields.Text(string='Notes')

    match_count = fields.Integer(
        string='Nombre de Correspondances',
        readonly=True,
        default=0,
        help="Nombre de fois que cette règle a été utilisée"
    )

    last_match_date = fields.Datetime(
        string='Dernière Correspondance',
        readonly=True
    )

    def check_match(self, line):
        """Vérifie si la ligne correspond à cette règle"""
        self.ensure_one()

        if not self.active:
            return False

        # Vérifier le journal
        if self.journal_ids and line.import_id.journal_id.id not in self.journal_ids.ids:
            return False

        if self.rule_type == 'reference_pattern':
            return self._check_reference_pattern(line)

        elif self.rule_type == 'amount_range':
            return self._check_amount_range(line)

        elif self.rule_type == 'partner_keyword':
            return self._check_partner_keyword(line)

        elif self.rule_type == 'description_keyword':
            return self._check_description_keyword(line)

        elif self.rule_type == 'combined':
            return self._check_combined(line)

        return False

    def _check_reference_pattern(self, line):
        """Vérifie le pattern de référence"""
        if not self.reference_pattern or not line.ref:
            return False

        try:
            pattern = re.compile(self.reference_pattern, re.IGNORECASE)
            return bool(pattern.search(line.ref))
        except re.error:
            _logger.warning("Pattern invalide pour règle %s: %s", self.id, self.reference_pattern)
            return False

    def _check_amount_range(self, line):
        """Vérifie la plage de montant"""
        amount = abs(line.amount)

        if self.amount_min and amount < self.amount_min:
            return False

        if self.amount_max and amount > self.amount_max:
            return False

        return True

    def _check_partner_keyword(self, line):
        """Vérifie les mots-clés du partenaire"""
        if not self.partner_keywords:
            return False

        partner_text = (line.partner_name or '').lower()

        keywords = [k.strip().lower() for k in self.partner_keywords.split(',')]

        return any(keyword in partner_text for keyword in keywords if keyword)

    def _check_description_keyword(self, line):
        """Vérifie les mots-clés de la description"""
        if not self.description_keywords:
            return False

        description_text = (line.name or '').lower()

        keywords = [k.strip().lower() for k in self.description_keywords.split(',')]

        return any(keyword in description_text for keyword in keywords if keyword)

    def _check_combined(self, line):
        """Vérifie une règle combinée (ET logique)"""
        results = []

        if self.reference_pattern:
            results.append(self._check_reference_pattern(line))

        if self.description_keywords:
            results.append(self._check_description_keyword(line))

        if self.partner_keywords:
            results.append(self._check_partner_keyword(line))

        if self.amount_min or self.amount_max:
            results.append(self._check_amount_range(line))

        # Toutes les conditions doivent être vraies
        return all(results) if results else False

    def apply_rule(self, line):
        """Applique la règle à la ligne"""
        self.ensure_one()

        # Assigner le partenaire si défini
        if self.partner_id and not line.partner_id:
            line.partner_id = self.partner_id

        # Incrémenter le compteur de correspondances
        self.write({
            'match_count': self.match_count + 1,
            'last_match_date': fields.Datetime.now(),
        })

        return {
            'confidence_boost': self.confidence_boost,
            'account_id': self.account_id.id if self.account_id else False,
        }

    @api.model
    def apply_rules_to_line(self, line):
        """Applique toutes les règles correspondantes à une ligne"""
        rules = self.search([
            ('active', '=', True),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', line.import_id.company_id.id),
        ], order='sequence, id')

        total_confidence_boost = 0.0
        matched_rules = []

        for rule in rules:
            if rule.check_match(line):
                result = rule.apply_rule(line)
                total_confidence_boost += result.get('confidence_boost', 0)
                matched_rules.append(rule.name)

        if matched_rules:
            _logger.info(
                "Règles appliquées à la ligne %s: %s (boost: %.2f)",
                line.id, ', '.join(matched_rules), total_confidence_boost
            )

            # Ajouter le boost au score de confiance
            if line.confidence_score:
                line.confidence_score = min(1.0, line.confidence_score + total_confidence_boost)

        return matched_rules
