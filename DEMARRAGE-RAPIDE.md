# 🚀 Démarrage Rapide - Créer votre première démo Odoo

Guide ultra-simple pour créer une démo Odoo en 5 minutes.

## 📋 Ce dont vous avez besoin

- ✅ Votre token Railway : `2d3d74d6-a369-4bf5-b1f7-758adb680a45`
- ✅ Un terminal (bash)
- ✅ 5 minutes de votre temps

---

## 🎯 Option 1 : Méthode Manuelle (Recommandée pour débuter)

### Étape 1 : Aller sur Railway

1. Allez sur [railway.app/new](https://railway.app/new)
2. Cliquez sur **"Deploy from GitHub repo"**

### Étape 2 : Sélectionner le dépôt

1. Recherchez : `MASITH-developpement/EZAYNOVA2`
2. Sélectionnez le dépôt
3. Branche : `claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro`
4. Cliquez sur **"Deploy"**

### Étape 3 : Ajouter PostgreSQL

1. Dans votre projet, cliquez sur **"+ New"**
2. Sélectionnez **"Database"**
3. Choisissez **"PostgreSQL"**
4. Attendez 30 secondes que PostgreSQL soit provisionné

### Étape 4 : Configurer les Variables (IMPORTANT !)

1. Cliquez sur le service **Odoo** (pas PostgreSQL)
2. Allez dans l'onglet **"Variables"**
3. Ajoutez ces variables **une par une** :

```
Nom: DB_HOST
Valeur: ${{Postgres.PGHOST}}

Nom: DB_PORT
Valeur: ${{Postgres.PGPORT}}

Nom: DB_USER
Valeur: ${{Postgres.PGUSER}}

Nom: DB_PASSWORD
Valeur: ${{Postgres.PGPASSWORD}}

Nom: DB_NAME
Valeur: ${{Postgres.PGDATABASE}}

Nom: ADMIN_PASSWORD
Valeur: MonMotDePasseSecurise123!
```

⚠️ **Important** : Copiez exactement `${{Postgres.PGHOST}}` (avec les doubles accolades)

### Étape 5 : Générer un domaine

1. Allez dans **"Settings"** → **"Networking"**
2. Cliquez sur **"Generate Domain"**
3. Copiez l'URL générée

### Étape 6 : Redéployer

1. Retournez à **"Deployments"**
2. Cliquez sur **"Redeploy"**
3. Attendez 2-3 minutes

### Étape 7 : Accéder à Odoo

1. Ouvrez l'URL générée dans votre navigateur
2. Vous verrez la page Odoo ! 🎉
3. Utilisateur : `admin`
4. Mot de passe : celui que vous avez défini dans `ADMIN_PASSWORD`

---

## 🤖 Option 2 : Automatisation CLI (Pour créer plusieurs démos)

### Installation Railway CLI

```bash
# macOS / Linux
curl -fsSL https://railway.app/install.sh | sh

# Ou avec npm
npm install -g @railway/cli
```

### Configuration

```bash
# Définir le token
export RAILWAY_TOKEN='2d3d74d6-a369-4bf5-b1f7-758adb680a45'
```

### Déploiement

```bash
# Rendre le script exécutable
chmod +x deploy-with-cli.sh

# Créer une démo
./deploy-with-cli.sh "Demo Client ABC" "client@example.com"
```

**Résultat en 2-3 minutes** :
```
✅ DÉPLOIEMENT RÉUSSI !

🌐 URL Odoo: https://xxx.up.railway.app
👤 Utilisateur: admin
🔑 Mot de passe: [généré automatiquement]
📧 Email client: client@example.com
```

---

## 🌐 Option 3 : Template Railway (Pour site web)

### Créer un Template

1. Suivez d'abord l'**Option 1** pour créer un projet manuellement
2. Une fois que tout fonctionne, allez dans votre projet
3. Cliquez sur **"Share"** → **"Create Template"**
4. Railway génère une URL : `https://railway.app/template/XXXXXX`

### Utiliser le Template

Ajoutez ce bouton à votre site :

```html
<a href="https://railway.app/template/VOTRE-TEMPLATE-ID">
  <img src="https://railway.app/button.svg" alt="Deploy on Railway">
</a>
```

Vos utilisateurs pourront créer leur propre démo en un clic !

---

## 🔍 Vérification

### Comment vérifier que ça fonctionne ?

Regardez les logs du déploiement sur Railway :

```
========================================
=== DEMARRAGE ENTRYPOINT ODOO 19 CE ===
========================================

Variables d'environnement disponibles:
  DB_HOST: postgres.railway.internal
  DB_PORT: 5432
  DB_USER: postgres
  DB_PASSWORD: ***DEFINI***
  DB_NAME: railway
  ADMIN_PASSWORD: ***DEFINI***

Configuration des variables d'environnement... OK

Attente de la disponibilité de PostgreSQL...
PostgreSQL est prêt!

Démarrage d'Odoo 19 CE en français...
```

✅ **Si vous voyez ça** → Tout fonctionne !

❌ **Si vous voyez "NON DEFINI"** → Retournez à l'Étape 4 et vérifiez les variables

---

## 🎯 Pour Votre Site Web

Une fois que vous avez testé manuellement, voici comment intégrer dans votre site :

### Backend Node.js

```javascript
const express = require('express');
const { exec } = require('child_process');

app.post('/api/create-demo', (req, res) => {
  const { name, email } = req.body;

  exec(
    `./deploy-with-cli.sh "Demo ${name}" "${email}"`,
    {
      env: {
        ...process.env,
        RAILWAY_TOKEN: '2d3d74d6-a369-4bf5-b1f7-758adb680a45'
      }
    },
    (error, stdout) => {
      if (error) {
        return res.status(500).json({ error: error.message });
      }

      // Parser le résultat et envoyer l'email
      res.json({ success: true, message: 'Démo créée !' });
    }
  );
});
```

### Frontend HTML

```html
<form id="demoForm">
  <input type="text" name="name" placeholder="Votre nom" required>
  <input type="email" name="email" placeholder="Votre email" required>
  <button type="submit">Créer ma démo gratuite</button>
</form>

<script>
document.getElementById('demoForm').onsubmit = async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const response = await fetch('/api/create-demo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: formData.get('name'),
      email: formData.get('email')
    })
  });

  const result = await response.json();
  alert('Votre démo est en cours de création ! Vous recevrez un email dans 2-3 minutes.');
};
</script>
```

---

## ❓ FAQ

### Q : Combien de temps pour créer une démo ?
**R :** 2-3 minutes automatiquement

### Q : Quel est le coût par démo ?
**R :** ~$2-3/mois sur Railway (Plan Hobby : $5 gratuit/mois)

### Q : Comment supprimer une démo ?
**R :** Sur Railway Dashboard → Sélectionner le projet → Settings → Delete

### Q : Peut-on limiter la durée des démos ?
**R :** Oui, créez un cron job qui supprime les démos de plus de 7-30 jours

### Q : C'est sécurisé ?
**R :** Oui, chaque démo a son propre mot de passe généré aléatoirement

---

## 🎉 Félicitations !

Vous savez maintenant comment :

- ✅ Créer une démo Odoo manuellement
- ✅ Automatiser avec Railway CLI
- ✅ Créer un template pour votre site
- ✅ Intégrer dans votre backend

**Prêt à offrir des démos gratuites à vos clients ! 🚀**

---

## 🆘 Besoin d'aide ?

- 📖 Guide complet : `README.md`
- 🤖 Automatisation avancée : `AUTOMATION.md`
- ⚡ Ce guide : `DEMARRAGE-RAPIDE.md`

**Bon déploiement ! 💪**
