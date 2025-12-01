# 🗺️ GUIDE DE CONFIGURATION - CALCUL DISTANCE ET TEMPS DE TRAJET

## 🎯 Objectif

Calculer automatiquement la distance en kilomètres et le temps de trajet estimé entre votre entreprise et l'adresse d'intervention.

## 📊 Fonctionnement

### ✅ Calcul automatique

-   **Déclenchement** : Dès que l'adresse d'intervention est remplie (automatiquement via client ou manuellement)
-   **Affichage** : Distance en km et temps en minutes directement dans la fiche intervention
-   **API** : Utilise OpenRouteService (gratuite) ou calcul approximatif si pas d'API

### 🔄 Méthodes de calcul

#### 1. **API OpenRouteService (Recommandée)**

-   ✅ **Gratuit** : 2000 requêtes/jour
-   ✅ **Précis** : Distance routière réelle + temps réel
-   ✅ **Facile** : Inscription gratuite en 2 minutes

#### 2. **Calcul approximatif (Secours)**

-   📏 Distance à vol d'oiseau × 1.3
-   ⏱️ 1 km = 1.5 minutes en moyenne
-   🔄 Utilisé automatiquement si pas d'API

## ⚙️ Configuration

### Étape 1 : Obtenir une clé API gratuite

1. Aller sur [openrouteservice.org/dev/#/signup](https://openrouteservice.org/dev/#/signup)
2. S'inscrire gratuitement (email + mot de passe)
3. Confirmer l'email
4. Récupérer votre clé API

### Étape 2 : Configurer dans Odoo

1. Aller dans **Paramètres > Paramètres généraux**
2. Chercher la section **"Interventions"**
3. Renseigner :
    - **Clé API OpenRouteService** : Votre clé obtenue
    - **Latitude entreprise** : Ex: 48.8566 (Paris)
    - **Longitude entreprise** : Ex: 2.3522 (Paris)
4. Sauvegarder

### Étape 3 : Obtenir les coordonnées de votre entreprise

-   **Google Maps** : Clic droit sur votre adresse → coordonnées
-   **GPS** : Latitude/Longitude de votre siège
-   **Exemple Paris** : 48.8566, 2.3522

## 📱 Utilisation

### Calcul automatique

1. Créer une intervention
2. Sélectionner le client final (MOREAU Stéphane)
3. ✨ **L'adresse se remplit automatiquement**
4. ✨ **Distance et temps se calculent automatiquement**

### Recalcul manuel

-   Bouton **🔄 Recalculer** dans la fiche intervention
-   Utile si l'adresse est modifiée manuellement

### Affichage

```
📍 Adresse d'intervention: 3972 route de manosque 04210 valensole
🗺️ Distance: 45.2 km - ⏱️ Temps trajet: 38 min  🔄 Recalculer
```

## 🔧 Champs ajoutés

### Dans le modèle intervention

-   `distance_km` : Distance en kilomètres (décimal, 2 décimales)
-   `duree_trajet_min` : Temps de trajet en minutes (entier)
-   `lien_waze` : Lien direct pour navigation Waze

### Dans l'interface

-   Affichage en ligne après l'adresse d'intervention
-   Champs en lecture seule (calculés automatiquement)
-   Bouton de recalcul manuel

## 📈 Avantages métier

### ⏰ Planification

-   **Estimation précise** du temps de déplacement
-   **Optimisation** des tournées de techniciens
-   **Calcul automatique** des frais de déplacement

### 💰 Facturation

-   Base pour facturer les frais kilométriques
-   Estimation du temps de trajet pour devis
-   Justification des coûts de déplacement

### 📊 Reporting

-   Analyse des distances par technicien
-   Optimisation géographique des interventions
-   Suivi des coûts de transport

## 🚨 Limites et bonnes pratiques

### Limites API gratuite

-   **2000 requêtes/jour** avec OpenRouteService
-   Calcul approximatif en cas de dépassement
-   Pas de calcul en temps réel du trafic

### Bonnes pratiques

-   Configurer les coordonnées exactes de l'entreprise
-   Tester avec quelques adresses connues
-   Vérifier les résultats lors des premières utilisations

## 🛠️ Dépannage

### Pas de calcul de distance

1. Vérifier la clé API dans les paramètres
2. Vérifier les coordonnées de l'entreprise
3. S'assurer que l'adresse est géocodée (latitude/longitude)

### Distance incorrecte

1. Vérifier l'adresse d'intervention
2. Utiliser le bouton "Recalculer"
3. Contrôler les coordonnées GPS dans la fiche

### Erreurs API

-   Vérification automatique du quota
-   Basculement sur calcul approximatif
-   Messages d'erreur dans les logs Odoo

---

_Configuration recommandée pour une utilisation optimale du calcul de distance et temps de trajet_ 🚀
