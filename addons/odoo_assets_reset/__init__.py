# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Hook appelé après l'installation du module.
    Vide tous les assets pour forcer leur régénération.
    """
    _logger.info("=" * 80)
    _logger.info("DÉBUT: Nettoyage des assets Odoo")
    _logger.info("=" * 80)

    try:
        # Supprimer tous les attachments d'assets
        assets = env['ir.attachment'].sudo().search([
            ('name', 'ilike', '.min.js'),
        ])
        if assets:
            _logger.info(f"Suppression de {len(assets)} fichiers d'assets JavaScript...")
            assets.unlink()

        assets_css = env['ir.attachment'].sudo().search([
            ('name', 'ilike', '.min.css'),
        ])
        if assets_css:
            _logger.info(f"Suppression de {len(assets_css)} fichiers d'assets CSS...")
            assets_css.unlink()

        # Vider le cache des assets
        env.registry.clear_caches()

        _logger.info("✓ Assets nettoyés avec succès")
        _logger.info("✓ Les assets seront régénérés au prochain chargement de page")

    except Exception as e:
        _logger.error(f"Erreur lors du nettoyage des assets: {e}")

    _logger.info("=" * 80)
    _logger.info("FIN: Nettoyage des assets Odoo")
    _logger.info("=" * 80)
