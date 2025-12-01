# 🤖 Automatisation Complète - Déploiement Odoo 19 CE

Ce document explique comment déployer **automatiquement** Odoo 19 CE sur Railway **sans intervention manuelle**, parfait pour offrir des démos gratuites via votre site internet.

## 🎯 Objectif

Permettre à vos utilisateurs de créer instantanément une instance Odoo de démonstration en cliquant sur un bouton, sans configuration manuelle.

## 📋 Prérequis

1. **Compte Railway** avec accès API
2. **Token API Railway** (obtenir sur [railway.app/account/tokens](https://railway.app/account/tokens))
3. **Node.js 16+** ou **Python 3.8+** (selon la méthode choisie)

## 🚀 Méthodes de Déploiement Automatique

### Méthode 1 : Bouton "Deploy on Railway" (Le plus simple)

Ajoutez ce bouton à votre site web :

```html
<a href="https://railway.app/template/odoo-19-ce?referralCode=YOUR_CODE">
  <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a>
```

**Avantages** :
- ✅ Un clic pour déployer
- ✅ Pas de code backend nécessaire
- ✅ Railway gère tout automatiquement

**Configuration** :
1. Créez un template Railway avec `railway-template.json`
2. Publiez-le sur Railway Templates
3. Utilisez l'URL du template dans votre bouton

---

### Méthode 2 : API Railway via Node.js (Contrôle total)

Utilisez cette méthode si vous voulez créer une API backend pour gérer les démos.

#### Installation

```bash
# Installer les dépendances
npm install axios

# Ou avec le package.json fourni
npm install
```

#### Utilisation basique

```javascript
const { deployOdooDemo } = require('./deploy-automation.js');

// Déployer une démo
const result = await deployOdooDemo(
  'YOUR_RAILWAY_API_TOKEN',
  'Demo Client ABC'
);

console.log('URL:', result.url);
console.log('Mot de passe:', result.adminPassword);
```

#### Exemple d'API Express

```javascript
const express = require('express');
const { deployOdooDemo } = require('./deploy-automation.js');

const app = express();
app.use(express.json());

// Endpoint pour créer une démo
app.post('/api/create-demo', async (req, res) => {
  const { clientName, email } = req.body;

  try {
    const demoName = `Demo ${clientName} ${Date.now()}`;
    const result = await deployOdooDemo(
      process.env.RAILWAY_TOKEN,
      demoName
    );

    // Enregistrer dans votre base de données
    // await saveDemo({ email, url: result.url, password: result.adminPassword });

    // Envoyer email au client avec les identifiants
    // await sendEmail(email, result);

    res.json({
      success: true,
      url: result.url,
      credentials: {
        username: 'admin',
        password: result.adminPassword
      },
      message: 'Votre démo Odoo est prête !'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(3000, () => {
  console.log('API démarr��e sur le port 3000');
});
```

#### CLI Node.js

```bash
# Déployer depuis la ligne de commande
node deploy-automation.js \
  --token your_railway_token \
  --demo-name "Demo Client ABC"
```

---

### Méthode 3 : API Railway via Python

Pour les backends Python (Django, Flask, FastAPI).

#### Installation

```bash
pip install requests
```

#### Utilisation basique

```python
from deploy_automation import RailwayAutoDeploy

# Créer l'instance
deployer = RailwayAutoDeploy('YOUR_RAILWAY_API_TOKEN')

# Déployer une démo
result = deployer.deploy_odoo_demo('Demo Client ABC')

print(f"URL: {result['url']}")
print(f"Mot de passe: {result['admin_password']}")
```

#### Exemple d'API FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deploy_automation import RailwayAutoDeploy
import os

app = FastAPI()
deployer = RailwayAutoDeploy(os.getenv('RAILWAY_TOKEN'))

class DemoRequest(BaseModel):
    client_name: str
    email: str

@app.post("/api/create-demo")
async def create_demo(request: DemoRequest):
    try:
        demo_name = f"Demo {request.client_name}"
        result = deployer.deploy_odoo_demo(demo_name)

        # Enregistrer dans votre base de données
        # await save_demo(request.email, result)

        # Envoyer email
        # await send_email(request.email, result)

        return {
            "success": True,
            "url": result["url"],
            "credentials": {
                "username": "admin",
                "password": result["admin_password"]
            },
            "message": "Votre démo Odoo est prête !"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### CLI Python

```bash
# Déployer depuis la ligne de commande
python deploy-automation.py \
  --token your_railway_token \
  --demo-name "Demo Client ABC"
```

---

## 🔧 Configuration Railway API

### Obtenir un Token API

1. Allez sur [railway.app/account/tokens](https://railway.app/account/tokens)
2. Cliquez sur **"Create New Token"**
3. Donnez un nom : `Odoo Demo Automation`
4. Copiez le token (vous ne le verrez qu'une fois !)

### Sécuriser le Token

**Jamais dans le code source !** Utilisez des variables d'environnement :

```bash
# .env
RAILWAY_TOKEN=your_token_here
```

**Node.js** :
```javascript
require('dotenv').config();
const token = process.env.RAILWAY_TOKEN;
```

**Python** :
```python
import os
token = os.getenv('RAILWAY_TOKEN')
```

---

## 💡 Flux d'Automatisation Recommandé

### Pour votre site web

```
┌─────────────┐
│  Utilisateur │
│  visite le  │
│  site web   │
└──────┬──────┘
       │
       v
┌─────────────────┐
│  Remplit le     │
│  formulaire     │
│  (Nom, Email)   │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│  Click "Créer   │
│  ma démo"       │
└──────┬──────────┘
       │
       v
┌─────────────────────┐
│  Votre API Backend  │
│  (Node/Python)      │
│                     │
│  1. Appel Railway   │
│  2. Créer projet    │
│  3. Créer Postgres  │
│  4. Créer Odoo      │
│  5. Attendre URL    │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Email automatique  │
│  avec:              │
│  - URL Odoo         │
│  - Login/Password   │
│  - Instructions     │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Utilisateur reçoit │
│  et accède à Odoo   │
│  en 2-3 minutes !   │
└─────────────────────┘
```

---

## 📊 Exemple Frontend (HTML + JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Démo Odoo Gratuite</title>
  <style>
    .demo-form {
      max-width: 500px;
      margin: 50px auto;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
    }
    button {
      background: #6c5ce7;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 4px;
      cursor: pointer;
    }
    .loading { display: none; }
    .result { margin-top: 20px; padding: 20px; background: #d4edda; }
  </style>
</head>
<body>
  <div class="demo-form">
    <h1>🚀 Créez votre démo Odoo gratuite</h1>
    <form id="demoForm">
      <div>
        <label>Nom :</label>
        <input type="text" name="name" required>
      </div>
      <div>
        <label>Email :</label>
        <input type="email" name="email" required>
      </div>
      <button type="submit">Créer ma démo</button>
      <div class="loading">⏳ Création en cours (2-3 min)...</div>
    </form>
    <div id="result" class="result" style="display:none;"></div>
  </div>

  <script>
    document.getElementById('demoForm').addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(e.target);
      const loading = document.querySelector('.loading');
      const result = document.getElementById('result');

      loading.style.display = 'block';

      try {
        const response = await fetch('/api/create-demo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            client_name: formData.get('name'),
            email: formData.get('email')
          })
        });

        const data = await response.json();

        if (data.success) {
          result.innerHTML = `
            <h3>✅ Votre démo est prête !</h3>
            <p><strong>URL:</strong> <a href="${data.url}" target="_blank">${data.url}</a></p>
            <p><strong>Utilisateur:</strong> ${data.credentials.username}</p>
            <p><strong>Mot de passe:</strong> ${data.credentials.password}</p>
            <p>📧 Un email a été envoyé avec ces informations.</p>
          `;
          result.style.display = 'block';
          e.target.reset();
        }
      } catch (error) {
        alert('Erreur: ' + error.message);
      } finally {
        loading.style.display = 'none';
      }
    });
  </script>
</body>
</html>
```

---

## ⚙️ Fonctionnalités Automatiques

Le script d'automatisation gère **tout automatiquement** :

- ✅ Création du projet Railway
- ✅ Déploiement de PostgreSQL
- ✅ Configuration des variables d'environnement
- ✅ Déploiement d'Odoo depuis GitHub
- ✅ Génération d'un mot de passe admin sécurisé
- ✅ Attribution d'un domaine public
- ✅ Vérification que tout fonctionne

**Temps total** : 2-3 minutes par démo

---

## 💰 Coûts Railway

- **Plan Hobby (gratuit)** : 500 heures/mois, $5 de crédit
- **Plan Developer** : $20/mois pour ressources illimitées
- Chaque démo consomme environ 2-3$ de crédit/mois

**Recommandation** : Limitez la durée des démos (7-30 jours) et nettoyez automatiquement les anciennes.

---

## 🧹 Gestion des Démos

### Supprimer une démo automatiquement

**Node.js** :
```javascript
async function deleteDemo(token, projectId) {
  const query = `
    mutation DeleteProject($id: String!) {
      projectDelete(id: $id)
    }
  `;
  await railwayGraphQL(token, query, { id: projectId });
}
```

**Python** :
```python
def delete_demo(self, project_id: str):
    query = """
    mutation DeleteProject($id: String!) {
      projectDelete(id: $id)
    }
    """
    self._graphql_request(query, {"id": project_id})
```

### Créer un système de nettoyage automatique

```javascript
// Supprimer les démos de plus de 7 jours
const deleteOldDemos = async () => {
  const oldDemos = await db.demos.find({
    created_at: { $lt: Date.now() - 7 * 24 * 60 * 60 * 1000 }
  });

  for (const demo of oldDemos) {
    await deleteDemo(RAILWAY_TOKEN, demo.project_id);
    await db.demos.delete(demo.id);
  }
};

// Exécuter tous les jours
setInterval(deleteOldDemos, 24 * 60 * 60 * 1000);
```

---

## 📧 Email Automatique

Exemple d'email à envoyer après création :

```javascript
const nodemailer = require('nodemailer');

async function sendDemoEmail(email, demoInfo) {
  const transporter = nodemailer.createTransporter({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASSWORD
    }
  });

  await transporter.sendMail({
    from: 'noreply@votresite.com',
    to: email,
    subject: '🎉 Votre démo Odoo est prête !',
    html: `
      <h2>Votre démo Odoo 19 CE est prête !</h2>

      <p>Accédez à votre instance Odoo :</p>
      <p><strong>URL:</strong> <a href="${demoInfo.url}">${demoInfo.url}</a></p>
      <p><strong>Utilisateur:</strong> admin</p>
      <p><strong>Mot de passe:</strong> ${demoInfo.adminPassword}</p>

      <p>Cette démo sera disponible pendant 7 jours.</p>

      <p>Besoin d'aide ? Consultez notre <a href="https://votresite.com/docs">documentation</a></p>
    `
  });
}
```

---

## 🔐 Sécurité

### Bonnes pratiques

1. **Limitez les taux de création** : Évitez les abus
   ```javascript
   const rateLimit = require('express-rate-limit');

   const demoLimiter = rateLimit({
     windowMs: 60 * 60 * 1000, // 1 heure
     max: 3, // 3 démos max par heure par IP
     message: 'Trop de démos créées, réessayez plus tard'
   });

   app.post('/api/create-demo', demoLimiter, createDemo);
   ```

2. **Validez les emails** : Évitez les emails jetables
3. **Ajoutez un CAPTCHA** : Protection anti-bot
4. **Logs et monitoring** : Suivez les créations
5. **Nettoyage automatique** : Supprimez les démos expirées

---

## 📚 Ressources

- [Railway API Documentation](https://docs.railway.app/reference/public-api)
- [Railway Templates](https://railway.app/templates)
- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)

---

## 🆘 Support

Si vous rencontrez des problèmes :

1. Vérifiez que votre token Railway est valide
2. Consultez les logs Railway de votre projet
3. Vérifiez les limites de votre plan Railway
4. Contactez le support Railway si nécessaire

---

**Prêt à automatiser vos démos Odoo ! 🚀**
