# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FunnelSubmissionValue(models.Model):
    _name = 'sales.funnel.submission.value'
    _description = 'Valeur de Soumission'
    _order = 'field_id'

    submission_id = fields.Many2one(
        'sales.funnel.submission',
        string='Soumission',
        required=True,
        ondelete='cascade'
    )
    field_id = fields.Many2one(
        'sales.funnel.field',
        string='Champ',
        required=True
    )
    value = fields.Text(
        string='Valeur'
    )
    file_data = fields.Binary(
        string='Fichier',
        attachment=True
    )
    file_name = fields.Char(
        string='Nom du fichier'
    )
