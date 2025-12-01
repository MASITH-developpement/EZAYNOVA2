# Guide de Personnalisation des Couleurs - Module Intervention

## 📌 Vue d'ensemble

Le module intervention utilise désormais un système de **variables CSS dynamiques** qui permettent de changer facilement toutes les couleurs depuis un seul endroit.

## 🎨 Variables de couleurs disponibles

Les couleurs sont définies au début du fichier CSS (`static/src/css/intervention_enhanced.css`) :

```css
:root {
    /* Couleurs principales */
    --intervention-primary: #0277bd;        /* Couleur principale du module */
    --intervention-primary-light: #29b6f6;  /* Variante claire */
    --intervention-primary-dark: #01579b;   /* Variante foncée */
    --intervention-secondary: #4caf50;      /* Couleur secondaire */
    --intervention-accent: #ff9800;         /* Couleur d'accent */

    /* Couleurs de fond */
    --intervention-bg-light: #f8fcff;       /* Fond très clair */
    --intervention-bg-medium: #e3f2fd;      /* Fond moyen */
    --intervention-bg-dark: #bbdefb;        /* Fond plus foncé */

    /* Couleurs de statut */
    --intervention-success: #4caf50;        /* Succès/validation */
    --intervention-warning: #ff9800;        /* Attention */
    --intervention-danger: #f44336;         /* Erreur */
    --intervention-info: #2196f3;          /* Information */
}
```

## 🔧 Comment personnaliser les couleurs

### Méthode 1 : Modifier directement le fichier CSS

1. Ouvrez le fichier : `/opt/odoo/odoo18/odoo/addons-perso/intervention/static/src/css/intervention_enhanced.css`

2. Modifiez les variables dans la section `:root` (lignes 3-25)

3. Redémarrez Odoo :
   ```bash
   sudo systemctl restart odoo18
   ```

4. Actualisez votre navigateur (Ctrl+F5 pour forcer le rechargement du CSS)

### Méthode 2 : Via les paramètres Odoo (future fonctionnalité)

*À implémenter : Un menu de configuration dans Odoo permettra de choisir les couleurs via une interface graphique*

## 🎨 Palettes de couleurs prêtes à l'emploi

### 1. **Bleu Professionnel** (Par défaut - Actuel)
```css
--intervention-primary: #0277bd;
--intervention-primary-light: #29b6f6;
--intervention-primary-dark: #01579b;
--intervention-secondary: #4caf50;
--intervention-accent: #ff9800;
```

### 2. **Vert Énergie**
```css
--intervention-primary: #2e7d32;
--intervention-primary-light: #66bb6a;
--intervention-primary-dark: #1b5e20;
--intervention-secondary: #8bc34a;
--intervention-accent: #ff9800;
```

### 3. **Rouge Dynamique**
```css
--intervention-primary: #d32f2f;
--intervention-primary-light: #ef5350;
--intervention-primary-dark: #c62828;
--intervention-secondary: #ff5722;
--intervention-accent: #ffc107;
```

### 4. **Violet Moderne**
```css
--intervention-primary: #7b1fa2;
--intervention-primary-light: #9c27b0;
--intervention-primary-dark: #6a1b9a;
--intervention-secondary: #ab47bc;
--intervention-accent: #ff9800;
```

### 5. **Orange Plomberie**
```css
--intervention-primary: #f57c00;
--intervention-primary-light: #ff9800;
--intervention-primary-dark: #e65100;
--intervention-secondary: #ff5722;
--intervention-accent: #4caf50;
```

### 6. **Gris Élégant**
```css
--intervention-primary: #546e7a;
--intervention-primary-light: #78909c;
--intervention-primary-dark: #455a64;
--intervention-secondary: #90a4ae;
--intervention-accent: #ff9800;
```

## 📍 Éléments affectés par les variables

### `--intervention-primary` (Couleur principale)
- Boutons d'action principaux
- En-têtes de tableaux
- Onglets actifs
- Bordures actives des champs
- Barre de navigation

### `--intervention-secondary` (Couleur secondaire)
- Éléments d'accent
- Badges de statut
- Indicateurs visuels

### `--intervention-success` (Succès)
- Statut "Terminé"
- Messages de validation
- Indicateurs de succès

### `--intervention-bg-light` et `--intervention-bg-medium` (Fonds)
- Arrière-plans des groupes
- Hover des lignes de tableau
- Zones de surbrillance

## 🚀 Bonnes pratiques

1. **Contraste** : Assurez-vous que vos couleurs ont un bon contraste pour la lisibilité
   - Texte foncé sur fond clair
   - Texte clair sur fond foncé

2. **Cohérence** : Utilisez des couleurs de la même famille pour `primary`, `primary-light` et `primary-dark`

3. **Accessibilité** : Testez avec des outils comme le [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)

4. **Sauvegarde** : Avant de modifier, faites une copie du fichier CSS

## 🔄 Réinitialiser aux couleurs par défaut

Si vous souhaitez revenir aux couleurs d'origine, utilisez la palette "Bleu Professionnel" ci-dessus.

## 📝 Notes importantes

- Les modifications CSS nécessitent un redémarrage d'Odoo
- Les navigateurs peuvent mettre en cache le CSS : utilisez Ctrl+F5 pour forcer le rechargement
- Les couleurs s'appliquent à tout le module intervention
- Compatible avec le mode responsive et mobile

## 🛠️ Dépannage

**Les couleurs ne changent pas ?**
1. Vérifiez que vous avez bien modifié le bon fichier
2. Redémarrez Odoo : `sudo systemctl restart odoo18`
3. Videz le cache du navigateur (Ctrl+Shift+Delete)
4. Actualisez avec Ctrl+F5

**Les couleurs sont cassées ?**
1. Vérifiez la syntaxe CSS (pas de point-virgule manquant)
2. Utilisez des codes couleur hexadécimaux valides (#RRGGBB)
3. Restaurez le fichier depuis la sauvegarde

## 💡 Astuces

- Utilisez un outil comme [Adobe Color](https://color.adobe.com/) pour créer des palettes harmonieuses
- Testez sur différents écrans (ordinateur, tablette, mobile)
- Demandez l'avis des utilisateurs avant de déployer en production

---

**Version** : 1.0  
**Date** : 4 novembre 2025  
**Module** : Intervention - Odoo 18 CE
