# 🚀 Déploiement Automatique sur Railway

Ce guide vous explique comment déployer automatiquement l'API de démos sur Railway.

## 🎯 3 Méthodes de déploiement

### Méthode 1 : Script Python Automatique (Recommandé) ⚡

Le plus rapide et entièrement automatisé !

**Prérequis** :
```bash
pip install requests
```

**Étapes** :

1. **Obtenez votre token Railway** :
   - Allez sur https://railway.app/account/tokens
   - Cliquez sur "Create Token"
   - Copiez le token

2. **Lancez le script** :
   ```bash
   cd demo_automation
   python3 deploy_to_railway.py VOTRE_TOKEN_ICI
   ```

3. **C'est tout !** Le script va :
   - ✅ Trouver votre projet "remarkable-comfort"
   - ✅ Créer le service API
   - ✅ Configurer toutes les variables d'environnement
   - ✅ Générer un domaine public
   - ✅ Lancer le déploiement

**Exemple de sortie** :
```
======================================================================
🚀 DÉPLOIEMENT AUTOMATIQUE DE L'API DEMO SUR RAILWAY
======================================================================

📋 Étape 1/5 : Recherche du projet...
✓ Projet trouvé: remarkable-comfort (ID: abc12345...)

🔨 Étape 2/5 : Création du service...
  Repository: MASITH-developpement/EZAYNOVA2
  Branch: claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro
  Root Directory: demo_automation
✓ Service créé: demo-api (ID: def67890...)

⚙️  Étape 3/5 : Configuration des variables d'environnement...
  - Ajout de ODOO_URL...
  - Ajout de MASTER_PASSWORD...
  - Ajout de API_KEY...
  - Ajout de DB_PATH...
  - Ajout de PORT...
✓ Variables configurées

🌐 Étape 4/5 : Génération du domaine public...
✓ Domaine généré: https://demo-api-production.up.railway.app

🚀 Étape 5/5 : Déploiement en cours...
⏳ Railway construit et déploie le service...

======================================================================
✅ CONFIGURATION TERMINÉE !
======================================================================

🌐 URL de l'API: https://demo-api-production.up.railway.app

🧪 Pour tester :
  curl https://demo-api-production.up.railway.app/health
```

---

### Méthode 2 : Script Shell Interactif 🖥️

Utilise le CLI Railway (nécessite installation).

**Installation du CLI** :
```bash
npm i -g @railway/cli
# ou
curl -fsSL https://railway.app/install.sh | sh
```

**Lancement** :
```bash
cd demo_automation
./setup_railway.sh
```

Le script vous guide pas à pas !

---

### Méthode 3 : Configuration Manuelle 👐

Si vous préférez tout faire via l'interface web Railway.

**Étapes** :

1. **Créer le service** :
   - Allez sur https://railway.app/dashboard
   - Ouvrez "remarkable-comfort"
   - Cliquez sur "+ New" → "GitHub Repo"
   - Repo : `MASITH-developpement/EZAYNOVA2`
   - Branch : `claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro`
   - Root Directory : `demo_automation`

2. **Configurer les variables** (Settings → Variables) :
   ```
   ODOO_URL=https://ezaynova2-production.up.railway.app
   MASTER_PASSWORD=admin
   API_KEY=u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo
   DB_PATH=/app/data/demos.db
   PORT=8080
   ```

3. **Générer le domaine** :
   - Settings → Networking → "Generate Domain"

4. **Attendre le déploiement** :
   - Surveillez l'onglet "Deployments"

---

## 🧪 Tester l'API après déploiement

### 1. Health Check
```bash
curl https://VOTRE-URL/health
```

**Réponse attendue** :
```json
{"status": "ok", "service": "Odoo Demo API"}
```

### 2. Créer une démo de test
```bash
curl -X POST https://VOTRE-URL/api/demo/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo" \
  -d '{
    "email": "test@eazynova.fr",
    "name": "Test User",
    "duration_hours": 72
  }'
```

**Réponse attendue** :
```json
{
  "success": true,
  "demo": {
    "url": "https://ezaynova2-production.up.railway.app/web?db=demo_...",
    "login": "admin",
    "password": "...",
    "db_name": "demo_...",
    "expires_at": "2024-XX-XX...",
    "expires_in_hours": 72
  }
}
```

### 3. Voir les statistiques
```bash
curl https://VOTRE-URL/api/demo/stats \
  -H "X-API-Key: u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo"
```

---

## 📊 Surveillance

**Logs en temps réel** :
1. Allez sur Railway Dashboard
2. Cliquez sur votre service "demo-api"
3. Onglet "Deployments" → Sélectionnez le déploiement actif
4. Cliquez sur "View Logs"

**Métriques importantes** :
- CPU et RAM utilisés
- Nombre de requêtes
- Temps de réponse
- Erreurs éventuelles

---

## 🔑 Informations importantes

**Clé API** : `u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo`

⚠️ **IMPORTANT** :
- Ne jamais exposer cette clé dans le frontend
- Toujours appeler l'API depuis votre backend
- Utilisez HTTPS uniquement

---

## 🐛 Dépannage

### Problème : "Service failed to deploy"

**Solutions** :
1. Vérifiez les logs dans Railway
2. Vérifiez que le `Dockerfile.api` est correct
3. Vérifiez que toutes les variables sont définies

### Problème : "Health check failed"

**Solutions** :
1. Vérifiez que le PORT est bien 8080
2. Vérifiez que le service écoute sur 0.0.0.0
3. Vérifiez les logs d'erreur

### Problème : "Clé API invalide"

**Solutions** :
1. Vérifiez le header `X-API-Key`
2. Pas d'espaces avant/après la clé
3. Vérifiez que la variable `API_KEY` est bien définie dans Railway

---

## 📞 Support

Pour plus d'informations, consultez :
- 📖 Documentation complète : `DEPLOY_RAILWAY.md`
- 🌐 Railway Docs : https://docs.railway.app/
- 💬 Railway Discord : https://discord.gg/railway

---

## ✅ Checklist de déploiement

- [ ] Token Railway obtenu
- [ ] Script de déploiement lancé
- [ ] Service créé avec succès
- [ ] Variables d'environnement configurées
- [ ] Domaine généré
- [ ] Health check réussi
- [ ] Démo de test créée avec succès
- [ ] Logs vérifiés

---

**Dernière mise à jour** : 2025-12-01
**Version** : 1.0.0
