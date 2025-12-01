# Guide : Gestion des Disponibilités et Conflits de Planning

## 📋 Vue d'ensemble

Le module intervention intègre maintenant une **gestion intelligente des disponibilités** qui détecte automatiquement les conflits de planning et propose des créneaux libres optimisés pour vos techniciens.

## 🎯 Fonctionnalités

### ✅ **Détection automatique des conflits**

-   Vérification en temps réel lors de la planification
-   Analyse des événements calendrier existants
-   Contrôle des chevauchements avec d'autres interventions

### 💡 **Suggestions intelligentes**

-   Proposition de créneaux libres alternatifs
-   Calcul automatique des disponibilités sur 7 jours
-   Respect des horaires de travail (8h-18h, lun-ven)

### ⚠️ **Alertes visuelles**

-   Notifications claires en cas de conflit
-   Affichage des détails des conflits
-   Interface intuitive avec codes couleur

## 🚀 Utilisation

### 1. Création d'intervention avec vérification

Lors de la création ou modification d'une intervention :

1. **Sélectionnez le technicien principal**
2. **Définissez la date et heure prévue**
3. **Indiquez la durée prévue**
4. **Consultez automatiquement** :
    - ✅ **Zone verte** : Aucun conflit détecté
    - ⚠️ **Zone orange** : Conflit détecté avec détails

### 2. Gestion des conflits détectés

Quand un conflit apparaît :

#### **Informations affichées :**

-   📅 **Date/heure** du conflit
-   ⏱️ **Durée** du chevauchement
-   📝 **Description** de l'événement en conflit
-   🔍 **Type** : Événement calendrier ou autre intervention

#### **Actions possibles :**

1. **Modifier la date/heure** de l'intervention
2. **Utiliser un créneau suggéré** (voir suggestions)
3. **Valider malgré le conflit** (bouton d'override)
4. **Assigner un autre technicien**

### 3. Utilisation des suggestions

La section **"Créneaux libres suggérés"** propose :

```
💡 CRÉNEAUX LIBRES SUGGÉRÉS :
• 08/07/2025 08:00 - 08/07/2025 11:00 (3.0h)
• 08/07/2025 14:00 - 08/07/2025 18:00 (4.0h)
• 09/07/2025 08:00 - 09/07/2025 18:00 (10.0h)
```

**Comment utiliser :**

-   Choisissez un créneau avec une durée suffisante
-   Modifiez la date/heure de votre intervention
-   La vérification se met à jour automatiquement

## 📊 Exemples pratiques

### **Scénario 1 : Intervention sans conflit**

```
✅ Aucun conflit détecté
Planning libre pour cette intervention
```

→ **Action** : Procédez normalement

### **Scénario 2 : Conflit avec événement calendrier**

```
⚠️ CONFLITS DÉTECTÉS :
• 08/07/2025 14:00 - 08/07/2025 16:00 : Réunion équipe

💡 CRÉNEAUX LIBRES SUGGÉRÉS :
• 08/07/2025 08:00 - 08/07/2025 14:00 (6.0h)
• 08/07/2025 16:00 - 08/07/2025 18:00 (2.0h)
```

→ **Action** : Décaler avant 14h ou après 16h

### **Scénario 3 : Conflit avec autre intervention**

```
⚠️ CONFLITS DÉTECTÉS :
• 08/07/2025 09:00 - 08/07/2025 11:00 : Intervention INT-0012
```

→ **Action** : Réorganiser le planning ou assigner un autre technicien

## ⚙️ Configuration et paramétrage

### **Horaires de travail par défaut**

-   **Début** : 08h00
-   **Fin** : 18h00
-   **Jours** : Lundi à Vendredi
-   **Weekends** : Exclus des suggestions

### **Période de suggestions**

-   **Horizon** : 7 jours à partir d'aujourd'hui
-   **Limite** : 5 suggestions maximum
-   **Tri** : Chronologique (plus proches en premier)

## 🔧 Cas d'usage avancés

### **Planning d'équipe**

1. **Situation** : Intervention nécessitant plusieurs techniciens
2. **Solution** : Vérifier les disponibilités de chaque membre
3. **Optimisation** : Utiliser les créneaux communs suggérés

### **Interventions urgentes**

1. **Situation** : Intervention à programmer immédiatement
2. **Option 1** : Utiliser "Valider malgré le conflit"
3. **Option 2** : Décaler une intervention moins prioritaire
4. **Option 3** : Assigner un technicien disponible

### **Planification optimisée**

1. **Étape 1** : Créer toutes les interventions
2. **Étape 2** : Identifier tous les conflits
3. **Étape 3** : Utiliser les suggestions pour optimiser
4. **Étape 4** : Valider le planning final

## 💡 Bonnes pratiques

### **Planification préventive**

-   ✅ Planifiez en début de semaine
-   ✅ Laissez des marges entre interventions
-   ✅ Vérifiez les calendriers personnels des techniciens

### **Gestion des conflits**

-   ✅ Priorisez selon l'urgence client
-   ✅ Communiquez les changements rapidement
-   ✅ Tenez compte des déplacements (temps de trajet)

### **Optimisation continue**

-   ✅ Analysez les patterns de conflit
-   ✅ Ajustez les durées prévisionnelles
-   ✅ Formez l'équipe aux nouveaux outils

## 🚨 Limitations et points d'attention

### **Ce qui EST détecté :**

-   ✅ Événements calendrier Odoo
-   ✅ Autres interventions planifiées
-   ✅ Chevauchements de créneaux

### **Ce qui N'EST PAS détecté :**

-   ❌ Congés non saisis dans Odoo
-   ❌ Événements calendriers externes
-   ❌ Temps de trajet entre interventions
-   ❌ Pauses personnelles non planifiées

### **Recommandations :**

-   Maintenez les calendriers Odoo à jour
-   Saisissez tous les événements importants
-   Prévoyez des marges pour les imprévus

## ❓ Questions fréquentes

### **Q: Que faire si toutes les suggestions sont inadéquates ?**

**R:** Vous pouvez :

-   Étendre la recherche manuellement à plus de 7 jours
-   Assigner un autre technicien disponible
-   Reporter l'intervention à la semaine suivante
-   Diviser l'intervention en plusieurs créneaux

### **Q: Le système bloque-t-il la création en cas de conflit ?**

**R:** Non, le système **avertit mais ne bloque pas**. Vous pouvez valider malgré le conflit avec le bouton "Valider malgré le conflit".

### **Q: Comment gérer les interventions multi-techniciens ?**

**R:** Créez une intervention par technicien ou vérifiez manuellement les disponibilités de chaque membre de l'équipe.

### **Q: Les suggestions prennent-elles en compte les temps de trajet ?**

**R:** Actuellement non. Il faut manuellement prévoir du temps pour les déplacements entre interventions.

## 🔄 Mises à jour futures

### **Améliorations prévues :**

-   🚀 Intégration du temps de trajet dans les suggestions
-   🚀 Synchronisation avec calendriers externes (Google, Outlook)
-   🚀 Suggestions multi-techniciens intelligentes
-   🚀 Notifications automatiques en cas de conflit

---

📞 **Support** : En cas de question sur cette fonctionnalité, consultez ce guide ou contactez votre administrateur système.

🎯 **Objectif** : Optimiser votre planning, réduire les conflits et améliorer l'efficacité de vos équipes techniques.
