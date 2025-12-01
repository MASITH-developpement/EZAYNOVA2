#!/bin/bash
set -e

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Démarrage de l'entrypoint Odoo 19 CE ===${NC}"

# Vérifier les variables d'environnement obligatoires
REQUIRED_VARS=("DB_HOST" "DB_PORT" "DB_USER" "DB_PASSWORD" "ADMIN_PASSWORD")
MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}Erreur: Variables d'environnement manquantes:${NC}"
    printf '%s\n' "${MISSING_VARS[@]}"
    exit 1
fi

echo -e "${YELLOW}Configuration des variables d'environnement...${NC}"

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
chown odoo:odoo /etc/odoo/odoo.conf

echo -e "${GREEN}Démarrage d'Odoo 19 CE en français...${NC}"

# Démarrer Odoo en tant qu'utilisateur odoo
if [ "$(id -u)" = '0' ]; then
    exec gosu odoo odoo -c /etc/odoo/odoo.conf "$@"
else
    exec odoo -c /etc/odoo/odoo.conf "$@"
fi
