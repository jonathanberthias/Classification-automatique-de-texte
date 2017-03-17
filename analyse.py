"""Analyse du texte."""

import math
import os
from collections import Counter


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


class RecuperateurTexte:
    """Classe chargée de récupérer les mots associés à un film."""

    @staticmethod
    def _get_comments(id_film, dossier):
        """Récupère les commentaires d'un film.

        :param id_film: identifiant du film voulu.
        :param dossier: dossier contenant les fichiers à lire.
        """
        try:
            with open(os.path.join(dossier, id_film), encoding='utf8') as com:
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
        for film in os.listdir(self.dossier):
            self._ajouter_film(film)

    def _ajouter_film(self, film_id):
        """Ajoute un film et son compte de mots dans la base.

        Erreur si le film a déjà été compté.
        """
        if film_id in self.occurences:
            raise ValueError("Film %s a déjà été compté." % film_id)
        mots = RecuperateurTexte.get_mots_film(film_id, self.dossier)
        compte = Compteur.compter(mots)
        self.occurences[film_id] = compte
        # update ajoute le compte au total (sans créer de nouveau Counter)
        self.total.update(compte)

    def get_compte_film(self, film_id):
        """Renvoie l'objet Counter associé à un film."""
        if film_id in self.occurences:
            return self.occurences[film_id]
        raise ValueError("Film %s pas compté." % film_id)

    def compte_total(self):
        """Renvoie les occurences dans la totalité des textes du dossier."""
        return self.total


class Calculateur_indices:
    """Calcule l'indice TF-IDF des mots."""

    def __init__(self):
        pass

    @staticmethod
    def indice_tf(mot, occurences_texte):
        """Renvoie l'indice TF d'un mot dans un texte.

        Forme simple: fréquence brute.

        :param mot: mot dont on cherche la fréquence.
        :param occurences_texte: 'Counter' des occurences de chaque mot du 
                                 texte.
        """
        try:
            return occurences_texte[mot]
        except KeyError as key_err:
            print("%s pas apparu." % mot)
            raise key_err

    @staticmethod
    def indice_idf(mot, occurences_corpus):
        """Calcule l'indice IDF d'un mot dans un corpus.

        log_10 du nombre de textes divisé par le nombre de textes où le mot
        apparait.

        :param mot: mot dont on cherche l'indice TDF.
        :param occurences_corpus: Dictionnaire de tous les 'Counter' des textes
                                  du corpus.
        """
        nb_textes = len(occurences_corpus)
        apparu = sum([mot in occ for occ in occurences_corpus.values()])
        return math.log10(nb_textes / apparu)
