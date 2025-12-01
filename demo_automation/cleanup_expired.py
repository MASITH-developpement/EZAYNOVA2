#!/usr/bin/env python3
"""
Script pour nettoyer automatiquement les démos Odoo expirées
À exécuter avec un cron job (ex: toutes les heures)
"""

import xmlrpc.client
import sqlite3
from datetime import datetime
import os

class DemoCleanup:
    def __init__(self, odoo_url, master_password, db_path='demos.db'):
        """
        Args:
            odoo_url: URL de votre instance Odoo
            master_password: Le ADMIN_PASSWORD configuré dans Railway
            db_path: Chemin vers la base de données SQLite pour tracker les démos
        """
        self.odoo_url = odoo_url
        self.master_password = master_password
        self.db_path = db_path
        self.db_manager = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/db')
        self._init_database()

    def _init_database(self):
        """Initialise la base de données SQLite pour tracker les démos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demos (
                db_name TEXT PRIMARY KEY,
                user_email TEXT,
                created_at TEXT,
                expires_at TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        conn.commit()
        conn.close()

    def register_demo(self, db_name, user_email, created_at, expires_at):
        """Enregistre une nouvelle démo dans la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO demos (db_name, user_email, created_at, expires_at, status)
            VALUES (?, ?, ?, ?, 'active')
        ''', (db_name, user_email, created_at, expires_at))
        conn.commit()
        conn.close()

    def get_expired_demos(self):
        """Retourne la liste des démos expirées"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            SELECT db_name, user_email, expires_at
            FROM demos
            WHERE expires_at < ? AND status = 'active'
        ''', (now,))
        expired = cursor.fetchall()
        conn.close()
        return expired

    def mark_as_deleted(self, db_name):
        """Marque une démo comme supprimée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE demos
            SET status = 'deleted'
            WHERE db_name = ?
        ''', (db_name,))
        conn.commit()
        conn.close()

    def cleanup_expired_demos(self, dry_run=False):
        """
        Supprime toutes les démos expirées

        Args:
            dry_run: Si True, liste les démos à supprimer sans les supprimer
        """
        expired_demos = self.get_expired_demos()

        if not expired_demos:
            print("✅ Aucune démo expirée à supprimer")
            return

        print(f"🔍 {len(expired_demos)} démo(s) expirée(s) trouvée(s)\n")

        for db_name, user_email, expires_at in expired_demos:
            expires_date = datetime.fromisoformat(expires_at)
            print(f"📋 Base: {db_name}")
            print(f"   Email: {user_email}")
            print(f"   Expirée depuis: {expires_date.strftime('%d/%m/%Y %H:%M')}")

            if dry_run:
                print("   ⏸️  Mode DRY RUN - Non supprimée\n")
            else:
                try:
                    # Supprimer via l'API Odoo
                    self.db_manager.drop(self.master_password, db_name)
                    self.mark_as_deleted(db_name)
                    print("   ✅ Supprimée avec succès\n")
                except Exception as e:
                    print(f"   ❌ Erreur: {str(e)}\n")

    def get_active_demos_count(self):
        """Retourne le nombre de démos actives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM demos WHERE status = "active"')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_stats(self):
        """Retourne des statistiques sur les démos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Démos actives
        cursor.execute('SELECT COUNT(*) FROM demos WHERE status = "active"')
        active = cursor.fetchone()[0]

        # Démos expirées
        now = datetime.now().isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM demos
            WHERE expires_at < ? AND status = "active"
        ''', (now,))
        expired = cursor.fetchone()[0]

        # Total créé
        cursor.execute('SELECT COUNT(*) FROM demos')
        total = cursor.fetchone()[0]

        conn.close()

        return {
            'active': active,
            'expired': expired,
            'total_created': total,
            'deleted': total - active
        }


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    # Configuration
    ODOO_URL = "https://ezaynova2-production.up.railway.app"
    MASTER_PASSWORD = "VotreMotDePasseSecurise123!"  # À remplacer

    cleanup = DemoCleanup(ODOO_URL, MASTER_PASSWORD)

    print("="*60)
    print("NETTOYAGE DES DÉMOS EXPIRÉES")
    print("="*60 + "\n")

    # Afficher les statistiques
    stats = cleanup.get_stats()
    print("📊 STATISTIQUES")
    print(f"   Démos actives: {stats['active']}")
    print(f"   Démos expirées: {stats['expired']}")
    print(f"   Total créées: {stats['total_created']}")
    print(f"   Total supprimées: {stats['deleted']}\n")

    # Mode DRY RUN (liste sans supprimer)
    print("🔍 MODE DRY RUN - Vérification des démos à supprimer")
    print("-" * 60 + "\n")
    cleanup.cleanup_expired_demos(dry_run=True)

    # Décommentez pour vraiment supprimer les démos expirées
    # cleanup.cleanup_expired_demos(dry_run=False)
