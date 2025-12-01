# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class InterventionQuickCreate(models.TransientModel):
    _name = 'intervention.quick.create'
    _description = 'Assistant de création rapide d\'intervention'

    # Étape 1 : Informations client
    donneur_ordre_id = fields.Many2one(
        'res.partner',
        string="Donneur d'ordre",
        required=True,
        help="Personne/entreprise qui commande l'intervention"
    )

    client_final_id = fields.Many2one(
        'res.partner',
        string="Client final",
        help="Si différent du donneur d'ordre"
    )

    # Étape 2 : Informations intervention
    type_intervention = fields.Selection([
        ('plomberie', 'Plomberie'),
        ('electricite', 'Électricité'),
        ('mixte', 'Plomberie + Électricité')
    ], string="Type d'intervention", required=True, default='plomberie')

    date_prevue = fields.Datetime(
        string="Date prévue",
        required=True,
        default=fields.Datetime.now
    )

    duree_prevue = fields.Float(string="Durée prévue (h)", default=2.0)

    technicien_principal_id = fields.Many2one(
        'hr.employee',
        string="Technicien principal",
        required=True,
        domain=['|', ('category_ids.name', 'ilike', 'Technicien'),
                ('active', '=', True)],
        help="Sélectionnez un technicien ou un employé pour l'intervention"
    )

    # Étape 3 : Localisation
    adresse_intervention = fields.Text(
        string="Adresse d'intervention",
        required=True,
        help="Saisissez l'adresse complète de l'intervention"
    )

    # Étape 4 : Description
    description = fields.Text(
        string="Description du problème",
        help="Décrivez brièvement le problème à résoudre..."
    )

    priorite = fields.Selection([
        ('normale', 'Normale'),
        ('urgente', 'Urgente'),
        ('critique', 'Critique')
    ], string="Priorité", default='normale')

    # Options
    creer_devis = fields.Boolean(
        string="Créer automatiquement un devis",
        default=True,
        help="Un devis sera créé automatiquement après la création de l'intervention"
    )

    creer_evenement_calendrier = fields.Boolean(
        string="Créer un événement calendrier",
        default=True,
        help="Un événement sera ajouté au calendrier du technicien"
    )

    def action_create_intervention(self):
        """Créer l'intervention avec toutes les informations saisies"""
        self.ensure_one()

        # Validation des données
        if not self.donneur_ordre_id:
            raise UserError("Veuillez sélectionner un donneur d'ordre.")

        if not self.technicien_principal_id:
            raise UserError("Veuillez sélectionner un technicien principal.")

        # Préparer les valeurs pour l'intervention
        intervention_vals = {
            'donneur_ordre_id': self.donneur_ordre_id.id,
            'client_final_id': self.client_final_id.id if self.client_final_id else False,
            'type_intervention': self.type_intervention,
            'date_prevue': self.date_prevue,
            'duree_prevue': self.duree_prevue,
            'technicien_principal_id': self.technicien_principal_id.id,
            'adresse_intervention': self.adresse_intervention,
            'description': self.description,
            'priorite': self.priorite,
        }

        # Créer l'intervention
        intervention = self.env['intervention.intervention'].create(
            intervention_vals)

        # Actions optionnelles
        if self.creer_devis:
            try:
                intervention.action_create_sale_order()
            except Exception as e:
                # Si la création du devis échoue, on continue
                pass

        if self.creer_evenement_calendrier:
            try:
                intervention._create_calendar_event()
            except Exception as e:
                # Si la création de l'événement échoue, on continue
                pass

        # Retourner l'action pour ouvrir l'intervention créée
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'intervention.intervention',
            'res_id': intervention.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'create': False}
        }

    @api.onchange('donneur_ordre_id')
    def _onchange_donneur_ordre_id(self):
        """Pré-remplir automatiquement l'adresse si disponible"""
        if self.donneur_ordre_id and not self.adresse_intervention:
            partner = self.donneur_ordre_id
            address_parts = []
            if partner.street:
                address_parts.append(partner.street)
            if partner.street2:
                address_parts.append(partner.street2)
            if partner.zip:
                address_parts.append(partner.zip)
            if partner.city:
                address_parts.append(partner.city)

            if address_parts:
                self.adresse_intervention = ', '.join(address_parts)

    @api.onchange('client_final_id')
    def _onchange_client_final_id(self):
        """Utiliser l'adresse du client final si renseigné"""
        if self.client_final_id:
            partner = self.client_final_id
            address_parts = []
            if partner.street:
                address_parts.append(partner.street)
            if partner.street2:
                address_parts.append(partner.street2)
            if partner.zip:
                address_parts.append(partner.zip)
            if partner.city:
                address_parts.append(partner.city)

            if address_parts:
                self.adresse_intervention = ', '.join(address_parts)
