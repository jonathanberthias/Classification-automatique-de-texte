"""Module principal pour appeler chaque partie du programme."""
import os
import time
from tkinter.filedialog import askdirectory

import analyse
import traitement

import random

# Variables par défaut
if os.path.exists(os.path.join("..", "imdb")):  # dossier parent du fichier
    PATH_TO_RESOURCES = os.path.join("..", "imdb")
elif os.path.exists("imdb"):  # meme dossier que le fichier
    PATH_TO_RESOURCES = "imdb"
else:  # autre part
    PATH_TO_RESOURCES = askdirectory(
        mustexist=True,
        title="Veuillez sélectionner votre dossier 'imdb'.")
# Pour tests
#   PATH_TO_RESOURCES = "../imdb_test"
PATH_TO_INDEX = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "title_index"))
PATH_TO_COMMENTS = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "comments"))
PATH_TO_FILMS = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "films"))

NOMBRE_COMMENTAIRES = 5000
OVERWRITE = True


def main():
    """Fonction principale."""
    if OVERWRITE:
        traiteur = traitement.Traitement(
            PATH_TO_INDEX, PATH_TO_COMMENTS, PATH_TO_FILMS)
        debut = time.time()
        traiteur.traiter(NOMBRE_COMMENTAIRES)
        duree = time.time() - debut
        print("%d commentaires traités en %.3fs." %
              (NOMBRE_COMMENTAIRES, duree))
    else:
        print("Traitement sauté.")
    analyseur = analyse.StockeurIndicesTfIdf(PATH_TO_FILMS)
    # film = random.choice(list(analyseur.indices.keys()))
    # print(analyseur.indices[film])

if __name__ == "__main__":
    main()
