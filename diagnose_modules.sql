-- Script de diagnostic pour identifier les problèmes de modules et assets

-- 1. État des modules website_booking et sales_funnel
SELECT
    name,
    state,
    latest_version,
    installed_version
FROM ir_module_module
WHERE name IN ('website_booking', 'sales_funnel', 'eazynova_website')
ORDER BY name;

-- 2. Tous les modules bloqués
SELECT
    name,
    state,
    COUNT(*) as count
FROM ir_module_module
WHERE state NOT IN ('installed', 'uninstalled')
GROUP BY name, state
ORDER BY state, name;

-- 3. Assets problématiques
SELECT
    COUNT(*) as total_assets,
    SUM(CASE WHEN name LIKE '%.min.%' THEN 1 ELSE 0 END) as minified_assets,
    SUM(CASE WHEN name LIKE '%assets_%' THEN 1 ELSE 0 END) as generated_assets
FROM ir_attachment;

-- 4. Cron jobs actifs (peuvent bloquer les opérations)
SELECT
    id,
    name,
    active,
    state
FROM ir_cron
WHERE active = true
ORDER BY name;

-- 5. Vérifier les dépendances des modules
SELECT
    m.name as module,
    d.name as depends_on,
    dep_mod.state as dependency_state
FROM ir_module_module m
JOIN ir_module_module_dependency d ON d.module_id = m.id
JOIN ir_module_module dep_mod ON dep_mod.name = d.name
WHERE m.name IN ('website_booking', 'sales_funnel')
ORDER BY m.name, d.name;
