-- =====================================================================
-- FIX WEBSITE REDIRECT - Correction d'accès backend Odoo
-- =====================================================================
-- Ce script corrige le problème de redirection du module website
-- qui empêche l'accès au backend Odoo
-- =====================================================================

-- 1. Afficher les sites web actuels
\echo '📊 Sites web actuels:'
SELECT id, name, domain, is_default_website
FROM website
WHERE active = true;

-- 2. Réinitialiser tous les domaines (vide = accepte tous les domaines)
\echo ''
\echo '🔧 Réinitialisation des domaines...'
UPDATE website
SET domain = ''
WHERE active = true;

-- 3. S'assurer qu'il n'y a qu'un seul site par défaut
\echo ''
\echo '🔧 Configuration du site par défaut...'
UPDATE website
SET is_default_website = false;

UPDATE website
SET is_default_website = true
WHERE id = (SELECT MIN(id) FROM website WHERE active = true);

-- 4. Afficher les sites web après correction
\echo ''
\echo '✅ Sites web après correction:'
SELECT id, name, domain, is_default_website
FROM website
WHERE active = true;

\echo ''
\echo '✅ Correction terminée!'
\echo '🔄 IMPORTANT: Redémarrez le serveur Odoo sur Railway pour appliquer les changements'
