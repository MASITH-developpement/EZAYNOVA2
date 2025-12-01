#!/usr/bin/env node
/**
 * Script Node.js pour déployer automatiquement Odoo 19 CE sur Railway
 * Utilisable depuis un site web via une API backend
 *
 * Usage:
 *   node deploy-automation.js --token YOUR_RAILWAY_TOKEN --demo-name "Demo Client"
 *
 * Ou depuis votre code:
 *   const { deployOdooDemo } = require('./deploy-automation');
 *   const result = await deployOdooDemo(apiToken, 'Demo Client');
 */

const axios = require('axios');
const crypto = require('crypto');

const RAILWAY_API = 'https://backboard.railway.app/graphql/v2';
const GITHUB_REPO = 'MASITH-developpement/EZAYNOVA2';
const GITHUB_BRANCH = 'claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro';

/**
 * Générer un mot de passe sécurisé
 */
function generateSecurePassword(length = 24) {
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
  let password = '';
  const randomBytes = crypto.randomBytes(length);
  for (let i = 0; i < length; i++) {
    password += charset[randomBytes[i] % charset.length];
  }
  return password;
}

/**
 * Exécuter une requête GraphQL vers Railway
 */
async function railwayGraphQL(token, query, variables = {}) {
  const response = await axios.post(
    RAILWAY_API,
    { query, variables },
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}

/**
 * Créer un projet Railway
 */
async function createProject(token, projectName) {
  const query = `
    mutation CreateProject($name: String!) {
      projectCreate(input: {name: $name}) {
        id
        name
      }
    }
  `;
  const result = await railwayGraphQL(token, query, { name: projectName });
  const projectId = result.data.projectCreate.id;
  console.log(`✅ Projet créé: ${projectName} (${projectId})`);
  return projectId;
}

/**
 * Créer le service PostgreSQL
 */
async function createPostgresService(token, projectId) {
  const query = `
    mutation CreatePostgres($projectId: String!) {
      databaseCreate(input: {
        projectId: $projectId,
        type: POSTGRES
      }) {
        id
        name
      }
    }
  `;
  const result = await railwayGraphQL(token, query, { projectId });
  const serviceId = result.data.databaseCreate.id;
  console.log(`✅ PostgreSQL créé (${serviceId})`);
  return serviceId;
}

/**
 * Créer le service Odoo
 */
async function createOdooService(token, projectId, postgresServiceId) {
  const adminPassword = generateSecurePassword();

  // Créer le service depuis GitHub
  const createQuery = `
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
  `;

  const result = await railwayGraphQL(token, createQuery, {
    projectId,
    repo: GITHUB_REPO,
    branch: GITHUB_BRANCH
  });

  const serviceId = result.data.serviceCreate.id;

  // Configurer les variables d'environnement
  const variables = {
    DB_HOST: '${{postgres.RAILWAY_PRIVATE_DOMAIN}}',
    DB_PORT: '5432',
    DB_USER: 'postgres',
    DB_PASSWORD: '${{postgres.POSTGRES_PASSWORD}}',
    DB_NAME: 'postgres',
    ADMIN_PASSWORD: adminPassword,
    WORKERS: '2'
  };

  const setVarsQuery = `
    mutation SetVariables($serviceId: String!, $variables: JSON!) {
      variableCollectionUpsert(input: {
        serviceId: $serviceId,
        variables: $variables
      })
    }
  `;

  await railwayGraphQL(token, setVarsQuery, { serviceId, variables });

  console.log(`✅ Service Odoo créé (${serviceId})`);
  console.log(`🔑 Mot de passe admin: ${adminPassword}`);

  return { serviceId, adminPassword };
}

/**
 * Obtenir le domaine public d'un service
 */
async function getServiceDomain(token, serviceId) {
  const query = `
    query GetService($serviceId: String!) {
      service(id: $serviceId) {
        domains {
          domain
        }
      }
    }
  `;
  const result = await railwayGraphQL(token, query, { serviceId });
  const domains = result.data?.service?.domains || [];
  return domains.length > 0 ? domains[0].domain : null;
}

/**
 * Attendre le déploiement et obtenir l'URL
 */
async function waitForDeployment(token, serviceId, maxAttempts = 30) {
  console.log('\n⏳ Attente du déploiement (2-3 minutes)...');

  for (let i = 0; i < maxAttempts; i++) {
    await new Promise(resolve => setTimeout(resolve, 10000)); // 10 secondes

    const domain = await getServiceDomain(token, serviceId);
    if (domain) {
      return domain;
    }

    if ((i + 1) % 6 === 0) {
      console.log(`  ⏳ Toujours en attente... (${i + 1}/${maxAttempts})`);
    }
  }

  return null;
}

/**
 * Déployer une démo Odoo complète
 *
 * @param {string} apiToken - Token API Railway
 * @param {string} demoName - Nom de la démo
 * @returns {Promise<Object>} Informations de déploiement
 */
async function deployOdooDemo(apiToken, demoName = null) {
  if (!demoName) {
    demoName = `Odoo Demo ${Date.now()}`;
  }

  console.log(`\n🚀 Démarrage du déploiement automatique: ${demoName}`);
  console.log('='.repeat(60));

  try {
    // 1. Créer le projet
    const projectId = await createProject(apiToken, demoName);
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 2. Créer PostgreSQL
    const postgresId = await createPostgresService(apiToken, projectId);
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 3. Créer Odoo
    const { serviceId: odooId, adminPassword } = await createOdooService(
      apiToken,
      projectId,
      postgresId
    );
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 4. Attendre le déploiement
    const domain = await waitForDeployment(apiToken, odooId);

    if (domain) {
      console.log('\n✅ Déploiement terminé!');
      console.log('='.repeat(60));
      console.log(`🌐 URL Odoo: https://${domain}`);
      console.log(`👤 Utilisateur: admin`);
      console.log(`🔑 Mot de passe: ${adminPassword}`);
      console.log('='.repeat(60));

      return {
        success: true,
        projectId,
        url: `https://${domain}`,
        adminPassword,
        demoName,
        credentials: {
          username: 'admin',
          password: adminPassword
        }
      };
    } else {
      console.log('⚠️  Le déploiement prend plus de temps. Vérifiez sur Railway.');
      return {
        success: false,
        projectId,
        message: 'Déploiement en cours, vérifiez sur Railway'
      };
    }
  } catch (error) {
    console.error('❌ Erreur:', error.message);
    throw error;
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const tokenIndex = args.indexOf('--token');
  const nameIndex = args.indexOf('--demo-name');

  if (tokenIndex === -1) {
    console.error('Usage: node deploy-automation.js --token YOUR_TOKEN [--demo-name "Name"]');
    process.exit(1);
  }

  const token = args[tokenIndex + 1];
  const demoName = nameIndex !== -1 ? args[nameIndex + 1] : null;

  deployOdooDemo(token, demoName)
    .then(result => {
      console.log('\n📦 Résultat JSON:');
      console.log(JSON.stringify(result, null, 2));
      process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
      console.error('Erreur:', error);
      process.exit(1);
    });
}

// Export pour utilisation dans d'autres modules
module.exports = { deployOdooDemo, generateSecurePassword };
