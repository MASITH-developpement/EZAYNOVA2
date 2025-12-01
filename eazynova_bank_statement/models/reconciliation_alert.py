# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ReconciliationAlert(models.Model):
    _name = 'eazynova.reconciliation.alert'
    _description = 'Alerte de Rapprochement Bancaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    import_id = fields.Many2one(
        'eazynova.bank.statement.import',
        string='Import',
        required=True,
        ondelete='cascade',
        index=True
    )

    line_id = fields.Many2one(
        'eazynova.bank.statement.line',
        string='Ligne Bancaire',
        ondelete='cascade',
        index=True
    )

    alert_type = fields.Selection([
        ('not_reconciled', 'Non Rapproché'),
        ('uncertain', 'Rapprochement Incertain'),
        ('duplicate', 'Doublon Potentiel'),
        ('amount_mismatch', 'Montant Incohérent'),
        ('date_mismatch', 'Date Incohérente'),
        ('missing_partner', 'Partenaire Manquant'),
        ('manual_review', 'Révision Manuelle Requise'),
    ], string='Type d\'Alerte', required=True, tracking=True)

    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('critical', 'Critique'),
    ], string='Sévérité', required=True, default='warning', tracking=True)

    state = fields.Selection([
        ('new', 'Nouveau'),
        ('in_progress', 'En Cours'),
        ('resolved', 'Résolu'),
        ('ignored', 'Ignoré'),
    ], string='État', default='new', tracking=True, required=True)

    message = fields.Text(string='Message', required=True)

    resolution_note = fields.Text(string='Note de Résolution')

    resolved_by = fields.Many2one(
        'res.users',
        string='Résolu Par',
        readonly=True
    )

    resolved_date = fields.Datetime(string='Date de Résolution', readonly=True)

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        related='import_id.company_id',
        store=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Assigné à',
        tracking=True
    )

    priority = fields.Selection([
        ('0', 'Faible'),
        ('1', 'Normal'),
        ('2', 'Élevé'),
        ('3', 'Urgent'),
    ], string='Priorité', default='1', tracking=True)

    @api.model
    def create(self, vals):
        alert = super().create(vals)

        # Créer une activité si nécessaire
        if alert.severity in ['error', 'critical']:
            alert.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Alerte de rapprochement: %s') % alert.alert_type,
                note=alert.message,
                user_id=alert.user_id.id if alert.user_id else self.env.user.id,
            )

        return alert

    def action_resolve(self):
        """Marque l'alerte comme résolue"""
        for record in self:
            record.write({
                'state': 'resolved',
                'resolved_by': self.env.user.id,
                'resolved_date': fields.Datetime.now(),
            })

            # Marquer les activités comme terminées
            record.activity_ids.action_feedback(feedback=_('Alerte résolue'))

    def action_ignore(self):
        """Ignore l'alerte"""
        for record in self:
            record.write({
                'state': 'ignored',
                'resolved_by': self.env.user.id,
                'resolved_date': fields.Datetime.now(),
            })

            record.activity_ids.unlink()

    def action_in_progress(self):
        """Marque l'alerte comme en cours"""
        self.write({'state': 'in_progress'})

    def action_view_line(self):
        """Ouvre la ligne bancaire associée"""
        self.ensure_one()

        if not self.line_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'name': _('Ligne Bancaire'),
            'res_model': 'eazynova.bank.statement.line',
            'res_id': self.line_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_import(self):
        """Ouvre l'import associé"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Bancaire'),
            'res_model': 'eazynova.bank.statement.import',
            'res_id': self.import_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def get_unresolved_count(self):
        """Retourne le nombre d'alertes non résolues"""
        return self.search_count([
            ('state', 'in', ['new', 'in_progress']),
        ])

    @api.model
    def get_critical_count(self):
        """Retourne le nombre d'alertes critiques non résolues"""
        return self.search_count([
            ('state', 'in', ['new', 'in_progress']),
            ('severity', '=', 'critical'),
        ])
