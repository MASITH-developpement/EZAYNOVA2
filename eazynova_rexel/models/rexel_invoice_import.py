# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class RexelInvoiceImport(models.Model):
    """Import de facture Rexel"""
    _name = 'eazynova.rexel.invoice.import'
    _description = 'Import Facture Rexel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default='Nouveau'
    )

    import_date = fields.Datetime(
        string='Date d\'import',
        default=fields.Datetime.now,
        required=True,
        readonly=True
    )

    source_type = fields.Selection([
        ('email', 'Email'),
        ('upload', 'Upload Manuel'),
        ('api', 'API')
    ], string='Type de source', default='email', required=True, readonly=True)

    file_name = fields.Char(
        string='Nom du fichier',
        readonly=True
    )

    file_data = fields.Binary(
        string='Fichier',
        attachment=True,
        readonly=True
    )

    file_type = fields.Selection([
        ('pdf', 'PDF'),
        ('xml', 'XML'),
        ('edi', 'EDI')
    ], string='Type de fichier', readonly=True)

    # Données extraites
    invoice_number = fields.Char(
        string='Numéro de facture',
        tracking=True
    )

    invoice_date = fields.Date(
        string='Date de facture',
        tracking=True
    )

    invoice_amount = fields.Monetary(
        string='Montant',
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Fournisseur',
        tracking=True
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Bon de commande',
        tracking=True
    )

    # Facture créée
    invoice_id = fields.Many2one(
        'account.move',
        string='Facture créée',
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('extracted', 'Données Extraites'),
        ('matched', 'Rapprochée'),
        ('created', 'Facture Créée'),
        ('error', 'Erreur')
    ], string='État', default='draft', required=True, tracking=True)

    error_message = fields.Text(
        string='Message d\'erreur',
        readonly=True
    )

    extraction_data = fields.Text(
        string='Données extraites (JSON)',
        help='Données brutes extraites du document'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Importé par',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Génère la référence automatiquement"""
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('eazynova.rexel.invoice.import') or 'Nouveau'
        return super().create(vals_list)

    def action_extract_data(self):
        """Extrait les données du document"""
        self.ensure_one()

        if not self.file_data:
            raise UserError('Aucun fichier à traiter.')

        config = self.env['eazynova.rexel.config'].sudo().search([], limit=1)

        try:
            # Décoder le fichier
            file_content = base64.b64decode(self.file_data)

            # TODO: Implémenter l'extraction selon le type de fichier
            if self.file_type == 'pdf' and config and config.use_ocr:
                # Utiliser le module OCR si disponible
                extraction_result = self._extract_from_pdf_ocr(file_content)
            elif self.file_type == 'xml':
                extraction_result = self._extract_from_xml(file_content)
            else:
                extraction_result = {}

            # Mettre à jour les champs
            self.write({
                'state': 'extracted',
                'invoice_number': extraction_result.get('invoice_number'),
                'invoice_date': extraction_result.get('invoice_date'),
                'invoice_amount': extraction_result.get('amount'),
                'partner_id': extraction_result.get('partner_id'),
                'extraction_data': str(extraction_result)
            })

            # Essayer de rapprocher avec un BC
            if config and config.auto_match_po:
                self.action_match_purchase_order()

        except Exception as e:
            _logger.error(f"Erreur extraction facture Rexel: {str(e)}")
            self.write({
                'state': 'error',
                'error_message': str(e)
            })

    def _extract_from_pdf_ocr(self, file_content):
        """Extrait les données d'un PDF avec OCR"""
        # TODO: Intégrer avec module eazynova_facture_ocr
        return {}

    def _extract_from_xml(self, file_content):
        """Extrait les données d'un fichier XML"""
        # TODO: Parser XML (Factur-X, UBL, etc.)
        return {}

    def action_match_purchase_order(self):
        """Rapproche avec un bon de commande"""
        self.ensure_one()

        if not self.invoice_number:
            return

        # Rechercher un BC correspondant
        po = self.env['purchase.order'].search([
            ('name', 'ilike', self.invoice_number),
            ('state', 'in', ['purchase', 'done']),
            ('partner_id', '=', self.partner_id.id if self.partner_id else False)
        ], limit=1)

        if po:
            self.write({
                'purchase_order_id': po.id,
                'state': 'matched'
            })

    def action_create_invoice(self):
        """Crée la facture brouillon"""
        self.ensure_one()

        if self.invoice_id:
            return self.invoice_id

        config = self.env['eazynova.rexel.config'].sudo().search([], limit=1)

        # Valeurs de base
        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id if self.partner_id else config.partner_id.id,
            'invoice_date': self.invoice_date or fields.Date.today(),
            'ref': self.invoice_number,
            'journal_id': config.default_journal_id.id if config and config.default_journal_id else False,
        }

        # Si rapproché avec BC, utiliser ses lignes
        if self.purchase_order_id:
            invoice_vals['purchase_id'] = self.purchase_order_id.id

        # Créer la facture
        invoice = self.env['account.move'].create(invoice_vals)

        # Attacher le document
        if self.file_data:
            self.env['ir.attachment'].create({
                'name': self.file_name or 'facture_rexel.pdf',
                'datas': self.file_data,
                'res_model': 'account.move',
                'res_id': invoice.id,
                'type': 'binary'
            })

        self.write({
            'invoice_id': invoice.id,
            'state': 'created'
        })

        # Notifier les utilisateurs
        if config and config.notification_user_ids:
            invoice.message_subscribe(partner_ids=config.notification_user_ids.mapped('partner_id').ids)
            invoice.message_post(
                body=f'Facture Rexel importée automatiquement depuis {self.name}',
                subject='Nouvelle facture Rexel'
            )

        return invoice

    def action_view_invoice(self):
        """Affiche la facture créée"""
        self.ensure_one()

        if not self.invoice_id:
            return

        return {
            'name': 'Facture',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
