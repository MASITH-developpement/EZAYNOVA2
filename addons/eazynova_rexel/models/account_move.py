# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    """Extension du modèle facture"""
    _inherit = 'account.move'

    rexel_import_id = fields.Many2one(
        'eazynova.rexel.invoice.import',
        string='Import Rexel',
        readonly=True,
        help='Import automatique dont est issue cette facture'
    )

    is_rexel_invoice = fields.Boolean(
        string='Facture Rexel',
        compute='_compute_is_rexel',
        store=True
    )

    @api.depends('rexel_import_id')
    def _compute_is_rexel(self):
        """Détermine si c'est une facture Rexel"""
        for move in self:
            move.is_rexel_invoice = bool(move.rexel_import_id)

    def action_view_rexel_import(self):
        """Affiche l'import Rexel associé"""
        self.ensure_one()

        if not self.rexel_import_id:
            return

        return {
            'name': 'Import Rexel',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.rexel.invoice.import',
            'res_id': self.rexel_import_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
