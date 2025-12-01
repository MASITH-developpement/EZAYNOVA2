# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bs4 import BeautifulSoup


class ProductTemplate(models.Model):
    """
    Extension du modèle produit pour la vérification des prix
    """
    _inherit = 'product.template'

    def onchange(self):
        pass

    external_avg_price = fields.Float(
        string='Prix moyen externe',
        compute='_compute_external_avg_price',
        help="Prix moyen récupéré automatiquement depuis Datab ou Hemea."
    )

    def _compute_external_avg_price(self):
        """
        Récupère le prix moyen externe depuis Datab ou Hemea en temps réel.
        (Exemple générique, à adapter selon l'API réelle)
        """
        import requests
        DATAB_API_KEY = self.env['ir.config_parameter'].sudo().get_param(
            'eazynova_prix.datab_api_key'
        )
        for product in self:
            query = product.barcode or product.default_code or product.name
            price = 0.0
            # 1. Tentative API Datab
            if DATAB_API_KEY:
                try:
                    url = (
                        f'https://api.datab.io/v1/products/lookup?ean={query}'
                    )
                    headers = {'Authorization': f'Bearer {DATAB_API_KEY}'}
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.ok:
                        data = response.json()
                        price = data.get('average_price') or 0.0
                except (requests.RequestException, ValueError):
                    price = 0.0
            # 2. Fallback scraping Hemea
            if not price:
                try:
                    url = f'https://www.hemea.com/prix-travaux?q={query}'
                    response = requests.get(url, timeout=5)
                    if response.ok:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        price_span = soup.find('span', class_='average-price')
                        if price_span:
                            import re
                            match = re.search(
                                r'(\d+[\.,]?\d*)', price_span.text
                            )
                            if match:
                                price = float(match.group(1).replace(',', '.'))
                except (requests.RequestException, ValueError):
                    price = 0.0
            product.external_avg_price = price

    price_check_ids = fields.One2many(
        'eazynova.price.check',
        'product_tmpl_id',
        string='Vérifications de prix'
    )

    price_check_count = fields.Integer(
        string='Nombre de vérifications',
        compute='_compute_price_check_count'
    )

    last_price_check = fields.Datetime(
        string='Dernière vérification',
        compute='_compute_last_price_check'
    )

    price_status = fields.Selection([
        ('ok', 'Prix Correct'),
        ('warning', 'Attention'),
        ('alert', 'Alerte'),
        ('never', 'Jamais vérifié')
    ], string='Statut des prix', compute='_compute_price_status', store=True)

    enable_price_check = fields.Boolean(
        string='Activer la vérification des prix',
        default=True,
        help='Activer la vérification automatique des prix pour cet article'
    )

    @api.depends('price_check_ids')
    def _compute_price_check_count(self):
        """Calcule le nombre de vérifications"""
        for product in self:
            product.price_check_count = len(product.price_check_ids)

    @api.depends('price_check_ids.check_date')
    def _compute_last_price_check(self):
        """Récupère la date de la dernière vérification"""
        for product in self:
            if product.price_check_ids:
                product.last_price_check = max(
                    product.price_check_ids.mapped('check_date'))
            else:
                product.last_price_check = False

    @api.depends('price_check_ids.status')
    def _compute_price_status(self):
        """Détermine le statut global des prix"""
        for product in self:
            if not product.price_check_ids:
                product.price_status = 'never'
            else:
                # Récupérer la dernière vérification
                latest_check = product.price_check_ids.sorted(
                    'check_date', reverse=True)[0]
                product.price_status = latest_check.status

    def action_check_prices(self):
        """Lance la vérification des prix pour ce produit"""
        self.ensure_one()

        # Ouvrir le wizard de vérification
        return {
            'name': 'Vérifier les Prix',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.price.verification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_ids': [(6, 0, self.product_variant_ids.ids)]
            }
        }

    def action_view_price_checks(self):
        """Affiche l'historique des vérifications de prix"""
        self.ensure_one()

        return {
            'name': f'Vérifications de prix - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'eazynova.price.check',
            'view_mode': 'tree,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {'default_product_id': self.product_variant_id.id}
        }

    def cron_check_prices(self):
        """Tâche planifiée pour vérifier les prix automatiquement"""
        # Récupérer les produits avec vérification activée
        products = self.search([('enable_price_check', '=', True)])

        # Récupérer la source de prix par défaut
        default_source = self.env['eazynova.price.source'].search([
            ('active', '=', True)
        ], limit=1)

        if not default_source:
            return

        # Créer une vérification pour chaque produit
        for product in products:
            for variant in product.product_variant_ids:
                self.env['eazynova.price.check'].create({
                    'product_id': variant.id,
                    'source_id': default_source.id,
                    'current_sale_price': product.list_price,
                    'current_cost_price': product.standard_price,
                    # Les prix de référence seront mis à jour par l'API
                    'reference_sale_price': product.list_price,
                    'reference_cost_price': product.standard_price,
                })
