#!/usr/bin/env python3
"""
Script pour corriger le problème de redirection du module website
qui empêche l'accès au backend Odoo
"""
import psycopg2
import os
import sys

def fix_website_domain():
    """Réinitialise le domaine du website pour permettre l'accès backend"""

    # Récupérer la connexion DB depuis l'environnement
    db_host = os.getenv('PGHOST', 'localhost')
    db_port = os.getenv('PGPORT', '5432')
    db_name = os.getenv('PGDATABASE', 'railway')
    db_user = os.getenv('PGUSER', 'postgres')
    db_password = os.getenv('PGPASSWORD', '')

    print(f"🔧 Connexion à la base de données...")
    print(f"   Host: {db_host}")
    print(f"   Port: {db_port}")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")

    try:
        # Connexion
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()

        # 1. Vérifier les sites web existants
        print("\n📊 Vérification des sites web...")
        cursor.execute("""
            SELECT id, name, domain, is_default_website
            FROM website
            WHERE active = true
        """)
        websites = cursor.fetchall()

        if not websites:
            print("❌ Aucun site web trouvé")
            return False

        print(f"✅ {len(websites)} site(s) trouvé(s):")
        for ws_id, name, domain, is_default in websites:
            print(f"   - {name} (ID: {ws_id})")
            print(f"     Domain: {domain}")
            print(f"     Default: {is_default}")

        # 2. Réinitialiser le domaine pour tous les sites
        print("\n🔧 Réinitialisation des domaines...")
        cursor.execute("""
            UPDATE website
            SET domain = ''
            WHERE active = true
        """)

        affected = cursor.rowcount
        print(f"✅ {affected} domaine(s) réinitialisé(s)")

        # 3. S'assurer qu'il y a un site par défaut
        print("\n🔧 Configuration du site par défaut...")
        cursor.execute("""
            UPDATE website
            SET is_default_website = false
        """)

        cursor.execute("""
            UPDATE website
            SET is_default_website = true
            WHERE id = (SELECT MIN(id) FROM website WHERE active = true)
        """)

        print("✅ Site par défaut configuré")

        # 4. Commit
        conn.commit()
        print("\n✅ Modifications sauvegardées")

        # 5. Vérification finale
        print("\n📊 Vérification finale...")
        cursor.execute("""
            SELECT id, name, domain, is_default_website
            FROM website
            WHERE active = true
        """)
        websites = cursor.fetchall()

        print(f"Sites web après correction:")
        for ws_id, name, domain, is_default in websites:
            print(f"   - {name} (ID: {ws_id})")
            print(f"     Domain: '{domain}' (vide = accepte tous les domaines)")
            print(f"     Default: {is_default}")

        cursor.close()
        conn.close()

        print("\n✅ Correction terminée avec succès!")
        print("\n🔄 IMPORTANT: Redémarrez le serveur Odoo pour appliquer les changements")
        print("   Sur Railway: Settings > Deploy > Restart")

        return True

    except psycopg2.Error as e:
        print(f"\n❌ Erreur PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🔧 FIX WEBSITE REDIRECT - Correction d'accès backend Odoo")
    print("=" * 70)

    success = fix_website_domain()

    if success:
        print("\n✅ Le backend Odoo devrait maintenant être accessible!")
        print("   1. Redémarrez le serveur Odoo sur Railway")
        print("   2. Attendez 1-2 minutes")
        print("   3. Accédez à /web/login")
        sys.exit(0)
    else:
        print("\n❌ La correction a échoué")
        sys.exit(1)
