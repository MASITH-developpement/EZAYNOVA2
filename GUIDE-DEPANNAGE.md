# 🔧 GUIDE DE DÉPANNAGE - Installation des modules Odoo

## ❌ Problème : Les modules n'apparaissent pas dans Apps

### ✅ Solution 1 : Vérifier le déploiement Railway

1. **Aller sur Railway Dashboard**
2. **Deployments** → Vérifier que le dernier commit est `fb08086`
3. Si ce n'est pas le cas : **Cliquer sur Redeploy**

### ✅ Solution 2 : Débloquer la base de données (PRIORITAIRE)

**Via Railway PostgreSQL Interface :**

1. Cliquer sur le service **PostgreSQL**
2. Onglet **Data** ou **Query**
3. **Sélectionner la base `eazynova`** dans le menu déroulant
4. Exécuter ces commandes **UNE PAR UNE** :

```sql
-- Étape 1 : Voir les modules bloqués
SELECT name, state FROM ir_module_module
WHERE state IN ('to install', 'to upgrade', 'to remove');

-- Étape 2 : Débloquer TOUS les modules
UPDATE ir_module_module
SET state = 'uninstalled'
WHERE state IN ('to install', 'to upgrade', 'to remove');

-- Étape 3 : Vérification
SELECT COUNT(*) as modules_bloques
FROM ir_module_module
WHERE state IN ('to install', 'to upgrade', 'to remove');
-- Devrait retourner 0

-- Étape 4 : Supprimer les modules problématiques s'ils existent
DELETE FROM ir_module_module
WHERE name IN ('website_booking', 'sales_funnel', 'odoo_unlock');
```

### ✅ Solution 3 : Redémarrer Odoo

**Après avoir exécuté le SQL :**

1. Dans Railway : **Restart** l'application Odoo
2. Attendre **3-5 minutes** (important !)
3. Vérifier les logs : chercher "Loading module"

### ✅ Solution 4 : Update Apps List dans Odoo

1. Aller dans **Apps**
2. Cliquer sur **⟳ Update Apps List**
3. Attendre la fin (peut prendre 1-2 min)
4. Activer **Developer Mode** (⚙️ → Activate Developer Mode)
5. Retourner dans **Apps**
6. Retirer le filtre "Apps" et chercher "eazynova" ou "booking"

### ✅ Solution 5 : Vérifier le chemin addons

**Dans Railway, vérifier les variables d'environnement :**

```
ADDONS_PATH devrait contenir : /mnt/extra-addons
```

Si ce n'est pas le cas, ajouter cette variable.

---

## 🔍 Diagnostic des problèmes

### Vérifier les logs Railway

Chercher ces messages dans les logs :

**✅ BON :**
```
addons paths: [...'/mnt/extra-addons'...]
loading module website_booking
loading module sales_funnel
```

**❌ MAUVAIS :**
```
Skipping database eazynova because of modules to install/upgrade/remove
Failed to load module
```

### Si vous voyez "Skipping database"

→ **La base est bloquée** → Exécuter les commandes SQL (Solution 2)

### Si les modules n'apparaissent toujours pas

→ **Le code n'est pas déployé** → Redéployer Railway (Solution 1)

---

## 🎯 Checklist complète

- [ ] Railway a déployé le commit `fb08086`
- [ ] Les commandes SQL ont été exécutées
- [ ] Odoo a été redémarré
- [ ] Update Apps List a été fait
- [ ] Developer Mode est activé
- [ ] La recherche ne filtre pas les modules techniques

---

## 📞 Si rien ne fonctionne

Fournissez-moi :

1. **Capture d'écran** de la page Apps avec Developer Mode activé
2. **Les dernières lignes des logs Railway** (50 lignes)
3. **Le résultat de cette requête SQL :**
   ```sql
   SELECT name, state, latest_version
   FROM ir_module_module
   WHERE name LIKE '%booking%' OR name LIKE '%funnel%' OR name LIKE '%unlock%';
   ```

---

## 🚀 Ordre d'installation recommandé

Une fois les modules visibles :

1. **odoo_unlock** (installer en premier pour nettoyer)
2. Attendre 2 min
3. **Désinstaller odoo_unlock**
4. **website_booking** (Prise de RDV)
5. **sales_funnel** (Tunnel de vente)

**Ne PAS installer les 3 en même temps !**
