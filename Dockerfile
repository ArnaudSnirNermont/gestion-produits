FROM python:3.11-slim 
#Image de base : Python 3.11 pré-installé, sur une variante slim — une Debian allégée (sans les outils de compilation, documentation, etc. de l'image standard). Compromis entre poids réduit et compatibilité (contrairement à alpine, slim reste basé sur glibc, ce qui évite des soucis de compatibilité avec certaines libs Python compilées).

WORKDIR /app
#Définit /app comme répertoire de travail à l'intérieur du conteneur. Toutes les commandes suivantes (COPY, RUN, CMD) s'exécutent depuis ce dossier — équivalent d'un cd /app qui reste actif pour le reste du fichier, et qui crée le dossier s'il n'existe pas.

# Dépendances système pour PyMySQL
# Installe des dépendances système (pas Python) nécessaires à la compilation de certains packages :
#default-libmysqlclient-dev : fichiers d'en-tête C pour compiler des drivers MySQL/MariaDB natifs
#gcc : compilateur C, nécessaire si un package Python (ou une de ses dépendances) doit être compilé depuis les sources plutôt qu'installé en binaire précompilé
#rm -rf /var/lib/apt/lists/* : supprime le cache des listes de paquets APT après installation, pour ne pas alourdir l'image finale inutilement

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

#Copie uniquement le fichier requirements.txt depuis le dossier projet vers /app dans le conteneur
COPY requirements.txt .
#Installe les dépendances Python listées dans requirements.txt (Flask, SQLAlchemy, PyMySQL, Gunicorn, etc.). --no-cache-dir évite que pip garde en cache les paquets téléchargés, ce qui réduit la taille de l'image
RUN pip install --no-cache-dir -r requirements.txt

#Copie maintenant tout le reste du contenu du dossier projet (le code source Flask, les templates, etc.) vers /app dans le conteneur. À ce stade, l'image contient le code applicatif complet.
#Il est préférable d'installer d'abord les dépendances (moins volatiles que le code). Si on fait COPY . . en premier, la moindre modification de code invaliderait le cache et forcerait à réinstaller toutes les dépendances à chaque build — beaucoup plus lent en développement itératif.
COPY . .

#Le conteneur écoute sur le port 5000. C'est purement informatif — ça ne publie ni n'ouvre réellement le port (c'est le rôle de expose:/ports: dans docker-compose.yml). C'est une convention de bonne pratique qui indique clairement, en lisant le Dockerfile, quel port l'application utilise.
EXPOSE 5000

#Commande exécutée au démarrage du conteneur, en syntaxe "exec form" (tableau JSON, recommandée plutôt que la syntaxe shell) :
#gunicorn : serveur WSGI de production — remplace le serveur de développement Flask (flask run), qui n'est pas fait pour tenir en charge
#--bind 0.0.0.0:5000 : écoute sur toutes les interfaces réseau du conteneur (0.0.0.0, pas juste localhost), port 5000 — indispensable pour que le trafic venant d'autres conteneurs (nginx) puisse l'atteindre
#--workers 2 : lance 2 processus travailleurs pour gérer les requêtes en parallèle
#app:create_app() : indique à Gunicorn où trouver l'application. Le format est module:variable_ou_fonction. Ici, app est le module (fichier app.py ou package app/), et create_app() est appelé pour obtenir l'instance Flask — c'est le pattern application factory, courant dans les projets Flask structurés en Blueprints comme le tien.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:create_app()"]