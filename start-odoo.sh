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

# Nettoyer les assets corrompus ET débloquer les modules
echo ""
echo "========================================"
echo "=== NETTOYAGE ET DÉBLOCAGE ODOO ======"
echo "========================================"
PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d "${DB_NAME}" << 'EOSQL'
-- Nettoyer les assets
DELETE FROM ir_attachment WHERE name LIKE '%.min.js%' OR name LIKE '%.min.css%' OR name LIKE '%assets_%';
VACUUM ANALYZE ir_attachment;

-- Débloquer tous les modules bloqués
UPDATE ir_module_module SET state='uninstalled' WHERE state IN ('to install', 'to upgrade', 'to remove');
UPDATE ir_module_module SET state='installed' WHERE state='to upgrade';

-- Afficher les résultats
SELECT COUNT(*) as "Assets supprimés" FROM ir_attachment WHERE name LIKE '%.min.%';
SELECT COUNT(*) as "Modules débloqués" FROM ir_module_module WHERE state='uninstalled';
EOSQL

if [ $? -eq 0 ]; then
    echo "✓ Nettoyage et déblocage réussis"
else
    echo "⚠ Nettoyage ignoré (normal au premier démarrage)"
fi
echo "========================================"
echo ""

# Lancer Odoo
echo "Démarrage d'Odoo..."
exec odoo -c /etc/odoo/odoo.conf