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

# Créer la configuration Odoo
cat > /etc/odoo/odoo.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}
db_name = ${DB_NAME}
admin_passwd = ${ADMIN_PASSWORD}
list_db = False
proxy_mode = True
workers = 2
EOF

echo "Configuration Odoo créée!"
echo "Connexion: ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Attendre PostgreSQL
echo "Attente de PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" > /dev/null 2>&1; then
        echo "PostgreSQL prêt!"
        break
    fi
    sleep 2
done

# Lancer Odoo avec l'option --no-database-list pour accepter l'utilisateur postgres
echo "Démarrage d'Odoo..."
exec odoo -c /etc/odoo/odoo.conf --no-database-list