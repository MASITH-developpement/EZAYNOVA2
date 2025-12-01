# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ChantierCloseWizard(models.TransientModel):
    _name = 'chantier.close.wizard'
    _description = 'Assistant de clôture de chantier'

    chantier_id = fields.Many2one(
        'chantier.chantier',
        string='Chantier',
        required=True,
        readonly=True,
    )

    date_fin_reelle = fields.Date(
        string='Date de fin réelle',
        required=True,
        default=fields.Date.today,
    )

    phase_count = fields.Integer(
        string='Nombre de phases',
        related='chantier_id.phase_count',
    )

    phase_terminee_count = fields.Integer(
        string='Phases terminées',
        compute='_compute_phase_terminee_count',
    )

    tache_count = fields.Integer(
        string='Nombre de tâches',
        compute='_compute_tache_count',
    )

    tache_terminee_count = fields.Integer(
        string='Tâches terminées',
        compute='_compute_tache_terminee_count',
    )

    montant_devis = fields.Monetary(
        string='Montant devis',
        related='chantier_id.montant_devis',
        currency_field='currency_id',
    )

    montant_facture = fields.Monetary(
        string='Montant facturé',
        related='chantier_id.montant_facture',
        currency_field='currency_id',
    )

    montant_depense = fields.Monetary(
        string='Dépenses totales',
        related='chantier_id.montant_depense',
        currency_field='currency_id',
    )

    marge = fields.Monetary(
        string='Marge',
        related='chantier_id.marge',
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='chantier_id.currency_id',
    )

    note_cloture = fields.Text(
        string='Notes de clôture',
        help='Commentaires et remarques sur la clôture du chantier',
    )

    force_close = fields.Boolean(
        string='Forcer la clôture',
        help='Cocher pour clôturer le chantier même si toutes les phases/tâches ne sont pas terminées',
    )

    @api.depends('chantier_id', 'chantier_id.phase_ids', 'chantier_id.phase_ids.state')
    def _compute_phase_terminee_count(self):
        for wizard in self:
            wizard.phase_terminee_count = len(wizard.chantier_id.phase_ids.filtered(lambda p: p.state == 'done'))

    @api.depends('chantier_id', 'chantier_id.phase_ids', 'chantier_id.phase_ids.tache_ids')
    def _compute_tache_count(self):
        for wizard in self:
            wizard.tache_count = len(wizard.chantier_id.phase_ids.mapped('tache_ids'))

    @api.depends('chantier_id', 'chantier_id.phase_ids', 'chantier_id.phase_ids.tache_ids', 'chantier_id.phase_ids.tache_ids.state')
    def _compute_tache_terminee_count(self):
        for wizard in self:
            wizard.tache_terminee_count = len(wizard.chantier_id.phase_ids.mapped('tache_ids').filtered(lambda t: t.state == 'done'))

    def action_close_chantier(self):
        """Clôturer le chantier"""
        self.ensure_one()

        if not self.force_close:
            # Vérifier que toutes les phases sont terminées
            if self.phase_terminee_count < self.phase_count:
                raise UserError(_(
                    "Toutes les phases ne sont pas terminées (%s/%s). "
                    "Veuillez terminer toutes les phases ou cocher 'Forcer la clôture'."
                ) % (self.phase_terminee_count, self.phase_count))

            # Vérifier que toutes les tâches sont terminées
            if self.tache_count > 0 and self.tache_terminee_count < self.tache_count:
                raise UserError(_(
                    "Toutes les tâches ne sont pas terminées (%s/%s). "
                    "Veuillez terminer toutes les tâches ou cocher 'Forcer la clôture'."
                ) % (self.tache_terminee_count, self.tache_count))

        # Mettre à jour le chantier
        vals = {
            'state': 'done',
            'date_fin_reelle': self.date_fin_reelle,
        }

        if self.note_cloture:
            current_note = self.chantier_id.note or ''
            vals['note'] = current_note + '\n\n=== Notes de clôture ===\n' + self.note_cloture

        self.chantier_id.write(vals)

        # Message dans le chatter
        self.chantier_id.message_post(
            body=_("Chantier clôturé le %s.<br/>Marge finale: %s") % (
                self.date_fin_reelle.strftime('%d/%m/%Y'),
                "{:,.2f} {}".format(self.marge, self.currency_id.symbol)
            ),
            subject=_("Clôture du chantier"),
        )

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Annuler la clôture"""
        return {'type': 'ir.actions.act_window_close'}
