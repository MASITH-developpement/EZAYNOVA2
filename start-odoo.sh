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

# Nettoyer TOUTES les bases de données Odoo existantes
echo ""
echo "========================================"
echo "=== NETTOYAGE MULTI-BASE ODOO ========"
echo "========================================"

# Récupérer la liste de toutes les bases (exclure postgres, template0, template1)
DATABASES=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d postgres -tAc "SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres');" 2>/dev/null)

if [ -z "$DATABASES" ]; then
    echo "⚠ Aucune base de données trouvée - Premier démarrage"
else
    echo "Bases de données détectées:"
    echo "$DATABASES"
    echo ""

    # Pour chaque base de données
    for DB in $DATABASES; do
        echo "--- Traitement de la base: $DB ---"

        # Vérifier si c'est une base Odoo
        IS_ODOO=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d "$DB" -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='ir_module_module');" 2>/dev/null || echo "f")

        if [ "$IS_ODOO" = "t" ]; then
            echo "  ✓ Base Odoo détectée - Nettoyage en cours..."

            # Nettoyage SÉCURISÉ - déblocage uniquement, pas de suppression d'assets critiques
            PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d "$DB" << 'EOSQL' 2>/dev/null
-- Désactiver les cron temporairement
UPDATE ir_cron SET active = false WHERE active = true;

-- Débloquer TOUS les modules
UPDATE ir_module_module SET state = 'uninstalled' WHERE state NOT IN ('installed', 'uninstalled');

-- Réactiver les cron essentiels
UPDATE ir_cron SET active = true WHERE name IN ('Auto-vacuum internal data', 'Update Notification');
EOSQL

            if [ $? -eq 0 ]; then
                echo "  ✓ Nettoyage réussi pour $DB"
            else
                echo "  ⚠ Erreur lors du nettoyage de $DB"
            fi
        else
            echo "  - Base non-Odoo, ignorée"
        fi
        echo ""
    done

    echo "✓ Nettoyage multi-base terminé"
fi
echo "========================================"
echo ""

# ======================================
# FIX: Réinitialiser le domaine website
# ======================================
echo "========================================"
echo "=== FIX WEBSITE REDIRECT ============="
echo "========================================"

if [ -n "$DATABASES" ]; then
    for DB in $DATABASES; do
        # Vérifier si le module website est installé
        HAS_WEBSITE=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d "$DB" -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='website');" 2>/dev/null || echo "f")

        if [ "$HAS_WEBSITE" = "t" ]; then
            echo "Correction du domaine website pour la base: $DB"

            PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "odoo" -d "$DB" << 'EOSQL' 2>/dev/null
-- Réinitialiser tous les domaines website (vide = accepte tous les domaines)
UPDATE website SET domain = '' WHERE active = true;

-- S'assurer qu'il y a un site par défaut
UPDATE website SET is_default_website = false;
UPDATE website SET is_default_website = true WHERE id = (SELECT MIN(id) FROM website WHERE active = true);
EOSQL

            if [ $? -eq 0 ]; then
                echo "  ✓ Domaine website corrigé pour $DB"
            else
                echo "  ⚠ Erreur lors de la correction du domaine pour $DB"
            fi
        fi
    done
fi

echo "========================================"
echo ""

# Lancer Odoo avec mise à jour forcée des modules de base
echo "Démarrage d'Odoo avec régénération des assets..."
exec odoo -c /etc/odoo/odoo.conf --update=base,web