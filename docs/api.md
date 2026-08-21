# Documentation de l'API

## GET /produits

Retourne la liste des produits enregistrés, triés par identifiant décroissant.

**Réponse** (`200 OK`, JSON) :
```json
[
  {"id": 1, "nom": "Clavier", "prix": 29.99, "stock": 10}
]
```

## GET /produits/ajouter

Affiche le formulaire HTML d'ajout d'un produit.

## POST /produits/ajouter

Traite la soumission du formulaire d'ajout.

**Paramètres du formulaire** (`application/x-www-form-urlencoded`) :

| Champ | Type | Obligatoire |
|---|---|---|
| `nom` | texte | Oui |
| `prix` | nombre décimal | Oui |
| `stock` | entier | Oui |

**Comportement** :
- Si `nom` est vide : message flash d'erreur, redirection vers la liste
- Si valide : création du produit, message flash de succès, redirection vers la liste (pattern Post/Redirect/Get)