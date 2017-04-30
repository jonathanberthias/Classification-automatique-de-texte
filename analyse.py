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

    def __init__(self):
        """Initialise le stockeur.

        :occurences: dictionnaire qui associe à un film l'objet
        collections.Counter de ses commentaires.
        occurences: film_id -> dictionnaire: mot -> occurences dans le texte
        :nb_apparitions_uniques: compte le nombre de films dans lesquels chaque
                                 mot apparaît
        :total: stocke le compte parmi tous les textes ensembles
        """
        self.occurences = {}
        self.total = Counter()
        self.nb_apparitions_uniques = Counter()
        self.nb_films = 0

    def compter_tous_films(self, dossier):
        """Ajoute un film et son compte de mots dans la base.

        :param dossier: dossier où chercher les fichiers des films.
        """
        for film_id in os.listdir(dossier):
            mots = get_mots_film(film_id, dossier)
            compte = compter_occurences(mots)

            self.occurences[film_id] = compte
            for mot in compte.keys():
                self.nb_apparitions_uniques[mot] += 1
            # update ajoute le compte au total (sans créer de nouveau Counter)
            self.total.update(compte)
            self.nb_films += 1

    def get_compte_film(self, film_id):
        """Renvoie l'objet Counter associé à un film."""
        if film_id in self.occurences:
            return self.occurences[film_id]
        raise ValueError("Film %s pas compté." % film_id)

    def get_compte_total(self):
        """Renvoie les occurences dans la totalité des textes du dossier."""
        return self.total

    def get_nb_films_apparu(self, mot):
        """Renvoie le nombre de films où un mot est apparu."""
        return self.nb_apparitions_uniques[mot]

    def get_occurences_mot_dans_film(self, film, mot):
        """Renvoie le nombre d'apapritions d'un mot dans un film."""
        return self.get_compte_film(film).get(mot, 0)

    def get_nb_films_total(self):
        """Renvoie le nombre de films traités."""
        return self.nb_films

    def get_apparitions_uniques(self):
        """Renvoie le nombre de films où apparait chaque mot."""
        return self.nb_apparitions_uniques


class CalculateurIndices:
    """Calcule l'indice TF-IDF des mots."""

    def __init__(self):
        """Initialise un dctionnaire pour stocker les indices IDF."""
        self.indices_idf = {}

    def indice_tf(self, mot, occurences_texte):
        """Renvoie l'indice TF d'un mot dans un texte.

        Forme simple: fréquence relative.

        :param mot: mot dont on cherche la fréquence.
        :param occurences_texte: 'Counter' des occurences de chaque mot du
                                 texte.
        """
        return math.log(occurences_texte[mot]) / len(occurences_texte.keys())

    def indice_idf(self, mot, apparitions_uniques, nb_films):
        """Calcule l'indice IDF d'un mot dans un corpus.

        log base 10 du nombre de textes divisé par le nombre de textes où le
        mot apparait.

        :param mot: mot dont on cherche l'indice TDF.
        :param occurences_total: Dictionnaire des 'Counter' de tous les textes
                                 du corpus.
        """
        if mot in self.indices_idf:
            return self.indices_idf[mot]
        apparu = apparitions_uniques[mot]
        idf = math.log10(nb_films / apparu)
        self.indices_idf[mot] = idf
        return idf

    def indice_tfidf(self, mot, film, stockeur_frequences):
        """Indice TF-IDF d'un mot d'un texte par rapport au corpus.

        :param mot: mot dont on cherche l'indice TF-IDF.
        :param occurences_texte: 'Counter' des mots du texte contenant le mot.
        :param occurences_corpus: Dictionnaire des 'Counter' des mots dans tout
                                  le corpus.
        """
        ind_tf = self.indice_tf(
            mot, stockeur_frequences.get_compte_film(film))
        ind_idf = self.indice_idf(mot,
                                  stockeur_frequences.get_apparitions_uniques(),
                                  stockeur_frequences.get_nb_films_total())
        return ind_tf * ind_idf


def filtrer_dictionnaire_mots(mots_pertinents, dictionnaire):
    """Renvoie un compteur avec seulement les mots pertinents.

    :param mots_pertinents: liste des mots à garder
    :param dictionnaire: dictionnaire associé aux mots d'un film
    """
    # cles_a_garder = filter(lambda x: x in mots_pertinents,
    # dictionnaire.keys())
    return {x: dictionnaire[x] for x in dictionnaire.keys()
            if x in mots_pertinents}


class StockeurIndicesTfIdf:
    """Pour chaque film, enregistre l'indice TF-IDF de chaque mot."""

    def __init__(self, dossier, prop_min, prop_max):
        """Initialise le stockeur des indices TF-IDF.

        Par défaut, calcule tous les indices TF-IDF des mots.

        :param dossier: dossier contenant les fichiers des films.
        :param occ_min: nombre minimal de films où doit apparaitre un mot pour
                        etre pris en compte dans le k-means.
        """
        self.stockeur_freq = StockeurFrequences()
        self.calculateur = CalculateurIndices()
        """ Indices_tf_idf est un dictionnaire de dictionnaires:
        film -> dictionnaire: mot -> indice_tf_idf
        ou matrice[film][mot]
        """
        self.indices_tf_idf = {}
        self.indices_tf_idf_filtres = {}

        print("Compte des occurences de chaque mot.")
        debut = time.time()
        self.stockeur_freq.compter_tous_films(dossier)
        print("Comptage terminé en %.3fs." % (time.time() - debut))

        print("%d films" % self.stockeur_freq.get_nb_films_total())
        self.occ_min = int(prop_min * self.stockeur_freq.get_nb_films_total())
        self.occ_max = int(prop_max * self.stockeur_freq.get_nb_films_total())
        print("Occurences minimum: %d\tOccurences maximum: %d" %
              (self.occ_min, self.occ_max))

        print("Calcul des indices TF-IDF")
        debut = time.time()
        for film, occ_film in self.stockeur_freq.occurences.items():
            self.indices_tf_idf[film] = {}
            for mot in occ_film.keys():
                self.indices_tf_idf[film][mot] = self.calculateur.indice_tfidf(
                    mot, film, self.stockeur_freq)
        print("Calcul des indices effectué en %.3fs." % (time.time() - debut))

    def get_idf_mot(self, mot):
        """Renvoie l'indice IDF d'un mot donné."""
        return self.calculateur.indices_idf.get(mot, 0)

    def get_tous_idf(self):
        """Renvoie le dictionnaire des indices IDF de tous les mots."""
        return self.calculateur.indices_idf

    def get_tf_idf(self, mot, film):
        """Renvoie l'indice TF-IDF d'un mot pour un film donné."""
        return self.indices_tf_idf[film].get(mot, 0)

    def get_tf_idf_film(self, film):
        """Renvoie le dictionnaire des indices TF-IDF du film."""
        return self.indices_tf_idf[film]

    def get_max_tf_idf(self, mot):
        """Renvoie le max des indices TF-IDF d'un mot pour tous les films."""
        liste_des_films = self.stockeur_freq.occurences.keys()
        return max([self.get_tf_idf(mot, film) for film in liste_des_films])

    def get_stockeur_frequences(self):
        """Renvoie le stockeur de fréquences brutes."""
        return self.stockeur_freq

    def get_compte_frequences_film(self, film):
        """Renvoie le compte des fréquences des mots du film."""
        return self.stockeur_freq.get_compte_film(film)

    def est_assez_frequent(self, mot):
        """Renvoie vrai si le mot apparait dans au moins `seuil` films."""
        apparitions = self.get_stockeur_frequences().get_nb_films_apparu(mot)
        trop_peu = apparitions <= self.occ_min
        trop_bcp = self.occ_max < apparitions
        if trop_bcp:
            print("%s" % mot, end=", ")
        return not(trop_peu or trop_bcp)

    def get_indices_tfidf_mots_filtres(self, film, liste_mots):
        """Renvoie le dictionnaire pour les mots donnés et le film donné."""
        if film in self.indices_tf_idf_filtres:
            return self.indices_tf_idf_filtres.get(film)
        dico = filtrer_dictionnaire_mots(
            liste_mots, self.get_tf_idf_film(film))
        """
        mots_finaux = filter(lambda x: x in liste_mots,
                             self.get_compte_frequences_film(film).keys())
        dico = {x: self.get_tf_idf(x, film) for x in mots_finaux}
        """
        self.indices_tf_idf_filtres[film] = dico
        return dico
