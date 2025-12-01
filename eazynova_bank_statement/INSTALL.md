# Guide d'Installation - EAZYNOVA Bank Statement Import

## 🔧 Installation Rapide

### 1. Dépendances Système

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-fra poppler-utils
```

#### macOS
```bash
brew install tesseract tesseract-lang poppler
```

### 2. Dépendances Python

```bash
pip install ofxparse pandas PyPDF2 pytesseract Pillow pdf2image
```

### 3. Installation du Module

1. Le module est déjà dans : `addons/addons-perso/eazynova/eazynova_bank_statement/`

2. Redémarrer Odoo :
```bash
./odoo-bin -c odoo.conf --stop-after-init
./odoo-bin -c odoo.conf
```

3. Dans Odoo :
   - Activer le mode développeur
   - Applications → Mettre à jour la liste des applications
   - Chercher "EAZYNOVA - Import Relevés Bancaires"
   - Installer

## ✅ Vérification

### Test des dépendances

```python
# Dans un terminal Python
import ofxparse
import pandas
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

print("Toutes les dépendances sont installées ✅")
```

### Test Tesseract

```bash
tesseract --version
# Doit afficher la version de Tesseract
```

### Test Poppler

```bash
pdftoppm -v
# Doit afficher la version de Poppler
```

## 🚀 Premier Import

1. **Menu** : Comptabilité → Imports Bancaires → Nouvel Import

2. **Configuration** :
   - Journal : Sélectionner votre journal bancaire
   - Type de fichier : Auto (détection automatique)
   - Charger votre fichier

3. **Options** :
   - ✅ Rapprochement automatique
   - ✅ Utiliser l'IA
   - Seuil : 80%

4. **Cliquer** sur "Importer"

## ❓ Problèmes Courants

### "Module eazynova not found"

Le module EAZYNOVA Core doit être installé en premier.

### "Permission denied" pour Tesseract

```bash
sudo chmod +x /usr/bin/tesseract
```

### Erreur d'import CSV

Vérifier que le CSV a :
- Un en-tête
- Au moins une colonne Date et une colonne Montant
- Un délimiteur standard (;, ,, ou tab)

## 📚 Documentation Complète

Voir [README.md](README.md) pour la documentation complète.

## 🆘 Support

En cas de problème :
1. Vérifier les logs Odoo
2. Vérifier les dépendances système
3. Contacter le support EAZYNOVA
