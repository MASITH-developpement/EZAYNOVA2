# EAZYNOVA - Prise de Rendez-vous en ligne

Module de prise de rendez-vous en ligne similaire à Calendly pour Odoo 19.

## Fonctionnalités

### Backend
- **Types de rendez-vous** : Créez différents types de rendez-vous avec durées personnalisées
- **Gestion des disponibilités** : Configurez vos horaires de disponibilité par jour de la semaine
- **Calendrier intégré** : Synchronisation automatique avec le module calendrier d'Odoo
- **Gestion des rendez-vous** : Visualisez tous vos rendez-vous en liste, formulaire ou calendrier
- **Notifications automatiques** : Emails de confirmation et rappels

### Frontend
- **Interface publique** : Page de réservation accessible sans connexion
- **Calendrier interactif** : Sélection intuitive de date et créneaux horaires
- **Formulaire personnalisable** : Collectez les informations dont vous avez besoin
- **Confirmation immédiate** : Page de confirmation avec détails du rendez-vous
- **Gestion client** : Annulation et reprogrammation en ligne

## Installation

1. Copiez le module dans votre dossier `addons`
2. Redémarrez votre serveur Odoo
3. Mettez à jour la liste des applications
4. Installez "EAZYNOVA - Prise de Rendez-vous en ligne"

## Configuration

### 1. Créer un type de rendez-vous

1. Allez dans **Rendez-vous > Types de Rendez-vous**
2. Créez un nouveau type
3. Configurez :
   - Nom et description
   - Durée
   - Délais de réservation
   - Utilisateurs disponibles
   - Options du formulaire

### 2. Configurer les disponibilités

1. Allez dans **Rendez-vous > Disponibilités**
2. Pour chaque utilisateur, définissez les créneaux disponibles par jour
3. Exemple : Lundi 9h-12h et 14h-17h

### 3. Partager le lien

- Le lien de réservation se trouve sur chaque type de rendez-vous
- Format : `https://votre-domaine.com/booking/[ID]`
- Partagez ce lien avec vos clients

## Utilisation

### Réserver un rendez-vous (Client)

1. Accédez au lien de réservation
2. Sélectionnez une date
3. Choisissez un créneau horaire disponible
4. Remplissez vos informations
5. Confirmez votre rendez-vous

### Gérer les rendez-vous (Interne)

1. Visualisez tous les rendez-vous dans **Rendez-vous > Rendez-vous**
2. Consultez le calendrier pour une vue d'ensemble
3. Confirmez, marquez comme effectué ou annulez les rendez-vous
4. Les événements sont automatiquement créés dans le calendrier

## Permissions

### Utilisateur
- Voir et gérer ses propres rendez-vous
- Configurer ses disponibilités

### Manager
- Accès complet à tous les rendez-vous
- Gérer les types de rendez-vous
- Gérer les disponibilités de tous les utilisateurs

## Support

Pour toute question ou problème, contactez le support EAZYNOVA.

## Auteur

**EAZYNOVA - S. MOREAU**
- Site web : https://eazynova.fr
- License : Propriétaire
