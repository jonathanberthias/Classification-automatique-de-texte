"""Distance entre textes."""

import math


def filtrer_frequence_minimale(stockeur, occ_min):
    return [mot for mot in stockeur.keys() if stockeur[mot] >= occ_min]


def pertinence(num_mots, stockeur):
    """Renvoie la liste des n mots les plus pertinents avec l'IDF.

    :param num_mots: nombre de mots à garder.
    :param stockeur: objet StockeurIndicesTfIdf complet.
    """
    dico = stockeur.get_tous_idf()
    print("%d mots au total." % len(dico.keys()))
    dicotrie = sorted(dico.keys(), key=dico.get, reverse=True)
    coef = 2
    return set(dicotrie[coef*num_mots:(coef+1)*num_mots])


def pertinence_tfidf(num, stockeur):
    """Renvoie la liste des n mots les plus pertinents avec le TF-IDF.

    :param num: nombre de mots à garder.
    :param stockeur: objet StockeurIndicesTfIdf complet.
    """
    mots_a_considerer = filtrer_frequence_minimale(stockeur.stockeur_freq.compte_total(), 50)
    tf_idf = stockeur.indices
    dico = {}
    for dic_mots in tf_idf.values():
        for mot, ind in dic_mots.items():
            if mot in dico and mot in mots_a_considerer:
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
    for film, occurences in stockeur_frequences.items():
        dico[film] = filtrer_pertinents(mots_pertinents, occurences)
    return dico


def distance_vecteurs(prem, sec):
    """Calcule la distance cosinus entre 2 dictionnaires."""
    num = sum([prem.get(i, 0) * sec.get(i, 0) for i in set(prem).union(set(sec))])
    denom = math.sqrt(sum([prem[i]**2 for i in prem]) *
                      sum([sec[i]**2 for i in sec]))
    if denom != 0:
        return num / denom
    return math.inf
