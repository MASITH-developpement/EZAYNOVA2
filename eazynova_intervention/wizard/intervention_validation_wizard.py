# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class InterventionValidationWizard(models.TransientModel):
    _name = 'intervention.validation.wizard'
    _description = 'Assistant de validation et signature client'

    intervention_id = fields.Many2one(
        'intervention.intervention',
        string="Intervention",
        required=True
    )
    
    nom_signataire = fields.Char(
        string="Nom du signataire",
        required=True,
        help="Nom de la personne qui signe"
    )
    
    signature_client = fields.Binary(
        string="Signature client",
        help="Signature numérique du client"
    )
    
    travaux_realises = fields.Text(
        string="Travaux réalisés",
        help="Résumé des travaux effectués"
    )
    
    observations_client = fields.Text(
        string="Observations du client",
        help="Commentaires ou remarques du client"
    )
    
    satisfaction_client = fields.Selection([
        ('1', '⭐ Très insatisfait'),
        ('2', '⭐⭐ Insatisfait'),
        ('3', '⭐⭐⭐ Correct'),
        ('4', '⭐⭐⭐⭐ Satisfait'),
        ('5', '⭐⭐⭐⭐⭐ Très satisfait')
    ], string="Satisfaction client", default='4')
    
    @api.model
    def default_get(self, fields_list):
        """Pré-remplir avec les données de l'intervention"""
        defaults = super().default_get(fields_list)
        
        if 'intervention_id' in defaults and defaults['intervention_id']:
            intervention = self.env['intervention.intervention'].browse(defaults['intervention_id'])
            if 'travaux_realises' in fields_list:
                defaults['travaux_realises'] = intervention.travaux_realises or intervention.description
                
        return defaults
    
    def action_valider_signature(self):
        """Valider l'intervention avec signature client et envoyer le rapport par mail (utilise la méthode centrale)"""
        self.ensure_one()
        self.intervention_id.validate_client_signature(
            nom_signataire=self.nom_signataire,
            signature_client=self.signature_client,
            travaux_realises=self.travaux_realises,
            observations_client=self.observations_client,
            satisfaction_client=self.satisfaction_client
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Validation enregistrée',
                'message': f'Intervention validée et rapport envoyé par mail à tous les destinataires.',
                'type': 'success',
                'sticky': False,
            }
        }
