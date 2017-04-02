"""Analyse du texte."""

import math
import os
import time
from collections import Counter


def compter_occurences(mots):
    """Compte les occurences de chaque mot.

    :param mots: liste des mots à compter.
    :retourne: objet collections.Counter, implémentation d'un dictionnaire
                pour le comptage d'éléments d'un itérable.
    """
    return Counter(mots)


def _get_comments(id_film, dossier):
    """Récupère les commentaires d'un film.

    :param id_film: identifiant du film voulu.
    :param dossier: dossier contenant les fichiers à lire.
    """
    chemin = os.path.join(dossier, id_film)
    if os.path.exists(chemin):
        with open(chemin, encoding='utf8') as com:
            return com.read()
    else:
        raise ValueError("%s inexistant dans le dossier %s." %
                         (id_film, dossier))


def _get_mots(comment):
    """Renvoie la liste des mots d'un commentaire."""
    return comment.strip().split()


def get_mots_film(id_film, dossier):
    """Renvoie les mots des commentaire d'un film dans le dossier."""
    commentaire = _get_comments(id_film, dossier)
    return _get_mots(commentaire)


class StockeurFrequences:
    """Conserve pour chaque film son compte de mots."""

    def __init__(self, dossier):
        """Initialise le stockeur.

        :param dossier: dossier contenant les commentaires de films.
        :occurences: dictionnaire qui associe à un film l'objet
        collections.Counter de ses commentaires.
        occurences: film_id -> dictionnaire: mot -> occurences dans le texte
        :total: stocke le compte parmi tous les textes ensembles
        """
        self.occurences = {}
        self.total = Counter()
        self._ajouter_films(dossier)

    def _ajouter_films(self, dossier):
        """Ajoute un film et son compte de mots dans la base.

        Erreur si le film a déjà été compté.
        """
        for film_id in os.listdir(dossier):
            mots = get_mots_film(film_id, dossier)
            compte = compter_occurences(mots)
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

    def _indice_tf(self, mot, occurences_texte, mode="simple"):
        """Renvoie l'indice TF d'un mot dans un texte.

        Forme simple: fréquence brute.

        :param mot: mot dont on cherche la fréquence.
        :param occurences_texte: 'Counter' des occurences de chaque mot du
                                 texte.
        :param mode: 'simple', 'log' ou 'binaire'
                     'simple': fréquence brute
                     'log': 1 + log(fréquence brute)
                     'binaire': 1 si le mot apparait
        """
        if mode == 'binaire':
            return int(mot in occurences_texte)
        elif mode == 'simple':
            # `Counter` renvoie 0 si le mot n'est pas dans le dictionnaire.
            return occurences_texte[mot]
        elif mode == 'log':
            try:
                return 1 + math.log(occurences_texte[mot])
            except ValueError:
                # Le mot n'apparait pas, erreur avec le log.
                return 0
        else:
            raise ValueError("Mode %s inconnu." % mode)

    def _indice_idf(self, mot, occurences_total):
        """Calcule l'indice IDF d'un mot dans un corpus.

        log base 10 du nombre de textes divisé par le nombre de textes où le
        mot apparait.

        :param mot: mot dont on cherche l'indice TDF.
        :param occurences_total: Dictionnaire des 'Counter' de tous les textes
                                 du corpus.
        """
        if mot in self.indices_idf:
            return self.indices_idf[mot]
        nb_textes = len(occurences_total)
        apparu = sum([mot in occ for occ in occurences_total.values()])
        idf = math.log10(nb_textes / apparu)
        self.indices_idf[mot] = idf
        return idf

    def indice_tf_idf(self, mot, occurences_texte, occurences_total):
        """Indice TF-IDF d'un mot d'un texte par rapport au corpus.

        :param mot: mot dont on cherche l'indice TF-IDF.
        :param occurences_texte: 'Counter' des mots du texte contenant le mot.
        :param occurences_corpus: Dictionnaire des 'Counter' des mots dans tout
                                  le corpus.
        """
        ind_tf = self._indice_tf(mot, occurences_texte)
        ind_idf = self._indice_idf(mot, occurences_total)
        return ind_tf * ind_idf


class StockeurIndicesTfIdf:
    """Pour chaque film, enregistre l'indice TF-IDF de chaque mot."""

    def __init__(self, dossier):
        """Initialise le stockeur des indices TF-IDF.

        Par défaut, calcule tous les indices TF-IDF des mots.
        """
        # Fréquences brutes.
        print("Calcul des occurences de chaque mot.")
        debut = time.time()
        self.stockeur_freq = StockeurFrequences(dossier)
        print("Comptage terminé en %.3fs." % (time.time() - debut))
        # Indices TF-IDF
        print("Calcul des indices IDF.")
        self.calculateur = CalculateurIndices()
        debut = time.time()
        """ Dictionnaire de dictionnaires:
        film -> dictionnaire: mot -> indice_tf_idf
        """
        self.indices = {}
        for film, occ_film in self.stockeur_freq.occurences.items():
            self.indices[film] = {}
            for mot in occ_film.keys():
                self.indices[film][mot] = self.calculateur.indice_tf_idf(
                    mot, occ_film, self.stockeur_freq.occurences)
        print("Calcul des indices effectué en %.3fs." % (time.time() - debut))

    def get_idf_mot(self, mot):
        """Renvoie l'indice IDF d'un mot donné."""
        if mot in self.calculateur.indices_idf:
            return self.calculateur.indices_idf[mot]
        raise KeyError("%s n'a pas d'indice IDF." % mot)

    def get_tous_idf(self):
        """Renvoie le dictionnaire des indices IDF de tous les mots."""
        return self.calculateur.indices_idf

    def get_tf_idf(self, mot, film):
        """Renvoie l'indice TF-IDF d'un mot pour un film donné."""
        if film in self.indices and mot in self.indices[film]:
            return self.indices[film][mot]
        # Le mot n'est pas dans le film.
        return 0

    def get_stockeur_frequences(self):
        """Renvoie le stockeur de fréquences brutes."""
        return self.stockeur_freq
