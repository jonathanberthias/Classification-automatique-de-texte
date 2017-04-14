"""Distance entre textes."""

import math


def pertinence(num_mots, stockeur):
    """Renvoie la liste des n mots les plus pertinents avec l'IDF.

    :param num_mots: nombre de mots à garder.
    :param stockeur: objet StockeurIndicesTfIdf complet.
    """
    dico = stockeur.get_tous_idf()
    dicotrie = sorted(dico.keys(), key=dico.get, reverse=True)
    return set(dicotrie[:num_mots])


def pertinence_tfidf(num, stockeur):
    """Renvoie la liste des n mots les plus pertinents avec le TF-IDF.

    :param num: nombre de mots à garder.
    :param stockeur: objet StockeurIndicesTfIdf complet.
    """
    tf_idf = stockeur.indices
    dico = {}
    for dic_mots in tf_idf.values():
        for mot, ind in dic_mots.items():
            if mot in dico:
                dico[mot] = max(dico[mot], ind)
            else:
                dico[mot] = ind
    dicotrie = sorted(dico.keys(), key=dico.get, reverse=True)
    return set(dicotrie[:num])


def filtrer_pertinents(mots_pertinents, compteur):
    """Renvoie un compteur avec seulement les mots pertinents.

    :param mots_pertinents: liste des mots à garder
    :param compteur:  compteur des mots d'un film
    """
    cles_a_garder = filter(lambda x: x in mots_pertinents, compteur.keys())
    return {x: compteur[x] for x in cles_a_garder}


def get_dico_des_films(stockeur_frequences, mots_pertinents):
    """Filtre le dictionnaire d'occurences pour tous les films.

    :renvoie: dictionnaire qui à chaque film associe son compte d'occurences
              pour les mots pertinents.
    """
    dico = {}
    for film, occurences in stockeur_frequences.occurences.items():
        dico[film] = filtrer_pertinents(mots_pertinents, occurences)
    return dico


def distance_vecteurs(prem, sec):
    """Calcule la distance cosinus entre 2 dictionnaires."""
    num = sum([prem[i] * sec[i] for i in set(prem).intersection(set(sec))])
    denom = math.sqrt(sum([prem[i]**2 for i in prem]) *
                      sum([sec[i]**2 for i in sec]))
    if denom != 0:
        return num / denom
    return math.inf
