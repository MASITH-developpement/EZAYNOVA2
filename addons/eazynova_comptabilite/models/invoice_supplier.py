# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InvoiceSupplier(models.Model):
    """
    Modèle hérité d'account.move pour les factures fournisseurs
    Ajoute des fonctionnalités spécifiques aux factures fournisseurs avec OCR
    """
    _inherit = 'account.move'

    # OCR et extraction automatique
    has_attachment = fields.Boolean(
        string='A une pièce jointe',
        compute='_compute_has_attachment'
    )

    ocr_status = fields.Selection([
        ('pending', 'En attente'),
        ('processing', 'Traitement en cours'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ], string='Statut OCR', default='pending')

    ocr_confidence = fields.Float(
        string='Confiance OCR',
        help='Niveau de confiance de l\'extraction OCR (0-100)'
    )

    ocr_extracted_data = fields.Text(
        string='Données extraites',
        help='Données brutes extraites par OCR'
    )

    # Validation
    is_validated = fields.Boolean(
        string='Validé',
        default=False,
        help='La facture a été validée par un humain'
    )

    validation_required = fields.Boolean(
        string='Validation requise',
        compute='_compute_validation_required',
        help='La facture nécessite une validation manuelle'
    )

    # Workflow d\'approbation
    approval_status = fields.Selection([
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ], string='Statut d\'approbation', default='pending')

    approver_id = fields.Many2one(
        'res.users',
        string='Approbateur'
    )

    approval_date = fields.Datetime(
        string='Date d\'approbation'
    )

    # Matching avec commandes d\'achat
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Commande d\'achat',
        help='Commande d\'achat liée'
    )

    def _compute_has_attachment(self):
        """Vérifie si la facture a une pièce jointe"""
        for invoice in self:
            invoice.has_attachment = bool(invoice.attachment_count > 0)

    @api.depends('ocr_confidence')
    def _compute_validation_required(self):
        """Détermine si une validation manuelle est requise"""
        for invoice in self:
            # Si confiance OCR < 80%, validation requise
            invoice.validation_required = (
                invoice.ocr_confidence < 80.0 and
                invoice.ocr_status == 'done' and
                not invoice.is_validated
            )

    def action_extract_ocr(self):
        """Lance l'extraction OCR sur la facture"""
        for invoice in self:
            # Récupérer les pièces jointes
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', invoice.id)
            ])

            if not attachments:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Erreur'),
                        'message': _('Aucune pièce jointe trouvée.'),
                        'type': 'warning',
                    }
                }

            # Marquer comme en traitement
            invoice.ocr_status = 'processing'

            # Lancer le service OCR
            ocr_service = self.env['eazynova.invoice.ocr.service']
            result = ocr_service.extract_invoice_data(attachments[0])

            if result.get('success'):
                # Mettre à jour les champs
                invoice.write({
                    'partner_id': result.get('partner_id'),
                    'invoice_date': result.get('invoice_date'),
                    'invoice_date_due': result.get('invoice_date_due'),
                    'ref': result.get('reference'),
                    'amount_total': result.get('amount_total'),
                    'ocr_status': 'done',
                    'ocr_confidence': result.get('confidence', 0.0),
                    'ocr_extracted_data': str(result.get('raw_data')),
                })

                # Créer les lignes de facture
                if result.get('lines'):
                    for line_data in result['lines']:
                        self.env['account.move.line'].create({
                            'move_id': invoice.id,
                            'name': line_data.get('description', '/'),
                            'quantity': line_data.get('quantity', 1.0),
                            'price_unit': line_data.get('price_unit', 0.0),
                            'account_id': line_data.get('account_id'),
                            'tax_ids': line_data.get('tax_ids', []),
                        })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Succès'),
                        'message': _('Extraction OCR terminée avec succès.'),
                        'type': 'success',
                    }
                }
            else:
                invoice.ocr_status = 'error'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Erreur'),
                        'message': result.get('error', _('Erreur lors de l\'extraction OCR.')),
                        'type': 'danger',
                    }
                }

        return True

    def action_validate_invoice(self):
        """Valide manuellement la facture après vérification"""
        for invoice in self:
            invoice.write({
                'is_validated': True,
                'validation_required': False
            })

        return True

    def action_approve(self):
        """Approuve la facture"""
        for invoice in self:
            invoice.write({
                'approval_status': 'approved',
                'approver_id': self.env.user.id,
                'approval_date': fields.Datetime.now()
            })

        return True

    def action_reject(self):
        """Rejette la facture"""
        for invoice in self:
            invoice.write({
                'approval_status': 'rejected',
                'approver_id': self.env.user.id,
                'approval_date': fields.Datetime.now()
            })

        return True
