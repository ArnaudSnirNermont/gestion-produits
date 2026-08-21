# Gestion Produits

Application web de gestion de produits développée en Flask, conteneurisée avec Docker Compose (Nginx + Gunicorn + MariaDB).

Ce projet a été réalisé dans le cadre du BTS CIEL, comme support pédagogique pour l'épreuve E6.

## Stack technique

- **Backend** : Flask, SQLAlchemy
- **Base de données** : MariaDB
- **Serveur d'application** : Gunicorn
- **Reverse proxy** : Nginx
- **Orchestration** : Docker Compose
- **CI/CD** : GitHub Actions (lint, tests, build)

## Démarrage rapide

```bash
git clone https://github.com/ArnaudSnirNermont/gestion-produits.git
cd gestion-produits
docker compose up --build
```

L'application est accessible sur [http://localhost](http://localhost).