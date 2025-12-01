# Eazynova Prix

Ce module Odoo ajoute un champ "Prix moyen externe" sur les articles, récupéré automatiquement depuis Datab (API) ou Hemea (scraping web) à chaque affichage de fiche produit.

## Fonctionnalités principales

-   Affichage du prix moyen externe à côté du prix de vente sur la fiche article.
-   Récupération automatique :
    -   **API Datab** (si clé API renseignée dans Odoo)
    -   **Scraping Hemea** (fallback si pas de clé API Datab)
-   Aucun stockage local massif : interrogation à la volée.
-   Compatible Odoo 16+ (Community/Enterprise)

## Installation

1. **Dépendances Python** (à installer dans l’environnement Odoo) :

    ```bash
    pip install beautifulsoup4 requests
    ```

2. **Clé API Datab (optionnel mais recommandé)** :
    - Renseignez la clé dans Odoo : menu Paramètres > Paramètres système > Ajoutez la clé `eazynova_prix.datab_api_key` avec la valeur de votre clé API Datab.
    - Si aucune clé n’est renseignée, le module utilisera automatiquement le scraping Hemea (moins fiable, plus lent).

## Configuration

-   **Datab** : nécessite un contrat et une clé API ([documentation Datab](https://api.datab.io/docs))
-   **Hemea** : aucune configuration, mais scraping toléré uniquement en faible volume.

## Limites & recommandations

-   Le scraping Hemea dépend de la structure HTML du site : si le site change, l’extraction peut cesser de fonctionner.
-   Respectez les CGU des sources.
-   Pour usage professionnel, privilégiez Datab avec API.

## Exemple d’utilisation

-   Ouvrez une fiche article : le champ "Prix moyen externe" s’affiche automatiquement.
-   Le prix est mis à jour à chaque affichage (pas de cache local).

## Support

Pour toute question ou évolution : contact@eazynova.com

---

Module développé par Eazynova. Licence AGPL-3.
