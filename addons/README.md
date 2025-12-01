# 📦 Modules Odoo Personnalisés

Ce dossier contient vos modules Odoo personnalisés (modules `eazynova*` et autres).

## 🚀 Comment ajouter un module

### 1. Structure d'un module Odoo

```
addons/
├── eazynova_crm/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── votre_model.py
│   ├── views/
│   │   └── votre_vue.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   └── static/
│       └── description/
│           └── icon.png
```

### 2. Exemple de `__manifest__.py`

```python
{
    'name': 'EAZYNOVA CRM Extension',
    'version': '19.0.1.0.0',
    'category': 'CRM',
    'summary': 'Extension personnalisée pour le CRM',
    'description': """
        Module personnalisé EAZYNOVA pour étendre les fonctionnalités du CRM
    """,
    'author': 'EAZYNOVA',
    'website': 'https://eazynova.com',
    'license': 'LGPL-3',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/votre_vue.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### 3. Ajouter votre module

#### Option A : Créer directement dans ce dossier
```bash
cd addons/
mkdir eazynova_mon_module
cd eazynova_mon_module
# Créer vos fichiers ici
```

#### Option B : Cloner depuis un repository Git
```bash
cd addons/
git clone https://github.com/votre-org/eazynova_module.git
```

#### Option C : Copier depuis votre machine locale
```bash
# Sur votre machine
scp -r mon_module/ user@server:/path/to/EZAYNOVA2/addons/
```

### 4. Déployer sur Railway

Une fois vos modules ajoutés dans ce dossier :

```bash
git add addons/
git commit -m "Add: Module eazynova_mon_module"
git push origin claude/setup-odoo-railway-01FfKyFWbhfsz5yffgwXx4ro
```

Railway redéploiera automatiquement avec vos modules.

### 5. Activer le module dans Odoo

1. Connectez-vous à votre instance Odoo
2. Allez dans **Apps** (Applications)
3. Cliquez sur **Update Apps List** (Mettre à jour la liste des applications)
4. Recherchez votre module `eazynova_*`
5. Cliquez sur **Install** (Installer)

## 📋 Modules actuellement installés

- *(Ajoutez ici la liste de vos modules au fur et à mesure)*

## 🔧 Configuration

Le chemin des addons est configuré automatiquement dans `start-odoo.sh` :

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

Tous les modules placés dans ce dossier `addons/` seront copiés vers `/mnt/extra-addons` dans le conteneur Docker et seront disponibles dans Odoo.

## 🐛 Debugging

### Voir les logs du déploiement
Allez sur Railway → Service EZAYNOVA2 → Deployments → View logs

### Vérifier que votre module est chargé
Regardez les logs de démarrage, vous devriez voir :
```
odoo.modules.loading: Modules loaded.
```

### Module non visible dans Odoo
1. Vérifiez que le `__manifest__.py` est correct
2. Vérifiez les permissions des fichiers
3. Mettez à jour la liste des applications dans Odoo

## 📚 Ressources

- [Documentation Odoo 19](https://www.odoo.com/documentation/19.0/)
- [Guide de développement de modules](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Structure d'un module Odoo](https://www.odoo.com/documentation/19.0/developer/tutorials/getting_started.html)

## ⚠️ Important

- Ne commitez **jamais** de données sensibles (mots de passe, clés API, etc.)
- Testez toujours vos modules localement avant de déployer
- Gardez vos modules compatibles avec Odoo 19
- Suivez les bonnes pratiques de développement Odoo
