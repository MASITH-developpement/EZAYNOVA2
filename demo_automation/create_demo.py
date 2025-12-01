#!/usr/bin/env python3
"""
Script pour créer automatiquement des démos Odoo via l'API XML-RPC
Utilisable depuis votre site web pour créer des instances de démo gratuites
"""

import xmlrpc.client
import secrets
import string
from datetime import datetime, timedelta

class OdooDemo:
    def __init__(self, odoo_url, master_password):
        """
        Args:
            odoo_url: URL de votre instance Odoo (ex: https://ezaynova2-production.up.railway.app)
            master_password: Le ADMIN_PASSWORD configuré dans Railway
        """
        self.odoo_url = odoo_url
        self.master_password = master_password
        self.db_manager = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/db')

    def generate_demo_credentials(self):
        """Génère des identifiants aléatoires pour une démo"""
        # Nom de base de données unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(4))
        db_name = f"demo_{timestamp}_{random_suffix}"

        # Mot de passe admin aléatoire
        admin_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

        return db_name, admin_password

    def create_demo_database(self, user_email, demo_duration_hours=72):
        """
        Crée une nouvelle base de données Odoo pour une démo

        Args:
            user_email: Email de l'utilisateur qui demande la démo
            demo_duration_hours: Durée de validité de la démo (défaut: 72h = 3 jours)

        Returns:
            dict: Informations de connexion à la démo
        """
        try:
            # Générer les identifiants
            db_name, admin_password = self.generate_demo_credentials()

            # Créer la base de données via l'API Odoo
            print(f"🔄 Création de la démo: {db_name}")
            print(f"📧 Pour l'utilisateur: {user_email}")

            # Appel à l'API Odoo pour créer la base de données
            self.db_manager.create_database(
                self.master_password,  # Master password
                db_name,               # Nom de la base de données
                True,                  # Charger les données de démo
                'fr_FR',              # Langue (français)
                admin_password        # Mot de passe admin
            )

            # Calculer la date d'expiration
            expiration_date = datetime.now() + timedelta(hours=demo_duration_hours)

            # Informations de connexion
            demo_info = {
                'success': True,
                'db_name': db_name,
                'url': f"{self.odoo_url}/web?db={db_name}",
                'login': 'admin',
                'password': admin_password,
                'email': user_email,
                'created_at': datetime.now().isoformat(),
                'expires_at': expiration_date.isoformat(),
                'duration_hours': demo_duration_hours
            }

            print(f"✅ Démo créée avec succès!")
            print(f"🔗 URL: {demo_info['url']}")
            print(f"👤 Login: admin")
            print(f"🔑 Password: {admin_password}")
            print(f"⏰ Expire le: {expiration_date.strftime('%d/%m/%Y %H:%M')}")

            return demo_info

        except Exception as e:
            print(f"❌ Erreur lors de la création de la démo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_databases(self):
        """Liste toutes les bases de données existantes"""
        try:
            databases = self.db_manager.list()
            return databases
        except Exception as e:
            print(f"❌ Erreur lors de la liste des bases: {str(e)}")
            return []

    def delete_demo_database(self, db_name):
        """
        Supprime une base de données de démo

        Args:
            db_name: Nom de la base de données à supprimer
        """
        try:
            print(f"🗑️  Suppression de la démo: {db_name}")
            self.db_manager.drop(self.master_password, db_name)
            print(f"✅ Démo supprimée avec succès!")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {str(e)}")
            return False


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    # Configuration
    ODOO_URL = "https://ezaynova2-production.up.railway.app"
    MASTER_PASSWORD = "VotreMotDePasseSecurise123!"  # À remplacer par votre ADMIN_PASSWORD

    # Créer une instance du gestionnaire
    demo_manager = OdooDemo(ODOO_URL, MASTER_PASSWORD)

    # Exemple 1: Créer une démo pour un utilisateur
    print("\n" + "="*60)
    print("CRÉATION D'UNE NOUVELLE DÉMO")
    print("="*60 + "\n")

    demo_info = demo_manager.create_demo_database(
        user_email="test@example.com",
        demo_duration_hours=72  # 3 jours
    )

    if demo_info['success']:
        print("\n📋 Informations à envoyer à l'utilisateur:")
        print(f"   URL: {demo_info['url']}")
        print(f"   Login: {demo_info['login']}")
        print(f"   Password: {demo_info['password']}")
        print(f"   Expire le: {demo_info['expires_at']}")

    # Exemple 2: Lister toutes les bases de données
    print("\n" + "="*60)
    print("BASES DE DONNÉES EXISTANTES")
    print("="*60 + "\n")

    databases = demo_manager.list_databases()
    for db in databases:
        print(f"  - {db}")

    # Exemple 3: Supprimer une démo expirée
    # demo_manager.delete_demo_database("demo_20240101_120000_abcd")
