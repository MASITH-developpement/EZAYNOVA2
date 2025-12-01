# Recommandations d'Optimisation Avancées

## 🎯 Optimisations Performance BDD

### 1. Indexation des Champs
Ajouter dans `models/intervention.py` :

```python
_sql_constraints = [
    ('numero_unique', 'UNIQUE(numero)', 'Le numéro d\'intervention doit être unique.'),
]

def init(self):
    """Créer les index pour optimiser les requêtes"""
    self.env.cr.execute("""
        CREATE INDEX IF NOT EXISTS intervention_date_prevue_idx 
        ON intervention_intervention(date_prevue);
        
        CREATE INDEX IF NOT EXISTS intervention_statut_idx 
        ON intervention_intervention(statut);
        
        CREATE INDEX IF NOT EXISTS intervention_coords_idx 
        ON intervention_intervention(latitude, longitude);
        
        CREATE INDEX IF NOT EXISTS intervention_technicien_idx 
        ON intervention_intervention(technicien_principal_id);
    """)
```

**Gain attendu** : Requêtes 50-70% plus rapides sur grandes volumétries

---

## 🚀 Optimisations Requêtes SQL

### 2. Utiliser `search_read` au lieu de `search` + `read`

**Avant** :
```python
interventions = self.env['intervention.intervention'].search([...])
for interv in interventions:
    print(interv.numero, interv.statut)  # N+1 queries
```

**Après** :
```python
interventions = self.env['intervention.intervention'].search_read(
    domain=[...],
    fields=['numero', 'statut']
)
for interv in interventions:
    print(interv['numero'], interv['statut'])  # 1 seule query
```

**Gain** : Réduction de N+1 queries → 1 seule requête

---

### 3. Utiliser `read_group` pour les agrégations

```python
# Au lieu de calculer manuellement
data = self.env['intervention.intervention'].read_group(
    domain=[('statut', '=', 'termine')],
    fields=['technicien_principal_id', 'duree_reelle:sum'],
    groupby=['technicien_principal_id']
)
```

---

## ⚡ Optimisations Compute Methods

### 4. Ajouter `store=True` quand pertinent

```python
# Évaluer chaque champ computed
lien_waze = fields.Char(
    compute='_compute_lien_waze',
    store=True,  # ✅ Stocker si utilisé dans recherches/filtres
)

distance_km = fields.Float(
    compute='_compute_distance',
    store=True,  # ✅ Évite recalculs répétés
)
```

---

### 5. Optimiser les dépendances `@api.depends`

```python
# ❌ Mauvais : dépendances trop larges
@api.depends('donneur_ordre_id', 'client_final_id', 'facturer_a')
def _compute_something(self):
    pass

# ✅ Bon : dépendances précises
@api.depends('facturer_a', 'donneur_ordre_id.email', 'client_final_id.email')
def _compute_something(self):
    pass
```

---

## 🔄 Optimisations Cache & Mémoïsation

### 6. Utiliser `tools.cache` pour méthodes coûteuses

```python
from odoo.tools import ormcache

class InterventionIntervention(models.Model):
    _name = 'intervention.intervention'
    
    @ormcache('self.id')
    def _get_complex_calculation(self):
        """Cache le résultat par ID"""
        # Calcul complexe ici
        return result
```

---

### 7. Batching des appels API externes

```python
def geocode_addresses_batch(self, addresses):
    """Géocoder plusieurs adresses en une seule requête"""
    # Utiliser l'API batch de Nominatim ou autre provider
    url = "https://nominatim.openstreetmap.org/batch"
    response = requests.post(url, json={'addresses': addresses})
    return response.json()
```

---

## 📊 Optimisations Vues & Interface

### 8. Lazy Loading des onglets

```xml
<!-- Au lieu de charger toutes les données -->
<notebook>
    <page string="Matériaux" name="materials" lazy="true">
        <!-- Contenu chargé uniquement si onglet ouvert -->
        <field name="materiel_ids"/>
    </page>
</notebook>
```

---

### 9. Limiter les champs dans les listes

```xml
<!-- Vue liste optimisée -->
<tree string="Interventions" limit="20" default_order="date_prevue desc">
    <!-- Afficher uniquement les champs essentiels -->
    <field name="numero"/>
    <field name="date_prevue"/>
    <field name="donneur_ordre_id"/>
    <field name="statut"/>
    <!-- Éviter computed fields coûteux -->
</tree>
```

---

## 🧪 Tests Unitaires & Performance

### 10. Ajouter des tests de performance

Créer `tests/test_performance.py` :

```python
from odoo.tests import TransactionCase
import time

class TestInterventionPerformance(TransactionCase):
    
    def test_geocoding_cache(self):
        """Vérifier que le cache fonctionne"""
        intervention = self.env['intervention.intervention'].create({
            'numero': 'TEST001',
            'adresse_intervention': '10 Rue de Rivoli, 75001 Paris, France',
            # ...
        })
        
        # Premier appel (sans cache)
        start = time.time()
        intervention._geocoder_adresse()
        duration_no_cache = time.time() - start
        
        # Deuxième appel (avec cache)
        start = time.time()
        intervention._geocoder_adresse()
        duration_with_cache = time.time() - start
        
        # Le cache doit être 10x plus rapide
        self.assertLess(duration_with_cache, duration_no_cache / 10)
    
    def test_bulk_operations(self):
        """Tester création en masse"""
        start = time.time()
        interventions = self.env['intervention.intervention'].create([
            {'numero': f'TEST{i:04d}', ...} for i in range(100)
        ])
        duration = time.time() - start
        
        # Doit prendre moins de 5 secondes pour 100 enregistrements
        self.assertLess(duration, 5.0)
```

---

## 🔐 Optimisations Sécurité & Permissions

### 11. Utiliser `sudo()` avec parcimonie

```python
# ❌ Mauvais : sudo() trop large
interventions = self.env['intervention.intervention'].sudo().search([])

# ✅ Bon : sudo() ciblé
cache = self.env['intervention.geocoding.cache'].sudo().search([...], limit=1)
```

---

### 12. Record rules optimisées

Dans `security/intervention_record_rules.xml` :

```xml
<!-- Éviter domain_force complexes -->
<record id="intervention_user_rule" model="ir.rule">
    <field name="domain_force">
        [('technicien_principal_id.user_id', '=', user.id)]
    </field>
    <!-- Ajouter index sur technicien_principal_id.user_id -->
</record>
```

---

## 📱 Optimisations Mobile & PWA

### 13. Assets conditionnels

Dans `__manifest__.py` :

```python
'assets': {
    'web.assets_backend': [
        'intervention/static/src/css/intervention_enhanced.css',
    ],
    'web.assets_frontend': [
        # Assets uniquement pour mobile
        'intervention/static/src/css/mobile_optimized.css',
    ],
}
```

---

## 🌐 Optimisations API Externes

### 14. Implémenter rate limiting

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Supprimer appels anciens
            self.calls = [c for c in self.calls if now - c < self.period]
            
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                time.sleep(sleep_time)
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper

# Usage
@RateLimiter(max_calls=1, period=1.0)  # 1 appel/seconde max
def geocode_address(self, address):
    # Appel API
    pass
```

---

## 📈 Monitoring & Logging

### 15. Logger structuré avec contexte

```python
import logging
_logger = logging.getLogger(__name__)

def action_calculer_distance(self):
    context = {
        'intervention_id': self.id,
        'numero': self.numero,
        'adresse': self.adresse_intervention,
    }
    
    _logger.info("Calcul distance démarré", extra={'context': context})
    
    try:
        # Calcul
        _logger.info("Calcul réussi", extra={
            'context': context,
            'distance_km': self.distance_km,
            'duree_min': self.duree_trajet_min,
        })
    except Exception as e:
        _logger.error("Erreur calcul", extra={
            'context': context,
            'error': str(e),
        }, exc_info=True)
```

---

## 🎨 Optimisations CSS/JS

### 16. Minifier les assets

Ajouter dans le pipeline de build :

```bash
# Installer uglify-js et cssnano
npm install -g uglify-js cssnano-cli

# Minifier JS
uglifyjs static/src/js/*.js -o static/src/js/bundle.min.js

# Minifier CSS
cssnano static/src/css/*.css static/src/css/bundle.min.css
```

---

## 📊 Métriques à Surveiller

### KPIs de Performance :
- ⏱️ Temps moyen de chargement page intervention : < 1s
- 🗄️ Nombre de requêtes SQL par action : < 20
- 🌐 Temps d'appel API géocodage : < 500ms (sans cache)
- 💾 Taux de hit du cache : > 80%
- 📊 Temps de génération rapport PDF : < 2s

---

## 🔄 Plan de Mise en Œuvre

### Phase 1 (Critique) - Semaine 1
- [ ] Indexation BDD
- [ ] Optimisation requêtes SQL (search_read)
- [ ] Cache géocodage (déjà fait ✅)

### Phase 2 (Important) - Semaine 2
- [ ] Tests unitaires performance
- [ ] Rate limiting API
- [ ] Lazy loading vues

### Phase 3 (Amélioration) - Semaine 3
- [ ] Monitoring & logging structuré
- [ ] Minification assets
- [ ] Documentation complète

---

**Dernière mise à jour** : 4 novembre 2025
