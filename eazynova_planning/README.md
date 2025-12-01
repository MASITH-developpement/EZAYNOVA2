# EAZYNOVA Planning

**Version:** 19.0.1.0.0
**Licence:** LGPL-3
**Auteur:** EAZYNOVA

## Description

Module de planification et gestion des ressources pour EAZYNOVA. Permet une gestion complète de la planification des tâches, l'affectation des ressources (humaines et matérielles), la gestion des calendriers et des absences.

## Fonctionnalités principales

### 📋 Tâches de planning
- Création et suivi des tâches planifiées
- Gestion des priorités (basse, normale, haute, urgente)
- Workflow complet: brouillon → planifié → confirmé → en cours → terminé
- Suivi de la progression (%)
- Détection automatique des retards
- Récurrence des tâches
- Géolocalisation des tâches
- Intégration avec les projets Odoo

### 👥 Ressources
- Gestion des ressources humaines, équipements, véhicules et matériels
- Compétences et qualifications
- Calendriers de disponibilité personnalisés
- Coût horaire par ressource
- Suivi de la capacité d'allocation
- Maintenance pour les équipements (dernière/prochaine maintenance)
- Statut de disponibilité en temps réel
- Lien avec les employés Odoo (hr.employee)

### 📅 Calendriers
- Calendriers standards:
  - Standard (5 jours, 40h)
  - Étendu (6 jours, 48h)
  - Continu (7 jours)
  - Postes (3x8)
  - Personnalisé
- Gestion des créneaux horaires
- Jours fériés français pré-configurés
- Horaires flexibles par jour

### 🎯 Assignations de ressources
- Attribution manuelle ou automatique des ressources aux tâches
- Pourcentage d'allocation (0-100%)
- Détection automatique des conflits
- Calcul automatique des coûts
- Suivi des heures planifiées vs réelles
- Workflow: brouillon → confirmé → en cours → terminé

### 🚫 Gestion des absences
- Types d'absence:
  - Congés payés
  - Arrêt maladie
  - Formation
  - Maintenance (pour équipements)
  - Indisponibilité
  - Autre
- Workflow d'approbation: brouillon → soumis → approuvé/refusé
- Détection des conflits avec les assignations
- Gestion des remplacements
- Notifications automatiques

### 🤖 Fonctionnalités intelligentes
- **Assignation automatique**:
  - Recherche de ressources par compétences
  - Vérification automatique de la disponibilité
  - Suggestion de ressources optimales

- **Détection de conflits**:
  - Ressources assignées plusieurs fois
  - Conflits absence/assignation
  - Dépassement de capacité
  - Compétences manquantes

- **Créneaux de planning (slots)**:
  - Gestion fine des disponibilités
  - Allocation par capacité
  - Récurrence possible

### 📊 Rapports et statistiques
- Vue Gantt pour visualisation temporelle
- Vue calendrier pour les assignations et absences
- Statistiques de charge par ressource
- Rapports de disponibilité
- Heures planifiées vs heures réelles
- Coûts par ressource et par tâche

## Installation

### Prérequis
- Odoo 19.0 (Community Edition)
- Module `eazynova` (core) installé
- Module `project` (Odoo standard)
- Module `hr` (Ressources humaines Odoo)
- Module `resource` (Odoo standard)

### Installation du module

1. Placer le module dans le répertoire addons:
```bash
addons/addons-perso/eazynova/eazynova_planning/
```

2. Mettre à jour la liste des modules:
```
Settings → Apps → Update Apps List
```

3. Rechercher "EAZYNOVA Planning" et cliquer sur Install

4. Le module créera automatiquement:
   - Groupes de sécurité (Utilisateur, Gestionnaire, Administrateur)
   - Calendriers standards
   - Compétences de base (BTP)
   - Jours fériés français
   - Séquences pour les références

## Configuration

### 1. Calendriers

Aller dans: **Planning → Configuration → Calendriers**

- Créer ou modifier les calendriers selon vos besoins
- Définir les jours travaillés et les horaires
- Assigner les jours fériés

### 2. Compétences

Aller dans: **Planning → Configuration → Compétences**

- Créer les compétences spécifiques à votre activité
- Définir le niveau requis (basique, intermédiaire, avancé, expert)

Compétences pré-configurées (BTP):
- Électricien
- Plombier
- Charpentier
- Maçon
- Peintre
- Chef de projet
- Conduite d'engins (CACES)

### 3. Ressources

Aller dans: **Planning → Ressources → Ressources**

Pour chaque ressource, configurer:
- Type (humaine, équipement, véhicule, matériel)
- Compétences
- Calendrier
- Capacité (1.0 = temps plein, 0.5 = mi-temps)
- Coût horaire
- Pour les équipements: intervalle de maintenance

### 4. Groupes de sécurité

Assigner les utilisateurs aux groupes:
- **Planning - Utilisateur**: Consultation et gestion de ses propres assignations
- **Planning - Gestionnaire**: Gestion complète du planning
- **Planning - Administrateur**: Tous les droits + configuration

## Utilisation

### Créer une tâche de planning

1. Aller dans: **Planning → Tâches → Tâches de planning**
2. Cliquer sur **Créer**
3. Remplir:
   - Nom de la tâche
   - Dates de début et fin
   - Projet (optionnel)
   - Priorité
   - Compétences requises
   - Nombre de ressources nécessaires
4. Cliquer sur **Assigner automatiquement** ou créer les assignations manuellement

### Assigner des ressources automatiquement

1. Sur une tâche de planning, cliquer sur **Assignation automatique**
2. Définir les critères:
   - Type de ressource
   - Compétences requises
   - Nombre de ressources
3. Cliquer sur **Rechercher**
4. Sélectionner les ressources proposées
5. Confirmer l'assignation

### Gérer les absences

**Demander une absence:**
1. Aller dans: **Planning → Absences → Mes absences**
2. Créer une nouvelle absence
3. Remplir le motif, les dates, le type
4. Soumettre pour approbation

**Approuver une absence:**
1. Aller dans: **Planning → Absences → À approuver**
2. Ouvrir la demande
3. Vérifier les conflits potentiels (bouton "Voir les conflits")
4. Approuver ou refuser avec motif

### Détecter et résoudre les conflits

1. Aller dans: **Planning → Rapports → Conflits**
2. Le système affiche tous les conflits détectés:
   - Ressources assignées plusieurs fois
   - Absences pendant des assignations
   - Dépassement de capacité
3. Choisir une action de résolution:
   - Ignorer (résolution manuelle)
   - Reprogrammer
   - Réassigner
   - Annuler les assignations

### Vues disponibles

**Vue Liste:** Tableau de toutes les tâches/ressources/assignations

**Vue Formulaire:** Détails complets d'un enregistrement

**Vue Calendrier:** Visualisation temporelle
- Code couleur par état/priorité
- Glisser-déposer pour modifier les dates
- Filtrage par ressource, projet, etc.

**Vue Gantt:** Diagramme de Gantt
- Visualisation des tâches sur une timeline
- Dépendances entre tâches
- Identification rapide des chevauchements

**Vue Kanban:** Organisation par étapes (pour les tâches)

## Intégrations

### Avec eazynova_chantier (Module Chantiers)
- Créer automatiquement des tâches de planning pour les chantiers
- Assigner des équipes aux phases de chantier
- Suivre la progression des travaux

### Avec project (Module Projets Odoo)
- Lier les tâches de planning aux tâches de projet
- Bouton "Créer tâche de planning" sur les tâches projet
- Statistiques de planning dans les projets

### Avec hr (Module RH Odoo)
- Lien direct avec les employés
- Synchronisation des absences
- Compétences des employés

## Cas d'usage typiques

### Cas 1: Planifier une équipe pour un chantier

1. Créer une tâche de planning "Installation électrique - Chantier XYZ"
2. Dates: 15-20 mars 2024
3. Compétence requise: Électricien
4. Nombre de ressources: 2
5. Cliquer sur "Assignation automatique"
6. Le système propose 2 électriciens disponibles
7. Confirmer → 2 assignations créées

### Cas 2: Gérer une absence imprévue

1. Un employé tombe malade
2. Créer une absence "Arrêt maladie"
3. Le système détecte les assignations en conflit
4. Ouvrir l'assistant de résolution de conflits
5. Réassigner automatiquement à un autre employé disponible

### Cas 3: Planifier la maintenance d'un équipement

1. Équipement: "Nacelle élévatrice N°5"
2. Dernière maintenance: 01/01/2024
3. Intervalle: 90 jours
4. Prochaine maintenance: 01/04/2024
5. Créer une absence type "Maintenance" du 01-03/04/2024
6. Le système bloque automatiquement l'assignation de cet équipement

## Architecture technique

### Modèles principaux

| Modèle | Description |
|--------|-------------|
| `eazynova.planning.task` | Tâches de planning |
| `eazynova.planning.resource` | Ressources (humaines, matérielles) |
| `eazynova.planning.assignment` | Assignations ressource → tâche |
| `eazynova.planning.absence` | Absences et indisponibilités |
| `eazynova.planning.calendar` | Calendriers de travail |
| `eazynova.planning.slot` | Créneaux de planning |
| `eazynova.planning.resource.skill` | Compétences |

### Wizards

| Wizard | Description |
|--------|-------------|
| `eazynova.planning.auto.assign.wizard` | Assignation automatique de ressources |
| `eazynova.planning.conflict.wizard` | Détection et résolution de conflits |
| `eazynova.planning.absence.refuse.wizard` | Refus d'absence avec motif |

### Séquences

- **PLAN-XXXXX**: Tâches de planning
- **ASS-XXXXX**: Assignations
- **ABS-XXXXX**: Absences

## Sécurité

### Groupes

| Groupe | Droits |
|--------|--------|
| Planning - Utilisateur | Lecture sur tout, écriture sur ses assignations et absences |
| Planning - Gestionnaire | Tous les droits sauf suppression |
| Planning - Administrateur | Tous les droits + configuration |

### Règles d'enregistrement (Record Rules)

- Utilisateurs: voient uniquement leurs tâches et assignations
- Gestionnaires: voient tout
- Multi-sociétés: isolation automatique par société

## Support et contribution

### Problèmes connus
Aucun pour le moment.

### Roadmap
- [ ] Optimisation automatique du planning (IA)
- [ ] Application mobile pour pointage
- [ ] Intégration calendrier Google/Outlook
- [ ] Notifications SMS
- [ ] Dashboard analytique avancé
- [ ] Export iCal/ICS
- [ ] API REST pour intégrations externes

### Contribuer
1. Fork le projet
2. Créer une branche (`feature/ma-fonctionnalite`)
3. Commit vos modifications
4. Push vers la branche
5. Créer une Pull Request

### Support
- Documentation: Ce README
- Issues: GitHub Issues
- Email: support@eazynova.com

## Changelog

### Version 19.0.1.0.0 (2024-11-22)
- Création initiale du module
- Gestion complète des tâches de planning
- Gestion des ressources avec compétences
- Calendriers et absences
- Assignation automatique
- Détection de conflits
- Intégration projets Odoo

## Licence

Ce module est sous licence **LGPL-3**.

Vous êtes libre de:
- Utiliser le module dans un contexte commercial
- Modifier le code source
- Distribuer vos modifications

Sous conditions de:
- Partager les modifications sous la même licence
- Conserver les notices de copyright
- Indiquer les modifications apportées

## Crédits

**Développé par:** Équipe EAZYNOVA
**Sponsor:** MASITH Développement
**Site web:** https://eazynova-production.up.railway.app/

---

Pour toute question ou demande d'assistance, n'hésitez pas à nous contacter.
