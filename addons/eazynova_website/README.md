# EAZYNOVA - Site Web SaaS

Module de site web commercial pour la vente d'EAZYNOVA en mode SaaS.

## Description

Ce module fournit une solution complète pour vendre EAZYNOVA en mode SaaS avec :

### Fonctionnalités principales

- **Site web marketing** avec pages :
  - Page d'accueil présentant EAZYNOVA
  - Page de tarification détaillée
  - Page de fonctionnalités
  - Formulaire d'inscription en ligne

- **Gestion des abonnements SaaS** :
  - Plans d'abonnement configurables
  - Essai gratuit de 30 jours
  - Facturation automatique mensuelle
  - Gestion des utilisateurs et tarification par paliers

- **Provisioning automatique** :
  - Création automatique d'instances Odoo
  - Intégration avec Railway pour le déploiement
  - Gestion du cycle de vie des instances

- **Portail client** :
  - Tableau de bord pour gérer son abonnement
  - Mise à niveau du nombre d'utilisateurs
  - Accès aux factures
  - Gestion de l'instance

- **Automatisations** :
  - Suppression automatique des bases inactives après 30 jours
  - Génération automatique des factures mensuelles
  - Notifications par email à chaque étape
  - Vérification quotidienne des périodes d'essai

## Tarification par défaut

- **Prix de base** : 250 € HT/mois
- **Utilisateurs inclus** : 5
- **Utilisateurs supplémentaires** : 20 € HT/mois/utilisateur
- **Configuration complète** : 1 800 € HT (une fois)
- **Essai gratuit** : 30 jours

## Installation

1. Copier le module dans `addons/addons-perso/`
2. Mettre à jour la liste des modules
3. Installer le module `eazynova_website`

## Configuration

### Prérequis

Le module nécessite :
- Module `website`
- Module `portal`
- Module `payment`
- Module `account`
- Module `sale_management`

### Configuration initiale

1. **Configurer le plan SaaS** :
   - Aller dans SaaS EAZYNOVA > Configuration > Plans
   - Le plan par défaut "EAZYNOVA Standard" est créé automatiquement
   - Modifier selon vos besoins

2. **Configurer l'API Railway** (optionnel) :
   - Définir la variable d'environnement `RAILWAY_API_TOKEN`
   - Nécessaire pour le provisioning automatique

3. **Personnaliser les emails** :
   - Aller dans Paramètres > Technique > Emails > Templates
   - Modifier les templates email selon vos besoins

4. **Configurer les tâches planifiées** :
   - Les crons sont activés par défaut
   - Vérifier dans Paramètres > Technique > Automation > Actions planifiées

## Utilisation

### Pour les administrateurs

1. **Gérer les abonnements** :
   - SaaS EAZYNOVA > Abonnements
   - Voir tous les abonnements clients
   - Actions : Démarrer essai, Activer, Suspendre, Annuler

2. **Gérer les instances** :
   - SaaS EAZYNOVA > Instances
   - Voir toutes les instances provisionnées
   - Actions : Provisionner, Suspendre, Réactiver, Supprimer

3. **Gérer les plans** :
   - SaaS EAZYNOVA > Configuration > Plans
   - Créer/modifier les plans d'abonnement
   - Configurer les fonctionnalités et tarifs

### Pour les clients

1. **S'inscrire** :
   - Visiter /saas/signup
   - Remplir le formulaire
   - Recevoir les credentials par email

2. **Gérer son abonnement** :
   - Se connecter au portail
   - Aller dans "Mes abonnements"
   - Modifier le nombre d'utilisateurs
   - Activer/annuler l'abonnement

## Architecture technique

### Modèles de données

- `saas.plan` : Plans d'abonnement
- `saas.plan.feature` : Fonctionnalités des plans
- `saas.subscription` : Abonnements clients
- `saas.instance` : Instances Odoo provisionnées

### Contrôleurs

- `main.py` : Routes publiques du site web
- `portal.py` : Routes du portail client

### Tâches planifiées (Crons)

- **Vérifier les périodes d'essai expirées** : Quotidien
- **Générer les factures mensuelles** : Quotidien
- **Supprimer les bases inactives** : Quotidien
- **Mettre à jour les statistiques** : Quotidien

### Templates email

- Bienvenue essai gratuit
- Credentials de l'instance
- Période d'essai expirée
- Abonnement activé
- Instance supprimée

## Sécurité

Le module définit deux groupes de sécurité :
- **Utilisateur SaaS** : Voir ses propres abonnements
- **Manager SaaS** : Gérer tous les abonnements

## Notes importantes

1. **Suppression des données** :
   - Les bases de données sont conservées 30 jours après expiration
   - Après ce délai, suppression définitive
   - Envoyer une notification au client avant suppression

2. **Provisioning** :
   - Le provisioning automatique nécessite une intégration avec Railway
   - Sans cette intégration, le mode "simulation" est activé
   - Adapter le code selon votre plateforme d'hébergement

3. **Facturation** :
   - Les factures sont générées automatiquement chaque mois
   - La facturation de configuration est générée lors de l'activation
   - Intégrer avec un système de paiement pour automatiser complètement

## Personnalisation

### Changer les tarifs

Modifier le plan dans SaaS EAZYNOVA > Configuration > Plans

### Changer la durée d'essai

Modifier le champ `trial_days` dans le plan

### Ajouter des fonctionnalités

1. Créer de nouvelles fonctionnalités dans `saas.plan.feature`
2. Les associer au plan
3. Elles apparaîtront automatiquement sur le site

### Personnaliser le design

Modifier les fichiers CSS dans `static/src/css/`

## Support

Pour toute question ou problème :
- Email : contact@masith.fr
- Documentation : https://github.com/MASITH-developpement/EAZYNOVA

## Licence

LGPL-3

## Auteur

EAZYNOVA / MASITH Développement

## Version

19.0.1.0.0 - Compatible Odoo 19 CE
