from flask import Blueprint, jsonify
#Importe Blueprint, le mécanisme Flask qui permet de regrouper des routes dans un module séparé plutôt que de tout mettre dans __init__.py — c'est ce qui structure une app Flask en modules réutilisables.

from .models import Produit
#Importe la classe Produit définie dans app/models.py. Le . signifie "depuis le package courant" (app/). C'est cet import qui permet d'utiliser Produit.query juste en dessous — et au passage, il a le même effet bénéfique que celui qu'on a ajouté dans __init__.py : il force l'enregistrement du modèle dans les métadonnées SQLAlchemy (donc techniquement, avec cette ligne présente, l'import explicite dans __init__.py devient redondant mais reste une sécurité utile si routes.py change un jour).

main = Blueprint("main", __name__) #Crée le Blueprint nommé "main" — c'est exactement ce nom (main) que app/__init__.py importe (from .routes import main) et enregistre (app.register_blueprint(main)).

@main.route("/produits")
#Décorateur qui associe l'URL / à la fonction juste en dessous. Chaque requête HTTP GET vers http://localhost/ va déclencher l'exécution de cette fonction.
def liste():
    #Nom de la fonction — Flask s'en sert en interne pour générer les URLs (via url_for('main.liste') en cas de besoin ailleurs, par exemple dans un template pour un lien de retour à l'accueil).
    produits = Produit.query.order_by(Produit.id.desc()).all()
    #Trois opérations enchaînées :
    # Produit.query : point d'entrée SQLAlchemy pour interroger la table produit
    #.order_by(Produit.id.desc()) : trie les résultats par id décroissant — donc les produits les plus récemment ajoutés apparaissent en premier
    #.all() : exécute la requête SQL (un SELECT * FROM produit ORDER BY id DESC) et renvoie tous les résultats sous forme de liste d'objets Produit
    resultat = [
        {"id": p.id, "nom": p.nom, "prix": p.prix, "stock": p.stock}
        for p in produits
    ]
    return jsonify(resultat)
    #jsonify convertit directement la liste de dictionnaires Python construite par compréhension en réponse JSON avec le bon Content-Type: application/json