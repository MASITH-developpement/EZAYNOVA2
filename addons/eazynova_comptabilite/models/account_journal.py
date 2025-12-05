# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _name = 'account.journal'
    _description = 'Journal comptable'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom du journal',
        required=True,
        help='Nom du journal comptable'
    )

    code = fields.Char(
        string='Code',
        required=True,
        size=10,
        help='Code court du journal (ex: VE, AC, BQ)'
    )

    type = fields.Selection([
        ('sale', 'Ventes'),
        ('purchase', 'Achats'),
        ('cash', 'Caisse'),
        ('bank', 'Banque'),
        ('general', 'Opérations diverses'),
    ], string='Type', required=True, help='Type de journal')

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help='Ordre d\'affichage'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        help='Devise du journal. Laissez vide pour utiliser la devise de la société'
    )

    # Comptes par défaut
    default_account_id = fields.Many2one(
        'account.chart',
        string='Compte par défaut',
        help='Compte utilisé par défaut pour ce journal',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]"
    )

    # Banque
    bank_account_id = fields.Many2one(
        'eazynova.bank.account',
        string='Compte bancaire',
        help='Compte bancaire associé à ce journal',
        domain="[('company_id', '=', company_id)]"
    )

    bank_statements_source = fields.Selection([
        ('manual', 'Saisie manuelle'),
        ('file_import', 'Import de fichier'),
        ('api', 'Connexion API'),
    ], string='Source des relevés', default='manual')

    # Numérotation
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Séquence d\'écriture',
        help='Séquence utilisée pour numéroter les écritures',
        copy=False
    )

    refund_sequence = fields.Boolean(
        string='Séquence dédiée pour avoirs',
        default=False,
        help='Utilise une séquence dédiée pour les avoirs'
    )

    # Sécurité
    restrict_mode_hash_table = fields.Boolean(
        string='Verrouillage avec hash',
        default=False,
        help='Active le verrouillage inaltérable des écritures'
    )

    # Statistiques
    entries_count = fields.Integer(
        string='Nombre d\'écritures',
        compute='_compute_entries_count'
    )

    # Écritures
    move_ids = fields.One2many(
        'account.move',
        'journal_id',
        string='Écritures'
    )

    @api.depends('move_ids')
    def _compute_entries_count(self):
        """Compte le nombre d'écritures"""
        for journal in self:
            journal.entries_count = len(journal.move_ids)

    @api.constrains('code', 'company_id')
    def _check_code_unique(self):
        """Vérifie l'unicité du code par société"""
        for journal in self:
            if self.search_count([
                ('code', '=', journal.code),
                ('company_id', '=', journal.company_id.id),
                ('id', '!=', journal.id)
            ]) > 0:
                raise ValidationError(_(
                    'Le code de journal %s existe déjà pour cette société.'
                ) % journal.code)

    @api.model
    def create(self, vals):
        """Création du journal avec séquence automatique"""
        journal = super(AccountJournal, self).create(vals)

        # Créer la séquence automatiquement
        if not journal.sequence_id:
            sequence = self.env['ir.sequence'].create({
                'name': f"Séquence {journal.name}",
                'code': f'account.move.{journal.code.lower()}',
                'implementation': 'standard',
                'prefix': f'{journal.code}/',
                'padding': 5,
                'number_increment': 1,
                'company_id': journal.company_id.id,
            })
            journal.sequence_id = sequence.id

        return journal

    def action_view_moves(self):
        """Affiche les écritures du journal"""
        self.ensure_one()
        return {
            'name': _('Écritures - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('journal_id', '=', self.id)],
            'context': {'default_journal_id': self.id}
        }

    def action_create_new_move(self):
        """Crée une nouvelle écriture dans ce journal"""
        self.ensure_one()
        return {
            'name': _('Nouvelle écriture'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'context': {
                'default_journal_id': self.id,
                'default_move_type': 'entry'
            }
        }
