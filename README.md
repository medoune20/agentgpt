# Application de gestion de stock

Cette application Python permet de gérer un stock de produits depuis une interface en ligne de commande.

## Fonctionnalités

- Ajout de produits (SKU, nom, quantité, seuil minimum, prix unitaire)
- Mise à jour des quantités en stock
- Modification des informations d'un produit
- Suppression d'un produit
- Affichage des produits
- Détection des produits en stock faible
- Calcul de la valeur totale du stock
- Persistance automatique dans `inventory.json`

## Prérequis

- Python 3.10+
- `pytest` pour exécuter les tests

## Lancer l'application

```bash
python stock_app.py
```

## Exécuter les tests

```bash
pytest -q
```
