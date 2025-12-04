-- Script SQL pour nettoyer les assets corrompus
-- À exécuter dans la console PostgreSQL de Railway

-- Supprimer tous les assets minifiés
DELETE FROM ir_attachment WHERE name LIKE '%.min.js%' OR name LIKE '%.min.css%';

-- Supprimer tous les assets web générés
DELETE FROM ir_attachment WHERE name LIKE '%assets_%';

-- Supprimer les attachments liés au website builder
DELETE FROM ir_attachment WHERE name LIKE '%website%builder%';

-- Nettoyer la base
VACUUM ANALYZE ir_attachment;

-- Vérifier le résultat
SELECT COUNT(*) as "Assets minifiés restants" FROM ir_attachment WHERE name LIKE '%.min.%';
