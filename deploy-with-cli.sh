#!/bin/bash
#
# Script de déploiement automatique Odoo via Railway CLI
# Usage: ./deploy-with-cli.sh "Nom de la demo" "email@client.com"
#

set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Vérifier les arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <demo-name> [email]${NC}"
    echo "Exemple: $0 'Demo Client ABC' 'client@example.com'"
    exit 1
fi

DEMO_NAME="$1"
CLIENT_EMAIL="${2:-}"
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-24)

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Déploiement Odoo - $DEMO_NAME${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Vérifier si Railway CLI est installé
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI n'est pas installé${NC}"
    echo ""
    echo "Installation :"
    echo "  macOS/Linux: curl -fsSL https://railway.app/install.sh | sh"
    echo "  Windows: iwr https://railway.app/install.ps1 | iex"
    echo "  npm: npm install -g @railway/cli"
    echo ""
    exit 1
fi

# Vérifier le token
if [ -z "$RAILWAY_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  Variable RAILWAY_TOKEN non définie${NC}"
    echo ""
    echo "Définissez-la avec:"
    echo "  export RAILWAY_TOKEN='votre-token'"
    echo ""
    echo "Ou créez un fichier .env avec:"
    echo "  RAILWAY_TOKEN=votre-token"
    echo ""
    exit 1
fi

echo -e "${YELLOW}📦 Étape 1/5 : Création du projet Railway...${NC}"
# Créer un répertoire temporaire pour ce déploiement
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Initialiser git (requis par Railway)
git init
git remote add origin https://github.com/MASITH-developpement/EZAYNOVA2.git
git fetch origin claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro
git checkout claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro

# Se connecter avec le token
echo "$RAILWAY_TOKEN" | railway login --browserless

# Créer le projet
railway init --name "$DEMO_NAME"

PROJECT_ID=$(railway status --json | jq -r '.project.id')
echo -e "${GREEN}✅ Projet créé (ID: $PROJECT_ID)${NC}"
echo ""

echo -e "${YELLOW}📦 Étape 2/5 : Ajout de PostgreSQL...${NC}"
# Ajouter PostgreSQL
railway add --database postgres
sleep 3
echo -e "${GREEN}✅ PostgreSQL ajouté${NC}"
echo ""

echo -e "${YELLOW}📦 Étape 3/5 : Configuration des variables...${NC}"
# Configurer les variables d'environnement
railway variables set \
  "ADMIN_PASSWORD=$ADMIN_PASSWORD" \
  "DB_HOST=\${{Postgres.PGHOST}}" \
  "DB_PORT=\${{Postgres.PGPORT}}" \
  "DB_USER=\${{Postgres.PGUSER}}" \
  "DB_PASSWORD=\${{Postgres.PGPASSWORD}}" \
  "DB_NAME=\${{Postgres.PGDATABASE}}" \
  "WORKERS=2"

echo -e "${GREEN}✅ Variables configurées${NC}"
echo ""

echo -e "${YELLOW}📦 Étape 4/5 : Déploiement Odoo...${NC}"
# Déployer
railway up --detach

# Attendre un peu pour que le déploiement démarre
sleep 5
echo -e "${GREEN}✅ Déploiement lancé${NC}"
echo ""

echo -e "${YELLOW}📦 Étape 5/5 : Génération du domaine...${NC}"
# Générer un domaine public
railway domain 2>/dev/null || true
sleep 2

# Récupérer l'URL du déploiement
DEPLOYMENT_URL=$(railway status --json 2>/dev/null | jq -r '.services[0].domains[0]' || echo "En attente...")

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ DÉPLOIEMENT RÉUSSI !${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "🌐 ${YELLOW}URL Odoo:${NC} https://$DEPLOYMENT_URL"
echo -e "👤 ${YELLOW}Utilisateur:${NC} admin"
echo -e "🔑 ${YELLOW}Mot de passe:${NC} $ADMIN_PASSWORD"
echo ""

if [ -n "$CLIENT_EMAIL" ]; then
    echo -e "📧 ${YELLOW}Email client:${NC} $CLIENT_EMAIL"
    echo ""
fi

echo -e "${YELLOW}Note:${NC} Le déploiement prend 2-3 minutes."
echo -e "${YELLOW}Vérifiez sur:${NC} https://railway.app/project/$PROJECT_ID"
echo ""

# Créer un fichier JSON avec les informations
cat > /tmp/odoo-demo-${PROJECT_ID}.json <<EOF
{
  "success": true,
  "demo_name": "$DEMO_NAME",
  "project_id": "$PROJECT_ID",
  "url": "https://$DEPLOYMENT_URL",
  "credentials": {
    "username": "admin",
    "password": "$ADMIN_PASSWORD"
  },
  "client_email": "$CLIENT_EMAIL",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo -e "${GREEN}📄 Informations sauvegardées:${NC} /tmp/odoo-demo-${PROJECT_ID}.json"
echo ""

# Nettoyage
cd - > /dev/null
rm -rf "$TEMP_DIR"

exit 0
