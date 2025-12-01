# Guide rapide : Annuler et Replanifier une intervention

## 📋 Vue d'ensemble

Ce guide explique comment gérer les annulations et replanifications d'interventions dans Odoo.

---

## ✖️ Annuler une intervention

### Quand utiliser ?
- Le client annule la commande
- Le donneur d'ordre annule l'intervention
- L'intervention ne peut pas être réalisée

### Comment faire ?

1. **Ouvrir l'intervention** à annuler
2. **Cliquer sur le bouton "✖️ Annuler"** dans le header (en haut)
3. **Confirmer** l'annulation dans la pop-up
4. ✅ L'intervention passe au statut **"Annulé"**

### Que se passe-t-il ?

- ✅ Le statut change de `Planifié`/`En cours` → `Annulé`
- ✅ L'événement calendrier est marqué [ANNULÉ] et désactivé
- ✅ Une notification est envoyée dans le chatter
- ✅ L'intervention apparaît en **gris** dans la liste

### ⚠️ Limitations

Vous **ne pouvez pas** annuler une intervention si :
- ❌ Elle est déjà **terminée** (contacter un administrateur)
- ❌ Elle est déjà **facturée** (annuler/créditer la facture d'abord)

---

## 🔄 Replanifier une intervention annulée

### Quand utiliser ?
- Le client redemande l'intervention
- L'intervention peut finalement être réalisée
- Reprogrammer une intervention annulée par erreur

### Comment faire ?

1. **Ouvrir l'intervention annulée**
   - Utilisez le filtre **"Annulées"** dans la recherche pour la trouver

2. **Mettre à jour les informations** (si nécessaire) :
   - 📅 Modifier la **Date prévue** (nouvelle date d'intervention)
   - 👤 Vérifier/modifier le **Technicien principal**
   - ⏱️ Ajuster la **Durée prévue** si besoin

3. **Cliquer sur le bouton "🔄 Replanifier"** dans le header

4. ✅ L'intervention repasse au statut **"Planifié"**

### Que se passe-t-il ?

- ✅ Le statut change de `Annulé` → `Planifié`
- ✅ Les dates de début/fin/arrivée sont réinitialisées
- ✅ L'événement calendrier est réactivé avec les nouvelles dates
- ✅ Une notification de réactivation est envoyée dans le chatter
- ✅ L'intervention réapparaît dans le planning normal

### ⚠️ Contrôles obligatoires

Vous **devez** définir avant de replanifier :
- ❌ **Date prévue** : Une nouvelle date d'intervention
- ❌ **Technicien principal** : L'intervenant assigné

---

## 📊 Trouver les interventions annulées

### Méthode 1 : Filtre de recherche
1. Aller dans **Interventions** → **Interventions**
2. Cliquer sur **Recherche** (icône entonnoir)
3. Sélectionner le filtre **"Annulées"**

### Méthode 2 : Vue liste
Les interventions annulées apparaissent en **gris** (texte atténué) dans la liste.

---

## 🔄 Workflow complet

```
┌─────────────────────────────────────────────────────────┐
│ 1. INTERVENTION PLANIFIÉE                               │
│    Statut : Planifié                                    │
│    Calendrier : Événement actif                         │
└───────────────┬─────────────────────────────────────────┘
                │
                │ ✖️ Client annule
                ▼
┌─────────────────────────────────────────────────────────┐
│ 2. INTERVENTION ANNULÉE                                 │
│    Statut : Annulé                                      │
│    Calendrier : [ANNULÉ] + désactivé                    │
│    Apparence : Gris dans la liste                       │
└───────────────┬─────────────────────────────────────────┘
                │
                │ 🔄 Client redemande
                │ → Modifier date/technicien
                │ → Clic "Replanifier"
                ▼
┌─────────────────────────────────────────────────────────┐
│ 3. INTERVENTION REPLANIFIÉE                             │
│    Statut : Planifié                                    │
│    Calendrier : Réactivé avec nouvelles dates           │
│    Dates : Réinitialisées (début/fin/arrivée)          │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Conseils pratiques

### ✅ Bonnes pratiques

1. **Avant d'annuler** :
   - Vérifier qu'aucune facture n'a été émise
   - Prévenir le technicien si déjà assigné

2. **Avant de replanifier** :
   - Confirmer avec le client la nouvelle date
   - Vérifier la disponibilité du technicien
   - Mettre à jour la date prévue dans la fiche

3. **Suivi** :
   - Les notifications dans le chatter permettent de tracer l'historique
   - Utilisez le filtre "Annulées" pour suivre les interventions en attente

### ❌ À éviter

- ❌ Ne pas annuler une intervention déjà en cours sans vérifier avec le technicien
- ❌ Ne pas replanifier sans avoir confirmé avec le client
- ❌ Ne pas oublier de mettre à jour la date avant de replanifier

---

## 🆘 Problèmes courants

### "Impossible d'annuler une intervention déjà terminée"
**Solution** : Contacter un administrateur. Les interventions terminées ne peuvent normalement pas être annulées.

### "Impossible d'annuler une intervention déjà facturée"
**Solution** : Annuler ou créditer la facture d'abord, puis annuler l'intervention.

### "Veuillez d'abord définir une nouvelle date d'intervention"
**Solution** : Modifier le champ "Date prévue" avant de cliquer sur "Replanifier".

### "Veuillez d'abord assigner un technicien"
**Solution** : Sélectionner un technicien dans le champ "Intervenant" avant de cliquer sur "Replanifier".

---

## 📞 Support

Pour toute question ou problème, contactez l'équipe technique MASITH.

**Date de mise à jour** : 4 novembre 2025
