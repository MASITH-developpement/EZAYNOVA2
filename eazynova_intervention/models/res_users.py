# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Droits interventions
    intervention_access_read = fields.Boolean(string="Lecture interventions")
    intervention_access_write = fields.Boolean(string="Écriture interventions")
    intervention_access_create = fields.Boolean(string="Création interventions")
    intervention_access_unlink = fields.Boolean(string="Suppression interventions")

    # Droits devis
    quotation_access_create = fields.Boolean(string="Création devis")
    quotation_access_read = fields.Boolean(string="Lecture devis")
    quotation_access_write = fields.Boolean(string="Modification devis")
    quotation_access_unlink = fields.Boolean(string="Suppression devis")

    # Droits facture
    invoice_access_create = fields.Boolean(string="Création facture")
    invoice_access_read = fields.Boolean(string="Lecture facture")
    invoice_access_write = fields.Boolean(string="Modification facture")
    invoice_access_unlink = fields.Boolean(string="Suppression facture")

    # Droits rapport d'intervention
    report_access_create = fields.Boolean(string="Création rapport d'intervention")
    report_access_write = fields.Boolean(string="Modification rapport d'intervention")
    report_access_unlink = fields.Boolean(string="Suppression rapport d'intervention")

    # Droits photo avant/après intervention
    photo_access_create = fields.Boolean(string="Création photo avant/après")
    photo_access_write = fields.Boolean(string="Modification photo avant/après")
    photo_access_unlink = fields.Boolean(string="Suppression photo avant/après")

    # Droits heure début/fin intervention
    hour_access_create = fields.Boolean(string="Création heure début/fin")
    hour_access_write = fields.Boolean(string="Modification heure début/fin")
    hour_access_unlink = fields.Boolean(string="Suppression heure début/fin")