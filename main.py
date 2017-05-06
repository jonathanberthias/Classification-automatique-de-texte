"""Module principal pour appeler chaque partie du programme."""

import os
import time
from tkinter.filedialog import askdirectory

import analyse
import classification
import distance
import traitement
import voisins


"""
PARAMETRES
"""

# Si vrai, supprimer et réécrire le dossier de films. Sinon, sauter la partie 1
# Nécessaire la première fois que le programme tourne et à chaque fois
# qu'on change le nombre de commentaires.
OVERWRITE = True

# Nombre de commentaires à traiter (25000 pour tous)
NOMBRE_COMMENTAIRES = 25000

# Nombre de groupes pour le k-means
NB_GROUPES = 7

# Nombre de mots pertinents à utiliser pour la classification
NB_MOTS = 1000

# Proportion de films différents dans lesquels un film doit apparaitre pour
# être pris en compte dans la sélection des mots pertinents
PROPORTION_MINIMUM = 0.05
PROPORTION_MAXIMUM = 0.5

# Si vrai, utiliser l'indice TF-IDF pour déterminer la pertinence d'un mot
# (max pour l'ensemble des textes). Sinon, utiliser l'indice IDF.
TFIDF = True

# Si vrai, utiliser la distance cosinus. Sinon, utiliser la distance
# euclidienne.
COSINUS = True

# Active l'indicateur de progression, marche mal sous Windows
PROGRESS = True

"""BONUS"""

# Nombre de voisins les plus proches à prendre en compte.
NB_VOISINS = 5

# Nombre de films dont on connait la note pour la comparer aux autres films
# 3456 films au total si on prend en compte les 25000 commentaires.
NB_REFERENTS = 1000

# Différence maximale entre la vrai note et la note estimée pour que
# l'estimation soit jugée correcte. La note est entre 1 et 10.
TOLERENCE = 1.5


"""
REGLAGES
"""

if os.path.exists(os.path.join("..", "imdb")):  # dossier parent du fichier
    PATH_TO_RESOURCES = os.path.join("..", "imdb")
elif os.path.exists("imdb"):  # meme dossier que le fichier
    PATH_TO_RESOURCES = "imdb"
else:  # autre part
    PATH_TO_RESOURCES = askdirectory(
        mustexist=True,
        title="Veuillez sélectionner votre dossier 'imdb'.")

PATH_TO_INDEX = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "title_index"))
PATH_TO_COMMENTS = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "comments"))
PATH_TO_FILMS = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "films"))
PATH_TO_MOYENNES = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "moyennes"))


"""
PROGRAMME PRINCIPAL
"""


def _afficher_groupes(groupes, centres):
    """Afficher les mots les plus pertinents de chaque centre."""
    print()
    for index_groupe, centre in enumerate(centres):
        print("Groupe %d:" % index_groupe)
        print(", ".join(sorted(centre, key=centre.get, reverse=True)[:15]))
        print("Composé de %d films." % len(groupes[index_groupe]))
        print("=" * 50)


def partie1():
    """Appelle la partie 1, traitement."""
    associateur = traitement.AssociateurCommentairesFilms(PATH_TO_INDEX)
    traiteur = traitement.Traitement(PATH_TO_COMMENTS,
                                     PATH_TO_FILMS,
                                     PATH_TO_MOYENNES)
    if OVERWRITE:
        traiteur.traiter(nb_com=NOMBRE_COMMENTAIRES,
                         progress=PROGRESS,
                         associateur=associateur)
    else:
        print("Traitement sauté.")
    return associateur


def partie2():
    """Appelle la parie 2, analyse."""
    stock_indices = analyse.StockeurIndicesTfIdf(dossier=PATH_TO_FILMS,
                                                 prop_min=PROPORTION_MINIMUM,
                                                 prop_max=PROPORTION_MAXIMUM)
    return stock_indices


def partie3(stockeur):
    """Appelle la partie 3, distance."""
    mots_perti = distance.plus_pertinents(num_mots=NB_MOTS,
                                          mots=stockeur.get_tous_idf().keys(),
                                          stockeur_indices=stockeur,
                                          utiliser_tfidf=TFIDF)
    return mots_perti


def partie4(mots_perti, stockeur):
    """Appelle la partie 4, classification."""
    return classification.kmeans(nb_groupes=NB_GROUPES,
                                 liste_films=stockeur.indices_tf_idf.keys(),
                                 mots_pertinents=mots_perti,
                                 distance_cosinus=COSINUS,
                                 stockeur_indices=stockeur)


def bonus(stockeur_indices, mots_perti, asso):
    print("BONUS")
    deb = time.time()
    liste_films = stockeur_indices.get_stockeur_frequences().occurences.keys()
    vrai, corr = voisins.devine_toutes_notes(
        PATH_TO_MOYENNES, NB_VOISINS, NB_REFERENTS, TOLERENCE,
        liste_films, mots_perti, stockeur_indices, asso)
    print("Bonus effectué en %.3fs" % (time.time() - deb))
    print("Correct (total): %.2f%%" % (100 * vrai))
    print("Correct (corrigé): %.2f%%" % (100 * corr))


def main():
    """Fonction principale."""
    debut = time.time()
    asso = partie1()
    stockeur = partie2()
    deb = time.time()
    mots_perti = partie3(stockeur)
    groupes, centres = partie4(mots_perti, stockeur)
    _afficher_groupes(groupes, centres)
    print("Classification terminée en %.3fs." % (time.time() - deb))
    print("Opération totale terminée en %.3fs." % (time.time() - debut))
    bonus(stockeur, mots_perti, asso)


if __name__ == "__main__":
    main()
