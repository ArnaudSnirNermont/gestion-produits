# Cahier de recettes

Ce document formalise les tests manuels réalisés pour valider les fonctionnalités du projet Gestion Produits.

## Légende

- ✅ Succès — comportement conforme à l'attendu
- ❌ Échec — anomalie détectée
- 🔧 Corrigé — anomalie détectée puis résolue

---

## TC-01 — Démarrage de l'infrastructure Docker Compose

**Objectif** : vérifier que les 3 services démarrent correctement.

| | |
|---|---|
| **Préconditions** | Docker Desktop actif, projet cloné |
| **Étapes** | 1. `docker compose up --build`<br>2. `docker compose ps` |
| **Résultat attendu** | Les 3 conteneurs (`db`, `flask`, `nginx`) sont à l'état `Up`, `db` passe à `healthy` |
| **Résultat obtenu** | Conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : conflit entre un fichier `app.py` et un dossier `app/` du même nom, provoquant l'erreur `Failed to find attribute 'create_app' in 'app'`. Gunicorn important le mauvais module.

**Correction** : suppression du doublon fichier/dossier, structure clarifiée en package `app/`.

---

## TC-01bis — Persistance des données après redémarrage des conteneurs

**Objectif** : vérifier que les données MariaDB survivent à un arrêt/redémarrage des conteneurs grâce au volume nommé `db_data`, indépendamment du modèle applicatif Flask.

**Note méthodologique** : ce test utilise une table SQL créée manuellement (`test_persistance`), et non la table `produit`, afin d'isoler la vérification de l'infrastructure Docker de la logique applicative SQLAlchemy — cette dernière étant testée séparément en TC-03.

| | |
|---|---|
| **Préconditions** | TC-01 validé |
| **Étapes** | 1. `docker compose up -d`<br>2. `docker compose exec db mariadb -u flask_user -pflask_pass produits_db -e "CREATE TABLE test_persistance (id INT PRIMARY KEY, valeur VARCHAR(50)); INSERT INTO test_persistance VALUES (1, 'donnee_test');"`<br>3. `docker compose down` (sans `-v`)<br>4. `docker compose up -d`<br>5. `docker compose exec db mariadb -u flask_user -pflask_pass produits_db -e "SELECT * FROM test_persistance;"`<br>6. `docker compose exec db mariadb -u flask_user -pflask_pass produits_db -e "DROP TABLE test_persistance;"` (nettoyage) |
| **Résultat attendu** | La ligne insérée à l'étape 2 est toujours présente après le redémarrage |
| **Résultat obtenu** | Table et donnée bien présentes après redémarrage :<br>`+----+--------------+`<br>`| id | valeur       |`<br>`+----+--------------+`<br>`|  1 | donnee_test  |`<br>`+----+--------------+` |
| **Statut** | ✅ Succès |

**Point de vigilance** : refaire le même test avec `docker compose down -v` (flag `-v`) à la place de l'étape 3 doit, à l'inverse, **supprimer** la donnée — ça valide que c'est bien le volume nommé qui assure la persistance, et non un simple hasard de configuration.

---
## TC-01ter — Prise en compte de la configuration Nginx via bind mount

**Objectif** : vérifier que les modifications apportées à `nginx.conf` sur la machine hôte sont bien répercutées dans le conteneur `nginx` sans reconstruction d'image.

| | |
|---|---|
| **Préconditions** | TC-01 et TC-02 validés |
| **Étapes** | 1. `docker compose up -d`<br>2. Ajout d'une ligne `add_header X-Test-Bind-Mount "ok" always;` dans le bloc `location` de `nginx.conf`<br>3. `docker compose restart nginx`<br>4. `curl.exe -I http://localhost` |
| **Résultat attendu** | Le header `X-Test-Bind-Mount: ok` apparaît dans la réponse, confirmant que le fichier modifié côté hôte est bien lu par le conteneur |
| **Résultat obtenu** | Header présent dans la réponse :<br>`HTTP/1.1 200 OK`<br>`Server: nginx/1.25.4`<br>`X-Test-Bind-Mount: ok` |
| **Statut** | ✅ Succès |

**Point de vigilance** : ce test valide concrètement le comportement du bind mount déclaré dans `docker-compose.yml` (`./nginx.conf:/etc/nginx/conf.d/default.conf`) — contrairement à un volume nommé, un bind mount reflète en temps réel les changements du fichier hôte, sans besoin de rebuild ni de recréation du volume.

**Note technique (PowerShell)** : sous PowerShell, l'alias `curl` pointe vers `Invoke-WebRequest`, dont la syntaxe diffère du vrai `curl` Unix. Utiliser `curl.exe` explicitement pour appeler le véritable exécutable curl (fourni avec Git for Windows).

--- 

## TC-02 — Accessibilité de l'application via Nginx

**Objectif** : vérifier que le reverse proxy transmet correctement les requêtes à Flask.

| | |
|---|---|
| **Préconditions** | TC-01 validé |
| **Étapes** | Ouvrir `http://localhost` dans le navigateur |
| **Résultat attendu** | Réponse de l'application Flask (code 200) |
| **Résultat obtenu** | `502 Bad Gateway` initialement, puis conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : `nginx.conf` absent, provoquant la création automatique d'un dossier vide par Docker au montage du volume (`not a directory`).

**Correction** : création du fichier `nginx.conf` avec configuration `proxy_pass` vers `flask:5000`.

---

## TC-03 — Connexion Flask ↔ MariaDB et création de la table

**Objectif** : vérifier que SQLAlchemy crée bien la table `produit` au démarrage.

| | |
|---|---|
| **Préconditions** | TC-01 validé |
| **Étapes** | 1. `docker compose up --build`<br>2. `docker compose exec db mariadb -u flask_user -pflask_pass produits_db`<br>3. `SHOW TABLES;` |
| **Résultat attendu** | La table `produit` apparaît dans la liste |
| **Résultat obtenu** | `Empty set` initialement, puis conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : le modèle `Produit` n'était importé nulle part dans `app/__init__.py`, empêchant SQLAlchemy d'enregistrer ses métadonnées avant `db.create_all()`. Aucune erreur visible dans les logs — l'application démarrait normalement malgré l'absence de table.

**Correction** : ajout de `from . import models  # noqa: F401` avant l'appel à `db.create_all()`.

---

## TC-04 — Affichage de la liste des produits

**Objectif** : vérifier que la route `GET /produits` retourne les produits enregistrés.

| | |
|---|---|
| **Préconditions** | TC-03 validé, au moins un produit en base |
| **Étapes** | Ouvrir `http://localhost/produits` |
| **Résultat attendu** | Tableau Bootstrap listant les produits, triés par id décroissant |
| **Résultat obtenu** | Conforme |
| **Statut** | ✅ Succès |

---

## TC-05 — Ajout d'un produit valide

**Objectif** : vérifier qu'un produit valide est bien enregistré.

| | |
|---|---|
| **Préconditions** | TC-04 validé |
| **Étapes** | 1. Aller sur `/produits/ajouter`<br>2. Renseigner nom, prix, stock valides<br>3. Soumettre |
| **Résultat attendu** | Redirection vers la liste, message flash de succès, produit visible dans le tableau |
| **Résultat obtenu** | Conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : `RuntimeError: The session is unavailable because no secret key was set` — `flash()` nécessite une `SECRET_KEY` configurée, absente initialement.

**Correction** : ajout de `app.config["SECRET_KEY"]` dans `create_app()`.

---

## TC-06 — Ajout d'un produit sans nom (cas d'erreur)

**Objectif** : vérifier que la validation empêche l'ajout d'un produit sans nom.

| | |
|---|---|
| **Préconditions** | TC-05 validé |
| **Étapes** | 1. Aller sur `/produits/ajouter`<br>2. Laisser le champ nom vide<br>3. Soumettre |
| **Résultat attendu** | Message flash "Le nom est obligatoire.", pas d'enregistrement en base |
| **Résultat obtenu** | `405 Method Not Allowed` initialement, puis conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : redirection vers `main.ajouter` (route acceptant uniquement `POST`) après un `flash()`, provoquant un `405` puisque la redirection s'effectue en `GET`.

**Correction** : redirection vers `main.liste_produits` (route `GET`) en cas d'erreur comme en cas de succès.

---

## TC-07 — Affichage des messages flash sur la liste

**Objectif** : vérifier que les messages de confirmation s'affichent après redirection.

| | |
|---|---|
| **Préconditions** | TC-05 validé |
| **Étapes** | Ajouter un produit valide et observer la page de liste après redirection |
| **Résultat attendu** | Message "Produit « X » ajouté avec succès." affiché en haut de la page |
| **Résultat obtenu** | Message absent initialement, puis conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : le bloc `get_flashed_messages()` n'était présent que dans `formulaire.html`, absent de `liste.html`.

**Correction** : ajout du même bloc Jinja2 dans `liste.html`.

---

## TC-08 — Pipeline CI : lint (flake8)

**Objectif** : vérifier que le job `lint` détecte les non-conformités PEP8.

| | |
|---|---|
| **Préconditions** | Pipeline CI en place (`.github/workflows/ci.yml`) |
| **Étapes** | `git push` sur une branche |
| **Résultat attendu** | Job `lint` passe si le code est conforme, échoue sinon |
| **Résultat obtenu** | Conforme après nettoyage des commentaires pédagogiques trop longs (E501) et des imports non signalés (F401) |
| **Statut** | ✅ Succès |

---

## TC-09 — Pipeline CI : tests (pytest)

**Objectif** : vérifier que le job `test` exécute la suite pytest sur une base SQLite en mémoire.

| | |
|---|---|
| **Préconditions** | Pipeline CI en place, `tests/test_produits.py` présent |
| **Étapes** | `git push` sur une branche |
| **Résultat attendu** | Job `test` passe, aucune dépendance à MariaDB |
| **Résultat obtenu** | Conforme après correction |
| **Statut** | 🔧 Corrigé |

**Anomalie rencontrée** : `ModuleNotFoundError: No module named 'app'` en CI (fonctionnait en local).

**Correction** : ajout d'un `pytest.ini` avec `pythonpath = .` pour fiabiliser la résolution du module `app` indépendamment du contexte d'exécution.

---

## TC-10 — Pipeline CI : build Docker (sur `main` uniquement)

**Objectif** : vérifier que le job `build` ne se déclenche qu'après merge sur `main`.

| | |
|---|---|
| **Préconditions** | TC-08 et TC-09 validés |
| **Étapes** | 1. Push sur une branche `feature/*` → observer `build`<br>2. Merge de la PR vers `main` → observer `build` |
| **Résultat attendu** | `build` skippé sur une branche `feature/*`, exécuté et réussi sur `main` |
| **Résultat obtenu** | Conforme |
| **Statut** | ✅ Succès |

---

## Synthèse

| Test | Statut final |
|---|---|
| TC-01 — Démarrage Docker Compose | ✅ |
| TC-01bis — Persistance du volume db_data | ✅ |
| TC-01ter — Bind mount nginx.conf | ✅ |
| TC-02 — Accès via Nginx | ✅ |
| TC-03 — Connexion MariaDB | ✅ |
| TC-04 — Liste des produits | ✅ |
| TC-05 — Ajout produit valide | ✅ |
| TC-06 — Ajout sans nom | ✅ |
| TC-07 — Messages flash | ✅ |
| TC-08 — CI lint | ✅ |
| TC-09 — CI test | ✅ |
| TC-10 — CI build | ✅ |

**10/10 scénarios validés.** 6 anomalies détectées et corrigées au cours du développement, documentées ci-dessus à titre de traçabilité.