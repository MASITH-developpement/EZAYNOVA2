# -*- coding: utf-8 -*-

import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InterventionMailConfig(models.Model):
    """Configuration des emails pour création automatique d'intervention"""
    
    _name = 'intervention.mail.config'
    _description = 'Configuration des emails pour création d\'intervention'
    _rec_name = 'email'

    email = fields.Char(
        string='Adresse email',
        required=True,
        help="Email depuis lequel les interventions peuvent être créées automatiquement"
    )
    
    donneur_ordre_id = fields.Many2one(
        'res.partner',
        string='Donneur d\'ordre par défaut',
        required=True,
        help="Donneur d'ordre à associer aux interventions créées depuis cet email"
    )
    
    active = fields.Boolean(
        default=True,
        string='Actif'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ('email_company_uniq',
         'unique(email, company_id)',
         'Cette adresse email est déjà configurée pour cette société!')
    ]

    @api.constrains('email')
    def _check_email_valid(self):
        """Valide le format de l'adresse email"""
        for record in self:
            if record.email:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                    raise ValidationError(
                        _("L'adresse email '%s' n'est pas valide") % record.email
                    )

    def name_get(self):
        """Affichage personnalisé : email → donneur d'ordre"""
        result = []
        for record in self:
            name = f"{record.email} → {record.donneur_ordre_id.name}"
            result.append((record.id, name))
        return result