#!/usr/bin/env python3
"""
Script de déploiement automatique sur Railway via l'API GraphQL
Usage: python3 deploy_to_railway.py <RAILWAY_TOKEN>
"""

import sys
import json
import requests
import time

# Configuration
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
GITHUB_REPO = "MASITH-developpement/EZAYNOVA2"
BRANCH = "claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro"
ROOT_DIR = "demo_automation"
SERVICE_NAME = "demo-api"

# Variables d'environnement à configurer
ENV_VARS = {
    "ODOO_URL": "https://ezaynova2-production.up.railway.app",
    "MASTER_PASSWORD": "admin",
    "API_KEY": "u0Pt75t-gCU0Ut2hFBJXeE8AfgTNP9phh8V-B5-MGlo",
    "DB_PATH": "/app/data/demos.db",
    "PORT": "8080"
}


def make_request(token, query, variables=None):
    """Faire une requête à l'API Railway"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(RAILWAY_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"❌ Erreur API: {response.status_code}")
        print(response.text)
        sys.exit(1)

    data = response.json()
    if "errors" in data:
        print(f"❌ Erreur GraphQL: {data['errors']}")
        sys.exit(1)

    return data.get("data", {})


def get_projects(token):
    """Récupérer la liste des projets"""
    query = """
    query {
        projects {
            edges {
                node {
                    id
                    name
                    services {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """

    result = make_request(token, query)
    return result.get("projects", {}).get("edges", [])


def create_service(token, project_id, repo, branch):
    """Créer un nouveau service depuis un repo GitHub"""
    query = """
    mutation ServiceCreate($input: ServiceCreateInput!) {
        serviceCreate(input: $input) {
            id
            name
        }
    }
    """

    variables = {
        "input": {
            "projectId": project_id,
            "name": SERVICE_NAME,
            "source": {
                "repo": repo,
                "branch": branch
            },
            "rootDirectory": ROOT_DIR
        }
    }

    result = make_request(token, query, variables)
    return result.get("serviceCreate", {})


def set_env_variables(token, service_id, env_vars):
    """Configurer les variables d'environnement"""
    query = """
    mutation VariableUpsert($input: VariableUpsertInput!) {
        variableUpsert(input: $input)
    }
    """

    for key, value in env_vars.items():
        print(f"  - Ajout de {key}...")
        variables = {
            "input": {
                "serviceId": service_id,
                "name": key,
                "value": value
            }
        }
        make_request(token, query, variables)


def generate_domain(token, service_id):
    """Générer un domaine public"""
    query = """
    mutation ServiceDomainCreate($input: ServiceDomainCreateInput!) {
        serviceDomainCreate(input: $input) {
            domain
        }
    }
    """

    variables = {
        "input": {
            "serviceId": service_id
        }
    }

    result = make_request(token, query, variables)
    return result.get("serviceDomainCreate", {}).get("domain")


def main():
    print("=" * 70)
    print("🚀 DÉPLOIEMENT AUTOMATIQUE DE L'API DEMO SUR RAILWAY")
    print("=" * 70)
    print()

    # Vérifier le token
    if len(sys.argv) < 2:
        print("Usage: python3 deploy_to_railway.py <RAILWAY_TOKEN>")
        print()
        print("Pour obtenir votre token :")
        print("  1. Allez sur https://railway.app/account/tokens")
        print("  2. Créez un nouveau token")
        print("  3. Copiez-le et utilisez-le avec ce script")
        print()
        sys.exit(1)

    token = sys.argv[1]

    # 1. Trouver le projet
    print("📋 Étape 1/5 : Recherche du projet...")
    projects = get_projects(token)

    project = None
    for p in projects:
        if p["node"]["name"] == "remarkable-comfort":
            project = p["node"]
            print(f"✓ Projet trouvé: {project['name']} (ID: {project['id'][:8]}...)")
            break

    if not project:
        print("❌ Projet 'remarkable-comfort' non trouvé")
        print("Projets disponibles :")
        for p in projects:
            print(f"  - {p['node']['name']}")
        sys.exit(1)

    print()

    # 2. Créer le service
    print("🔨 Étape 2/5 : Création du service...")
    print(f"  Repository: {GITHUB_REPO}")
    print(f"  Branch: {BRANCH}")
    print(f"  Root Directory: {ROOT_DIR}")

    service = create_service(token, project["id"], GITHUB_REPO, BRANCH)
    service_id = service.get("id")

    if not service_id:
        print("❌ Échec de la création du service")
        sys.exit(1)

    print(f"✓ Service créé: {service.get('name')} (ID: {service_id[:8]}...)")
    print()

    # 3. Configurer les variables d'environnement
    print("⚙️  Étape 3/5 : Configuration des variables d'environnement...")
    set_env_variables(token, service_id, ENV_VARS)
    print("✓ Variables configurées")
    print()

    # 4. Générer un domaine
    print("🌐 Étape 4/5 : Génération du domaine public...")
    domain = generate_domain(token, service_id)
    if domain:
        print(f"✓ Domaine généré: https://{domain}")
    else:
        print("⚠️  Domaine non généré (peut être fait manuellement)")
    print()

    # 5. Attendre le déploiement
    print("🚀 Étape 5/5 : Déploiement en cours...")
    print("⏳ Railway construit et déploie le service...")
    print()
    print("=" * 70)
    print("✅ CONFIGURATION TERMINÉE !")
    print("=" * 70)
    print()

    if domain:
        print(f"🌐 URL de l'API: https://{domain}")
        print()
        print("🧪 Pour tester :")
        print(f"  curl https://{domain}/health")
        print()
        print(f"  curl -X POST https://{domain}/api/demo/create \\")
        print(f"    -H 'Content-Type: application/json' \\")
        print(f"    -H 'X-API-Key: {ENV_VARS['API_KEY']}' \\")
        print(f"    -d '{{\"email\": \"test@example.com\", \"name\": \"Test\", \"duration_hours\": 72}}'")
    else:
        print("⚠️  Générez un domaine manuellement dans Railway:")
        print("  Settings → Networking → Generate Domain")

    print()
    print("📊 Surveillez le déploiement sur :")
    print("  https://railway.app/dashboard")
    print()
    print("📖 Documentation complète : demo_automation/DEPLOY_RAILWAY.md")
    print()


if __name__ == "__main__":
    main()
