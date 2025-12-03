# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Hook exécuté après l'installation du module
    Débloque tous les modules en attente d'opération
    """
    _logger.info("=" * 80)
    _logger.info("ODOO UNLOCK - Début du déblocage")
    _logger.info("=" * 80)

    try:
        # Récupérer tous les modules en attente
        Module = env['ir.module.module']

        # Chercher les modules bloqués
        blocked_modules = Module.search([
            ('state', 'in', ['to install', 'to upgrade', 'to remove'])
        ])

        if blocked_modules:
            _logger.warning(f"Modules bloqués trouvés : {blocked_modules.mapped('name')}")

            # Réinitialiser l'état
            blocked_modules.write({'state': 'uninstalled'})
            env.cr.commit()

            _logger.info(f"✓ {len(blocked_modules)} modules débloqués avec succès")
        else:
            _logger.info("✓ Aucun module bloqué trouvé")

        # Nettoyer les verrous de base de données
        env.cr.execute("""
            SELECT relname, pid
            FROM pg_locks l
            JOIN pg_class c ON l.relation = c.oid
            WHERE relname LIKE 'ir_module%'
        """)
        locks = env.cr.fetchall()

        if locks:
            _logger.warning(f"Verrous trouvés : {locks}")
            # Note: On ne peut pas tuer les processus depuis Python de manière sûre
            _logger.warning("Des verrous existent. Un redémarrage d'Odoo est recommandé.")
        else:
            _logger.info("✓ Aucun verrou actif")

        _logger.info("=" * 80)
        _logger.info("ODOO UNLOCK - Déblocage terminé")
        _logger.info("=" * 80)
        _logger.info("Vous pouvez maintenant désinstaller ce module et installer vos modules.")

    except Exception as e:
        _logger.error(f"❌ Erreur lors du déblocage : {e}")
        import traceback
        _logger.error(traceback.format_exc())
