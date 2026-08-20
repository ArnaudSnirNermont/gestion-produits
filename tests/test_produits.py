import pytest
from app import create_app, db
from app.models import Produit

@pytest.fixture
# Une fixture est une fonction préparatoire que pytest exécute avant chaque test qui la demande en paramètre. Ici, client prépare une app Flask fraîche avec une base SQLite vierge, et fournit un client de test HTTP.
def client():
    app = create_app()
    app.config["TESTING"] = True #Active le mode test de Flask — désactive certains comportements de production (comme la capture d'erreurs qui masquerait la vraie exception) pour faciliter le debug des tests
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" #mise en place de la bdd SQLite en RAM
    with app.app_context():
        db.create_all() #Crée les tables dans la base SQLite en RAM: nécessaire car en mode test on ne passe pas par le flux normal de create_app() avec MariaDB.
    
    # test_client() est un objet spécial fourni par Flask qui simule des requêtes HTTP (client.get(...), client.post(...)) sans lancer de vrai serveur web — tout se passe en mémoire, très rapide. yield (plutôt que return) permet d'exécuter du code de nettoyage après le test (ici, db.drop_all() pour repartir propre au test suivant).
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()

#Chaque fonction test_... :
# Utilise client (la fixture) en paramètre — pytest l'injecte automatiquement
# Fait une requête simulée (client.get, client.post)
# Vérifie le résultat avec assert — si la condition est fausse, pytest marque le test en échec

def test_liste_produits_vide(client):
    response = client.get("/produits")
    assert response.status_code == 200
    assert response.get_json() == []


def test_ajouter_produit(client):
    response = client.post("/ajouter", data={
        "nom": "Clavier",
        "prix": "29.99",
        "stock": "10"
    }, follow_redirects=True)
    assert response.status_code == 200  # redirection après succès


def test_ajouter_produit_sans_nom(client):
    response = client.post("/ajouter", data={
        "nom": "",
        "prix": "10",
        "stock": "5"
    }, follow_redirects=True)
    assert response.status_code == 200  # redirige quand même (vers liste)


def test_produit_bien_enregistre(client):
    client.post("/ajouter", data={
        "nom": "Souris",
        "prix": "15.50",
        "stock": "20"
    },follow_redirects=True)
    response = client.get("/produits")
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["nom"] == "Souris"