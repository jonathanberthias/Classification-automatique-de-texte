"""Module principal pour appeler chaque partie du programme."""
import os
import time
from tkinter.filedialog import askdirectory

import analyse
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
# Pour tests
#   PATH_TO_RESOURCES = "../imdb_test"
PATH_TO_INDEX = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "title_index"))
PATH_TO_COMMENTS = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "comments"))
PATH_TO_FILMS = os.path.abspath(os.path.join(PATH_TO_RESOURCES, "films"))

# Nombre de commentaires à traiter
NOMBRE_COMMENTAIRES = 5000
# Si vrai, supprime et réécrit e dossier de films. Sinon, saute la partie 1.
OVERWRITE = True


def partie1():
    """Appelle la partie 1, traitement."""
    if OVERWRITE:
        traiteur = traitement.Traitement(
            PATH_TO_INDEX, PATH_TO_COMMENTS, PATH_TO_FILMS)
        traiteur.traiter(NOMBRE_COMMENTAIRES)

    else:
        print("Traitement sauté.")


def partie2():
    """Appelle la parie 2, analyse."""
    stock_indices = analyse.StockeurIndicesTfIdf(PATH_TO_FILMS)
    return stock_indices


def partie3():
    """Appelle la partie 3, distance."""
    pass


def partie4():
    """Appelle la partie 4, classification."""
    pass


def main():
    """Fonction principale."""
    debut = time.time()
    partie1()
    partie2()
    partie3()
    partie4()

    print("Opération totale terminée en %.3fs." % (time.time() - debut))


if __name__ == "__main__":
    main()
