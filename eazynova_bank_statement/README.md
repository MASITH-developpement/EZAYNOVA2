# EAZYNOVA - Import Relevés Bancaires Intelligent

## 📋 Description

Module Odoo 19 Community pour l'import automatisé de relevés bancaires avec rapprochement intelligent par IA.

## ✨ Fonctionnalités Principales

### 🔄 Import Multi-Format
- **CSV** : Import avec détection automatique des colonnes
- **OFX** : Support des formats OFX 1.x et 2.x
- **PDF** : Extraction OCR avec analyse par IA

### 🤖 Rapprochement Intelligent
- Correspondance exacte par référence
- Correspondance par montant et date
- Analyse sémantique du libellé par IA
- Règles de rapprochement personnalisables
- Score de confiance pour chaque rapprochement

### 🚨 Système d'Alertes
- Alertes automatiques pour rapprochements incertains
- Alertes pour transactions non rapprochées
- Détection de doublons
- Gestion des priorités et affectation

### 📊 Statistiques et Rapports
- Tableaux de bord de rapprochement
- Statistiques par journal
- Historique des imports
- Taux de rapprochement automatique

## 🔧 Installation

### Prérequis

```bash
pip install ofxparse pandas PyPDF2 pytesseract Pillow pdf2image
```

**Système** :
- Tesseract OCR : `sudo apt-get install tesseract-ocr tesseract-ocr-fra`
- Poppler (pour pdf2image) : `sudo apt-get install poppler-utils`

### Installation du Module

1. Copier le module dans `addons/`
2. Redémarrer Odoo
3. Activer le mode développeur
4. Aller dans Applications → Mettre à jour la liste des applications
5. Chercher "EAZYNOVA - Import Relevés Bancaires"
6. Cliquer sur Installer

## 🚀 Utilisation

### Import Rapide

1. **Menu** : Comptabilité → Imports Bancaires → Nouvel Import
2. **Sélectionner** le journal bancaire
3. **Charger** le fichier (CSV, OFX ou PDF)
4. **Configurer** les options :
   - Rapprochement automatique
   - Utiliser l'IA
   - Seuil de confiance
5. **Cliquer** sur Importer

### Format CSV

Le module détecte automatiquement les colonnes. Colonnes supportées :
- Date (obligatoire)
- Libellé/Description
- Montant (ou Débit/Crédit séparés)
- Référence
- Numéro de compte

**Exemple CSV** :
```csv
Date;Libellé;Débit;Crédit;Référence
01/12/2024;Virement CLIENT ABC;;1500.00;VIR123456
02/12/2024;Prélèvement EDF;150.00;;PRLV987654
```

### Format OFX

Format standard supporté automatiquement. Pas de configuration nécessaire.

### Format PDF

Le module utilise l'OCR pour extraire les transactions. Pour de meilleurs résultats :
- Utiliser des PDF de bonne qualité
- Activer l'option "Utiliser l'IA"
- Le format du relevé doit être tabulaire

## ⚙️ Configuration

### Règles de Rapprochement

**Menu** : Comptabilité → Imports Bancaires → Configuration → Règles de Rapprochement

Les règles permettent d'améliorer le rapprochement automatique :

#### Types de Règles

1. **Pattern de Référence** : Regex sur la référence
   ```
   Exemple : VIR\d+ pour détecter les virements
   ```

2. **Mot-clé Description** : Mots-clés dans le libellé
   ```
   Exemple : PRELEVEMENT,PRLV,SEPA
   ```

3. **Mot-clé Partenaire** : Mots-clés dans le nom du partenaire
   ```
   Exemple : EDF,ORANGE,SFR
   ```

4. **Plage de Montant** : Filtrage par montant
   ```
   Exemple : 0.01 à 50.00 pour petits montants
   ```

5. **Règle Combinée** : Combinaison de plusieurs critères (ET logique)

#### Boost de Confiance

Chaque règle peut augmenter le score de confiance (0-1).
- 0.1-0.2 : Boost léger
- 0.3-0.5 : Boost moyen
- 0.6-1.0 : Boost fort (utiliser avec précaution)

### Seuil de Confiance

Le seuil de confiance détermine quand valider automatiquement un rapprochement :
- **0.9-1.0** : Très strict (peu de validations auto)
- **0.7-0.8** : Équilibré (recommandé)
- **0.5-0.6** : Permissif (beaucoup de validations auto)

## 🎯 Cas d'Usage

### Import CSV depuis une Banque

```python
# La banque fournit un CSV avec ce format :
# Date;Libellé;Montant;Référence

1. Créer une règle pour détecter le format spécifique de la banque
2. Importer le fichier CSV
3. Le module détecte automatiquement les colonnes
4. Les transactions sont rapprochées automatiquement
5. Les alertes signalent les rapprochements incertains
```

### Import PDF de Relevé

```python
1. Scanner ou récupérer le relevé PDF
2. L'importer avec l'option "Utiliser l'IA" activée
3. L'OCR extrait les transactions
4. L'IA analyse et structure les données
5. Le rapprochement automatique s'exécute
```

### Rapprochement Manuel

Pour les transactions sans correspondance :

1. Ouvrir la ligne bancaire
2. Voir les suggestions de rapprochement
3. Choisir une suggestion ou sélectionner manuellement l'écriture
4. Valider

## 📈 Performances

### Rapprochement par IA

Le module utilise l'IA (Claude/OpenAI) pour :
- Analyse sémantique des libellés
- Extraction intelligente depuis PDF
- Suggestions de rapprochement

**Configuration IA** : Module EAZYNOVA Core

### Optimisation

- Import par lot : Traite jusqu'à 1000 lignes
- Cache des règles de rapprochement
- Indexation des champs de recherche

## 🔒 Sécurité

### Groupes d'Accès

- **Utilisateur Import Bancaire** : Peut créer et utiliser les imports
- **Manager Import Bancaire** : Peut configurer les règles et supprimer

### Multi-Société

Le module respecte les règles multi-sociétés d'Odoo.

## 🐛 Dépannage

### "Bibliothèque manquante"

```bash
pip install <bibliothèque_manquante>
```

### "Impossible d'extraire du texte du PDF"

1. Vérifier que Tesseract est installé : `tesseract --version`
2. Vérifier que poppler est installé : `pdftoppm -v`
3. Essayer avec un PDF de meilleure qualité

### "Aucune correspondance trouvée"

1. Vérifier les règles de rapprochement
2. Réduire le seuil de confiance
3. Utiliser le rapprochement manuel

### "Colonnes CSV non détectées"

1. Vérifier que le CSV a un en-tête
2. Essayer de renommer les colonnes avec des noms standards
3. Vérifier le délimiteur (;, ,, tab)

## 📝 Changelog

### Version 19.0.1.0.0

- Import CSV avec détection automatique des colonnes
- Import OFX (1.x et 2.x)
- Import PDF avec OCR et IA
- Rapprochement automatique intelligent
- Système d'alertes
- Règles de rapprochement personnalisables
- Statistiques et rapports

## 🤝 Support

Pour toute question ou problème :
- GitHub Issues : [lien]
- Documentation : [lien]
- Email : support@eazynova.com

## 📄 Licence

LGPL-3

## 👥 Auteurs

EAZYNOVA - https://eazynova-production.up.railway.app/

---

**Note** : Ce module nécessite le module EAZYNOVA Core pour les fonctionnalités IA.
