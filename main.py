"""Module principal pour appeler chaque partie du programme."""
import os
import time
from tkinter.filedialog import askdirectory

import analyse
import classification
import distance
import traitement

# Variables par défaut
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

# Nombre de commentaires à traiter
NOMBRE_COMMENTAIRES = 20

# Nombre de groupes pour le k-means
NB_GROUPES = 2

# Si vrai, supprime et réécrit e dossier de films. Sinon, saute la partie 1.
OVERWRITE = True

# Active l'indicateur de progression, marche mal sous Windows
PROGRESS = False


def _afficher_dic(dico, associateur):
    for centre, films in dico.items():
        print("Groupe de centre %s" % associateur.get_titre(centre))
        print(", ".join(films))


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
    return associateur


def partie2():
    """Appelle la parie 2, analyse."""
    stock_indices = analyse.StockeurIndicesTfIdf(PATH_TO_FILMS)
    return stock_indices


def partie3(stockeur):
    """Appelle la partie 3, distance."""
    mots_perti = distance.pertinence(100, stockeur)
    return distance.get_dico_des_films(stockeur.get_stockeur_frequences(), mots_perti), mots_perti


def partie4(dico, mots_perti):
    """Appelle la partie 4, classification."""
    # centres = classification.generer_centres(2, dico)
    # print(centres)
    # groupes = classification.kmeans(NB_GROUPES, dico, associateur)
    # _afficher_dic(groupes, associateur)
    classification.resultats_k_means(NB_GROUPES, dico, mots_perti, 5)


def main():
    """Fonction principale."""
    debut = time.time()
    associateur = partie1()
    stockeur = partie2()
    deb = time.time()
    dico, mots_perti = partie3(stockeur)
    partie4(dico, mots_perti)
    print("Classification terminée en %.3fs." % (time.time() - deb))
    print("Opération totale terminée en %.3fs." % (time.time() - debut))


if __name__ == "__main__":
    main()
