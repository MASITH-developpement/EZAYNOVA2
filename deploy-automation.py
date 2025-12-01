#!/usr/bin/env python3
"""
Script d'automatisation pour créer automatiquement une démo Odoo 19 CE sur Railway.
Ce script utilise l'API Railway pour créer un projet complet sans intervention manuelle.

Usage:
    python deploy-automation.py --token YOUR_RAILWAY_TOKEN --demo-name "Demo Client"
"""

import os
import sys
import json
import time
import secrets
import argparse
import requests
from typing import Dict, Optional


class RailwayAutoDeploy:
    """Automatisation du déploiement Odoo sur Railway."""

    API_URL = "https://backboard.railway.app/graphql/v2"
    GITHUB_REPO = "MASITH-developpement/EZAYNOVA2"
    GITHUB_BRANCH = "claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro"

    def __init__(self, api_token: str):
        """Initialiser avec le token API Railway."""
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def _graphql_request(self, query: str, variables: Dict = None) -> Dict:
        """Exécuter une requête GraphQL vers l'API Railway."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.API_URL,
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def generate_secure_password(self, length: int = 24) -> str:
        """Générer un mot de passe sécurisé."""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def create_project(self, project_name: str) -> str:
        """Créer un nouveau projet Railway."""
        query = """
        mutation CreateProject($name: String!) {
            projectCreate(input: {name: $name}) {
                id
                name
            }
        }
        """
        variables = {"name": project_name}
        result = self._graphql_request(query, variables)
        project_id = result["data"]["projectCreate"]["id"]
        print(f"✅ Projet créé: {project_name} (ID: {project_id})")
        return project_id

    def create_postgres_service(self, project_id: str) -> Dict:
        """Créer le service PostgreSQL."""
        query = """
        mutation CreatePostgres($projectId: String!) {
            databaseCreate(input: {
                projectId: $projectId,
                type: POSTGRES
            }) {
                id
                name
            }
        }
        """
        variables = {"projectId": project_id}
        result = self._graphql_request(query, variables)
        service_id = result["data"]["databaseCreate"]["id"]
        print(f"✅ PostgreSQL créé (ID: {service_id})")
        return {
            "id": service_id,
            "name": "postgres"
        }

    def create_odoo_service(self, project_id: str, postgres_service_id: str) -> Dict:
        """Créer le service Odoo depuis GitHub."""
        # Générer un mot de passe admin sécurisé
        admin_password = self.generate_secure_password()

        query = """
        mutation CreateService($projectId: String!, $repo: String!, $branch: String!) {
            serviceCreate(input: {
                projectId: $projectId,
                source: {
                    repo: $repo,
                    branch: $branch
                }
            }) {
                id
                name
            }
        }
        """
        variables = {
            "projectId": project_id,
            "repo": self.GITHUB_REPO,
            "branch": self.GITHUB_BRANCH
        }
        result = self._graphql_request(query, variables)
        service_id = result["data"]["serviceCreate"]["id"]

        # Configurer les variables d'environnement
        self._set_environment_variables(service_id, {
            "DB_HOST": f"${{{{postgres.RAILWAY_PRIVATE_DOMAIN}}}}",
            "DB_PORT": "5432",
            "DB_USER": "postgres",
            "DB_PASSWORD": f"${{{{postgres.POSTGRES_PASSWORD}}}}",
            "DB_NAME": "postgres",
            "ADMIN_PASSWORD": admin_password,
            "WORKERS": "2"
        })

        print(f"✅ Service Odoo créé (ID: {service_id})")
        print(f"🔑 Mot de passe admin: {admin_password}")

        return {
            "id": service_id,
            "name": "odoo",
            "admin_password": admin_password
        }

    def _set_environment_variables(self, service_id: str, variables: Dict[str, str]):
        """Définir les variables d'environnement pour un service."""
        query = """
        mutation SetVariables($serviceId: String!, $variables: JSON!) {
            variableCollectionUpsert(input: {
                serviceId: $serviceId,
                variables: $variables
            })
        }
        """
        self._graphql_request(query, {
            "serviceId": service_id,
            "variables": variables
        })
        print(f"  ✓ Variables d'environnement configurées")

    def get_service_domain(self, service_id: str) -> Optional[str]:
        """Obtenir le domaine public d'un service."""
        query = """
        query GetService($serviceId: String!) {
            service(id: $serviceId) {
                domains {
                    domain
                }
            }
        }
        """
        result = self._graphql_request(query, {"serviceId": service_id})
        domains = result["data"]["service"]["domains"]
        return domains[0]["domain"] if domains else None

    def deploy_odoo_demo(self, demo_name: str) -> Dict:
        """
        Déployer une démo Odoo complète automatiquement.

        Returns:
            Dict contenant les informations de déploiement (URL, mot de passe, etc.)
        """
        print(f"\n🚀 Démarrage du déploiement automatique: {demo_name}")
        print("=" * 60)

        # 1. Créer le projet
        project_id = self.create_project(demo_name)
        time.sleep(2)

        # 2. Créer PostgreSQL
        postgres = self.create_postgres_service(project_id)
        time.sleep(5)  # Attendre que PostgreSQL soit provisionné

        # 3. Créer Odoo
        odoo = self.create_odoo_service(project_id, postgres["id"])
        time.sleep(3)

        # 4. Attendre le déploiement et obtenir l'URL
        print("\n⏳ Attente du déploiement (peut prendre 2-3 minutes)...")
        for i in range(30):  # Essayer pendant 5 minutes
            time.sleep(10)
            domain = self.get_service_domain(odoo["id"])
            if domain:
                print(f"\n✅ Déploiement terminé!")
                print("=" * 60)
                print(f"🌐 URL Odoo: https://{domain}")
                print(f"👤 Utilisateur: admin")
                print(f"🔑 Mot de passe: {odoo['admin_password']}")
                print("=" * 60)

                return {
                    "success": True,
                    "project_id": project_id,
                    "url": f"https://{domain}",
                    "admin_password": odoo["admin_password"],
                    "demo_name": demo_name
                }

        print("⚠️  Le déploiement prend plus de temps que prévu. Vérifiez sur Railway.")
        return {
            "success": False,
            "project_id": project_id,
            "message": "Déploiement en cours, vérifiez sur Railway"
        }


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Déploiement automatique d'Odoo 19 CE sur Railway"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Token API Railway (obtenir sur railway.app/account/tokens)"
    )
    parser.add_argument(
        "--demo-name",
        default=f"Odoo Demo {int(time.time())}",
        help="Nom de la démo (par défaut: Odoo Demo + timestamp)"
    )

    args = parser.parse_args()

    try:
        deployer = RailwayAutoDeploy(args.token)
        result = deployer.deploy_odoo_demo(args.demo_name)

        # Retourner le résultat en JSON pour intégration
        print("\n📦 Résultat JSON:")
        print(json.dumps(result, indent=2))

        sys.exit(0 if result["success"] else 1)

    except Exception as e:
        print(f"\n❌ Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
