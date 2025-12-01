#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de la qualité du code du module intervention
Exécuter : python3 check_quality.py
"""

import os
import re
import sys
from pathlib import Path


class CodeQualityChecker:
    """Vérificateur de qualité du code Python"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.info = []
        
    def check_all(self):
        """Exécute toutes les vérifications"""
        print("🔍 Vérification de la qualité du code...\n")
        
        self.check_imports()
        self.check_duplicate_code()
        self.check_file_headers()
        self.check_docstrings()
        self.check_code_complexity()
        
        self.print_report()
        
    def check_imports(self):
        """Vérifie l'organisation des imports"""
        print("📦 Vérification des imports...")
        
        for py_file in self.module_path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Vérifier l'ordre des imports
            import_lines = [l for l in lines if l.strip().startswith(('import ', 'from '))]
            
            if import_lines:
                # Vérifier présence du header
                if not lines[0].startswith('# -*- coding:'):
                    self.warnings.append(f"{py_file.name}: Header encoding manquant")
                
                # Vérifier imports groupés
                stdlib_imports = []
                external_imports = []
                odoo_imports = []
                
                for imp in import_lines:
                    if 'odoo' in imp:
                        odoo_imports.append(imp)
                    elif any(lib in imp for lib in ['requests', 'lxml', 'werkzeug']):
                        external_imports.append(imp)
                    else:
                        stdlib_imports.append(imp)
                
                # Vérifier l'ordre attendu
                expected_order = stdlib_imports + external_imports + odoo_imports
                if import_lines != expected_order:
                    self.info.append(f"{py_file.name}: Imports non optimalement ordonnés")
        
        print("   ✅ Vérification imports terminée\n")
    
    def check_duplicate_code(self):
        """Détecte le code dupliqué"""
        print("🔄 Détection du code dupliqué...")
        
        python_files = list(self.module_path.rglob("*.py"))
        code_blocks = {}
        
        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Rechercher les méthodes
            methods = re.findall(r'def\s+(\w+)\s*\([^)]*\):[^\n]*\n((?:\s{4,}.*\n)*)', content)
            
            for method_name, method_body in methods:
                # Normaliser le code (supprimer espaces/commentaires)
                normalized = re.sub(r'#.*', '', method_body)
                normalized = re.sub(r'\s+', ' ', normalized).strip()
                
                if len(normalized) > 100:  # Ignorer méthodes trop courtes
                    if normalized in code_blocks:
                        self.warnings.append(
                            f"Code potentiellement dupliqué: {method_name} similaire à {code_blocks[normalized]}"
                        )
                    else:
                        code_blocks[normalized] = f"{py_file.name}::{method_name}"
        
        print("   ✅ Détection doublons terminée\n")
    
    def check_file_headers(self):
        """Vérifie la présence des headers de fichier"""
        print("📄 Vérification des headers de fichiers...")
        
        for py_file in self.module_path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                
            if not first_line.startswith('# -*- coding:'):
                self.warnings.append(f"{py_file.name}: Header encoding manquant")
        
        print("   ✅ Vérification headers terminée\n")
    
    def check_docstrings(self):
        """Vérifie la présence de docstrings"""
        print("📝 Vérification des docstrings...")
        
        missing_docstrings = 0
        
        for py_file in self.module_path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Compter les méthodes sans docstring
            methods = re.findall(r'def\s+\w+\s*\([^)]*\):[^\n]*\n(?!\s*"""|\s*\'\'\')', content)
            missing_docstrings += len(methods)
        
        if missing_docstrings > 0:
            self.info.append(f"{missing_docstrings} méthodes sans docstring détectées")
        
        print("   ✅ Vérification docstrings terminée\n")
    
    def check_code_complexity(self):
        """Analyse la complexité du code"""
        print("📊 Analyse de la complexité...")
        
        for py_file in self.module_path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Vérifier longueur des fichiers
            if len(lines) > 1000:
                self.warnings.append(f"{py_file.name}: Fichier très long ({len(lines)} lignes)")
            
            # Vérifier longueur des lignes
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    self.info.append(f"{py_file.name}:{i}: Ligne trop longue ({len(line)} caractères)")
        
        print("   ✅ Analyse complexité terminée\n")
    
    def print_report(self):
        """Affiche le rapport de vérification"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE QUALITÉ DU CODE")
        print("="*60 + "\n")
        
        if self.errors:
            print("🔴 ERREURS:")
            for error in self.errors:
                print(f"   ❌ {error}")
            print()
        else:
            print("✅ Aucune erreur détectée\n")
        
        if self.warnings:
            print("⚠️  AVERTISSEMENTS:")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")
            print()
        else:
            print("✅ Aucun avertissement\n")
        
        if self.info:
            print("ℹ️  INFORMATIONS:")
            for info in self.info[:10]:  # Limiter à 10
                print(f"   ℹ️  {info}")
            if len(self.info) > 10:
                print(f"   ... et {len(self.info) - 10} autres")
            print()
        
        # Score de qualité
        score = 100
        score -= len(self.errors) * 10
        score -= len(self.warnings) * 5
        score -= len(self.info) * 0.5
        score = max(0, score)
        
        print(f"📈 SCORE DE QUALITÉ: {score:.1f}/100")
        
        if score >= 90:
            print("🌟 Excellente qualité de code!")
        elif score >= 75:
            print("✅ Bonne qualité de code")
        elif score >= 50:
            print("⚠️  Qualité acceptable, améliorations recommandées")
        else:
            print("❌ Qualité insuffisante, refactoring nécessaire")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Chemin du module
    module_path = os.path.dirname(os.path.abspath(__file__))
    
    checker = CodeQualityChecker(module_path)
    checker.check_all()
    
    sys.exit(0)
