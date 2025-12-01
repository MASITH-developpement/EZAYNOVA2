# 🚀 Template Railway - Déploiement 100% Automatique

Cette méthode permet à vos utilisateurs de créer une démo Odoo **en UN SEUL CLIC**, sans aucune configuration manuelle.

## 🎯 Concept

1. **Vous créez** : UN template Railway avec PostgreSQL + Odoo + Variables (une seule fois)
2. **Vos utilisateurs cliquent** : Sur un bouton sur votre site
3. **Railway clone** : Tout automatiquement (PostgreSQL + Odoo + Variables)
4. **2-3 minutes** : La démo est prête avec URL unique

**Zéro configuration manuelle pour vos utilisateurs !**

---

## 📋 Étape 1 : Créer le Template de Base (Une Seule Fois)

### Option A : Via l'interface Railway (Recommandé)

#### 1. Créer le projet de base

```bash
# Aller sur Railway
https://railway.app/new

# "Deploy from GitHub repo"
→ Sélectionner : MASITH-developpement/EZAYNOVA2
→ Branche : claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro
```

#### 2. Ajouter PostgreSQL

```bash
# Dans le projet
→ Cliquer "+ New"
→ "Database"
→ "PostgreSQL"
→ Attendre 30 secondes
```

#### 3. Configurer les variables (Important !)

```bash
# Cliquer sur le service "Odoo"
→ Onglet "Variables"
→ Ajouter ces variables :

DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_NAME=${{Postgres.PGDATABASE}}
ADMIN_PASSWORD=${{RAILWAY_STATIC_URL}}
```

**Note** : `ADMIN_PASSWORD=${{RAILWAY_STATIC_URL}}` génère un mot de passe unique par déploiement !

#### 4. Créer le Template

```bash
# Dans votre projet Railway
→ Cliquer "Share" (en haut à droite)
→ "Create Template"
→ Titre : "Odoo 19 CE - Demo Gratuite"
→ Description : "Démo Odoo 19 Community Edition en français"
→ Rendre public : OUI
→ Créer
```

Railway vous donne une URL comme :
```
https://railway.app/template/abc123
```

**C'EST TOUT !** 🎉

---

## 🌐 Étape 2 : Intégrer sur Votre Site Web

### Méthode 1 : Bouton Direct (Le Plus Simple)

```html
<!-- Sur votre site web -->
<a href="https://railway.app/template/abc123" target="_blank">
  <img src="https://railway.app/button.svg" alt="Créer ma démo gratuite">
</a>
```

**L'utilisateur** :
1. Clique sur le bouton
2. Railway s'ouvre
3. Il clique "Deploy"
4. 2-3 minutes → Sa démo est prête !

**Avantage** : Zéro code backend nécessaire
**Inconvénient** : Vous ne captez pas l'email (sauf si formulaire avant)

---

### Méthode 2 : Formulaire + Redirection (Mieux)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Démo Odoo Gratuite</title>
  <style>
    .demo-form {
      max-width: 500px;
      margin: 50px auto;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    input {
      width: 100%;
      padding: 12px;
      margin: 10px 0;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    button {
      width: 100%;
      background: #6c5ce7;
      color: white;
      border: none;
      padding: 15px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    button:hover {
      background: #5b4cdb;
    }
  </style>
</head>
<body>
  <div class="demo-form">
    <h1>🚀 Démo Odoo Gratuite</h1>
    <p>Créez votre instance Odoo en 2 minutes !</p>

    <form id="demoForm">
      <input type="text" name="name" placeholder="Votre nom" required>
      <input type="email" name="email" placeholder="Votre email" required>
      <input type="text" name="company" placeholder="Votre entreprise">
      <button type="submit">🎉 Créer ma démo maintenant</button>
    </form>
  </div>

  <script>
    document.getElementById('demoForm').addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(e.target);

      // Enregistrer dans votre backend
      await fetch('/api/save-demo-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.get('name'),
          email: formData.get('email'),
          company: formData.get('company'),
          timestamp: new Date().toISOString()
        })
      });

      // Rediriger vers le template Railway
      window.location.href = 'https://railway.app/template/abc123';
    });
  </script>
</body>
</html>
```

**Backend simple (Node.js)** :

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/api/save-demo-request', async (req, res) => {
  const { name, email, company, timestamp } = req.body;

  // Sauvegarder dans votre base de données
  await db.demos.insert({
    name,
    email,
    company,
    timestamp,
    status: 'creating'
  });

  // Envoyer email de suivi dans 5 minutes
  setTimeout(() => {
    sendFollowUpEmail(email, name);
  }, 5 * 60 * 1000);

  res.json({ success: true });
});

app.listen(3000);
```

---

### Méthode 3 : Webhook Railway + Email Automatique (Le Plus Pro)

Railway peut envoyer un webhook quand un déploiement est terminé !

#### Configurer le Webhook

```javascript
// webhook-handler.js
const express = require('express');
const nodemailer = require('nodemailer');

const app = express();
app.use(express.json());

app.post('/webhook/railway-deployment', async (req, res) => {
  const { deployment, project, environment } = req.body;

  if (deployment.status === 'SUCCESS') {
    const email = await getEmailFromProjectId(project.id);
    const url = environment.domains[0];
    const password = deployment.meta.variables.ADMIN_PASSWORD;

    // Envoyer email avec les identifiants
    await sendEmail(email, {
      url: `https://${url}`,
      username: 'admin',
      password: password
    });
  }

  res.json({ received: true });
});

async function sendEmail(to, credentials) {
  const transporter = nodemailer.createTransporter({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASSWORD
    }
  });

  await transporter.sendMail({
    from: 'demos@votresite.com',
    to: to,
    subject: '🎉 Votre démo Odoo est prête !',
    html: `
      <h2>Votre démo Odoo 19 CE est prête !</h2>

      <p>Accédez à votre instance :</p>

      <p><strong>🌐 URL :</strong> <a href="${credentials.url}">${credentials.url}</a></p>
      <p><strong>👤 Utilisateur :</strong> ${credentials.username}</p>
      <p><strong>🔑 Mot de passe :</strong> ${credentials.password}</p>

      <p>Cette démo sera disponible pendant 7 jours.</p>

      <hr>

      <p><small>Besoin d'aide ? Consultez notre <a href="https://votresite.com/docs">documentation</a></small></p>
    `
  });
}

app.listen(3000);
```

---

## 🎯 Méthode 4 : API Railway + Déploiement Programmatique (Le Plus Automatique)

Si vous voulez un contrôle TOTAL depuis votre site :

```javascript
// backend-complete.js
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const RAILWAY_TOKEN = '2d3d74d6-a369-4bf5-b1f7-758adb680a45';
const TEMPLATE_ID = 'abc123'; // Votre ID de template

app.post('/api/create-demo', async (req, res) => {
  const { name, email, company } = req.body;

  try {
    // 1. Créer depuis le template via API Railway
    const deployment = await deployFromTemplate(TEMPLATE_ID, {
      projectName: `Demo ${company}`,
      envVars: {
        ADMIN_PASSWORD: generateSecurePassword()
      }
    });

    // 2. Sauvegarder dans votre DB
    await db.demos.insert({
      email,
      name,
      company,
      projectId: deployment.projectId,
      url: deployment.url,
      password: deployment.password,
      createdAt: new Date()
    });

    // 3. Envoyer email immédiatement
    await sendEmail(email, {
      url: deployment.url,
      username: 'admin',
      password: deployment.password
    });

    res.json({
      success: true,
      message: 'Démo créée ! Vérifiez votre email.'
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

async function deployFromTemplate(templateId, options) {
  const response = await axios.post(
    'https://backboard.railway.app/graphql/v2',
    {
      query: `
        mutation DeployTemplate($templateId: String!, $projectName: String!) {
          templateDeploy(input: {
            templateId: $templateId,
            projectName: $projectName
          }) {
            projectId
            url
          }
        }
      `,
      variables: {
        templateId: templateId,
        projectName: options.projectName
      }
    },
    {
      headers: {
        'Authorization': `Bearer ${RAILWAY_TOKEN}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.data.templateDeploy;
}

app.listen(3000);
```

---

## 🔄 Flux Complet (100% Automatique)

```
┌────────────────┐
│ Utilisateur    │
│ sur votre site │
└───────┬────────┘
        │
        │ 1. Remplit formulaire
        │    (Nom, Email, Entreprise)
        v
┌────────────────┐
│ [Créer démo]   │ ← Bouton
└───────┬────────┘
        │
        │ 2. POST /api/create-demo
        v
┌────────────────────┐
│ Votre Backend      │
│                    │
│ - Enregistre email │
│ - Appelle Railway  │
│ - Template deploy  │
└───────┬────────────┘
        │
        │ 3. Railway clone template
        v
┌────────────────────┐
│ Railway            │
│                    │
│ Clone automatique: │
│ - PostgreSQL       │
│ - Odoo             │
│ - Variables        │
└───────┬────────────┘
        │
        │ 4. Déploiement (2-3 min)
        v
┌────────────────────┐
│ Webhook → Backend  │
│                    │
│ - Récupère URL     │
│ - Récupère mot     │
│   de passe         │
└───────┬────────────┘
        │
        │ 5. Email automatique
        v
┌────────────────────┐
│ 📧 Email au client │
│                    │
│ URL: xxx.app       │
│ User: admin        │
│ Pass: xxx          │
└───────┬────────────┘
        │
        v
┌────────────────────┐
│ ✅ Client accède   │
│ à sa démo !        │
└────────────────────┘
```

**Résultat** : 100% automatique, zéro intervention manuelle !

---

## 💡 Recommandation Finale

Pour un site web avec démos gratuites :

1. **Créez le template Railway** (Étape 1)
2. **Utilisez la Méthode 2** (Formulaire + Redirection) pour commencer
3. **Ajoutez la Méthode 3** (Webhook) pour les emails automatiques
4. **Optionnel** : Méthode 4 pour contrôle total

**Avantage** :
- ✅ 100% automatique pour l'utilisateur
- ✅ Aucune configuration manuelle
- ✅ Email avec identifiants
- ✅ Votre branding sur le formulaire
- ✅ Tracking dans votre DB

---

## 🎯 Action Immédiate

1. **Créez votre template** (15 minutes)
   - Allez sur railway.app/new
   - Déployez EZAYNOVA2
   - Ajoutez PostgreSQL
   - Configurez les variables
   - Créez le template

2. **Testez le bouton** sur votre site

3. **Ajoutez le formulaire** pour capter les emails

4. **Automatisez les emails** avec webhooks

**Voilà votre démo 100% automatique ! 🚀**
