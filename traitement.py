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

    a_garder = ["VB", "VBP", "NN", "JJ", "NNP", "ADJ", "NUM", "NOUN", "VERB"]

    # frozenset pour accès rapide rapide à une liste immuable
    # liste des mots inutiles les pus fréquents
    mots_trop_frequents = frozenset([
        'thi', 'movy', 'hav', 'ar', 'al', 'act', 'lik', 'ev', 'ther', 'tim',
        'mak', 'som', 'mor', 'charact', 'story', 'wer', 'wel', 'com', 'oth',
        'scen', 'bad', 'lov', 'wil', 'gre', 'peopl', 'direct', 'mad', 'becaus',
        'think', 'tak', 'giv', 'aft', 'plot', 'ov', 'lif', 'nev', 'littl',
        'best', 'wher', 'bet', 'doe', 'stil', 'yo', 'fin', 'writ', 'perform',
        'sery', 'thes', 'kil', 'whil', 'old', 'someth', 'rol', 'car',
        'interest', 'tru', 'star', 'thos', 'wom', 'cast', 'though', 'liv',
        'sam', 'funny', 'mus', 'anoth', 'bef', 'noth', 'try', '10', 'view',
        'start', 'believ', 'young', 'produc', 'hum', 'girl', 'again', 'origin',
        'long', 'turn', 'hor', 'lat', 'quit', 'lin', 'friend', 'minut',
        'comedy', 'pretty', 'wond', 'hap', 'sur', 'high', 'effect', 'howev',
        'hard', 'laugh', 'bas', 'fan', 'person', 'famy', 'ear', 'nee', 'tel',
        'beauty', 'becom', 'alway', 'class', 'mom', 'kid', 'sint', 'whol',
        'complet', 'mean', 'cre', 'plac', 'lead', 'script', 'expect', 'diff',
        'shot', 'book', 'mat', 'anyth', 'nam', 'prob', 'begin', 'cal', 'tal',
        '2', 'entertain', 'fun', 'run', 'sex', 'sens', 'tv', 'mov', 'art',
        'hop', 'rath', 'worst', 'anyon', 'audy', 'bor', 'poor', 'episod', 'rat',
        'war', 'spec', 'rel', 'op', 'appear', 'dialog', 'miss', 'keep',
        'surpr', 'espec', 'cours', 'second', 'anim', 'fac', 'nat', 'wor',
        'goe', 'perfect', 'vert', 'gen', 'money', 'mind', 'someon', 'problem',
        'nic', 'dvd', 'mayb', 'tri', 'ont', 'hous', 'typ', 'everyth', 'night',
        'aw', 'three', 'follow', 'boy', 'ful', 'recommend', 'suppos', 'ag',
        'leav', 'hand', 'excel', 'wast', 'togeth', 'dur', 'hom', 'dram',
        'obvy', 'sound', 'everyon', 'certain', 'john', 'fath', 'top', 'ad',
        '1', 'ey', 'decid', 'cut', 'fight', 'less', 'fal', 'review', 'terr',
        'hour', 'talk', 'ment', 'left', 'wif', 'black', 'understand', 'murd',
        'dead', 'head', 'includ', 'styl', 'rememb', 'chang', 'entir', 'els',
        'ide', 'pleas', 'sev', 'hist', 'stat', 'pow', 'clos', 'releas', 'pict',
        'rom', 'piec', 'involv', 'feat', 'tot', 'budget', 'non', 'pres',
        'poss', 'sav', 'attempt', 'hollywood', 'cinem', 'disappoint',
        'stupid', 'song', 'dea', 'sad', 'portray', 'expery', '3', 'coupl',
        'eith', 'video', 'definit', 'absolv', 'exceiv', 'abl', 'cop', 'cas',
        'easy', 'success', 'consid', 'lack', 'word', 'particul', 'child',
        'sci', 'amaz', 'fail', 'titl', 'until', 'camer', 'mess', 'along',
        'form', 'dark', 'loc', 'smal', 'hat', 'clear', 'emot', 'jok', 'dant',
        'adv', 'sort', 'viol', 'bring', 'next', 'cam', 'heart', 'light',
        'broth', 'gam', 'won', 'perhap', 'slow', 'near', 'flick', 'develop',
        'school', 'par', 'qual', 'pass', 'walk', 'moth', 'oft', 'vis', 'sequ',
        'sil', 'doing', 'meet', 'hil', 'imagin', 'ye', 'actress', 'bril',
        'sid', 'ex', 'horr', 'whit', 'unfortun', 'guess', 'el', 'itself',
        'sit', 'lost', 'exampl', 'stop', 'hero', 'forc', 'son', 'numb',
        'felt', 'impress', 'quest', 'childr', 'support', 'hit', 'ask',
        'couldn', 'rent', 'extrem', 'pol', 'wors', 'voic', 'und', 'against',
        'stand', 'evil', 'went', 'min', 'oh', 'somewh', 'mr', 'wait',
        'overal', 'list', 'favorit', 'mystery', 'un', 'edit', 'past',
        'already', '5', 'learn', 'spoil', '4', 'michael', 'marry', 'genr',
        'despit', 'deal', 'throughout', 'win', 'town', 'del', 'driv',
        'happy', 'dec', 'mem', 'teen', 'self', 'daught', 'mil', 'wish',
        'twist', 'credit', 'cult', 'annoy', 'soon', 'sing', 'touch', 'b',
        'city', 'today', 'sometim', 'simpl', 'behind', 'god', 'bil',
        'deserv', 'tre', 'bar', 'stay', 'zomby', 'pac', 'chant', 'blood',
        'novel', 'crit', 'plan', 'stuff', 'docu', 'comp', 'anyway', 'app',
        'import', 'ord', 'fil', 'body', 'gav', 'myself', 'hel', 'incred',
        'etc', 'level', 'fig', 'scor', 'er', 'exact', 'dream', 'maj', 'situ',
        'speak', 'die', 'themselv', 'capt', 'los', 'return', 'pet', 'hold',
        'room', 'shoot', 'ridic', 'group', 'lady', 'thank', 'tend',
        'cinematograph', 'acc', 'jam', 'break', 'pain', 'cont', 'fem',
        'heard', 'pick', 'rec', 'convint', 'robert', 'rock', 'husband',
        'valu', 'polit', 'took', 'simil', 'cannot', 'strong', 'predict',
        'fair', 'four', 'country', 'continu', 'known', 'hug', 'shock', 'im',
        'gor', 'cent', 'mot', 'season', 'fam', 'alon', 'told', 'opin',
        'wouldn', 'crap', 'hear', 'ten', 'result', 'caus'
    ])

    lemmatiseur_func = nltk.stem.LancasterStemmer().stem

    pattern = re.compile(r'[\W_]+')

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
        clean_comment = TraiteurCommentaires.pattern.sub(' ', comment.lower())
        """ Classification grammaticale de chaque mot.
        tokenized = word_tokenize(clean_comment)
        tokens = nltk.pos_tag(tokenized)
        to_keep = (x[0] for x in tokens if x[1]
                   in TraiteurCommentaires.a_garder and x[0] not in
                   TraiteurCommentaires.mots_a_enlever)
        lemmes = (TraiteurCommentaires._lemmatiser(x) for x in to_keep)
        ret = " ".join(lemmes)
        """
        # On lemmatise chaque mot et on garde que si il est pas trop fréquent.
        to_keep = filter(lambda x: x not in
                         TraiteurCommentaires.mots_trop_frequents, map(
                             TraiteurCommentaires.lemmatiseur_func,
                             clean_comment.split()))
        return " ".join(to_keep)

    @staticmethod
    def _lemmatiser(mot):
        """Lemmatise un mot."""
        return TraiteurCommentaires.lemmatiseur_func(mot)


class EcriveurFichiersFilms:
    """Crée les fichiers des films."""

    def __init__(self, path_to_folder):
        """Crée le dossier pour stocker les films.

        Renvoie 1 si un nouveau fichier film a été crée, 0 sinon.
        """
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
            return 0
        else:
            with open(fichier, 'w', encoding='utf8') as film:
                film.write(comment)
            return 1


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
        debut = time.time()

        get_film_id = AssociateurCommentairesFilms(
            self.path_to_index).get_film
        print("Répertoire créé en %.3fs." % (time.time() - debut))
        writer = EcriveurFichiersFilms(
            self.path_to_films).ecrire_commentaire

        traiter = TraiteurCommentaires.traiter_commentaire
        num_com = 0
        num_films = 0
        print("Ecriture des fichiers film.")
        debut = time.time()
        for com in os.listdir(self.path_to_comments):
            com_id = com[:com.find("_")]
            num_com += 1
            if num_com > nb_com:
                break
            # Indicateur de progression
            sys.stdout.write("\r%.1f%%" % (100 * num_com / nb_com))

            comment_path = os.path.join(self.path_to_comments, com)
            with open(comment_path, encoding='utf8') as comment:
                commentaire = comment.read()
                commentaire = traiter(commentaire)
                film_id = get_film_id(com_id)
                num_films += writer(commentaire, film_id)
        print("\n%d commentaires traités et %d fichiers film créés en %.3fs." %
              (nb_com, num_films, (time.time() - debut)))
