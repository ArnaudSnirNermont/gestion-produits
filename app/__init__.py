#Importe la classe Flask (pour créer l'application), SQLAlchemy (l'ORM qui va gérer la communication avec MariaDB), et le module os (pour lire les variables d'environnement, comme DATABASE_URL définie dans ton docker-compose.yml)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


db = SQLAlchemy() #Crée l'instance SQLAlchemy au niveau du module, donc en dehors de create_app(). Volontaire et important dans le pattern application factory : ça permet à models.py d'importer ce db (from . import db) sans dépendre d'une instance Flask déjà créée — on découple la définition des modèles de la création de l'app.

def create_app():
    app = Flask(__name__) #Fonction factory (celle que Gunicorn appelle via app:create_app() dans le Dockerfile). Crée l'instance Flask proprement dite
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://flask_user:flask_pass@db/produits_db"
    ) #Configure l'URL de connexion à la base. os.environ.get("DATABASE_URL", "...") lit la variable d'environnement DATABASE_URL (celle définie dans docker-compose.yml pour le service flask), avec une valeur de secours si elle n'existe pas — utile en cas de tests en dehors de Docker
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #Désactive un système de tracking de SQLAlchemy qui consomme de la mémoire inutilement (config recommandée par défaut)
    
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-a-changer") #obligé pour utiliser flash

    db.init_app(app) #Lie l'instance db créée plus haut à cette application Flask précise. C'est l'étape qui connecte réellement l'ORM à l'app — nécessaire car db = SQLAlchemy() seul ne fait encore rien tant qu'il n'est pas associé à une app via init_app.

    from .routes import main
    app.register_blueprint(main)  #Importe le Blueprint main depuis app/routes.py et l'enregistre sur l'application. Attention : le fichier routes.py doit exister
    
    from . import models #force l'enregistrement du modèle Produit
    

    with app.app_context():
        db.create_all()   # db.create_all() crée physiquement les tables en base (si elles n'existent pas déjà) à partir des modèles définis (ici, Produit). Le with app.app_context() est nécessaire car SQLAlchemy a besoin du contexte applicatif Flask pour savoir à quelle app/config se référer. Dans un vrai projet on utiliserait des migrations (Alembic/Flask-Migrate) pour gérer les évolutions de schéma proprement. 
        
    return app #Renvoie l'instance Flask configurée — c'est ce que Gunicorn récupère et utilise pour servir les requêtes
