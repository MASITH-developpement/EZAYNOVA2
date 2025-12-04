#!/bin/bash

echo "=========================================="
echo "EAZYNOVA - Script de démarrage avec nettoyage des assets"
echo "=========================================="

# Récupérer les informations de connexion PostgreSQL depuis l'environnement
DB_HOST="${PGHOST:-localhost}"
DB_PORT="${PGPORT:-5432}"
DB_NAME="${PGDATABASE:-odoo}"
DB_USER="${PGUSER:-odoo}"
DB_PASSWORD="${PGPASSWORD}"

echo "Connexion à la base de données: $DB_NAME@$DB_HOST:$DB_PORT"

# Nettoyer les assets via SQL
echo "Nettoyage des assets..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << 'EOF'
-- Supprimer tous les assets JavaScript minifiés
DELETE FROM ir_attachment WHERE name LIKE '%.min.js%' OR name LIKE '%assets_%';

-- Supprimer tous les assets CSS minifiés
DELETE FROM ir_attachment WHERE name LIKE '%.min.css%' OR name LIKE '%assets_%';

-- Vider le cache
VACUUM ANALYZE ir_attachment;

SELECT COUNT(*) as "Assets restants" FROM ir_attachment WHERE name LIKE '%.min.%';
EOF

if [ $? -eq 0 ]; then
    echo "✓ Assets nettoyés avec succès"
else
    echo "⚠ Impossible de nettoyer les assets (peut-être pas d'accès SQL)"
    echo "Odoo va démarrer quand même..."
fi

echo "=========================================="
echo "Démarrage d'Odoo..."
echo "=========================================="

# Démarrer Odoo avec les bons paramètres
exec odoo --database "$DB_NAME" \
    --db_host "$DB_HOST" \
    --db_port "$DB_PORT" \
    --db_user "$DB_USER" \
    --db_password "$DB_PASSWORD" \
    --workers 0 \
    --max-cron-threads 0 \
    "$@"
