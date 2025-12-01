#!/usr/bin/env python3
"""
Script de test pour créer une démo Odoo
"""

import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(__file__))

from create_demo import OdooDemo

# Configuration
ODOO_URL = "https://ezaynova2-production.up.railway.app"
MASTER_PASSWORD = "admin"  # Master password pour gérer les bases de données

def main():
    print("\n" + "="*70)
    print("🧪 TEST DE CRÉATION DE DÉMO ODOO")
    print("="*70 + "\n")

    # Créer une instance du gestionnaire
    demo_manager = OdooDemo(ODOO_URL, MASTER_PASSWORD)

    # Test 1: Lister les bases de données existantes
    print("📋 BASES DE DONNÉES EXISTANTES")
    print("-" * 70)
    databases = demo_manager.list_databases()
    if databases:
        for db in databases:
            print(f"  ✓ {db}")
    else:
        print("  Aucune base de données")
    print()

    # Test 2: Créer une démo de test
    print("🚀 CRÉATION D'UNE DÉMO DE TEST")
    print("-" * 70)
    demo_info = demo_manager.create_demo_database(
        user_email="test@eazynova.fr",
        demo_duration_hours=24  # 24 heures pour le test
    )

    if demo_info['success']:
        print("\n✅ SUCCÈS ! Démo créée avec succès !\n")
        print("="*70)
        print("📧 INFORMATIONS À ENVOYER À L'UTILISATEUR")
        print("="*70)
        print(f"\n🌐 URL: {demo_info['url']}")
        print(f"👤 Login: {demo_info['login']}")
        print(f"🔑 Password: {demo_info['password']}")
        print(f"📅 Créé le: {demo_info['created_at']}")
        print(f"⏰ Expire le: {demo_info['expires_at']}")
        print(f"⏱️  Durée: {demo_info['duration_hours']} heures")
        print("\n" + "="*70)
        print("\n💡 Conseil: Copiez ces informations avant de fermer cette fenêtre !\n")

        return demo_info
    else:
        print("\n❌ ÉCHEC de la création de la démo")
        print(f"Erreur: {demo_info.get('error', 'Erreur inconnue')}\n")
        return None

if __name__ == "__main__":
    result = main()

    if result:
        print("\n🎯 Test réussi ! La démo est accessible.")
    else:
        print("\n⚠️  Test échoué. Vérifiez la configuration.")
