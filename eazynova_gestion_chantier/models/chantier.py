# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class Chantier(models.Model):
    _name = 'chantier.chantier'
    _description = 'Chantier de Construction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc, id desc'

    # Informations de base
    name = fields.Char(
        string='Numéro',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
    )

    title = fields.Char(
        string='Nom du chantier',
        required=True,
        tracking=True,
    )

    description = fields.Html(
        string='Description',
        tracking=True,
    )

    # Type de chantier
    type_chantier = fields.Selection([
        ('construction', 'Construction neuve'),
        ('renovation', 'Rénovation'),
        ('extension', 'Extension'),
        ('demolition', 'Démolition'),
        ('amenagement', 'Aménagement'),
        ('autre', 'Autre'),
    ], string='Type de chantier', default='construction', required=True, tracking=True)

    # Client
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
    )

    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Téléphone',
        readonly=True,
    )

    partner_email = fields.Char(
        related='partner_id.email',
        string='Email',
        readonly=True,
    )

    # Adresse du chantier
    address_id = fields.Many2one(
        'res.partner',
        string='Adresse du chantier',
        domain="['|', ('id', '=', partner_id), ('parent_id', '=', partner_id)]",
    )

    street = fields.Char(
        string='Rue',
    )

    street2 = fields.Char(
        string='Rue 2',
    )

    zip = fields.Char(
        string='Code postal',
    )

    city = fields.Char(
        string='Ville',
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='État/Province',
    )

    country_id = fields.Many2one(
        'res.country',
        string='Pays',
    )

    # Géolocalisation
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
    )

    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
    )

    # Dates
    date_debut = fields.Date(
        string='Date de début',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )

    date_fin_prevue = fields.Date(
        string='Date de fin prévue',
        required=True,
        tracking=True,
    )

    date_fin_reelle = fields.Date(
        string='Date de fin réelle',
        tracking=True,
    )

    duree_prevue = fields.Integer(
        string='Durée prévue (jours)',
        compute='_compute_duree_prevue',
        store=True,
    )

    duree_reelle = fields.Integer(
        string='Durée réelle (jours)',
        compute='_compute_duree_reelle',
        store=True,
    )

    # Responsables
    user_id = fields.Many2one(
        'res.users',
        string='Chef de chantier',
        default=lambda self: self.env.user,
        tracking=True,
    )

    conducteur_travaux_id = fields.Many2one(
        'res.users',
        string='Conducteur de travaux',
        tracking=True,
    )

    # Projet lié
    project_id = fields.Many2one(
        'project.project',
        string='Projet',
        tracking=True,
    )

    # Phases
    phase_ids = fields.One2many(
        'chantier.phase',
        'chantier_id',
        string='Phases',
    )

    phase_count = fields.Integer(
        string='Nombre de phases',
        compute='_compute_phase_count',
    )

    # Équipes
    equipe_ids = fields.Many2many(
        'chantier.equipe',
        'chantier_equipe_rel',
        'chantier_id',
        'equipe_id',
        string='Équipes',
    )

    # Matériel
    materiel_ids = fields.One2many(
        'chantier.materiel',
        'chantier_id',
        string='Matériel',
    )

    # Dépenses
    depense_ids = fields.One2many(
        'chantier.depense',
        'chantier_id',
        string='Dépenses',
    )

    # Financier
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Bon de commande',
        readonly=True,
    )

    montant_devis = fields.Monetary(
        string='Montant devis',
        currency_field='currency_id',
        tracking=True,
    )

    montant_facture = fields.Monetary(
        string='Montant facturé',
        compute='_compute_montant_facture',
        store=True,
        currency_field='currency_id',
    )

    montant_depense = fields.Monetary(
        string='Dépenses totales',
        compute='_compute_montant_depense',
        store=True,
        currency_field='currency_id',
    )

    marge = fields.Monetary(
        string='Marge',
        compute='_compute_marge',
        store=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('preparation', 'En préparation'),
        ('in_progress', 'En cours'),
        ('pause', 'En pause'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé'),
    ], string='État', default='draft', required=True, tracking=True)

    # Priorité
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente'),
    ], string='Priorité', default='1', tracking=True)

    # Avancement
    progress = fields.Float(
        string='Avancement (%)',
        compute='_compute_progress',
        store=True,
    )

    # Photos et documents
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'chantier_attachment_rel',
        'chantier_id',
        'attachment_id',
        string='Documents',
    )

    photo_count = fields.Integer(
        string='Nombre de photos',
        compute='_compute_photo_count',
    )

    # Notes
    note = fields.Text(
        string='Notes internes',
    )

    # Couleur
    color = fields.Integer(
        string='Couleur',
        compute='_compute_color',
    )

    # Computes
    @api.depends('date_debut', 'date_fin_prevue')
    def _compute_duree_prevue(self):
        for record in self:
            if record.date_debut and record.date_fin_prevue:
                delta = record.date_fin_prevue - record.date_debut
                record.duree_prevue = delta.days
            else:
                record.duree_prevue = 0

    @api.depends('date_debut', 'date_fin_reelle')
    def _compute_duree_reelle(self):
        for record in self:
            if record.date_debut and record.date_fin_reelle:
                delta = record.date_fin_reelle - record.date_debut
                record.duree_reelle = delta.days
            else:
                record.duree_reelle = 0

    @api.depends('phase_ids')
    def _compute_phase_count(self):
        for record in self:
            record.phase_count = len(record.phase_ids)

    @api.depends('depense_ids.montant')
    def _compute_montant_depense(self):
        for record in self:
            record.montant_depense = sum(record.depense_ids.mapped('montant'))

    @api.depends('sale_order_id.amount_total')
    def _compute_montant_facture(self):
        for record in self:
            if record.sale_order_id:
                record.montant_facture = record.sale_order_id.amount_total
            else:
                record.montant_facture = record.montant_devis

    @api.depends('montant_facture', 'montant_depense')
    def _compute_marge(self):
        for record in self:
            record.marge = record.montant_facture - record.montant_depense

    @api.depends('phase_ids.progress')
    def _compute_progress(self):
        for record in self:
            if record.phase_ids:
                record.progress = sum(record.phase_ids.mapped('progress')) / len(record.phase_ids)
            else:
                record.progress = 0.0

    @api.depends('attachment_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len([a for a in record.attachment_ids if a.mimetype and a.mimetype.startswith('image/')])

    @api.depends('state', 'priority')
    def _compute_color(self):
        for record in self:
            if record.state == 'cancel':
                record.color = 1  # Rouge
            elif record.state == 'done':
                record.color = 10  # Vert
            elif record.priority == '3':
                record.color = 2  # Orange
            else:
                record.color = 0  # Blanc

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('chantier.chantier') or _('Nouveau')
        return super(Chantier, self).create(vals)

    def action_prepare(self):
        """Préparer le chantier"""
        self.ensure_one()
        self.state = 'preparation'

    def action_start(self):
        """Démarrer le chantier"""
        self.ensure_one()
        if not self.phase_ids:
            raise UserError(_("Veuillez créer au moins une phase avant de démarrer le chantier."))
        self.state = 'in_progress'

    def action_pause(self):
        """Mettre en pause le chantier"""
        self.ensure_one()
        self.state = 'pause'

    def action_resume(self):
        """Reprendre le chantier"""
        self.ensure_one()
        self.state = 'in_progress'

    def action_done(self):
        """Terminer le chantier"""
        self.ensure_one()
        self.write({
            'state': 'done',
            'date_fin_reelle': fields.Date.today(),
        })

    def action_cancel(self):
        """Annuler le chantier"""
        self.ensure_one()
        self.state = 'cancel'

    def action_draft(self):
        """Remettre en brouillon"""
        self.ensure_one()
        self.state = 'draft'

    def action_view_phases(self):
        """Afficher les phases"""
        self.ensure_one()
        return {
            'name': _('Phases - %s') % self.title,
            'type': 'ir.actions.act_window',
            'res_model': 'chantier.phase',
            'view_mode': 'tree,form,kanban',
            'domain': [('chantier_id', '=', self.id)],
            'context': {'default_chantier_id': self.id},
        }

    def action_view_photos(self):
        """Afficher les photos"""
        self.ensure_one()
        return {
            'name': _('Photos - %s') % self.title,
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.attachment_ids.ids), ('mimetype', '=like', 'image/%')],
            'context': {
                'default_res_model': 'chantier.chantier',
                'default_res_id': self.id,
            },
        }
