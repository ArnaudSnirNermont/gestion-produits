from . import db  # Importe l'instance db définie dans
# app/__init__.py (le . signifie "depuis le package courant",
# donc depuis app/). C'est ce lien qui permet au modèle
# Produit de "savoir" à quelle base de données il appartient.


class Produit(db.Model):  # Définit la classe Produit en héritant
    # de db.Model — c'est ce qui transforme une classe Python normale
    # en modèle ORM, mappé sur une table SQL
    __tablename__ = "produit"  # Nomme explicitement la table produit
    # en base. Sans cette ligne, SQLAlchemy générerait un nom
    # automatique (souvent en minuscules à partir du nom de classe)
    # — ici on le force pour être explicite et cohérent avec
    # le nom attendu par le cahier des charges

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    # Colonne nom, chaîne de caractères limitée à 100 caractères
    # (VARCHAR(100) en SQL), nullable=False signifiant que ce champ
    # est obligatoire — impossible d'insérer un produit sans nom.
    prix = db.Column(db.Float, nullable=False)
    # Colonne prix, nombre à virgule flottante, également obligatoire.
    stock = db.Column(db.Integer, nullable=False, default=0)
    # Colonne stock, entier, obligatoire, avec une valeur par défaut de 0

    def __repr__(self):
        return f"<Produit {self.nom}>"
    # Méthode spéciale Python qui définit la représentation
    # textuelle d'un objet Produit — utile en debug (dans un
    # shell Python ou dans les logs), cela affichera
    # <Produit Clavier> plutôt qu'une adresse mémoire illisible
    # du type <app.models.Produit object at 0x7f...>
