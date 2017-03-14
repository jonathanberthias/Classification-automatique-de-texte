"""Analyse du texte."""

import os
from collections import Counter


# from traitement import PATH_TO_FILMS


class Compteur:
    """Class pour compter les occurences de chaque mot d'un texte."""

    @staticmethod
    def compter(mots):
        """Compte les occurences de chaque mot.

        :param mots: liste des mots à compter.
        :return: objet collections.Counter, implémentation d'un dictionnaire
                 pour le comptage d'éléments d'un itérable.
        """
        return Counter(mots)
        """
        compte = {}
        for mot in mots:
            compte[mot] = compte.get(mot, 0) + 1
        return compte
        """


class RecuperateurTexte:
    """Classe chargée de récupérer les mots associés à un film."""

    @staticmethod
    def _get_comments(id_film, dossier):
        """Récupère les commentaires d'un film.

        :param id_film: identifiant du film voulu.
        :param dossier: dossier contenant les fichiers à lire.
        """
        try:
            with open(os.path.join(dossier, id_film), 'r') as com:
                return com.read()
        except FileNotFoundError:
            raise ValueError("%s inexistant dans le dossier %s." %
                             (id_film, dossier))

    @staticmethod
    def _get_mots(comment):
        """Retourne la liste des mots d'un commentaire."""
        return comment.split()

    @staticmethod
    def get_mots_film(id_film, dossier):
        """Renvoie les mots des commentaire d'un film dans le dossier."""
        commentaire = RecuperateurTexte._get_comments(id_film, dossier)
        return RecuperateurTexte._get_mots(commentaire)


class StockeurFrequences:
    """Conserve pour chaque film son compte de mots."""

    def __init__(self, dossier):
        """Initialise le stockeur.

        :param dossier: dossier contenant les commentaires de films.
        :occurences: dictionnaire qui associe à un film l'objet
        collections.Counter de ses commentaires.
        :total: stocke le compte parmi tous les textes
        """
        self.dossier = dossier
        self.occurences = {}
        self.total = Counter()

    def ajouter_film(self, film_id):
        """Ajoute un film et son compte de mots dans la base.

        Erreur si le film a déjà été compté.
        """
        if film_id in self.occurences:
            raise ValueError("Film %s a déjà été compté." % film_id)
        mots = RecuperateurTexte.get_mots_film(film_id, self.dossier)
        compte = Compteur.compter(mots)
        self.occurences[film_id] = compte
        self.total += compte

    def get_compte_film(self, film_id):
        """Renvoie l'objet Counter associé à un film."""
        if film_id in self.occurences:
            return self.occurences[film_id]
        raise ValueError("Film %s pas compté." % film_id)

    def compte_total(self):
        """Renvoie les occurences dans la totalité des textes du dossier."""
        return self.total
        for compte in self.occurences.values():
            # Opération '+' sur les Counter ajoute les occurences
            self.total += compte
        return self.total
