# Guide : Configuration de la Durée par Défaut des Interventions

## 📋 Vue d'ensemble

Le module intervention permet maintenant de configurer la durée par défaut des interventions directement depuis l'interface des paramètres. Cette durée sera automatiquement appliquée à toutes les nouvelles interventions créées.

## ⚙️ Configuration

### Accès aux paramètres

1. **Menu principal** → **Paramètres** → **Paramètres**
2. Recherchez la section **"Interventions"**
3. Trouvez le champ **"Durée intervention par défaut (heures)"**

### Configuration de la durée

-   **Valeur par défaut** : 1.0 heure
-   **Format** : Nombre décimal (ex: 1.5 pour 1h30)
-   **Unité** : Heures

### Exemples de valeurs courantes

| Durée      | Valeur à saisir | Usage typique        |
| ---------- | --------------- | -------------------- |
| 30 minutes | 0.5             | Diagnostic rapide    |
| 1 heure    | 1.0             | Réparation standard  |
| 1h30       | 1.5             | Intervention moyenne |
| 2 heures   | 2.0             | Réparation complexe  |
| 4 heures   | 4.0             | Grosse rénovation    |

## 🛠️ Utilisation

### Nouvelles interventions

Lorsque vous créez une nouvelle intervention :

1. **Durée automatique** : Le champ "Durée prévue (h)" sera automatiquement rempli avec votre valeur configurée
2. **Modification possible** : Vous pouvez toujours modifier cette durée pour chaque intervention individuelle
3. **Sauvegarde** : La valeur configurée reste votre défaut pour les prochaines interventions

### Interventions existantes

⚠️ **Important** : Cette configuration ne modifie **PAS** les interventions déjà créées. Elle s'applique uniquement aux nouvelles interventions.

## 💡 Conseils d'utilisation

### Définir la bonne valeur par défaut

1. **Analysez vos interventions** passées pour identifier la durée la plus fréquente
2. **Commencez conservateur** : mieux vaut sous-estimer et ajuster à la hausse
3. **Adaptez par secteur** :
    - Plomberie courante : 1-2 heures
    - Électricité : 1.5-3 heures
    - Urgences : 0.5-1 heure

### Bonnes pratiques

-   **Révisez régulièrement** votre valeur par défaut selon l'évolution de votre activité
-   **Formez votre équipe** à systématiquement vérifier et ajuster la durée prévue
-   **Utilisez les statistiques** de durée réelle pour affiner vos estimations

## 🔄 Modification en cours d'utilisation

### Changer la valeur par défaut

1. Allez dans **Paramètres** → **Paramètres** → **Interventions**
2. Modifiez la valeur dans **"Durée intervention par défaut"**
3. Cliquez sur **"Enregistrer"**
4. ✅ Les nouvelles interventions utiliseront immédiatement cette nouvelle valeur

### Effet immédiat

-   ✅ **Nouvelles interventions** : utilisent la nouvelle valeur
-   ❌ **Interventions en cours** : conservent leur durée actuelle
-   ❌ **Interventions terminées** : ne sont pas affectées

## 🧪 Test de fonctionnement

Pour vérifier que votre configuration fonctionne :

1. **Configurez** une valeur test (ex: 2.5 heures)
2. **Créez** une nouvelle intervention
3. **Vérifiez** que le champ "Durée prévue" contient bien votre valeur
4. **Sauvegardez** l'intervention
5. **Remettez** votre valeur par défaut habituelle

## 📊 Impact sur la planification

### Calculs automatiques

Cette durée par défaut influence :

-   ✅ **Planning des techniciens** : estimation du temps nécessaire
-   ✅ **Devis automatiques** : base de calcul pour le temps de main d'œuvre
-   ✅ **Rapports d'activité** : prévisionnel vs réel
-   ✅ **Optimisation des tournées** : estimation des créneaux horaires

### Précision importante

🎯 **Plus votre valeur par défaut est précise, meilleure sera votre planification !**

## ❓ Questions fréquentes

### Q: Puis-je avoir des valeurs par défaut différentes selon le type d'intervention ?

**R:** Actuellement, il n'y a qu'une seule valeur par défaut. Vous devez ajuster manuellement selon le type d'intervention.

### Q: Que se passe-t-il si je mets 0 ou une valeur négative ?

**R:** Le système utilisera 1.0 heure par défaut pour éviter les erreurs.

### Q: Les modifications affectent-elles mes collègues ?

**R:** Oui, cette configuration est globale pour toute l'entreprise.

### Q: Puis-je voir un historique des changements ?

**R:** Les modifications sont tracées dans les logs système accessibles aux administrateurs.

## 🚀 Prochaines étapes

Après avoir configuré votre durée par défaut :

1. **Testez** sur quelques interventions
2. **Analysez** l'écart entre prévisionnel et réel
3. **Ajustez** la valeur si nécessaire
4. **Formez** votre équipe aux bonnes pratiques

---

📞 **Support** : En cas de problème, consultez les logs d'erreur ou contactez votre administrateur système.
