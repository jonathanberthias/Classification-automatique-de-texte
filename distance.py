"""Distance entre textes."""

import math


def filtrer_frequence_minimale(mots, stockeur_indices):
    """Filtre la liste de mots pour garder que ceux qui apparaissent assez."""
    return list(filter(stockeur_indices.est_assez_frequent, mots))


def plus_pertinents(num_mots, mots, stockeur_indices, utiliser_tfidf):
    """Renvoie la liste des n mots les plus pertinents avec le critère donné.

    :param num: nombre de mots à garder.
    :param mots: liste des mots à trier.
    :param stockeur_indices: objet StockeurIndicesTfIdf complet.
    :param utiliser_tfidf: si False: IDF, si True: TF-IDF
    """
    if utiliser_tfidf:
        func = stockeur_indices.get_max_tf_idf
    else:
        func = stockeur_indices.get_idf_mot
    mots_a_considerer = filtrer_frequence_minimale(mots, stockeur_indices)
    trie = sorted(mots_a_considerer, key=func, reverse=True)
    final = set(trie[:num_mots])
    return final


class StockeurDistances:
    """Classe pour stocker la distance entre vecteurs."""

    distances = {}


def distance_dictionnaires(prm, sec, cosinus=True,
                           prm_idx="", sec_idx=""):
    """Mesure la distance cosinus entre 2 dictionnaires.

    Inverse de la similarité cosinus.
    :param prm/sec: dictionnaires {mot: valeur}
    :params idx: identifiant des films pour mémoisation
    :cosinus: si vrai, distance cosinus, sinon distance euclidienne
                (au carré)
    """
    if prm_idx > sec_idx:
        prm_idx, sec_idx = sec_idx, prm_idx
    if (prm_idx, sec_idx) in StockeurDistances.distances.keys():
        return StockeurDistances.distances[(prm_idx, sec_idx)]

    if cosinus:
        num = sum([prm[i] * sec[i] for i in set(prm).intersection(set(sec))])
        norme_prm = sum((x * x for x in prm.values()))
        norme_sec = sum((x * x for x in sec.values()))
        denom = math.sqrt(norme_prm * norme_sec)
        if denom != 0.0:
            dist = 1.0 - num / denom
        else:
            dist = 1.0
    else:
        dist = sum([(prm.get(i, 0.0) - sec.get(i, 0.0))**2
                    for i in set(prm).union(set(sec))])
    if prm_idx and sec_idx:
        StockeurDistances.distances[(prm_idx, sec_idx)] = dist
    return dist
