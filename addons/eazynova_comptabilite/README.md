# Module Eazynova Comptabilité

## Description

Module de comptabilité complet pour Odoo 19, inspiré de Pennylane, avec des fonctionnalités avancées d'IA, OCR, et connecteurs vers les principaux logiciels comptables.

## Fonctionnalités principales

### 📊 Comptabilité complète
- Plan comptable général français (PCG) modifiable
- Comptabilité analytique optionnelle
- Gestion multi-sociétés et multi-devises
- Gestion de la TVA (taux multiples, déclarations)

### 💰 Gestion bancaire
- Multi-comptes bancaires (France et international)
- Import automatisé de relevés bancaires (CSV, OFX, QIF)
- Rapprochement bancaire intelligent avec suggestions IA
- Connexion API aux banques

### 📄 Facturation
- **Factures clients** avec relances automatiques
- **Factures fournisseurs** avec OCR/IA automatique
  - Extraction automatique des données (PDF et photos)
  - Reconnaissance du fournisseur, montants, dates
  - Workflow d'approbation
- Notes de frais avec catégorisation automatique
- Conditions de paiement personnalisables

### 🤖 Intelligence Artificielle
- **OCR intelligent** pour factures PDF et photos
  - Support Tesseract OCR
  - Analyse IA pour extraction de données structurées
- **Assistant de codification**
  - Suggestion automatique des codes comptables
  - Apprentissage basé sur l'historique
  - Suggestions de partenaires et comptes

### 🔗 Passerelles logiciels comptables
Synchronisation bidirectionnelle avec :
- **Pennylane**
- **Sage**
- **Axonaut**
- **EBP Compta**
- **Ciel Compta**
- **Quadratus**
- **ACD**

### 📈 Rapports et analyses
- Balance comptable
- Grand livre
- Balance de vérification
- Bilan intermédiaire (conforme réglementation française)
- Bilan annuel
- Compte de résultat
- Indicateurs de trésorerie
- Export FEC (Fichier des Écritures Comptables)

### 💼 Gestion des tiers
- Comptes clients et fournisseurs
- Suivi des impayés
- Relances automatiques configurables
- Grand livre par partenaire

### 📤 Exports
- PDF (rapports)
- Excel (données détaillées)
- CSV
- Format FEC pour administration fiscale

## Installation

1. Copier le dossier `eazynova_comptabilite` dans le répertoire `addons` d'Odoo
2. Redémarrer le serveur Odoo
3. Activer le mode développeur
4. Mettre à jour la liste des applications
5. Rechercher "Eazynova Comptabilité" et installer

## Dépendances

### Modules Odoo
- `base`
- `mail`
- `portal`
- `web`
- `base_setup`
- `eazynova` (module core pour services IA)

### Bibliothèques Python
- `numpy`
- `pandas`
- `openpyxl`
- `xlsxwriter`
- `pdf2image`
- `pytesseract`
- `Pillow`
- `PyPDF2`
- `requests`

## Configuration

### 1. Plan comptable
Lors de la première installation, le plan comptable général français de base est créé automatiquement.
Vous pouvez le personnaliser dans : **Comptabilité > Configuration > Plan comptable**

### 2. Taxes
Les taux de TVA français standards sont pré-configurés (20%, 10%, 5.5%, 2.1%).
Personnalisation : **Comptabilité > Configuration > Taxes**

### 3. Comptes bancaires
Créer vos comptes bancaires : **Comptabilité > Banque > Comptes bancaires**
- Configurer l'import automatique (fichier ou API)
- Lier aux journaux comptables

### 4. Connecteurs externes
Configurer les passerelles : **Comptabilité > Configuration > Connecteurs**
- Saisir les clés API
- Tester la connexion
- Activer la synchronisation automatique

### 5. OCR et IA
S'assurer que le module `eazynova` est installé et configuré avec :
- Clé API Anthropic Claude ou OpenAI GPT-4
- Tesseract OCR installé sur le serveur

## Utilisation

### Créer une facture client
1. **Comptabilité > Facturation > Factures clients**
2. Cliquer sur "Créer"
3. Sélectionner le client
4. Ajouter les lignes de facture
5. Comptabiliser

### Traiter une facture fournisseur avec OCR
1. **Comptabilité > Facturation > Factures fournisseurs**
2. Créer une nouvelle facture
3. Glisser-déposer le PDF ou la photo
4. Cliquer sur "Extraire avec OCR"
5. Vérifier et valider les données extraites
6. Comptabiliser

### Importer un relevé bancaire
1. **Comptabilité > Banque > Relevés bancaires**
2. Sélectionner le compte bancaire
3. Cliquer sur "Importer un relevé"
4. Charger le fichier (CSV, OFX, QIF)
5. Rapprocher les lignes

### Générer un export comptable
1. **Comptabilité > Rapports > Balance** (ou autre rapport)
2. Sélectionner la période
3. Choisir le format (PDF, Excel, CSV)
4. Télécharger

## Sécurité et permissions

Trois niveaux d'accès :

### Utilisateur Comptabilité
- Consultation des données comptables
- Saisie de pièces (factures, paiements)
- Gestion de ses notes de frais

### Gestionnaire Comptabilité
- Toutes les permissions utilisateur
- Validation des pièces
- Gestion des tiers
- Paramétrage basique

### Comptable
- Toutes les permissions gestionnaire
- Configuration complète du plan comptable
- Gestion des taxes et positions fiscales
- Clôture d'exercice
- Accès aux connecteurs externes

## Traduction

Le module est entièrement traduisible. Fichiers de traduction :
- Français : `i18n/fr.po` (par défaut)
- Anglais : `i18n/en.po` (à compléter)

## Support et contributions

- **Documentation** : https://www.eazynova.com/docs
- **Issues** : Rapporter les bugs sur le dépôt GitHub
- **Contributions** : Les pull requests sont bienvenues

## Licence

LGPL-3

## Auteur

**Eazynova**
- Website: https://www.eazynova.com
- Email: contact@eazynova.com

## Changelog

### Version 1.0.0 (2025-12-05)
- Version initiale
- Plan comptable français
- Gestion factures clients/fournisseurs
- OCR et IA pour factures
- Import bancaire
- Notes de frais
- Comptabilité analytique
- Connecteurs Pennylane, Sage, Axonaut, EBP
- Rapports et exports
- Traduction FR/EN
