"""Distance entre textes."""

import math


def pertinence(num, stockeur):
    """Renvoie la liste des n mots les plus pertinents avec l'IDF.

    :param n: nombre de mots à garder.
    :param stockeur: objet StockeurIndicesTfIdf complet.
    """
    dico = stockeur.get_tous_idf()
    dicotrie = sorted(dico.keys(), key=dico.get, reverse=True)
    return set(dicotrie[:num])


def pertinence_tfidf(num, stockeur):
    """Renvoie la liste des n mots les plus pertinents avec le TF-IDF.

    :param n: nombre de mots à garder.
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
    d = {}
    mots_presents = set(compteur.keys())
    for mot in mots_pertinents:
        if mot in mots_presents:
            d[mot] = compteur[mot]
    return d


def get_dico_des_films(stockeur_frequences, mots_pertinents):
    dico = {}
    for film, occurences in stockeur_frequences.occurences.items():
        dico[film] = filtrer_pertinents(mots_pertinents, occurences)
    return dico


def distance_vecteurs(v1, v2):
    num = sum([v1[i] * v2[i] for i in set(v1).intersection(set(v2))])
    denom = math.sqrt(sum([v1[i]**2 for i in v1])) * \
        math.sqrt(sum([v2[i]**2 for i in v2]))
    if denom != 0:
        return num / denom
    return 0
