# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PlanningAbsenceRefuseWizard(models.TransientModel):
    _name = 'eazynova.planning.absence.refuse.wizard'
    _description = 'Assistant de refus d\'absence'

    absence_id = fields.Many2one(
        'eazynova.planning.absence',
        string="Absence",
        required=True
    )

    refused_reason = fields.Text(
        string="Motif du refus",
        required=True,
        help="Expliquez pourquoi cette demande d'absence est refusée"
    )

    def action_refuse(self):
        """Refuse l'absence avec le motif saisi"""
        self.ensure_one()

        if not self.refused_reason:
            raise UserError(_("Vous devez saisir un motif de refus."))

        self.absence_id.write({
            'state': 'refused',
            'refused_by': self.env.user.id,
            'refused_date': fields.Datetime.now(),
            'refused_reason': self.refused_reason,
        })

        # Envoyer une notification à la personne qui a demandé l'absence
        self.absence_id.message_post(
            body=_("Demande d'absence refusée.<br/><strong>Motif:</strong> %s") % self.refused_reason,
            subject=_("Absence refusée"),
            message_type='notification',
            partner_ids=self.absence_id.requested_by.partner_id.ids,
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Absence refusée"),
                'message': _("La demande d'absence a été refusée."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """Annule et ferme le wizard"""
        return {'type': 'ir.actions.act_window_close'}
