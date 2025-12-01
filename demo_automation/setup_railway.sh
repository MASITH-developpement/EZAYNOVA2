#!/bin/bash

# Script d'installation automatique de l'API de démos sur Railway
# Usage: ./setup_railway.sh

set -e

echo "=========================================="
echo "🚀 Configuration automatique Railway API"
echo "=========================================="
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_NAME="remarkable-comfort"
SERVICE_NAME="demo-api"
ODOO_URL="https://ezaynova2-production.up.railway.app"
MASTER_PASSWORD="admin"
API_KEY="u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo"
DB_PATH="/app/data/demos.db"
PORT="8080"

echo -e "${BLUE}📦 Étape 1/4 : Vérification de Railway CLI${NC}"
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI n'est pas installé${NC}"
    echo ""
    echo "Pour installer Railway CLI :"
    echo "  npm i -g @railway/cli"
    echo "  ou"
    echo "  curl -fsSL https://railway.app/install.sh | sh"
    echo ""
    echo -e "${YELLOW}Voulez-vous continuer avec la configuration manuelle ? (y/n)${NC}"
    read -r response
    if [[ "$response" != "y" ]]; then
        exit 1
    fi
    MANUAL_MODE=true
else
    echo -e "${GREEN}✓ Railway CLI trouvé${NC}"
    MANUAL_MODE=false
fi

echo ""
echo -e "${BLUE}📋 Étape 2/4 : Configuration des variables${NC}"
echo ""

if [ "$MANUAL_MODE" = true ]; then
    echo "Copiez ces commandes dans Railway (Settings → Variables) :"
    echo ""
    echo "ODOO_URL=${ODOO_URL}"
    echo "MASTER_PASSWORD=${MASTER_PASSWORD}"
    echo "API_KEY=${API_KEY}"
    echo "DB_PATH=${DB_PATH}"
    echo "PORT=${PORT}"
    echo ""
    echo "Puis dans Settings → General :"
    echo "  Root Directory: demo_automation"
    echo "  Build Command: (laissez vide, utilise Dockerfile.api)"
    echo ""
else
    echo -e "${GREEN}Configuration automatique avec Railway CLI...${NC}"

    # Se connecter à Railway (si pas déjà connecté)
    railway login 2>/dev/null || echo "Déjà connecté à Railway"

    # Lier au projet
    railway link

    # Configurer les variables d'environnement
    railway variables set ODOO_URL="${ODOO_URL}"
    railway variables set MASTER_PASSWORD="${MASTER_PASSWORD}"
    railway variables set API_KEY="${API_KEY}"
    railway variables set DB_PATH="${DB_PATH}"
    railway variables set PORT="${PORT}"

    echo -e "${GREEN}✓ Variables configurées${NC}"
fi

echo ""
echo -e "${BLUE}🔨 Étape 3/4 : Informations de déploiement${NC}"
echo ""
echo "Repository: MASITH-developpement/EZAYNOVA2"
echo "Branch: claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro"
echo "Root Directory: demo_automation"
echo "Dockerfile: Dockerfile.api"
echo ""

if [ "$MANUAL_MODE" = false ]; then
    echo -e "${BLUE}🚀 Étape 4/4 : Déploiement${NC}"
    echo ""
    echo -e "${YELLOW}Voulez-vous déployer maintenant ? (y/n)${NC}"
    read -r deploy_response
    if [[ "$deploy_response" = "y" ]]; then
        railway up
        echo -e "${GREEN}✓ Déploiement lancé${NC}"
    fi
else
    echo -e "${BLUE}📝 Étape 4/4 : Instructions manuelles${NC}"
    echo ""
    echo "1. Allez sur https://railway.app/dashboard"
    echo "2. Ouvrez le projet '${PROJECT_NAME}'"
    echo "3. Cliquez sur '+ New' → 'GitHub Repo'"
    echo "4. Sélectionnez: MASITH-developpement/EZAYNOVA2"
    echo "5. Branch: claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro"
    echo "6. Root Directory: demo_automation"
    echo "7. Ajoutez les variables d'environnement (copiées ci-dessus)"
    echo "8. Générez un domaine (Settings → Networking → Generate Domain)"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Configuration terminée !"
echo "==========================================${NC}"
echo ""
echo "📝 Notes importantes :"
echo "  - Clé API: ${API_KEY}"
echo "  - Master Password: ${MASTER_PASSWORD}"
echo "  - URL Odoo: ${ODOO_URL}"
echo ""
echo "🧪 Pour tester après déploiement :"
echo "  curl https://VOTRE-URL/health"
echo ""
echo "📖 Documentation complète : demo_automation/DEPLOY_RAILWAY.md"
echo ""
