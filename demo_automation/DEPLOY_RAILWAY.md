# 🚀 Déploiement de l'API de Démos sur Railway

Ce guide vous explique comment déployer l'API de création automatique de démos Odoo sur Railway.

## 📋 Prérequis

- Un compte Railway (https://railway.app)
- Une instance Odoo déployée (ex: ezaynova2-production.up.railway.app)
- Le mot de passe master de votre instance Odoo

## 🔧 Étape 1 : Créer un nouveau service Railway

### Option A : Depuis l'interface Railway (recommandé)

1. **Connectez-vous à Railway** : https://railway.app/dashboard

2. **Ouvrez votre projet** "remarkable-comfort" (ou créez-en un nouveau)

3. **Ajoutez un nouveau service** :
   - Cliquez sur "+ New"
   - Sélectionnez "GitHub Repo"
   - Choisissez le repository `MASITH-developpement/EZAYNOVA2`
   - Branch : `claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro`
   - Root Directory : `demo_automation`

4. **Railway détecte automatiquement le Dockerfile.api**

### Option B : Depuis le CLI Railway

```bash
cd /path/to/EZAYNOVA2/demo_automation
railway login
railway init
railway up
```

## ⚙️ Étape 2 : Configurer les variables d'environnement

Dans Railway, allez dans votre service API → Variables et ajoutez :

### Variables requises :

```bash
# URL de votre instance Odoo
ODOO_URL=https://ezaynova2-production.up.railway.app

# Master password (le même que ADMIN_PASSWORD de votre instance Odoo)
MASTER_PASSWORD=admin

# Clé API pour sécuriser l'accès (générez-en une forte)
API_KEY=votre-cle-api-secrete-aleatoire

# Chemin de la base de données SQLite
DB_PATH=/app/data/demos.db

# Port (Railway le gère automatiquement, mais vous pouvez forcer)
PORT=8080
```

### 🔑 Générer une clé API forte :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Exemple de sortie : `xK9mP2nQ8vL5zR7wT3yU6hJ4gF1dS0aB`

## 🌐 Étape 3 : Générer un domaine public

1. Dans Railway, allez dans **Settings** → **Networking**
2. Cliquez sur **Generate Domain**
3. Vous obtiendrez une URL du type : `https://demo-api-production.up.railway.app`

**Notez cette URL** - vous l'utiliserez dans votre site web !

## 📊 Étape 4 : Vérifier le déploiement

Une fois déployé, testez l'API :

### 1. Health Check :
```bash
curl https://demo-api-production.up.railway.app/health
```

Réponse attendue :
```json
{"status": "ok", "service": "Odoo Demo API"}
```

### 2. Créer une démo de test :
```bash
curl -X POST https://demo-api-production.up.railway.app/api/demo/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre-cle-api" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "duration_hours": 72
  }'
```

Réponse attendue :
```json
{
  "success": true,
  "demo": {
    "url": "https://ezaynova2-production.up.railway.app/web?db=demo_20240101_120000_abcd",
    "login": "admin",
    "password": "aB3dE5fG7hI9jK1l",
    "db_name": "demo_20240101_120000_abcd",
    "expires_at": "2024-01-04T12:00:00",
    "expires_in_hours": 72
  }
}
```

### 3. Voir les statistiques :
```bash
curl https://demo-api-production.up.railway.app/api/demo/stats \
  -H "X-API-Key: votre-cle-api"
```

## 🔗 Étape 5 : Intégrer à votre site web

### JavaScript Example :

```javascript
const API_URL = 'https://demo-api-production.up.railway.app';
const API_KEY = 'votre-cle-api';

async function createDemo(email, name) {
  const response = await fetch(`${API_URL}/api/demo/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      email: email,
      name: name,
      duration_hours: 72
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Démo créée:', data.demo);
    window.open(data.demo.url, '_blank');
  }
}

// Utilisation
createDemo('user@example.com', 'John Doe');
```

### PHP Example :

```php
<?php
$api_url = 'https://demo-api-production.up.railway.app/api/demo/create';
$api_key = 'votre-cle-api';

$data = [
    'email' => 'user@example.com',
    'name' => 'John Doe',
    'duration_hours' => 72
];

$ch = curl_init($api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    "X-API-Key: $api_key"
]);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
if ($result['success']) {
    echo "Démo créée: " . $result['demo']['url'];
}
?>
```

## 🧹 Étape 6 : Configuration du nettoyage automatique

Pour supprimer automatiquement les démos expirées, ajoutez un cron job dans Railway :

1. Créez un nouveau fichier `cleanup_cron.sh` :
```bash
#!/bin/bash
python3 cleanup_expired.py
```

2. Configurez un cron dans Railway ou utilisez un service externe comme :
   - **GitHub Actions** (gratuit)
   - **Cron-job.org** (gratuit)
   - **EasyCron** (gratuit pour petits usages)

Exemple de configuration cron :
```
0 * * * *  # Toutes les heures
```

## 📱 Étape 7 : Intégration avec le module eazynova_website

Le module `eazynova_website` peut utiliser cette API pour créer automatiquement des démos lors des inscriptions :

1. Dans Odoo, allez dans **Settings** → **Technical** → **System Parameters**
2. Ajoutez un nouveau paramètre :
   - **Key** : `eazynova.demo_api_url`
   - **Value** : `https://demo-api-production.up.railway.app`
3. Ajoutez un autre paramètre :
   - **Key** : `eazynova.demo_api_key`
   - **Value** : `votre-cle-api`

## 🎯 Endpoints disponibles

### POST `/api/demo/create`
Crée une nouvelle démo Odoo

**Headers** : `X-API-Key`, `Content-Type: application/json`

**Body** :
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+33612345678",
  "duration_hours": 72
}
```

### GET `/api/demo/stats`
Retourne les statistiques des démos

**Headers** : `X-API-Key`

### GET `/api/demo/list`
Liste toutes les démos actives

**Headers** : `X-API-Key`

### GET `/health`
Health check (pas de clé API requise)

## 🔒 Sécurité

### ⚠️ Important :

1. **Ne jamais exposer votre clé API** dans le code frontend
2. **Toujours appeler l'API depuis votre backend** (PHP, Node.js, etc.)
3. **Utiliser HTTPS** pour toutes les requêtes
4. **Régénérer la clé API** si elle est compromise
5. **Limiter le taux de création** (rate limiting)

### Exemple avec rate limiting :

Dans votre backend PHP :
```php
session_start();
$limit = 3; // Max 3 démos par session
$created = $_SESSION['demos_created'] ?? 0;

if ($created >= $limit) {
    die('Limite de démos atteinte');
}

// Créer la démo...
$_SESSION['demos_created'] = $created + 1;
```

## 📊 Monitoring

### Logs dans Railway :

1. Allez dans votre service API
2. Cliquez sur **Deployments**
3. Sélectionnez le déploiement actif
4. Cliquez sur **View Logs**

### Métriques importantes :

- Nombre de démos créées par jour
- Taux de succès/échec
- Temps de réponse
- Utilisation de la base de données

## 🐛 Dépannage

### Problème : API inaccessible

**Solution** :
1. Vérifiez que le déploiement est actif dans Railway
2. Vérifiez les logs : `railway logs`
3. Vérifiez le health check : `curl https://votre-url/health`

### Problème : Erreur "Clé API invalide"

**Solution** :
1. Vérifiez que le header `X-API-Key` est bien envoyé
2. Vérifiez que la clé correspond à celle configurée dans Railway
3. Pas d'espaces avant/après la clé

### Problème : "Database user 'postgres' is a security risk"

**Solution** :
C'est déjà géré dans notre configuration avec la création automatique de l'utilisateur `odoo`.

### Problème : Démos non supprimées

**Solution** :
1. Vérifiez que le cron de nettoyage s'exécute
2. Exécutez manuellement : `python3 cleanup_expired.py`
3. Vérifiez les logs du cleanup

## 💰 Coûts estimés

**Railway pricing :**
- API Flask : ~$5/mois (Hobby plan) ou gratuit (avec limitations)
- Total système : ~$15-25/mois (Odoo + API)

**Alternative gratuite :**
- Déployer l'API sur Vercel ou Render (gratuit)
- Garder seulement Odoo + PostgreSQL sur Railway

## 🆘 Support

Pour toute question ou problème :
1. Consultez les logs Railway
2. Vérifiez la documentation Odoo : https://www.odoo.com/documentation/19.0/
3. Contactez le support

## 📄 Licence

Propriétaire - EAZYNOVA
