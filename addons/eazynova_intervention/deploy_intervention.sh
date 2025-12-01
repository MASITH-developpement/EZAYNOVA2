#!/bin/bash

# Script de déploiement du module intervention optimisé
# Usage: ./deploy_intervention.sh

echo "🚀 Déploiement du module intervention optimisé"
echo "=============================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ODOO_USER="odoo"
ODOO_SERVICE="odoo"
MODULE_PATH="/Users/stephane/odoo18ce/addons/custom/intervention"
DATABASE_NAME="votre_base_de_donnees"  # À modifier selon votre configuration

# Fonction pour afficher des messages colorés
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si le script est exécuté depuis le bon répertoire
if [ ! -f "__manifest__.py" ]; then
    print_error "Ce script doit être exécuté depuis le répertoire du module intervention"
    exit 1
fi

print_status "Vérification de la structure du module..."

# Lancer les tests
if [ -f "test_module.py" ]; then
    print_status "Exécution des tests..."
    if python3 test_module.py; then
        print_success "Tous les tests sont passés !"
    else
        print_error "Certains tests ont échoué. Arrêt du déploiement."
        exit 1
    fi
else
    print_warning "Fichier de test non trouvé, passage des tests..."
fi

# Vérifier les permissions
print_status "Vérification des permissions..."
if [ ! -r "__manifest__.py" ]; then
    print_error "Permissions insuffisantes pour lire le module"
    exit 1
fi

# Option 1 : Redémarrage du service Odoo (nécessite les droits sudo)
restart_odoo_service() {
    print_status "Tentative de redémarrage du service Odoo..."
    if command -v systemctl &> /dev/null; then
        if sudo systemctl restart $ODOO_SERVICE; then
            print_success "Service Odoo redémarré avec succès"
            return 0
        else
            print_warning "Impossible de redémarrer le service Odoo automatiquement"
            return 1
        fi
    else
        print_warning "systemctl non disponible"
        return 1
    fi
}

# Option 2 : Instructions manuelles
manual_deployment() {
    print_warning "Déploiement manuel requis:"
    echo ""
    echo "1. Redémarrez votre serveur Odoo:"
    echo "   sudo systemctl restart odoo"
    echo "   # ou si vous utilisez un processus manuel:"
    echo "   # Arrêter le processus Odoo et le relancer"
    echo ""
    echo "2. Connectez-vous à votre interface Odoo"
    echo ""
    echo "3. Allez dans Apps > Mettre à jour la liste des apps"
    echo ""
    echo "4. Recherchez 'Interventions Plomberie'"
    echo ""
    echo "5. Cliquez sur 'Mettre à jour' ou 'Installer'"
    echo ""
    echo "Ou utilisez la ligne de commande:"
    echo "./odoo-bin -u intervention -d $DATABASE_NAME"
}

# Tentative de redémarrage automatique
print_status "Tentative de déploiement automatique..."

if restart_odoo_service; then
    print_success "Déploiement automatique réussi !"
    echo ""
    print_status "Prochaines étapes:"
    echo "1. Connectez-vous à votre interface Odoo"
    echo "2. Allez dans Apps et mettez à jour le module 'Interventions Plomberie'"
    echo "3. Testez les nouvelles fonctionnalités"
else
    manual_deployment
fi

echo ""
print_status "Récapitulatif des améliorations apportées:"
echo "✅ Correction des erreurs de syntaxe"
echo "✅ Optimisation des performances (index, cache)"
echo "✅ Interface utilisateur modernisée"
echo "✅ Assistant de création rapide"
echo "✅ Système de géocodage avec cache"
echo "✅ Méthodes de recherche optimisées"

echo ""
print_success "Déploiement terminé ! 🎉"
echo ""
echo "📖 Consultez README_OPTIMISATIONS.md pour plus de détails"
echo "🧪 Tests disponibles via: python3 test_module.py"

exit 0
