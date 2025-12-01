#!/bin/bash
#
# Script simplifié pour Railway CLI
# Ce script fonctionne avec Railway CLI installé
#

# 1. Installation Railway CLI (si pas déjà fait)
echo "📦 Installation Railway CLI..."
echo ""
echo "macOS/Linux:"
echo "  curl -fsSL https://railway.app/install.sh | sh"
echo ""
echo "Windows PowerShell:"
echo "  iwr https://railway.app/install.ps1 | iex"
echo ""
echo "Ou avec npm:"
echo "  npm install -g @railway/cli"
echo ""

# 2. Configuration du token
export RAILWAY_TOKEN='2d3d74d6-a369-4bf5-b1f7-758adb680a45'

# 3. Test de déploiement
echo "🚀 Pour déployer une démo, exécutez:"
echo ""
echo "./deploy-with-cli.sh 'Nom de la Demo' 'email@client.com'"
echo ""
