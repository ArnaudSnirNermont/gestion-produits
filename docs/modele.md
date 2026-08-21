# Modèle de données

## Diagramme de classe

![Diagramme de classe Produit](../diagrams/diagramme-classe.png)

## Table `produit`

| Colonne | Type | Contraintes |
|---|---|---|
| `id` | Integer | Clé primaire, auto-incrémentée |
| `nom` | String(100) | Non nul |
| `prix` | Float | Non nul |
| `stock` | Integer | Non nul, défaut 0 |