#!/bin/bash

# Script de test du déploiement Railway
# Usage: ./test_deployment.sh <URL_DE_VOTRE_API>

if [ -z "$1" ]; then
    echo "Usage: ./test_deployment.sh <URL_DE_VOTRE_API>"
    echo "Exemple: ./test_deployment.sh https://demo-api-production.up.railway.app"
    exit 1
fi

API_URL=$1
API_KEY="u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo"

echo "=========================================="
echo "🧪 TEST DE L'API DÉPLOYÉE SUR RAILWAY"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "📊 Test 1/3 : Health Check..."
echo "URL: ${API_URL}/health"
echo ""

HEALTH_RESPONSE=$(curl -s "${API_URL}/health")
echo "Réponse: ${HEALTH_RESPONSE}"

if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "✅ Health check réussi !"
else
    echo "❌ Health check échoué"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Créer une démo
echo "🚀 Test 2/3 : Création d'une démo de test..."
echo ""

DEMO_RESPONSE=$(curl -s -X POST "${API_URL}/api/demo/create" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "email": "test@eazynova.fr",
    "name": "Test Automatique",
    "duration_hours": 24
  }')

echo "Réponse:"
echo "$DEMO_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DEMO_RESPONSE"
echo ""

if echo "$DEMO_RESPONSE" | grep -q "success"; then
    echo "✅ Démo créée avec succès !"

    # Extraire l'URL de la démo
    DEMO_URL=$(echo "$DEMO_RESPONSE" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    DEMO_LOGIN=$(echo "$DEMO_RESPONSE" | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
    DEMO_PASSWORD=$(echo "$DEMO_RESPONSE" | grep -o '"password":"[^"]*"' | cut -d'"' -f4)

    echo ""
    echo "📧 Informations de connexion:"
    echo "  URL: ${DEMO_URL}"
    echo "  Login: ${DEMO_LOGIN}"
    echo "  Password: ${DEMO_PASSWORD}"
else
    echo "⚠️  Erreur lors de la création de la démo"
    echo "Cela peut être normal si Odoo n'est pas accessible"
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Statistiques
echo "📊 Test 3/3 : Statistiques des démos..."
echo ""

STATS_RESPONSE=$(curl -s "${API_URL}/api/demo/stats" \
  -H "X-API-Key: ${API_KEY}")

echo "Réponse:"
echo "$STATS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESPONSE"

if echo "$STATS_RESPONSE" | grep -q "total"; then
    echo ""
    echo "✅ Statistiques récupérées avec succès !"
else
    echo ""
    echo "❌ Erreur lors de la récupération des stats"
fi

echo ""
echo "=========================================="
echo "✅ TESTS TERMINÉS !"
echo "=========================================="
echo ""
echo "🎯 Résumé:"
echo "  API URL: ${API_URL}"
echo "  API Key: ${API_KEY}"
echo ""
echo "📖 Documentation: demo_automation/DEPLOY_RAILWAY.md"
echo ""
