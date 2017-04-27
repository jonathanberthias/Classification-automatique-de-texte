"""Module principal pour appeler chaque partie du programme."""
import os
import time
from tkinter.filedialog import askdirectory

import analyse
import classification
import distance
import traitement


"""
PARAMETRES
"""

# Si vrai, supprimer et réécrire le dossier de films. Sinon, sauter la partie 1
# Nécessaire la première fois que le programme tourne et à chaque fois
# qu'on augmente le nombre de commentaires.
OVERWRITE = True

# Nombre de commentaires à traiter (25000 pour tous)
NOMBRE_COMMENTAIRES = 1000

# Nombre de groupes pour le k-means
NB_GROUPES = 5

# Nombre de mots pertinents à utiliser pour la classification
NB_MOTS = 1000

# Nombre de films différents dans lesquels un film doit apparaitre pour
# être pris en compte dans la sélection des mots pertinents
OCCURENCES_MINIMUM = 20

# Si vrai, utiliser l'indice TF-IDF pour déterminer la pertinence d'un mot
# (max pour l'ensemble des textes). Sinon, utiliser l'indice IDF.
TFIDF = True

# Si vrai, utiliser la distance cosinus. Sinon, utiliser la distance
# euclidienne.
COSINUS = True

# Active l'indicateur de progression, marche mal sous Windows
PROGRESS = False


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
    traiteur = traitement.Traitement(PATH_TO_COMMENTS, PATH_TO_FILMS)
    associateur = traitement.AssociateurCommentairesFilms(PATH_TO_INDEX)
    if OVERWRITE:
        traiteur = traitement.Traitement(PATH_TO_COMMENTS, PATH_TO_FILMS)
        traiteur.traiter(NOMBRE_COMMENTAIRES,
                         progress=PROGRESS, associateur=associateur)
    else:
        print("Traitement sauté.")


def partie2():
    """Appelle la parie 2, analyse."""
    stock_indices = analyse.StockeurIndicesTfIdf(
        PATH_TO_FILMS, OCCURENCES_MINIMUM)
    return stock_indices


def partie3(stockeur):
    """Appelle la partie 3, distance."""
    mots_perti = distance.plus_pertinents(
        NB_MOTS, stockeur.get_tous_idf().keys(), stockeur, TFIDF)
    return mots_perti


def partie4(mots_perti, stockeur):
    """Appelle la partie 4, classification."""
    return classification.kmeans(
        NB_GROUPES, stockeur.indices_tf_idf.keys(),
        mots_perti, COSINUS, stockeur)


def main():
    """Fonction principale."""
    debut = time.time()
    partie1()
    stockeur = partie2()
    deb = time.time()
    mots_perti = partie3(stockeur)
    groupes, centres = partie4(mots_perti, stockeur)
    _afficher_groupes(groupes, centres)
    print("Classification terminée en %.3fs." % (time.time() - deb))
    print("Opération totale terminée en %.3fs." % (time.time() - debut))


if __name__ == "__main__":
    main()
