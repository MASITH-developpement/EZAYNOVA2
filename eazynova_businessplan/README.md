# EAZYNOVA - Business Plan

## Description

Module de gestion de business plans pour Odoo 19 CE permettant de créer, valider et suivre des business plans avec génération automatique d'indicateurs de performance.

## Fonctionnalités

### Gestion des Business Plans

- **Création de business plans structurés** avec :
  - Informations de base (nom, dates, responsable)
  - Résumé exécutif
  - Description détaillée
  - Objectifs stratégiques
  - Données financières (budget, CA cible, bénéfice cible, investissement)
  - Analyse de marché
  - Stratégie marketing
  - Structure organisationnelle

### Workflow de validation

- États du business plan :
  - **Brouillon** : Création et modification
  - **Soumis** : En attente de validation
  - **Validé** : Approuvé par un manager
  - **En cours** : Exécution active
  - **Terminé** : Objectifs atteints
  - **Annulé** : Abandonné

### Génération automatique d'indicateurs

Lors de la validation d'un business plan, le système génère automatiquement des indicateurs de suivi :

#### Indicateurs financiers
- Chiffre d'affaires réalisé vs objectif
- Bénéfice net vs objectif
- Consommation du budget

#### Indicateurs commerciaux
- Nombre de nouveaux clients
- Taux de conversion prospects → clients

#### Indicateurs de performance
- Taux de satisfaction client
- Effectif réalisé vs prévu

### Suivi des indicateurs

Chaque indicateur comprend :
- **Type** : Financier, Commercial, Performance, Qualité, RH, Opérationnel, Stratégique
- **Unité de mesure** : Monétaire, Pourcentage, Nombre, Ratio, Jours, Heures
- **Valeur cible** et **valeur actuelle**
- **Calculs automatiques** :
  - Progression (%)
  - Taux de réalisation (%)
  - Écart et écart en pourcentage
- **Alertes automatiques** :
  - OK (vert) : ≥ 80% de réalisation
  - Attention (jaune) : 50-80% de réalisation
  - Critique (rouge) : < 50% de réalisation
- **Fréquence de suivi** : Quotidien, Hebdomadaire, Mensuel, Trimestriel, Annuel
- **Historique des valeurs**

### Tableaux de bord et reporting

- Vue Kanban avec progression visuelle
- Graphiques d'analyse des indicateurs
- Tableaux croisés dynamiques (Pivot)
- Filtres et regroupements avancés

### Sécurité et droits d'accès

Deux niveaux de permissions :

1. **Utilisateur Business Plan** :
   - Création et gestion de ses propres business plans
   - Mise à jour de ses indicateurs
   - Lecture seule sur les autres BP

2. **Manager Business Plan** :
   - Validation des business plans
   - Gestion de tous les business plans
   - Accès complet aux indicateurs
   - Suppression de business plans

## Installation

1. Copier le module dans le répertoire `addons/addons-perso/`
2. Redémarrer Odoo
3. Activer le mode développeur
4. Aller dans Apps > Mettre à jour la liste des applications
5. Rechercher "EAZYNOVA - Business Plan"
6. Cliquer sur "Installer"

## Configuration

1. Aller dans **Paramètres > Utilisateurs et Sociétés > Utilisateurs**
2. Assigner les groupes appropriés aux utilisateurs :
   - `Utilisateur Business Plan` pour les créateurs de BP
   - `Manager Business Plan` pour les validateurs

## Utilisation

### Créer un business plan

1. Aller dans **Business Plans > Business Plans > Créer**
2. Remplir les informations de base
3. Compléter les onglets :
   - Résumé exécutif
   - Description
   - Objectifs
   - Finances
   - Marché et Stratégie
   - Organisation
4. Sauvegarder

### Soumettre et valider

1. Cliquer sur **Soumettre** (passe à l'état "Soumis")
2. Un manager clique sur **Valider**
3. Le système génère automatiquement les indicateurs
4. Le BP passe automatiquement à l'état "En cours"

### Suivre les indicateurs

1. Depuis le business plan, cliquer sur le bouton **Indicateurs**
2. Ou aller dans **Business Plans > Indicateurs**
3. Mettre à jour les valeurs actuelles régulièrement
4. Le système calcule automatiquement :
   - La progression
   - Le taux de réalisation
   - Les écarts
   - Le statut d'alerte

### Analyser les performances

1. Aller dans **Business Plans > Reporting > Analyse des indicateurs**
2. Utiliser les vues :
   - **Graphique** : Visualisation des performances
   - **Pivot** : Analyse croisée
3. Grouper par type, business plan, statut, etc.

## Structure technique

```
eazynova_businessplan/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── business_plan.py
│   └── business_plan_indicator.py
├── views/
│   ├── business_plan_views.xml
│   ├── business_plan_indicator_views.xml
│   └── businessplan_menu.xml
├── security/
│   ├── businessplan_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── sequence_data.xml
│   └── indicator_templates.xml
└── static/
    └── description/
        └── icon.png
```

## Modèles de données

### business.plan
Modèle principal pour les business plans avec workflow de validation et génération d'indicateurs.

### business.plan.indicator
Indicateurs de suivi avec calculs automatiques et système d'alertes.

### business.plan.indicator.history
Historique des valeurs des indicateurs pour analyse de tendances.

## Dépendances

- `base`
- `web`
- `mail`
- `portal`

## Auteur

**EAZYNOVA**

## Licence

LGPL-3

## Version

19.0.1.0.0

## Support

Pour toute question ou problème, veuillez contacter l'équipe EAZYNOVA.
