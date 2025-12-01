# Fonctionnalité d'annulation et replanification d'intervention

## Description
Cette fonctionnalité permet de :
1. **Annuler** une intervention lorsque le client ou le donneur d'ordre annule la commande
2. **Réactiver** une intervention annulée si le client redemande cette intervention

## 1. Annulation d'intervention

### Bouton d'annulation
Un bouton **"✖️ Annuler"** est disponible dans le header du formulaire d'intervention :
- **Visible** : Quand l'intervention est en statut "Planifié" ou "En cours"
- **Masqué** : Quand l'intervention est déjà "Terminée" ou "Annulée"
- **Confirmation** : Demande une confirmation avant d'annuler

### Contrôles de sécurité
L'annulation est **bloquée** dans les cas suivants :
1. **Intervention déjà terminée** : Message d'erreur indiquant de contacter un administrateur
2. **Intervention déjà facturée** : Obligation d'annuler/créditer la facture d'abord

### Actions automatiques lors de l'annulation

#### 1. Mise à jour des statuts
- `statut` → `'annule'`
- `statut_terrain` → réinitialisé à `'planifie'`

#### 2. Gestion de l'événement calendrier
Si un événement calendrier existe :
- Ajout du préfixe **[ANNULÉ]** au nom de l'événement
- Désactivation de l'événement (`active = False`)

#### 3. Notification dans le chatter
Message automatique posté avec :
- Nom de l'utilisateur qui a annulé
- Motif : "Annulation par le client final" ou "Annulation par le donneur d'ordre"
- Sujet : "Annulation intervention [N° INTERVENTION]"

#### 4. Notification visuelle
Pop-up affichée à l'utilisateur :
- Titre : "✖️ Intervention annulée"
- Message : "L'intervention [NUMERO] a été annulée"
- Type : Warning (jaune)

## 2. Replanification d'intervention

### Bouton de replanification
Un bouton **"🔄 Replanifier"** apparaît dans le header quand l'intervention est annulée :
- **Visible** : Uniquement quand l'intervention est en statut "Annulé"
- **Masqué** : Pour tous les autres statuts
- **Style** : Bouton bleu highlight pour indiquer une action positive

### Contrôles de sécurité
La replanification est **bloquée** si :
1. **Pas de date prévue** : Message demandant de définir une nouvelle date d'intervention
2. **Pas de technicien** : Message demandant d'assigner un technicien

### Modification des champs pour replanification
Les champs suivants sont **modifiables** même quand l'intervention est annulée :
- **Date prévue** : Pour définir la nouvelle date de l'intervention
- **Technicien principal** : Pour réassigner ou confirmer le technicien
- **Durée prévue** : Pour ajuster si nécessaire

Ces champs ne sont bloqués que quand l'intervention est "Terminée".

### Actions automatiques lors de la replanification

#### 1. Réinitialisation des statuts
- `statut` → `'planifie'`
- `statut_terrain` → `'planifie'`

#### 2. Réinitialisation des dates
- `date_debut` → `False`
- `date_fin` → `False`
- `heure_arrivee` → `False`

#### 3. Réactivation de l'événement calendrier
Si un événement existe :
- Suppression du préfixe **[ANNULÉ]** du nom
- Réactivation (`active = True`)
- Mise à jour des dates (start/stop)

Si aucun événement n'existe :
- Création automatique d'un nouvel événement calendrier

#### 4. Notification dans le chatter
Message automatique posté avec :
- Nom de l'utilisateur qui a réactivé
- Motif : "Le client final a redemandé cette intervention" ou "Le donneur d'ordre a redemandé cette intervention"
- Nouvelle date de l'intervention
- Sujet : "Réactivation intervention [N° INTERVENTION]"

#### 5. Notification visuelle
Pop-up affichée à l'utilisateur :
- Titre : "🔄 Intervention réactivée"
- Message : "L'intervention [NUMERO] a été remise au statut 'Planifié'"
- Type : Success (vert)

## 3. Vue liste

Les interventions annulées sont affichées en **gris** (classe `decoration-muted`) dans la vue liste.

## 4. Filtre de recherche

Un filtre **"Annulées"** permet de filtrer uniquement les interventions annulées :
- Menu **Recherche** → **Annulées**
- Domain : `[('statut', '=', 'annule')]`

## 5. Barre de statut

Le statut "Annulé" apparaît dans la barre de statut (statusbar) :
- Visible : `planifie,en_cours,termine,annule`

## Fichiers modifiés

### 1. `models/intervention.py`

#### a. Méthode `action_annuler()`
```python
def action_annuler(self):
    """Annuler une intervention (le client ou donneur d'ordre a annulé la commande)"""
    self.ensure_one()
    
    # Contrôles de sécurité
    if self.statut == 'termine':
        raise UserError("Impossible d'annuler une intervention déjà terminée...")
    
    if self.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
        raise UserError("Impossible d'annuler une intervention déjà facturée...")
    
    # Mise à jour des statuts
    self.write({'statut': 'annule', 'statut_terrain': 'planifie'})
    
    # Annulation de l'événement calendrier
    if self.calendar_event_id:
        self.calendar_event_id.write({
            'name': f"[ANNULÉ] {self.calendar_event_id.name}",
            'active': False
        })
    
    # Notifications...
```

#### b. Méthode `action_replanifier()` (NOUVEAU)
```python
def action_replanifier(self):
    """Réactiver une intervention annulée et la remettre au statut planifié"""
    self.ensure_one()
    
    # Vérifier que l'intervention est bien annulée
    if self.statut != 'annule':
        raise UserError("Cette action est réservée aux interventions annulées...")
    
    # Contrôles : date et technicien obligatoires
    if not self.date_prevue:
        raise UserError("Veuillez d'abord définir une nouvelle date...")
    
    if not self.technicien_principal_id:
        raise UserError("Veuillez d'abord assigner un technicien...")
    
    # Réinitialisation
    self.write({
        'statut': 'planifie',
        'statut_terrain': 'planifie',
        'date_debut': False,
        'date_fin': False,
        'heure_arrivee': False,
    })
    
    # Réactivation du calendrier
    if self.calendar_event_id:
        nom_event = self.calendar_event_id.name.replace('[ANNULÉ] ', '')
        self.calendar_event_id.write({
            'name': nom_event,
            'active': True,
            'start': self.date_prevue,
            'stop': self.date_prevue + timedelta(hours=self.duree_prevue or 2.0),
        })
    else:
        self._create_calendar_event()
    
    # Notifications...
```

### 2. `views/intervention_views.xml`

#### a. Boutons dans le header
```xml
<!-- Bouton Annuler -->
<button name="action_annuler" type="object" string="✖️ Annuler" 
        invisible="statut in ['termine', 'annule']" 
        class="btn-danger" 
        confirm="Êtes-vous sûr de vouloir annuler cette intervention ? Cette action notifiera les parties concernées."
        help="Annuler l'intervention (client ou donneur d'ordre a annulé)"/>

<!-- Bouton Replanifier (NOUVEAU) -->
<button name="action_replanifier" type="object" string="🔄 Replanifier" 
        invisible="statut != 'annule'" 
        class="oe_highlight" 
        help="Réactiver cette intervention annulée et la remettre au statut planifié"/>
```

#### b. Champs modifiables pour replanification
```xml
<field name="date_prevue" readonly="statut in ['termine']"/>
<field name="technicien_principal_id" readonly="statut in ['termine']"/>
```

Ces champs sont maintenant modifiables quand l'intervention est annulée, permettant de redéfinir la date et le technicien avant la replanification.

#### c. Barre de statut mise à jour
```xml
<field name="statut" widget="statusbar" statusbar_visible="planifie,en_cours,termine,annule"/>
```

#### d. Filtre de recherche
```xml
<filter name="annulees" string="Annulées"
        domain="[('statut', '=', 'annule')]"/>
```

#### e. Décoration dans la vue liste
```xml
<list decoration-info="statut=='planifie'" 
      decoration-warning="statut=='en_cours'" 
      decoration-success="statut=='termine'"
      decoration-muted="statut=='annule'">
```

## Workflow complet

### Scénario 1 : Annulation puis replanification

1. **Intervention planifiée** → Statut : `planifie`
2. **Client annule** → Clic sur "✖️ Annuler" → Statut : `annule`
3. **Client redemande** → 
   - Modifier la `date_prevue` si besoin
   - Vérifier/modifier le `technicien_principal_id` si besoin
   - Clic sur "🔄 Replanifier" → Statut : `planifie`
4. **Intervention reprend son cours normal**

### Scénario 2 : Annulation définitive

1. **Intervention planifiée** → Statut : `planifie`
2. **Client annule** → Clic sur "✖️ Annuler" → Statut : `annule`
3. **Pas de replanification** → L'intervention reste archivée en statut `annule`

## Date de mise en place
4 novembre 2025

## Auteur
Développement : GitHub Copilot
Demandé par : Utilisateur MASITH
