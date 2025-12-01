#!/bin/bash
set -e

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Forcer l'affichage immédiat (unbuffered)
export PYTHONUNBUFFERED=1

echo "========================================"
echo "=== DEMARRAGE ENTRYPOINT ODOO 19 CE ==="
echo "========================================"
echo ""

# Afficher les variables d'environnement pour le debug
echo "Variables d'environnement disponibles:"
echo "  DB_HOST: ${DB_HOST:-NON DEFINI}"
echo "  DB_PORT: ${DB_PORT:-NON DEFINI}"
echo "  DB_USER: ${DB_USER:-NON DEFINI}"
echo "  DB_PASSWORD: ${DB_PASSWORD:+***DEFINI***}"
echo "  DB_NAME: ${DB_NAME:-NON DEFINI (utilisera 'postgres')}"
echo "  ADMIN_PASSWORD: ${ADMIN_PASSWORD:+***DEFINI***}"
echo ""

# Vérifier les variables d'environnement obligatoires
REQUIRED_VARS=("DB_HOST" "DB_PORT" "DB_USER" "DB_PASSWORD" "ADMIN_PASSWORD")
MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "ERREUR: Variables d'environnement manquantes:"
    printf '  - %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "Veuillez configurer ces variables dans Railway:"
    echo "  DB_HOST=\${{Postgres.PGHOST}}"
    echo "  DB_PORT=\${{Postgres.PGPORT}}"
    echo "  DB_USER=\${{Postgres.PGUSER}}"
    echo "  DB_PASSWORD=\${{Postgres.PGPASSWORD}}"
    echo "  DB_NAME=\${{Postgres.PGDATABASE}}"
    echo "  ADMIN_PASSWORD=votre_mot_de_passe_securise"
    echo ""
    exit 1
fi

echo "Configuration des variables d'environnement... OK"
echo ""

# Variables par défaut
DB_NAME="${DB_NAME:-postgres}"

# Créer le fichier de configuration avec substitution des variables
cat > /etc/odoo/odoo.conf << EOF
[options]
# Paramètres généraux
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo

# Paramètres de la base de données
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}
db_name = ${DB_NAME}
db_maxconn = 64

# Paramètres réseau
http_port = 8069
http_interface = 0.0.0.0

# Langue par défaut (français uniquement)
load_language = fr_FR
translate_modules = ['all']

# Paramètres de sécurité
admin_passwd = ${ADMIN_PASSWORD}
list_db = True
proxy_mode = True

# Paramètres de logs
log_level = info
logfile = False

# Paramètres de performance
workers = ${WORKERS:-2}
max_cron_threads = 1
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

# Sans demo data
without_demo = True
EOF

echo -e "${GREEN}Configuration générée avec succès!${NC}"
echo -e "${YELLOW}Connexion à la base de données: ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}${NC}"

# Attendre que PostgreSQL soit prêt
echo -e "${YELLOW}Attente de la disponibilité de PostgreSQL...${NC}"
max_attempts=30
attempt=0

while ! pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo -e "${RED}Erreur: Impossible de se connecter à PostgreSQL après ${max_attempts} tentatives${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Tentative ${attempt}/${max_attempts} - PostgreSQL n'est pas encore prêt...${NC}"
    sleep 2
done

echo -e "${GREEN}PostgreSQL est prêt!${NC}"

# Donner les permissions appropriées
chown -R odoo:odoo /etc/odoo /var/lib/odoo /mnt/extra-addons 2>/dev/null || true

echo -e "${GREEN}Démarrage d'Odoo 19 CE en français...${NC}"

# Démarrer Odoo directement
exec odoo -c /etc/odoo/odoo.conf "$@"
