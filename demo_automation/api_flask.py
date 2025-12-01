#!/usr/bin/env python3
"""
API Flask pour créer automatiquement des démos Odoo
À déployer sur Railway ou autre plateforme
Votre site web appellera cette API pour créer des démos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import xmlrpc.client
import secrets
import string
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Permettre les requêtes depuis votre site web

# Configuration (à définir via variables d'environnement)
ODOO_URL = os.getenv('ODOO_URL', 'https://ezaynova2-production.up.railway.app')
MASTER_PASSWORD = os.getenv('MASTER_PASSWORD', 'VotreMotDePasseSecurise123!')
DB_PATH = os.getenv('DB_PATH', 'demos.db')
API_KEY = os.getenv('API_KEY', 'votre-cle-api-secrete')  # Pour sécuriser l'API

# Base de données SQLite pour tracker les démos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demos (
            db_name TEXT PRIMARY KEY,
            user_email TEXT,
            user_name TEXT,
            user_phone TEXT,
            created_at TEXT,
            expires_at TEXT,
            status TEXT DEFAULT 'active',
            access_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def verify_api_key():
    """Vérifie que la requête contient une clé API valide"""
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return False
    return True

def generate_credentials():
    """Génère des identifiants uniques pour une démo"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(4))
    db_name = f"demo_{timestamp}_{random_suffix}"
    admin_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    return db_name, admin_password

def register_demo(db_name, user_email, user_name, user_phone, created_at, expires_at):
    """Enregistre une nouvelle démo dans la base de données"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO demos (db_name, user_email, user_name, user_phone, created_at, expires_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'active')
    ''', (db_name, user_email, user_name, user_phone, created_at, expires_at))
    conn.commit()
    conn.close()


@app.route('/', methods=['GET'])
def index():
    """Page d'accueil de l'API avec documentation"""
    return jsonify({
        'service': 'Odoo Demo API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'GET /health': 'Health check (no auth required)',
            'POST /api/demo/create': 'Create a new Odoo demo (requires API key)',
            'GET /api/demo/stats': 'Get demo statistics (requires API key)',
            'GET /api/demo/list': 'List all demos (requires API key)'
        },
        'documentation': 'https://github.com/MASITH-developpement/EZAYNOVA2'
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé pour vérifier que l'API fonctionne"""
    return jsonify({'status': 'ok', 'service': 'Odoo Demo API'}), 200


@app.route('/api/demo/create', methods=['POST'])
def create_demo():
    """
    Crée une nouvelle démo Odoo

    Body JSON:
    {
        "email": "utilisateur@example.com",
        "name": "Nom de l'utilisateur",
        "phone": "+33612345678",  // optionnel
        "duration_hours": 72       // optionnel, défaut 72h
    }

    Headers:
    X-API-Key: votre-cle-api-secrete
    """
    # Vérifier la clé API
    if not verify_api_key():
        return jsonify({'error': 'Clé API invalide'}), 401

    # Récupérer les données
    data = request.get_json()
    user_email = data.get('email')
    user_name = data.get('name', 'Demo User')
    user_phone = data.get('phone', '')
    duration_hours = data.get('duration_hours', 72)

    if not user_email:
        return jsonify({'error': 'Email requis'}), 400

    try:
        # Générer les identifiants
        db_name, admin_password = generate_credentials()

        # Créer la base de données via l'API Odoo
        db_manager = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        db_manager.create_database(
            MASTER_PASSWORD,
            db_name,
            True,           # Données de démo
            'fr_FR',        # Langue française
            admin_password
        )

        # Calculer les dates
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=duration_hours)

        # Enregistrer dans la base de données
        register_demo(
            db_name,
            user_email,
            user_name,
            user_phone,
            created_at.isoformat(),
            expires_at.isoformat()
        )

        # Retourner les informations de connexion
        return jsonify({
            'success': True,
            'demo': {
                'url': f"{ODOO_URL}/web?db={db_name}",
                'login': 'admin',
                'password': admin_password,
                'db_name': db_name,
                'expires_at': expires_at.isoformat(),
                'expires_in_hours': duration_hours
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/demo/stats', methods=['GET'])
def get_stats():
    """
    Retourne des statistiques sur les démos

    Headers:
    X-API-Key: votre-cle-api-secrete
    """
    if not verify_api_key():
        return jsonify({'error': 'Clé API invalide'}), 401

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Démos actives
    cursor.execute('SELECT COUNT(*) FROM demos WHERE status = "active"')
    active = cursor.fetchone()[0]

    # Démos expirées
    now = datetime.now().isoformat()
    cursor.execute('''
        SELECT COUNT(*) FROM demos
        WHERE expires_at < ? AND status = "active"
    ''', (now,))
    expired = cursor.fetchone()[0]

    # Total créé
    cursor.execute('SELECT COUNT(*) FROM demos')
    total = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        'active_demos': active,
        'expired_demos': expired,
        'total_created': total,
        'total_deleted': total - active
    }), 200


@app.route('/api/demo/list', methods=['GET'])
def list_demos():
    """
    Liste toutes les démos actives

    Headers:
    X-API-Key: votre-cle-api-secrete
    """
    if not verify_api_key():
        return jsonify({'error': 'Clé API invalide'}), 401

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT db_name, user_email, user_name, created_at, expires_at, status
        FROM demos
        ORDER BY created_at DESC
        LIMIT 100
    ''')
    demos = cursor.fetchall()
    conn.close()

    return jsonify({
        'demos': [
            {
                'db_name': demo[0],
                'user_email': demo[1],
                'user_name': demo[2],
                'created_at': demo[3],
                'expires_at': demo[4],
                'status': demo[5]
            }
            for demo in demos
        ]
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
