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

### Étapes de déploiement (IMPORTANT)

#### Étape 1 : Créer le projet sur Railway

1. Connectez-vous à [Railway](https://railway.app)
2. Cliquez sur **"New Project"**
3. Sélectionnez **"Deploy from GitHub repo"**
4. Choisissez le dépôt **`MASITH-developpement/EZAYNOVA2`**
5. Railway commencera à construire le projet (il échouera sans PostgreSQL - c'est normal !)

#### Étape 2 : Ajouter PostgreSQL (CRITIQUE)

⚠️ **Sans PostgreSQL, Odoo ne fonctionnera pas !**

1. Dans votre projet Railway, cliquez sur **"+ New"**
2. Sélectionnez **"Database"**
3. Choisissez **"Add PostgreSQL"**
4. Attendez que PostgreSQL soit provisionné (≈ 30 secondes)
5. Railway créera automatiquement les variables `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

#### Étape 3 : Configurer les variables d'environnement (CRITIQUE)

⚠️ **Cette étape est OBLIGATOIRE pour que l'application fonctionne !**

1. Cliquez sur votre service **Odoo** (pas PostgreSQL)
2. Allez dans l'onglet **"Variables"**
3. Cliquez sur **"+ New Variable"** et ajoutez **CHAQUE** variable ci-dessous :

```bash
# === CONFIGURATION BASE DE DONNÉES ===
# IMPORTANT: Utilisez exactement ces références Railway
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_NAME=${{Postgres.PGDATABASE}}

# === CONFIGURATION ODOO ===
# IMPORTANT: Remplacez par un mot de passe fort et sécurisé
ADMIN_PASSWORD=VotreMotDePasseSecurise123!

# === OPTIONNEL ===
WORKERS=2
```

**Comment ajouter les variables :**
- Pour chaque ligne ci-dessus, créez une nouvelle variable
- **Nom** : La partie avant le `=` (exemple: `DB_HOST`)
- **Valeur** : La partie après le `=` (exemple: `${{Postgres.PGHOST}}`)
- Railway remplacera automatiquement `${{Postgres.PGHOST}}` par la vraie valeur

#### Étape 4 : Vérifier et redéployer

1. Après avoir ajouté toutes les variables, retournez à l'onglet **"Deployments"**
2. Cliquez sur **"Redeploy"** ou attendez le déploiement automatique
3. Surveillez les logs - vous devriez voir :
   ```
   ========================================
   === DEMARRAGE ENTRYPOINT ODOO 19 CE ===
   ========================================

   Variables d'environnement disponibles:
     DB_HOST: [votre-host]
     DB_PORT: 5432
     DB_USER: postgres
     ...
   ```

4. Si vous voyez `NON DEFINI`, retournez à l'étape 3 !

#### Étape 5 : Accéder à Odoo

1. Une fois le déploiement réussi, cliquez sur le service Odoo
2. Allez dans l'onglet **"Settings"**
3. Sous **"Networking"**, cliquez sur **"Generate Domain"** si ce n'est pas déjà fait
4. Cliquez sur l'URL générée (exemple: `https://votre-app.up.railway.app`)
5. Vous devriez voir la page de création de base de données Odoo

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
├── entrypoint.sh      # Script de démarrage intelligent avec validation
├── odoo.conf          # Configuration Odoo (template)
├── railway.toml       # Configuration Railway avec variables
├── railway.json       # Configuration Railway (backup)
├── .env.example       # Exemple de variables d'environnement
├── requirements.txt   # Dépendances Python supplémentaires
├── .gitignore        # Fichiers à ignorer
└── README.md         # Documentation complète
```

## 🔧 Architecture et fonctionnement

### Script entrypoint.sh

Le projet utilise un script d'entrée personnalisé (`entrypoint.sh`) qui :

1. **Valide les variables d'environnement** : Vérifie que toutes les variables requises sont définies
2. **Génère la configuration** : Crée dynamiquement le fichier `odoo.conf` avec les valeurs des variables d'environnement
3. **Attend PostgreSQL** : Vérifie que la base de données est prête avant de démarrer Odoo (max 30 tentatives)
4. **Lance Odoo** : Démarre Odoo avec la configuration générée

Ce système permet de :
- Utiliser les variables d'environnement de Railway directement
- Éviter les erreurs de configuration statique
- Garantir que la base de données est prête avant le démarrage
- Fournir des logs colorés et informatifs

## 🐛 Dépannage

### ❌ Erreur : "Variables d'environnement manquantes"

**Symptôme** : Dans les logs, vous voyez :
```
ERREUR: Variables d'environnement manquantes:
  - DB_HOST
  - DB_PORT
  - DB_USER
  ...
```

**Solution** :
1. Vérifiez que PostgreSQL est ajouté au projet
2. Allez dans le service Odoo → Onglet **"Variables"**
3. Ajoutez TOUTES les variables listées à l'Étape 3 ci-dessus
4. Assurez-vous d'utiliser la syntaxe exacte : `${{Postgres.PGHOST}}` (pas de guillemets)
5. Redéployez l'application

### ❌ Erreur : "database: default@default:default"

**Symptôme** : Dans les logs, vous voyez :
```
odoo: database: default@default:default
psycopg2.OperationalError: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed
```

**Cause** : Les variables d'environnement ne sont pas définies ou incorrectes.

**Solution** :
1. Vérifiez que vous avez bien ajouté les variables `DB_HOST`, `DB_PORT`, etc.
2. Vérifiez la syntaxe : `DB_HOST=${{Postgres.PGHOST}}` (avec les accolades et sans espaces)
3. Redéployez après avoir corrigé

### ❌ Erreur : "Running as user 'root' is a security risk"

**Symptôme** : Warning dans les logs

**Impact** : Aucun - c'est juste un avertissement. L'application fonctionne.

**Solution (optionnelle)** : Pour l'ignorer, c'est normal pour les conteneurs Docker.

### ❌ PostgreSQL n'est pas prêt

**Symptôme** : Dans les logs, vous voyez :
```
Tentative 1/30 - PostgreSQL n'est pas encore prêt...
```

**Solution** :
- C'est normal ! Le script attend que PostgreSQL soit prêt
- Cela devrait se résoudre en quelques secondes
- Si cela dépasse 30 tentatives, vérifiez que PostgreSQL est bien déployé

### ⚠️ L'application ne démarre pas

1. **Vérifiez les logs** dans Railway (onglet "Deployments" → cliquez sur le déploiement)
2. **Cherchez les messages d'erreur** du script entrypoint
3. **Vérifiez PostgreSQL** : Le service doit être actif (pas de croix rouge)
4. **Vérifiez les variables** : Toutes les variables requises doivent être définies
5. **Redéployez** : Parfois un simple redéploiement résout le problème

### 🐌 Performance lente

1. Augmentez les ressources dans Railway (Plan supérieur)
2. Modifiez la variable `WORKERS` (essayez 4 ou 6)
3. Vérifiez que votre base de données PostgreSQL a assez de ressources

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
