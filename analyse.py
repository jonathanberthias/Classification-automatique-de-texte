"""Analyse du texte."""

import math
import os
import time
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
        self.occurences = {}
        self.total = Counter()
        self._ajouter_films(dossier)

    def _ajouter_films(self, dossier):
        """Ajoute un film et son compte de mots dans la base.

        Erreur si le film a déjà été compté.
        """
        for film_id in os.listdir(dossier):
            mots = RecuperateurTexte.get_mots_film(film_id, dossier)
            # 'compte' est un 'Counter', une forme de dictionnaire.
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


class CalculateurIndices:
    """Calcule l'indice TF-IDF des mots."""

    def __init__(self):
        """Initialise un dctionnaire pour stocker les indices IDF."""
        self.indices_idf = {}

    def _indice_tf(self, mot, occurences_texte):
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

    def _indice_idf(self, mot, occurences_corpus):
        """Calcule l'indice IDF d'un mot dans un corpus.

        log base 10 du nombre de textes divisé par le nombre de textes où le
        mot apparait.

        :param mot: mot dont on cherche l'indice TDF.
        :param occurences_corpus: 'Counter' de tous les textes du corpus.
        """
        if mot in self.indices_idf:
            return self.indices_idf[mot]
        nb_textes = len(occurences_corpus)
        apparu = sum([mot in occ for occ in occurences_corpus.values()])
        idf = math.log10(nb_textes / apparu)
        self.indices_idf[mot] = idf
        return idf

    def indice_tf_idf(self, mot, occurences_texte, occurences_corpus):
        """Indice TF-IDF d'un mot d'un texte par rapport au corpus.

        :param mot: mot dont on cherche l'indice TF-IDF.
        :param occurences_texte: 'Counter' des mots du texte contenant le mot.
        :param occurences_corpus: 'Counter' des mots dans tout le corpus.
        """
        ind_tf = self._indice_tf(mot, occurences_texte)
        ind_idf = self._indice_idf(mot, occurences_corpus)
        return ind_tf * ind_idf


class StockeurIndicesTfIdf:
    """Pour chaque film, enregistre l'indice TF-IDF de chaque mot."""

    def __init__(self, dossier):
        """Initialise le stockeur des indices TF-IDF."""
        # Fréquences brutes.
        print("Calcul des occurences de chaque mot.")
        debut = time.time()
        self.stockeur_freq = StockeurFrequences(dossier)
        print("Comptage terminé en %.3fs." % (time.time() - debut))
        # Indices TF-IDF
        print("Calcul des indices TF-IDF.")
        self.calculateur = CalculateurIndices()
        debut = time.time()
        """ Dictionnaire de dictionnaires:
        film -> dictionnaire: mot -> indice_tf_idf
        """
        self.indices = {film:
                        {mot: self.calculateur.indice_tf_idf(
                            mot, occ_film, self.stockeur_freq.occurences)
                         for mot in occ_film}
                        for film, occ_film in
                        self.stockeur_freq.occurences.items()}
        print("Calcul des indices effectué en %.3fs." % (time.time() - debut))

    def get_idf_mot(self, mot):
        """Renvoie l'indice IDF d'un mot donné."""
        try:
            return self.calculateur.indices_idf[mot]
        except KeyError as key_err:
            print("%s n'a pas d'indice IDF." % mot)
            raise key_err

    def get_tous_idf(self):
        """Renvoie le dictionnaire des indices IDF de tous les mots."""
        return self.calculateur.indices_idf

    def get_tf_idf(self, mot, film):
        """Renvoie l'indice TF-IDF d'un mot pour un film donné."""
        try:
            return self.indices[film][mot]
        except KeyError:
            print("Mot %s pas dans le film %s" % (mot, film))
            return 0.

    def get_stockeur_frequences(self):
        """Renvoie les stockeur de fréquences brutes."""
        return self.stockeur_freq
