#!/usr/bin/env python3
"""
Script de diagnostic pour débloquer Odoo
"""

import psycopg2
import os
import sys

# Configuration - Adapter selon votre environnement
DB_NAME = os.environ.get('PGDATABASE', 'postgres')
DB_USER = os.environ.get('PGUSER', 'postgres')
DB_PASSWORD = os.environ.get('PGPASSWORD', '')
DB_HOST = os.environ.get('PGHOST', 'localhost')
DB_PORT = os.environ.get('PGPORT', '5432')

def check_module_locks():
    """Vérifier les verrous sur les modules"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        print("=" * 60)
        print("DIAGNOSTIC ODOO - Verrous de modules")
        print("=" * 60)

        # Vérifier les modules en cours d'installation
        cur.execute("""
            SELECT name, state, latest_version
            FROM ir_module_module
            WHERE state IN ('to install', 'to upgrade', 'to remove')
            ORDER BY name
        """)

        modules = cur.fetchall()
        if modules:
            print("\n⚠️  Modules en attente d'opération :")
            for name, state, version in modules:
                print(f"   - {name} : {state} (v{version})")
        else:
            print("\n✓ Aucun module en attente")

        # Vérifier les verrous PostgreSQL
        cur.execute("""
            SELECT
                pg_class.relname AS table_name,
                pg_locks.mode,
                pg_locks.granted,
                pg_stat_activity.query,
                pg_stat_activity.state,
                pg_stat_activity.pid
            FROM pg_locks
            JOIN pg_class ON pg_locks.relation = pg_class.oid
            LEFT JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
            WHERE pg_class.relname LIKE 'ir_module%'
            ORDER BY pg_class.relname
        """)

        locks = cur.fetchall()
        if locks:
            print("\n⚠️  Verrous actifs sur les tables de modules :")
            for table, mode, granted, query, state, pid in locks:
                print(f"   - Table: {table}")
                print(f"     Mode: {mode}, Granted: {granted}, State: {state}, PID: {pid}")
                if query:
                    print(f"     Query: {query[:100]}...")
        else:
            print("\n✓ Aucun verrou actif")

        # Vérifier les cron jobs en erreur
        cur.execute("""
            SELECT name, active, nextcall
            FROM ir_cron
            WHERE active = true
            AND nextcall < NOW()
            LIMIT 5
        """)

        crons = cur.fetchall()
        if crons:
            print("\n⚠️  Cron jobs en retard :")
            for name, active, nextcall in crons:
                print(f"   - {name} : nextcall={nextcall}")

        cur.close()
        conn.close()

        print("\n" + "=" * 60)
        print("RECOMMANDATIONS")
        print("=" * 60)

        if modules:
            print("\n1. Réinitialiser les états des modules :")
            print("   UPDATE ir_module_module SET state='uninstalled'")
            print("   WHERE name IN ('website_booking', 'sales_funnel');")

        if locks:
            print("\n2. Tuer les processus bloqués :")
            for _, _, _, _, _, pid in locks:
                print(f"   SELECT pg_terminate_backend({pid});")

        print("\n3. Redémarrer Odoo")
        print("\n4. Vider le cache Odoo")
        print("   rm -rf /var/lib/odoo/.local/share/Odoo/sessions/*")

    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données : {e}")
        print("\nAssurez-vous que les variables d'environnement sont définies :")
        print("  PGDATABASE, PGUSER, PGPASSWORD, PGHOST, PGPORT")
        sys.exit(1)

if __name__ == '__main__':
    check_module_locks()
