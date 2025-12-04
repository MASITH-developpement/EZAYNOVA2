# Configuration Railway - Commande de démarrage

## Problème
Les assets Odoo sont corrompus et empêchent l'installation des nouveaux modules.

## Solution
Utiliser le script `start-odoo-clean.sh` comme commande de démarrage dans Railway.

## Configuration Railway

### 1. Aller dans les Settings de votre service Odoo sur Railway

### 2. Dans la section "Deploy", trouver "Start Command"

### 3. Remplacer la commande actuelle par:
```bash
./start-odoo-clean.sh
```

### 4. Si le script n'est pas dans le répertoire racine, utiliser le chemin complet:
```bash
/app/start-odoo-clean.sh
```

### 5. Sauvegarder et redéployer

Le script va:
1. Se connecter à PostgreSQL automatiquement (variables d'environnement Railway)
2. Nettoyer tous les assets corrompus en base de données
3. Démarrer Odoo normalement

## Variables d'environnement requises

Railway fournit automatiquement ces variables pour PostgreSQL:
- `PGHOST` - Adresse du serveur PostgreSQL
- `PGPORT` - Port PostgreSQL (5432)
- `PGDATABASE` - Nom de la base de données
- `PGUSER` - Utilisateur PostgreSQL
- `PGPASSWORD` - Mot de passe PostgreSQL

**Aucune configuration supplémentaire n'est nécessaire** si vous utilisez le service PostgreSQL de Railway.

## Alternative si le script ne fonctionne pas

Si Railway ne peut pas exécuter le script bash, vous pouvez:

1. **Redéployer plusieurs fois** pour forcer Railway à nettoyer le cache
2. **Supprimer et recréer le service** Odoo sur Railway
3. **Utiliser le mode développeur Odoo** avec `--dev=all` dans la Start Command:
   ```bash
   odoo --dev=all
   ```

## Vérification

Après le redéploiement avec la nouvelle Start Command:
1. Vérifiez les logs Railway - vous devriez voir "Assets nettoyés avec succès"
2. Rafraîchissez votre navigateur (Ctrl+Shift+R)
3. Les erreurs d'assets devraient disparaître
4. Vous pourrez installer les modules Website Booking et Sales Funnel

## Retour à la normale

Une fois les modules installés et fonctionnels, vous pouvez:
- Retirer le script de nettoyage de la Start Command
- Revenir à la commande Odoo standard
- Le script restera disponible pour un usage futur si nécessaire
