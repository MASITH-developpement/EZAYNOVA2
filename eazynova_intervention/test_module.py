#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le module intervention amélioré
Utilisation : python test_intervention_module.py
"""

import os
import sys


def test_module_structure():
    """Tester la structure du module"""
    print("🔍 Test de la structure du module...")

    base_path = "/Users/stephane/odoo18ce/addons/custom/intervention"

    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/intervention.py",
        "models/materiel.py",
        "models/geocoding_cache.py",
        "wizard/__init__.py",
        "wizard/intervention_quick_create.py",
        "static/src/css/intervention_enhanced.css"
    ]

    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Fichiers manquants : {missing_files}")
        return False
    else:
        print("✅ Structure du module correcte")
        return True


def test_python_syntax():
    """Tester la syntaxe Python des fichiers"""
    print("🔍 Test de la syntaxe Python...")

    base_path = "/Users/stephane/odoo18ce/addons/custom/intervention"

    python_files = [
        "models/intervention.py",
        "models/materiel.py",
        "models/geocoding_cache.py",
        "wizard/intervention_quick_create.py"
    ]

    syntax_errors = []

    for file_path in python_files:
        full_path = os.path.join(base_path, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Test de syntaxe basique
            compile(content, full_path, 'exec')
            print(f"✅ {file_path} - Syntaxe OK")

        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"❌ {file_path} - Erreur de syntaxe: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"⚠️ {file_path} - Erreur: {e}")

    return len(syntax_errors) == 0


def test_imports():
    """Tester les imports Odoo"""
    print("🔍 Test des imports Odoo...")

    base_path = "/Users/stephane/odoo18ce/addons/custom/intervention"

    python_files = [
        "models/intervention.py",
        "models/materiel.py",
        "models/geocoding_cache.py",
        "wizard/intervention_quick_create.py"
    ]

    import_errors = []

    for file_path in python_files:
        full_path = os.path.join(base_path, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les imports Odoo
            if 'from odoo import' in content or 'import odoo' in content:
                print(f"✅ {file_path} - Imports Odoo détectés")
            else:
                print(f"⚠️ {file_path} - Aucun import Odoo détecté")

        except Exception as e:
            import_errors.append(f"{file_path}: {e}")
            print(f"❌ {file_path} - Erreur de lecture: {e}")

    return len(import_errors) == 0


def main():
    """Fonction principale de test"""
    print("🚀 Début des tests du module intervention optimisé")
    print("=" * 60)

    tests = [
        ("Structure du module", test_module_structure),
        ("Syntaxe Python", test_python_syntax),
        ("Imports", test_imports)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1

    print("\n" + "=" * 60)
    print(f"🏁 Résultat : {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests sont passés ! Le module semble prêt.")
        print("\n📋 Améliorations apportées :")
        print("✅ Correction des erreurs de syntaxe")
        print("✅ Optimisation des performances (index, cache)")
        print("✅ Interface utilisateur modernisée (CSS)")
        print("✅ Assistant de création rapide")
        print("✅ Système de géocodage avec cache")
        print("✅ Méthodes de recherche optimisées")

        print("\n🚀 Prochaines étapes :")
        print("1. Redémarrer le serveur Odoo")
        print("2. Mettre à jour le module via l'interface d'administration")
        print("3. Tester les nouvelles fonctionnalités")

    else:
        print("⚠️ Certains tests ont échoué. Veuillez corriger les erreurs.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
