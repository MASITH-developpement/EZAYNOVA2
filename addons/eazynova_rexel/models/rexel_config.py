# -*- coding: utf-8 -*-

from odoo import models, fields


class RexelConfig(models.Model):
    """Configuration Rexel"""
    _name = 'eazynova.rexel.config'
    _description = 'Configuration Rexel'

    name = fields.Char(
        string='Configuration',
        default='Configuration Rexel',
        required=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Fournisseur Rexel',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        help='Fiche fournisseur Rexel dans Odoo'
    )

    email_domain = fields.Char(
        string='Domaine Email',
        default='@rexel.fr',
        help='Domaine email pour filtrer les factures Rexel'
    )

    auto_create_draft = fields.Boolean(
        string='Création automatique brouillon',
        default=True,
        help='Créer automatiquement les factures en brouillon'
    )

    auto_match_po = fields.Boolean(
        string='Rapprochement automatique BC',
        default=True,
        help='Tenter de rapprocher avec les bons de commande'
    )

    use_ocr = fields.Boolean(
        string='Utiliser OCR',
        default=True,
        help='Utiliser l\'OCR pour extraire les données des PDF'
    )

    use_ai_validation = fields.Boolean(
        string='Validation IA',
        default=False,
        help='Utiliser l\'IA pour valider les factures (nécessite module OCR)'
    )

    default_journal_id = fields.Many2one(
        'account.journal',
        string='Journal par défaut',
        domain=[('type', '=', 'purchase')],
        help='Journal comptable pour les factures Rexel'
    )

    notification_user_ids = fields.Many2many(
        'res.users',
        string='Utilisateurs à notifier',
        help='Utilisateurs recevant les notifications de nouvelle facture'
    )

    import_count = fields.Integer(
        string='Nombre d\'imports',
        compute='_compute_import_count'
    )

    def _compute_import_count(self):
        """Calcule le nombre d'imports"""
        for config in self:
            config.import_count = self.env['eazynova.rexel.invoice.import'].search_count([])

    def action_view_imports(self):
        """Affiche les imports"""
        self.ensure_one()

        return {
            'name': 'Imports Rexel',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.rexel.invoice.import',
            'view_mode': 'tree,form',
            'target': 'current'
        }
