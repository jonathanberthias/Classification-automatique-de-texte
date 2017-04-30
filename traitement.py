"""Traitement des fichiers.

Pour chaque commentaire, lemmatiser les mots et écrire le résultat dans le
fichier du film qui lui correspond.
"""

import os
import re
import shutil
import sys
import time

import nltk


class AssociateurCommentairesFilms:
    """Lit le fichier d'index et stock le film associé à chaque commentaire."""

    def __init__(self, path_to_index):
        """Crée le répertoire entre les comentaires et les films associés.

        `comment_film` est un dictionnaire qui à chaque commentaire associe
                       l'identifiant du film qui lui correspond.
        `film_titre` est un dictionnaire qui à chaque identifiant de film
                     associe son titre.

        :param path_to_index: chemin relatif de ce fichier au fichier
        d'index.
        """
        self.comment_film = {}
        self.film_titre = {}
        self.notes = {}
        if not os.path.exists(path_to_index):
            raise IOError("Pas d'index au chemin: %s" % path_to_index)
        print("Chemin vers l'index: %s" % path_to_index)
        with open(path_to_index, 'r', encoding='utf8') as index:
            for ligne in index.readlines():
                vals = ligne.split(':')
                comment_id = vals[0]
                film_id = vals[1]
                titre = vals[2].strip()
                self.comment_film[comment_id] = film_id
                self.film_titre[film_id] = titre

    def get_film(self, comment_id):
        """Renvoie l'identifiant du film associé au commentaire donné."""
        if comment_id in self.comment_film:
            return self.comment_film[comment_id]
        raise IndexError(
            "Le commentaire %s n'est pas associé à un film." % comment_id)

    def get_titre(self, film_id):
        """Renvoie le titre du film correspondant."""
        if film_id in self.film_titre:
            return self.film_titre[film_id]
        raise IndexError("Le film %s n'a pas de titre." % film_id)


class TraiteurCommentaire:
    """Nettoie et lemmatise les commentaires."""

    def __init__(self):
        """Initialise le lemmatiseur et l'expression régulière."""
        self.lemmatiseur = nltk.stem.WordNetLemmatizer()
        # Ne garde que les caractères alphanumériques
        self.pattern = re.compile(r'[\W_]+')

    def traiter_commentaire(self, comment):
        """Renvoie le commentaire entièrement nettoyé."""
        clean_comment = self._enlever_tags(comment)
        clean_comment = self._enlever_ponctuation(clean_comment)
        clean_comment = self._lemmatiser(clean_comment.strip().split())
        return clean_comment

    def _enlever_tags(self, comment):
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
        fin = self._enlever_tags(comment[fermeture + 1:])
        return debut + fin

    def _enlever_ponctuation(self, comment):
        """Nettoie la ponctuation et remplace par des espaces."""
        return self.pattern.sub(' ', comment.lower())

    def _lemmatiser(self, mots):
        """Lemmatise une liste de mots."""
        return " ".join([self.lemmatiseur.lemmatize(mot) for mot in mots])


class EcriveurFichiersFilms:
    """Crée les fichiers des films."""

    def __init__(self, path_to_films, path_to_moyennes):
        """Crée le dossier pour stocker les films.

        Renvoie 1 si un nouveau fichier film a été crée, 0 sinon.
        """
        self.chemin_films = path_to_films
        if os.path.exists(self.chemin_films):
            # On supprime les fichiers qui existent déjà
            shutil.rmtree(self.chemin_films)
        os.makedirs(self.chemin_films)
        self.chemin_moyennes = path_to_moyennes

    def ecrire_commentaire(self, comment, film_id):
        """Ecrit le commentaire pour le film donné."""
        fichier = os.path.join(self.chemin_films, film_id)
        if os.path.exists(fichier):
            # 'utf8' pour éviter les problèmes d'encodage/décodage
            with open(fichier, 'a', encoding='utf8') as film:
                film.write("\n")
                film.write(comment)
            return 0
        else:
            with open(fichier, 'w', encoding='utf8') as film:
                film.write(comment)
            return 1

    def ecrire_moyennes(self, moyennes):
        """Ecrire un fichier pour stocker la note moyenne de chaque film."""
        with open(self.chemin_moyennes, 'w', encoding='utf8') as fichier:
            for film, moyenne in moyennes.items():
                fichier.write("%s:%.2f\n" % (film, moyenne))


class Traitement:
    """Traite les commentaires et les range nettoyés dans le bon fichier."""

    def __init__(self, path_to_comments, path_to_films, path_to_moyennes):
        """Initialise le traiteur.

        :param path_to_comments: chemin vers les commentaires
        :param path_to_films: chemin vers les films
        ;param path_to_moyennes: chemin vers le fichier de moyennes
        """
        self.path_to_comments = path_to_comments
        self.path_to_films = path_to_films
        self.path_to_moyennes = path_to_moyennes
        print("Chemin vers les commentaires: %s" % self.path_to_comments)
        print("Chemin vers les films: %s" % self.path_to_films)
        print("Chemin vers les moyennes: %s" % self.path_to_moyennes)

    def traiter(self, nb_com=25000, progress=True, associateur=None):
        """Effectue l'ensemble du traitement pour tous les commentaires."""
        traiteur = TraiteurCommentaire()
        writer = EcriveurFichiersFilms(self.path_to_films,
                                       self.path_to_moyennes)
        notes = {}
        notes_moyennes = {}

        num_com = 0
        num_films = 0
        print("Ecriture des fichiers film.")
        debut = time.time()
        for com in os.listdir(self.path_to_comments):
            sep = com.find("_")
            com_id = com[:sep]
            # Note entre 1 et 10
            note = com[sep + 1:com.find('.')]
            num_com += 1
            if num_com > nb_com:
                break
            # Indicateur de progression
            if progress:
                sys.stdout.write("\r%.1f%%" % (100 * num_com / nb_com))

            comment_path = os.path.join(self.path_to_comments, com)
            with open(comment_path, encoding='utf8') as comment:
                commentaire = comment.read()
                commentaire = traiteur.traiter_commentaire(commentaire)
                film_id = associateur.get_film(com_id)
                num_films += writer.ecrire_commentaire(commentaire, film_id)
                notes[film_id] = notes.get(film_id, []) + [note]
        for film, notes_film in notes.items():
            nb_com_film = len(notes_film)
            moyenne = sum(map(int, notes_film)) / nb_com_film
            notes_moyennes[film] = moyenne
        writer.ecrire_moyennes(notes_moyennes)
        print("\n%d commentaires traités et %d fichiers film créés en %.3fs." %
              (nb_com, num_films, (time.time() - debut)))
        return notes_moyennes
