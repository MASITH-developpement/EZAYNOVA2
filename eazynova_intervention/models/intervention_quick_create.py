# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import models, fields, api


class InterventionQuickCreate(models.TransientModel):
    """Wizard pour création rapide d'intervention"""
    _name = 'intervention.quick.create'
    _description = 'Création rapide d\'intervention'

    # Champs essentiels pour la création rapide
    donneur_ordre_id = fields.Many2one(
        'res.partner', 
        string='Donneur d\'ordre',
        required=True,
        domain=[('is_company', '=', True)]
    )
    
    client_final_id = fields.Many2one(
        'res.partner', 
        string='Client final',
        domain=[('parent_id', '=', False)]
    )
    
    type_intervention = fields.Selection([
        ('plomberie', 'Plomberie'),
        ('electricite', 'Électricité'),
        ('mixte', 'Mixte (Plomberie + Électricité)'),
        ('autre', 'Autre')
    ], string='Type d\'intervention', required=True, default='plomberie')
    
    adresse_intervention = fields.Text(
        string='Adresse intervention',
        required=True
    )
    
    date_prevue = fields.Datetime(
        string='Date prévue',
        required=True,
        default=lambda self: datetime.now() + timedelta(days=1)
    )
    
    technicien_principal_id = fields.Many2one(
        'hr.employee',
        string='Technicien principal',
        domain=[('category_ids.name', 'ilike', 'Technicien')]
    )
    
    description = fields.Text(
        string='Description',
        required=True,
        placeholder="Décrivez brièvement l'intervention à réaliser..."
    )
    
    urgence = fields.Selection([
        ('normale', 'Normale'),
        ('urgent', 'Urgent'),
        ('critique', 'Critique')
    ], string='Niveau d\'urgence', default='normale')

    @api.onchange('donneur_ordre_id')
    def _onchange_donneur_ordre_id(self):
        """Auto-remplir le client final si c'est le même que le donneur d'ordre"""
        if self.donneur_ordre_id and not self.client_final_id:
            self.client_final_id = self.donneur_ordre_id

    def action_create_intervention(self):
        """Créer l'intervention avec les données saisies"""
        self.ensure_one()
        
        # Données pour créer l'intervention
        vals = {
            'donneur_ordre_id': self.donneur_ordre_id.id,
            'client_final_id': self.client_final_id.id if self.client_final_id else self.donneur_ordre_id.id,
            'type_intervention': self.type_intervention,
            'adresse_intervention': self.adresse_intervention,
            'date_prevue': self.date_prevue,
            'technicien_principal_id': self.technicien_principal_id.id if self.technicien_principal_id else False,
            'description': self.description,
            'statut': 'planifie',
        }
        
        # Créer l'intervention
        intervention = self.env['intervention.intervention'].create(vals)
        
        # Retourner l'action pour ouvrir l'intervention créée
        return {
            'name': 'Intervention créée',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'intervention.intervention',
            'res_id': intervention.id,
            'target': 'current',
        }

    def action_create_and_new(self):
        """Créer l'intervention et ouvrir un nouveau wizard"""
        self.ensure_one()
        self.action_create_intervention()
        
        # Retourner une nouvelle instance du wizard
        return {
            'name': 'Création rapide d\'intervention',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'intervention.quick.create',
            'target': 'new',
        }
