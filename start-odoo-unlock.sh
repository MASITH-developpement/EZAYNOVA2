#!/bin/bash
set -e

echo "========================================="
echo "=== ODOO 19 CE STARTUP - AUTO UNLOCK ==="
echo "========================================="

# Configuration PostgreSQL
export PGHOST="${PGHOST:-postgres.railway.internal}"
export PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-railway}"
export PGUSER="${PGUSER:-postgres}"

echo "Vérification PostgreSQL..."
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" 2>/dev/null; do
    echo "Attente de PostgreSQL..."
    sleep 2
done

echo "PostgreSQL prêt!"

# Créer l'utilisateur odoo si nécessaire
echo "Configuration utilisateur PostgreSQL..."
psql -v ON_ERROR_STOP=0 << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'odoo') THEN
        CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo';
    END IF;
END
\$\$;
GRANT ALL PRIVILEGES ON DATABASE "$PGDATABASE" TO odoo;
EOF

echo "Configuration Odoo..."
cat > /etc/odoo/odoo.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/var/lib/odoo/addons/19.0,/mnt/extra-addons,/usr/lib/python3/dist-packages/addons
admin_passwd = \${ADMIN_PASSWORD:-admin}
db_host = $PGHOST
db_port = $PGPORT
db_user = odoo
db_password = odoo
db_name = $PGDATABASE
http_port = 8069
logfile = False
workers = 2
max_cron_threads = 1
EOF

# === DÉBLOCAGE AUTOMATIQUE DES MODULES ===
echo "========================================="
echo "DÉBLOCAGE AUTOMATIQUE DES MODULES"
echo "========================================="

# Liste des bases de données à débloquer
DBS=$(psql -t -c "SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres', 'template0', 'template1');" | grep -v '^$')

for DB in $DBS; do
    echo "Traitement de la base: $DB"

    # Vérifier si la table ir_module_module existe
    TABLE_EXISTS=$(psql -d "$DB" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ir_module_module');" 2>/dev/null | tr -d ' ')

    if [ "$TABLE_EXISTS" = "t" ]; then
        echo "  → Recherche de modules bloqués..."

        # Compter les modules bloqués
        BLOCKED=$(psql -d "$DB" -t -c "SELECT COUNT(*) FROM ir_module_module WHERE state IN ('to install', 'to upgrade', 'to remove');" 2>/dev/null | tr -d ' ')

        if [ "$BLOCKED" -gt 0 ]; then
            echo "  ⚠️  $BLOCKED module(s) bloqué(s) trouvé(s)"

            # Afficher les modules bloqués
            psql -d "$DB" -c "SELECT name, state FROM ir_module_module WHERE state IN ('to install', 'to upgrade', 'to remove');"

            # DÉBLOQUER
            echo "  → Déblocage en cours..."
            psql -d "$DB" << UNLOCK_SQL
-- Réinitialiser tous les modules bloqués
UPDATE ir_module_module
SET state = 'uninstalled'
WHERE state IN ('to install', 'to upgrade', 'to remove');

-- Supprimer les modules problématiques s'ils existent
DELETE FROM ir_module_module
WHERE name IN ('website_booking', 'sales_funnel', 'odoo_unlock')
AND state != 'installed';

-- Nettoyer les dépendances
DELETE FROM ir_module_module_dependency
WHERE module_id NOT IN (SELECT id FROM ir_module_module);
UNLOCK_SQL

            echo "  ✅ Base $DB débloquée"
        else
            echo "  ✅ Aucun module bloqué"
        fi
    else
        echo "  ℹ️  Base $DB non initialisée (table ir_module_module absente)"
    fi
done

echo "========================================="
echo "DÉBLOCAGE TERMINÉ - Démarrage d'Odoo"
echo "========================================="

# Démarrer Odoo
exec odoo -c /etc/odoo/odoo.conf "$@"
