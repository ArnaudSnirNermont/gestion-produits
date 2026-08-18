from flask import Blueprint
#Importe Blueprint, le mécanisme Flask qui permet de regrouper des routes dans un module séparé plutôt que de tout mettre dans __init__.py — c'est ce qui structure une app Flask en modules réutilisables.

main = Blueprint("main", __name__) #Crée le Blueprint nommé "main" — c'est exactement ce nom (main) que app/__init__.py importe (from .routes import main) et enregistre (app.register_blueprint(main)).

@main.route("/")
def index():
    return "App connectée à la base de données. Modèle Produit chargé."
    #Route de test minimale, juste pour vérifier que toute la chaîne fonctionne (Nginx → Flask → Blueprint → réponse), sans encore afficher de vrais produits