#!bin/bash
# -*- coding: utf-8 -*-
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
NOMBRE_COMMENTAIRES = 25000

# Si vrai, supprime et réécrit e dossier de films. Sinon, saute la partie 1.
OVERWRITE = True

# Active l'indicateur de progression, marche mal sous Windows
PROGRESS = True


def afficher_dic(dico, associateur):
    for centre, films in dico.items():
        print("Groupe de centre %s" % associateur.get_titre(centre))
        print(", ".join(films))


def partie1():
    """Appelle la partie 1, traitement."""
    traiteur = traitement.Traitement(
        PATH_TO_INDEX, PATH_TO_COMMENTS, PATH_TO_FILMS)
    associateur = traitement.AssociateurCommentairesFilms(PATH_TO_INDEX)
    if OVERWRITE:
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
    mots_perti = distance.pertinence_tfidf(10000, stockeur)
    return distance.get_dico_des_films(stockeur.get_stockeur_frequences(),
                                       mots_perti)


def partie4(dico, associateur):
    """Appelle la partie 4, classification."""
    groupes = classification.kmeans(20, dico, associateur)
    afficher_dic(groupes, associateur)


def main():
    """Fonction principale."""
    debut = time.time()
    associateur = partie1()
    stockeur = partie2()
    deb = time.time()
    dico = partie3(stockeur)
    partie4(dico, associateur)
    print("Classification terminée en %.3fs." % (time.time() - deb))

    print("Opération totale terminée en %.3fs." % (time.time() - debut))


if __name__ == "__main__":
    main()
