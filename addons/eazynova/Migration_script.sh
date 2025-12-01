#!/bin/bash

###############################################################################
# SCRIPT DE MIGRATION EAZYNOVA
# Restructure l'ancien module eazynova_chantier en architecture modulaire
###############################################################################

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   MIGRATION EAZYNOVA - Architecture Modulaire${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Chemins
OLD_MODULE="addons/addons-perso/eazynova_chantier"
NEW_BASE="addons/addons-perso"
BACKUP_DIR="eazynova_backup_$(date +%Y%m%d_%H%M%S)"

# Vérification existence ancien module
if [ ! -d "$OLD_MODULE" ]; then
    echo -e "${RED}✗ Erreur: Module $OLD_MODULE introuvable${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/6] Création d'une sauvegarde...${NC}"
cp -r "$OLD_MODULE" "$BACKUP_DIR"
echo -e "${GREEN}✓ Sauvegarde créée: $BACKUP_DIR${NC}"
echo ""

echo -e "${YELLOW}[2/6] Création de la structure modulaire...${NC}"

# Création des répertoires pour chaque module
modules=(
    "eazynova"
    "eazynova_chantier"
    "eazynova_compta"
    "eazynova_planning"
    "eazynova_facture_client"
    "eazynova_facture_fournisseur"
    "eazynova_intervention"
    "eazynova_achat"
    "eazynova_stock"
)

for module in "${modules[@]}"; do
    module_path="$NEW_BASE/$module"
    
    # Création de la structure de base
    mkdir -p "$module_path"/{models,views,wizard,security,data,report,static/{src/{css,js,xml},description},test,i18n}
    
    # Création des fichiers __init__.py
    touch "$module_path/__init__.py"
    touch "$module_path/models/__init__.py"
    touch "$module_path/wizard/__init__.py"
    touch "$module_path/controllers/__init__.py"
    touch "$module_path/test/__init__.py"
    
    echo -e "  ${GREEN}✓${NC} Module $module créé"
done

echo ""
echo -e "${YELLOW}[3/6] Migration du module CORE (eazynova)...${NC}"

# Fichiers à migrer vers CORE
core_files=(
    "models/res_config_settings.py"
    "models/res_users.py:models/eazynova_user_facial.py"
    "models/res_company.py:models/eazynova_company.py"
    "wizard/ai_assistant_wizard.py"
    "wizard/document_ocr_wizard.py"
    "wizard/facial_registration_wizard.py"
    "security/eazynova_security.xml"
    "data/eazynova_data.xml"
    "views/eazynova_dashboard_views.xml"
    "views/res_config_settings_views.xml"
    "views/res_company_views.xml"
    "views/res_users_views.xml"
    "views/eazynova_menu.xml"
    "static/*"
)

for file in "${core_files[@]}"; do
    if [[ "$file" == *":"* ]]; then
        # Fichier avec renommage
        src="${file%%:*}"
        dst="${file##*:}"
        if [ -f "$OLD_MODULE/$src" ]; then
            cp "$OLD_MODULE/$src" "$NEW_BASE/eazynova/$dst"
            echo -e "  ${GREEN}✓${NC} Migré: $src → $dst"
        fi
    else
        # Fichier sans renommage
        if [ -e "$OLD_MODULE/$file" ]; then
            cp -r "$OLD_MODULE/$file" "$NEW_BASE/eazynova/$file"
            echo -e "  ${GREEN}✓${NC} Migré: $file"
        fi
    fi
done

echo ""
echo -e "${YELLOW}[4/6] Création du module CHANTIER...${NC}"

# Le module CHANTIER est nouveau - on le crée from scratch
cat > "$NEW_BASE/eazynova_chantier/__manifest__.py" << 'EOF'
# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - Gestion de Chantiers',
    'version': '19.0.1.0.0',
    'category': 'Construction',
    'summary': 'Gestion complète des chantiers de construction',
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': ['eazynova', 'project'],
    'data': [
        'security/chantier_security.xml',
        'security/ir.model.access.csv',
        'data/chantier_data.xml',
        'data/chantier_sequence.xml',
        'views/eazynova_chantier_views.xml',
        'views/eazynova_chantier_phase_views.xml',
        'views/eazynova_chantier_tache_views.xml',
        'views/eazynova_chantier_equipe_views.xml',
        'views/chantier_menu.xml',
        'report/chantier_report_views.xml',
        'report/chantier_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF

echo -e "${GREEN}✓ Module CHANTIER créé${NC}"
echo ""

echo -e "${YELLOW}[5/6] Création des manifests des autres modules...${NC}"

# Fonction pour créer un manifest
create_manifest() {
    local module=$1
    local name=$2
    local category=$3
    local summary=$4
    local depends=$5
    
    cat > "$NEW_BASE/$module/__manifest__.py" << EOF
# -*- coding: utf-8 -*-
{
    'name': 'EAZYNOVA - $name',
    'version': '19.0.1.0.0',
    'category': '$category',
    'summary': '$summary',
    'author': 'EAZYNOVA',
    'website': 'https://eazynova-production.up.railway.app/',
    'license': 'LGPL-3',
    'depends': [$depends],
    'data': [
        'security/${module}_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF
    
    echo -e "  ${GREEN}✓${NC} Manifest créé pour $module"
}

# Création des manifests
create_manifest "eazynova_compta" "Comptabilité Analytique" "Accounting" "Comptabilité analytique par chantier" "'eazynova', 'eazynova_chantier', 'account', 'analytic'"
create_manifest "eazynova_planning" "Planning & Ressources" "Services" "Planification et gestion des ressources" "'eazynova', 'eazynova_chantier', 'resource'"
create_manifest "eazynova_facture_client" "Facturation Clients" "Accounting" "Facturation clients avancée" "'eazynova', 'eazynova_chantier', 'account'"
create_manifest "eazynova_facture_fournisseur" "Facturation Fournisseurs" "Accounting" "Gestion factures fournisseurs" "'eazynova', 'eazynova_chantier', 'account', 'purchase'"
create_manifest "eazynova_intervention" "Gestion Interventions" "Services" "Gestion des interventions terrain" "'eazynova', 'eazynova_chantier', 'project'"
create_manifest "eazynova_achat" "Analyse Achats" "Purchases" "Analyse et optimisation des achats" "'eazynova', 'eazynova_chantier', 'purchase', 'stock'"
create_manifest "eazynova_stock" "Gestion Stock" "Inventory" "Gestion de stock par chantier" "'eazynova', 'eazynova_chantier', 'stock'"

echo ""
echo -e "${YELLOW}[6/6] Nettoyage et finalisation...${NC}"

# Création d'un README dans chaque module
for module in "${modules[@]}"; do
    cat > "$NEW_BASE/$module/README.md" << EOF
# $module

Module EAZYNOVA - Voir documentation principale dans \`ARCHITECTURE.md\`

## Installation

\`\`\`bash
# Installer d'abord le module CORE
python odoo-bin -d database -i eazynova

# Puis installer ce module
python odoo-bin -d database -i $module
\`\`\`

## Configuration

Voir \`ARCHITECTURE.md\` pour la configuration complète.
EOF
done

echo -e "${GREEN}✓ Nettoyage terminé${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ MIGRATION TERMINÉE AVEC SUCCÈS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo -e "  1. Vérifier les fichiers migrés"
echo -e "  2. Mettre à jour la liste des modules Odoo"
echo -e "  3. Installer le module CORE: ${BLUE}eazynova${NC}"
echo -e "  4. Installer les modules métier souhaités"
echo ""
echo -e "${YELLOW}Sauvegarde disponible:${NC} $BACKUP_DIR"
echo ""