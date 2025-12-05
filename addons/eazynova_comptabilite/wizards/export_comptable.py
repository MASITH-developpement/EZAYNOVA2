# -*- coding: utf-8 -*-
from odoo import models, fields

class ExportComptableWizard(models.TransientModel):
    _name = 'export.comptable.wizard'
    _description = 'Assistant d\'export comptable'
    _inherit = 'accounting.export'
