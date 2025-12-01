# 🔒 SYSTÈME DE PERMISSIONS GRANULAIRES - MODULE INTERVENTION

## 📋 Vue d'ensemble

Le module intervention utilise un système de permissions granulaires qui permet à l'administrateur d'assigner individuellement chaque droit à chaque utilisateur.

## 👥 Groupes de base

### 🔧 Technicien

-   **Rôle** : Accès de base aux interventions
-   **Droits par défaut** : Consultation uniquement
-   **Droits à assigner manuellement** : Voir section "Droits granulaires"

### 👨‍💼 Gestionnaire

-   **Rôle** : Gestion des interventions
-   **Droits par défaut** : Consultation uniquement
-   **Droits à assigner manuellement** : Voir section "Droits granulaires"

### 📊 Comptable

-   **Rôle** : Consultation financière
-   **Droits par défaut** : Consultation uniquement
-   **Droits à assigner manuellement** : Voir section "Droits granulaires"

### 👑 Administrateur

-   **Rôle** : Accès complet
-   **Droits par défaut** : TOUS les droits automatiquement

## 🎯 Droits granulaires disponibles

### 👥 Gestion des partenaires

-   **Créer donneurs d'ordre** (`group_create_donneur_ordre`)

    -   Permet de créer de nouveaux donneurs d'ordre dans les formulaires
    -   Affiche le bouton "Créer" dans les listes déroulantes

-   **Créer clients finaux** (`group_create_client_final`)
    -   Permet de créer de nouveaux clients finaux
    -   Affiche le bouton "Créer" dans les listes déroulantes

### 🔧 Gestion des interventions

-   **Créer interventions** (`group_create_intervention`)

    -   Permet de créer de nouvelles interventions
    -   Accès au menu "Création rapide"

-   **Modifier toutes interventions** (`group_edit_all_interventions`)
    -   Peut modifier toutes les interventions (pas seulement les siennes)
    -   Sinon : accès en lecture seule aux interventions des autres

### 💰 Gestion commerciale et financière

-   **Créer devis** (`group_create_devis`)

    -   Affiche le bouton "Créer Devis" dans les interventions
    -   Accès aux fonctionnalités de vente

-   **Créer factures** (`group_create_facture`)

    -   Permet de créer et modifier des factures
    -   Accès aux fonctionnalités comptables

-   **Voir rapports financiers** (`group_view_financial_reports`)
    -   Accès aux statistiques et rapports financiers
    -   Tableau de bord avec métriques

### 📅 Gestion du planning

-   **Créer rendez-vous** (`group_create_rdv`)
    -   Affiche le bouton "Créer Événement" dans les interventions
    -   Permet de créer des événements calendrier

## 🛠️ Configuration des utilisateurs

### Pour assigner des droits à un utilisateur :

1. **Aller dans** : Paramètres → Utilisateurs et sociétés → Utilisateurs
2. **Sélectionner** l'utilisateur à configurer
3. **Onglet "Droits d'accès"**
4. **Section "Interventions"** :
    - Sélectionner le groupe de base (Technicien, Gestionnaire, Comptable, Administrateur)
    - Cocher les droits granulaires souhaités

### Exemples de configurations type :

#### 🔧 Technicien terrain

```
Groupe de base : Technicien
Droits granulaires :
☐ Créer donneurs d'ordre
☐ Créer clients finaux
☐ Créer interventions
☐ Modifier toutes interventions
☐ Créer devis
☐ Créer factures
☑ Créer rendez-vous
☐ Voir rapports financiers
```

#### 👨‍💼 Gestionnaire commercial

```
Groupe de base : Gestionnaire
Droits granulaires :
☐ Créer donneurs d'ordre
☑ Créer clients finaux
☑ Créer interventions
☑ Modifier toutes interventions
☑ Créer devis
☐ Créer factures
☑ Créer rendez-vous
☑ Voir rapports financiers
```

#### 📊 Comptable

```
Groupe de base : Comptable
Droits granulaires :
☐ Créer donneurs d'ordre
☐ Créer clients finaux
☐ Créer interventions
☐ Modifier toutes interventions
☐ Créer devis
☑ Créer factures
☐ Créer rendez-vous
☑ Voir rapports financiers
```

#### 👑 Administrateur

```
Groupe de base : Administrateur
Droits granulaires : TOUS automatiquement ✅
```

## 🎯 Avantages de ce système

### ✅ Flexibilité maximale

-   Chaque utilisateur peut avoir une configuration unique
-   Évolution facile des droits selon les besoins

### ✅ Sécurité renforcée

-   Principe du moindre privilège
-   Droits accordés uniquement sur demande

### ✅ Traçabilité

-   Historique des modifications de droits
-   Audit des accès possible

### ✅ Évolutivité

-   Nouveaux droits facilement ajoutables
-   Système modulaire et extensible

## 🔄 Mise à jour du module

Après modification des permissions :

```bash
cd /Users/stephane/odoo18ce
./odoo-bin -d intervention_db -u intervention --stop-after-init
./odoo-bin -d intervention_db --dev=reload
```

## 📞 Support

En cas de problème avec les permissions :

1. Vérifier que l'utilisateur a le groupe de base assigné
2. Vérifier que les droits granulaires sont cochés
3. Se déconnecter/reconnecter pour appliquer les changements
4. Vérifier les logs Odoo en cas d'erreur
