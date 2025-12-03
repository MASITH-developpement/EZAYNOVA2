-- Script SQL pour débloquer Odoo
-- Exécuter avec : psql -U postgres -d <database_name> -f fix_odoo_locks.sql

-- 1. Afficher les modules bloqués
SELECT name, state, latest_version
FROM ir_module_module
WHERE state IN ('to install', 'to upgrade', 'to remove')
ORDER BY name;

-- 2. Réinitialiser l'état des modules bloqués (DÉCOMMENTER SI NÉCESSAIRE)
-- UPDATE ir_module_module
-- SET state = 'uninstalled'
-- WHERE name IN ('website_booking', 'sales_funnel')
-- AND state IN ('to install', 'to upgrade');

-- 3. Afficher les verrous actifs
SELECT
    pg_class.relname AS table_name,
    pg_locks.mode,
    pg_locks.granted,
    pg_stat_activity.pid,
    pg_stat_activity.state,
    pg_stat_activity.query
FROM pg_locks
JOIN pg_class ON pg_locks.relation = pg_class.oid
LEFT JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
WHERE pg_class.relname LIKE 'ir_module%'
ORDER BY pg_class.relname;

-- 4. Tuer les processus bloqués (DÉCOMMENTER ET REMPLACER <PID> SI NÉCESSAIRE)
-- SELECT pg_terminate_backend(<PID>);

-- 5. Vérifier les cron jobs en erreur
SELECT name, active, nextcall, numbercall, priority
FROM ir_cron
WHERE active = true
ORDER BY nextcall DESC
LIMIT 10;
