"""Traitement des fichiers.

Pour chaque commentaire, lemmatiser les mots et écrire le résultat dans le
fichier du film qui lui correspond.
"""

import os
import re
import shutil
import sys

import nltk
from nltk.tokenize import word_tokenize


class AssociateurCommentairesFilms:
    """Lit le fichier d'index et stock le film associé à chaque commentaire."""

    def __init__(self, path_to_index):
        """Crée le répertoire entre les comentaires et les films associés.

        :param path_to_index: chemin relatif de ce fichier au fichier
        d'index.
        """
        self.films = {}
        if not os.path.exists(path_to_index):
            raise IOError("Pas d'index au chemin: %s" % path_to_index)
        with open(path_to_index, 'r') as index:
            for ligne in index.readlines():
                vals = ligne.split(':')
                comment_id = vals[0]
                film_id = vals[1]
                self.films[comment_id] = film_id

    def get_film(self, comment_id):
        """Retourne l'identifiant du film associé au commentaire donné."""
        if comment_id in self.films:
            return self.films[comment_id]
        raise IndexError(
            "Le commentaire %s n'est pas dans la base de commentaires." %
            comment_id)


class TraiteurCommentaires:
    """Lemmatise et enlève la ponctuation des commentaires."""

    # Mots les plus fréquents
    mots_a_enlever = [
        "i",
        "movie",
        "film",
        "have",
        "are",
        "be",
        "get",
        "other",
        "do",
        "go",
        "say",
        "make"
    ]

    a_garder = [
        "VB",
        "VBP",
        "NN",
        "JJ",
        "NNP",
        "ADJ",
        "NUM",
        "NOUN",
        "VERB"
    ]

    lemmatiseur_func = nltk.stem.SnowballStemmer(language='english').stem

    @staticmethod
    def traiter_commentaire(comment):
        """Renvoie le commentaire entièrement nettoyé."""
        clean_comment = TraiteurCommentaires._enlever_newlines(comment)
        clean_comment = TraiteurCommentaires._enlever_ponctuation(
            clean_comment)
        return clean_comment

    @staticmethod
    def _enlever_newlines(comment):
        """Nettoie tout ce qui se situe entre des tags <>."""
        ouverture = comment.find("<")
        if ouverture < 0:
            # Pas de tag
            return comment
        fermeture = comment.find(">")
        if fermeture < 0:
            # Probablement un smiley ou un truc du genre
            return comment
        # 'find' trouve la première occurence du symbole, donc il ne devrait
        # pas y en avoir avant 'ouverture'
        debut = comment[:ouverture]
        fin = TraiteurCommentaires._enlever_newlines(comment[fermeture + 1:])
        return debut + fin

    @staticmethod
    def _enlever_ponctuation(comment):
        """Nettoie la ponctuation."""
        # Ne garde que les lettres et les chiffres
        pattern = re.compile(r'[\W_]+')
        clean_comment = pattern.sub(' ', comment.lower())

        tokenized = word_tokenize(clean_comment)
        tokens = nltk.pos_tag(tokenized)
        to_keep = (x[0] for x in tokens if x[1]
                   in TraiteurCommentaires.a_garder and x[0] not in
                   TraiteurCommentaires.mots_a_enlever)
        lemmes = (TraiteurCommentaires.lemmatiseur_func(x) for x in to_keep)
        return " ".join(lemmes)

    @staticmethod
    def _lemmatiser(mot):
        """Lemmatise un mot.

        Pour l'instant, on utilise juste le module nltk.
        """
        return TraiteurCommentaires.lemmatiseur_func(mot)


class EcriveurFichiersFilms:
    """Crée les fichiers des films."""

    def __init__(self, path_to_folder):
        """Crée le dossier pour stocker les films."""
        self.chemin = path_to_folder
        if os.path.exists(self.chemin):
            # On importe que si besoin
            shutil.rmtree(self.chemin)
        os.makedirs(self.chemin)

    def ecrire_commentaire(self, comment, film_id):
        """Ecrit le commentaire pour le film donné."""
        fichier = os.path.join(self.chemin, film_id)
        if os.path.exists(fichier):
            # 'utf8' pour éviter les problèmes d'encodage/décodage
            with open(fichier, 'a', encoding='utf8') as film:
                film.write("\n")
                film.write(comment)
        else:
            with open(fichier, 'w', encoding='utf8') as film:
                film.write(comment)


class Traitement:
    """Traite les commentaires et les range nettoyés dans le bon fichier."""

    def __init__(self,
                 path_to_index,
                 path_to_comments,
                 path_to_films):
        """Initialise le traiteur.

        :param path_to_index: chemin relatif vers le fichier index
        :param path_to_comments: chemin relatif vers les commentaires
        :param path_to_films: chemin relatif vers les films
        """
        self.path_to_index = path_to_index
        self.path_to_comments = path_to_comments
        self.path_to_films = path_to_films
        print("Chemin vers l'index: %s" % self.path_to_index)
        print("Chemin vers les coms: %s" % self.path_to_comments)
        print("Chemin vers les films: %s" % self.path_to_films)

    def traiter(self, nb_com=25000):
        """Effectue l'ensemble du traitement pour tout les commentaires."""
        # Variables pour les fonctions pour gagner un peu de temps.
        print("Création du répertoire.")
        get_film_id = AssociateurCommentairesFilms(
            self.path_to_index).get_film
        print("Répertoire créé.")
        writer = EcriveurFichiersFilms(
            self.path_to_films).ecrire_commentaire
        traiter = TraiteurCommentaires.traiter_commentaire
        num_com = 0
        print("Ecriture des fichiers pour les films.")
        for com in os.listdir(self.path_to_comments):
            com_id = com[:com.find("_")]
            num_com += 1
            # Indicateur de progression
            if nb_com < 25000 and num_com > nb_com:
                break
            # sys.stdout.write("\r%.1f%%" % (100 * num_com / nb_com))
            with open(os.path.join(self.path_to_comments, com), encoding='utf8') as comment:
                commentaire = comment.read()
                commentaire = traiter(commentaire)
                film_id = get_film_id(com_id)
                writer(commentaire, film_id)
        print("\nFichiers films crées.")
