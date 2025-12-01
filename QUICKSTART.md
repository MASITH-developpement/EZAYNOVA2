# 🚀 Installation Rapide - Déploiement Automatique

Votre projet est prêt pour le déploiement automatique ! Voici les options recommandées :

## ✅ Option 1 : Railway CLI (Recommandé - Le Plus Simple)

### Installation Railway CLI

```bash
# macOS / Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Ou avec npm
npm install -g @railway/cli
```

### Connexion avec votre token

```bash
# Se connecter avec le token
railway login --browserless

# Entrez votre token quand demandé:
# 2d3d74d6-a369-4bf5-b1f7-758adb680a45
```

### Déploiement automatique

```bash
# Créer un nouveau projet et déployer
railway up

# Railway va automatiquement:
# ✅ Créer le projet
# ✅ Détecter le Dockerfile
# ✅ Builder l'image
# ✅ Déployer Odoo
```

### Ajouter PostgreSQL

```bash
# Ajouter PostgreSQL au projet
railway add

# Choisir "PostgreSQL" dans la liste
```

### Configurer les variables automatiquement

```bash
# Railway détecte automatiquement les services
# Les variables ${{Postgres.XXX}} sont liées automatiquement

# Définir le mot de passe admin
railway variables --set ADMIN_PASSWORD="VotreMotDePasseSecurise123!"
```

---

## ✅ Option 2 : Template Railway (Un Clic)

### Créer un Template Railway

1. Allez sur votre projet Railway créé
2. Cliquez sur **"Share"** → **"Create Template"**
3. Railway génère une URL de template
4. Utilisez ce bouton sur votre site :

```html
<a href="https://railway.app/template/[VOTRE-TEMPLATE-ID]">
  <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a>
```

---

## ✅ Option 3 : GitHub → Railway (Simple)

### Configuration

1. Allez sur [railway.app/new](https://railway.app/new)
2. Cliquez sur **"Deploy from GitHub repo"**
3. Sélectionnez `MASITH-developpement/EZAYNOVA2`
4. Railway détecte automatiquement le Dockerfile
5. Cliquez sur **"Add Variables"** :

```
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_NAME=${{Postgres.PGDATABASE}}
ADMIN_PASSWORD=VotreMotDePasseSecurise123!
```

6. Cliquez sur **"Deploy"**

---

## ✅ Option 4 : API Railway (Pour Site Web)

L'API Railway GraphQL a des limitations. Voici une approche alternative utilisant **Railway CLI en mode headless** :

### Script d'automatisation avec Railway CLI

```bash
#!/bin/bash
# deploy-with-cli.sh

# Configuration
DEMO_NAME=$1
RAILWAY_TOKEN="2d3d74d6-a369-4bf5-b1f7-758adb680a45"

# Se connecter
echo "$RAILWAY_TOKEN" | railway login --browserless

# Créer un nouveau projet
railway init --name "$DEMO_NAME"

# Ajouter PostgreSQL
railway add --database postgres

# Définir les variables
railway variables --set "ADMIN_PASSWORD=$(openssl rand -base64 24)"
railway variables --set "DB_HOST=\${{Postgres.PGHOST}}"
railway variables --set "DB_PORT=\${{Postgres.PGPORT}}"
railway variables --set "DB_USER=\${{Postgres.PGUSER}}"
railway variables --set "DB_PASSWORD=\${{Postgres.PGPASSWORD}}"
railway variables --set "DB_NAME=\${{Postgres.PGDATABASE}}"

# Déployer depuis GitHub
railway up --detach

# Obtenir l'URL
railway domain

echo "✅ Démo créée avec succès!"
```

### Utilisation depuis Node.js

```javascript
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function deployOdooDemo(demoName) {
  try {
    const { stdout } = await execPromise(
      `./deploy-with-cli.sh "${demoName}"`
    );
    console.log(stdout);
    return { success: true, output: stdout };
  } catch (error) {
    console.error('Erreur:', error);
    return { success: false, error: error.message };
  }
}

// Utilisation
deployOdooDemo('Demo Client ABC');
```

---

## 🎯 Méthode Recommandée pour Site Web

Pour offrir des démos via votre site web, la meilleure approche est :

### 1. Créer un Template Railway (Une fois)

```bash
# Déployer une première fois manuellement
railway up
railway add --database postgres

# Configurer les variables
# Sur railway.app → Votre projet → Variables

# Créer le template
# Sur railway.app → Votre projet → Share → Create Template
```

### 2. Utiliser le Template via URL

Sur votre site web, créez un lien unique par utilisateur :

```javascript
// Backend Node.js
app.post('/api/create-demo', (req, res) => {
  const uniqueId = generateUniqueId();
  const templateUrl = `https://railway.app/template/your-template-id?envs.DEMO_ID=${uniqueId}`;

  // Enregistrer dans votre DB
  await saveDemo({
    id: uniqueId,
    email: req.body.email,
    deployUrl: templateUrl
  });

  // Rediriger l'utilisateur
  res.redirect(templateUrl);
});
```

---

## 📊 Vérification

### Vérifier votre projet actuel sur Railway

Votre token a créé un projet : **Demo Test Automatique**

ID: `23aea171-d93d-4d0d-981c-3f1c350b3ae5`

Pour le voir :
1. Allez sur [railway.app/dashboard](https://railway.app/dashboard)
2. Vous verrez "Demo Test Automatique"
3. Vous pouvez le supprimer ou continuer avec

---

## 🔐 Sécurité du Token

⚠️ **IMPORTANT** : Votre token est maintenant dans `.env` qui est ignoré par Git.

### Bonnes pratiques :

1. **Ne jamais committer** le fichier `.env`
2. **Sur production**, utilisez les variables d'environnement du serveur
3. **Régénérez** le token si vous pensez qu'il a été exposé
4. **Limitez** les permissions du token sur Railway

---

## 💡 Prochaines Étapes

1. **Testez** avec Railway CLI :
   ```bash
   railway login --browserless
   # Entrez votre token
   railway up
   ```

2. **Ajoutez PostgreSQL** :
   ```bash
   railway add
   # Choisissez PostgreSQL
   ```

3. **Configurez les variables** :
   ```bash
   railway variables --set ADMIN_PASSWORD="VotreMotDePasse"
   ```

4. **Accédez à votre démo** :
   ```bash
   railway domain
   # Railway vous donnera l'URL
   ```

C'est tout ! En quelques commandes, votre démo Odoo sera en ligne ! 🚀
