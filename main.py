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
PATH_TO_INDEX = os.path.join(PATH_TO_RESOURCES, "title_index")
PATH_TO_COMMENTS = os.path.join(PATH_TO_RESOURCES, "comments")
PATH_TO_FILMS = os.path.join(PATH_TO_RESOURCES, "films")

NOMBRE_COMMENTAIRES = 1000


def main():
    """Fonction principale."""
    traiteur = traitement.Traitement(
        PATH_TO_INDEX, PATH_TO_COMMENTS, PATH_TO_FILMS)
    debut = time.time()
    traiteur.traiter(NOMBRE_COMMENTAIRES)
    duree = time.time() - debut
    print("%d commentaires traités en %.3fs." % (NUMBER_COMMENTS, duree))

    print("Comptage des mots.")
    debut = time.time()
    analyseur = analyse.StockeurFrequences(PATH_TO_FILMS)
    for film in os.listdir(PATH_TO_FILMS):
        analyseur.ajouter_film(film)
    stock = analyseur.compte_total()
    duree = time.time() - debut
    print("Opération effectuée en %.3fs." % duree)
    # print(stock.most_common(50))
    print(len(stock.keys()))


if __name__ == "__main__":
    main()
