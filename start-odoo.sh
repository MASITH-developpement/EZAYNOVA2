#!/bin/bash
set -e

echo "========================================"
echo "=== ODOO 19 CE STARTUP - V2 FIX ===="
echo "========================================"
echo ""

# Vérifier les variables
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$ADMIN_PASSWORD" ]; then
    echo "ERREUR: Variables d'environnement manquantes!"
    exit 1
fi

DB_NAME="${DB_NAME:-postgres}"

# Créer la configuration Odoo initiale
cat > /etc/odoo/odoo.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}
admin_passwd = ${ADMIN_PASSWORD}
list_db = True
workers = 2
EOF

echo "Configuration initiale créée"

# Attendre PostgreSQL
echo "Attente de PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" > /dev/null 2>&1; then
        echo "PostgreSQL prêt!"
        break
    fi
    sleep 2
done

# Créer un utilisateur Odoo dédié dans PostgreSQL (requis par Odoo 19)
echo "Création de l'utilisateur PostgreSQL 'odoo'..."
PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'odoo') THEN
        CREATE ROLE odoo WITH LOGIN PASSWORD '${DB_PASSWORD}' CREATEDB;
        GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO odoo;
    END IF;
END
\$\$;
" || echo "L'utilisateur odoo existe déjà ou erreur création"

# Recréer la configuration avec l'utilisateur 'odoo'
cat > /etc/odoo/odoo.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = odoo
db_password = ${DB_PASSWORD}
admin_passwd = ${ADMIN_PASSWORD}
list_db = True
workers = 2
EOF

echo "Configuration Odoo créée!"
echo "Connexion: odoo@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Nettoyer les assets corrompus ET débloquer les modules - VERSION AGRESSIVE
echo ""
echo "========================================"
echo "=== NETTOYAGE AGRESSIF ODOO =========="
echo "========================================"
PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d "${DB_NAME}" << 'EOSQL'
-- 1. Désactiver tous les cron jobs temporairement
UPDATE ir_cron SET active = false WHERE active = true;

-- 2. Débloquer TOUS les modules (très agressif)
UPDATE ir_module_module
SET state = 'uninstalled'
WHERE state NOT IN ('installed', 'uninstalled');

-- 3. Supprimer TOUS les assets générés (pas seulement minifiés)
DELETE FROM ir_attachment
WHERE res_model = 'ir.ui.view'
   OR name LIKE '%assets_%'
   OR name LIKE '%.min.%'
   OR name LIKE '%/web/content/%'
   OR name LIKE '%bundle%';

-- 4. Supprimer les vues QWeb compilées
DELETE FROM ir_ui_view
WHERE type = 'qweb'
  AND (name LIKE '%assets%' OR key LIKE '%assets%');

-- 5. Nettoyer le cache de traduction
TRUNCATE ir_translation;

-- 6. Réactiver uniquement les cron essentiels
UPDATE ir_cron SET active = true
WHERE name IN ('Auto-vacuum internal data', 'Update Notification');

-- 7. Vérifier l'état des modules critiques
DO $$
DECLARE
    booking_state TEXT;
    funnel_state TEXT;
BEGIN
    SELECT state INTO booking_state FROM ir_module_module WHERE name = 'website_booking';
    SELECT state INTO funnel_state FROM ir_module_module WHERE name = 'sales_funnel';

    RAISE NOTICE 'website_booking state: %', COALESCE(booking_state, 'NOT FOUND');
    RAISE NOTICE 'sales_funnel state: %', COALESCE(funnel_state, 'NOT FOUND');
END $$;

-- 8. Nettoyer et analyser
VACUUM ANALYZE ir_attachment;
VACUUM ANALYZE ir_module_module;
VACUUM ANALYZE ir_ui_view;

-- Afficher les résultats
SELECT
    COUNT(*) as "Total modules",
    SUM(CASE WHEN state = 'installed' THEN 1 ELSE 0 END) as "Installés",
    SUM(CASE WHEN state = 'uninstalled' THEN 1 ELSE 0 END) as "Non installés",
    SUM(CASE WHEN state NOT IN ('installed', 'uninstalled') THEN 1 ELSE 0 END) as "Bloqués restants"
FROM ir_module_module;

SELECT COUNT(*) as "Assets restants" FROM ir_attachment WHERE name LIKE '%asset%' OR name LIKE '%.min.%';
EOSQL

if [ $? -eq 0 ]; then
    echo "✓ Nettoyage agressif réussi"
else
    echo "⚠ Nettoyage échoué (vérifier les logs)"
fi
echo "========================================"
echo ""

# Lancer Odoo
echo "Démarrage d'Odoo..."
exec odoo -c /etc/odoo/odoo.conf