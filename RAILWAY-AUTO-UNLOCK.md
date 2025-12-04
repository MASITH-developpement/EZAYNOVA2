# Configuration Railway pour déblocage automatique

## 🚀 Utiliser le script de déblocage automatique

### Option 1 : Modifier la commande de démarrage dans Railway

Dans Railway, **Settings** → **Deploy** → **Start Command** :

```bash
bash /mnt/extra-addons/start-odoo-unlock.sh
```

### Option 2 : Modifier le Dockerfile

Si vous utilisez un Dockerfile personnalisé, remplacez la commande CMD par :

```dockerfile
CMD ["bash", "/mnt/extra-addons/start-odoo-unlock.sh"]
```

### Option 3 : Variable d'environnement

Ajouter dans Railway :

```
START_COMMAND=bash /mnt/extra-addons/start-odoo-unlock.sh
```

---

## ✨ Ce que fait ce script automatiquement

1. ✅ Démarre PostgreSQL
2. ✅ Configure Odoo
3. ✅ **Scanne TOUTES les bases de données**
4. ✅ **Détecte les modules bloqués**
5. ✅ **Les débloque automatiquement**
6. ✅ **Supprime les modules problématiques**
7. ✅ Démarre Odoo normalement

**Aucune intervention manuelle nécessaire !**

---

## 📊 Logs à surveiller

Vous verrez dans les logs Railway :

```
=========================================
DÉBLOCAGE AUTOMATIQUE DES MODULES
=========================================
Traitement de la base: eazynova
  ⚠️  3 module(s) bloqué(s) trouvé(s)
  → Déblocage en cours...
  ✅ Base eazynova débloquée
=========================================
DÉBLOCAGE TERMINÉ - Démarrage d'Odoo
=========================================
```

---

## 🔄 Activation

1. Commit et push le script
2. Dans Railway → Settings → Start Command
3. Entrer : `bash /mnt/extra-addons/start-odoo-unlock.sh`
4. Redéployer

**Le déblocage se fera automatiquement à chaque démarrage !** 🎉
