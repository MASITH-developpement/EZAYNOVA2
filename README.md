# EZAYNOVA2 - Odoo 19 CE SaaS (Français)

Ce projet configure et déploie Odoo 19 Community Edition en français sur Railway.

## 📋 Caractéristiques

- **Odoo 19 CE** (Community Edition)
- **Langue**: Français uniquement
- **Base de données**: PostgreSQL
- **Déploiement**: Railway
- **Container**: Docker

## 🚀 Déploiement sur Railway

### Prérequis

1. Compte Railway (https://railway.app)
2. Ce dépôt GitHub (EZAYNOVA2)

### Étapes de déploiement

#### 1. Créer un nouveau projet sur Railway

1. Connectez-vous à Railway
2. Cliquez sur "New Project"
3. Sélectionnez "Deploy from GitHub repo"
4. Choisissez le dépôt `EZAYNOVA2`

#### 2. Ajouter une base de données PostgreSQL

1. Dans votre projet Railway, cliquez sur "New"
2. Sélectionnez "Database" → "Add PostgreSQL"
3. Railway créera automatiquement une base de données PostgreSQL

#### 3. Configurer les variables d'environnement

Dans les paramètres de votre service Odoo, ajoutez les variables suivantes :

```bash
# Base de données (référencez votre service PostgreSQL)
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_NAME=${{Postgres.PGDATABASE}}

# Mot de passe administrateur Odoo
ADMIN_PASSWORD=votre_mot_de_passe_admin_securise

# Port (Railway l'assigne automatiquement)
PORT=8069
```

#### 4. Déployer

Railway détectera automatiquement le `Dockerfile` et commencera le déploiement.

## 🔧 Configuration

### Fichiers principaux

- **Dockerfile** : Image Docker basée sur Odoo 19
- **odoo.conf** : Configuration Odoo (langue, base de données, etc.)
- **railway.json** : Configuration du déploiement Railway
- **requirements.txt** : Dépendances Python supplémentaires

### Configuration Odoo

Le fichier `odoo.conf` est configuré pour :
- Langue française par défaut (`load_language = fr_FR`)
- Sans données de démonstration (`without_demo = True`)
- Optimisé pour Railway (2 workers, proxy mode activé)

## 📖 Utilisation

### Accéder à Odoo

Après le déploiement, Railway vous fournira une URL publique. Accédez-y dans votre navigateur :

```
https://votre-app.up.railway.app
```

### Première connexion

1. Accédez à l'URL de votre application
2. Créez une nouvelle base de données avec la langue française
3. Utilisez le mot de passe admin défini dans `ADMIN_PASSWORD`

### Créer une base de données

1. Sur la page d'accueil Odoo, cliquez sur "Créer une base de données"
2. Remplissez les informations :
   - **Nom de la base** : nom de votre choix
   - **Email** : votre email admin
   - **Mot de passe** : votre mot de passe (pas l'ADMIN_PASSWORD)
   - **Langue** : Français (déjà sélectionné)
   - **Pays** : France
   - **Données de démonstration** : Non

## 🔒 Sécurité

### Recommandations importantes

1. **Changez le mot de passe admin** défini dans `ADMIN_PASSWORD`
2. **Utilisez des mots de passe forts** pour tous les comptes
3. **Activez l'authentification à deux facteurs** si disponible
4. **Limitez l'accès** à votre instance via les paramètres Railway

### Variables d'environnement sensibles

Ne commitez jamais les valeurs suivantes dans votre dépôt :
- `ADMIN_PASSWORD`
- `DB_PASSWORD`
- Toute autre information sensible

## 📊 Monitoring et Logs

### Voir les logs

Dans Railway, accédez à l'onglet "Deployments" puis cliquez sur votre déploiement actif pour voir les logs en temps réel.

### Health Check

Railway vérifie automatiquement la santé de votre application via `/web/health`.

## 🛠️ Personnalisation

### Ajouter des modules personnalisés

1. Créez un dossier `addons` à la racine du projet
2. Placez vos modules Odoo personnalisés dans ce dossier
3. Modifiez le `Dockerfile` pour copier ces modules :

```dockerfile
COPY ./addons /mnt/extra-addons
```

### Modifier la configuration

Éditez le fichier `odoo.conf` selon vos besoins, puis redéployez sur Railway.

## 📝 Structure du projet

```
EZAYNOVA2/
├── Dockerfile          # Image Docker Odoo 19
├── odoo.conf          # Configuration Odoo
├── railway.json       # Configuration Railway
├── requirements.txt   # Dépendances Python
├── .gitignore        # Fichiers à ignorer
└── README.md         # Ce fichier
```

## 🐛 Dépannage

### L'application ne démarre pas

1. Vérifiez les logs dans Railway
2. Assurez-vous que toutes les variables d'environnement sont définies
3. Vérifiez que la base de données PostgreSQL est bien connectée

### Erreur de connexion à la base de données

1. Vérifiez que le service PostgreSQL est actif
2. Vérifiez les variables d'environnement `DB_*`
3. Assurez-vous que les références `${{Postgres.*}}` sont correctes

### Performance lente

1. Augmentez les ressources Railway si nécessaire
2. Modifiez les paramètres `workers` dans `odoo.conf`
3. Optimisez la mémoire avec `limit_memory_*`

## 📚 Ressources

- [Documentation Odoo](https://www.odoo.com/documentation/19.0/)
- [Documentation Railway](https://docs.railway.app/)
- [Odoo sur GitHub](https://github.com/odoo/odoo)

## 📄 Licence

Ce projet utilise Odoo Community Edition, sous licence LGPL v3.

## 🤝 Support

Pour toute question ou problème :
1. Consultez la documentation Odoo
2. Vérifiez les issues GitHub
3. Contactez le support Railway pour les problèmes de déploiement

---

**Note** : Ce projet est configuré pour un usage SaaS en français uniquement. Pour d'autres langues, modifiez le paramètre `load_language` dans `odoo.conf`.
