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
    trie = sorted(filtrer_frequence_minimale(
        mots, stockeur_indices), key=func, reverse=True)
    return set(trie[:num_mots])


def filtrer_dictionnaire_mots(mots_pertinents, dictionnaire):
    """Renvoie un compteur avec seulement les mots pertinents.

    :param mots_pertinents: liste des mots à garder
    :param dictionnaire: dictionnaire associé aux mots d'un film
    """
    cles_a_garder = filter(lambda x: x in mots_pertinents, dictionnaire.keys())
    return {x: dictionnaire[x] for x in cles_a_garder}


def distance_dictionnaires(prm, sec, cosinus=True):
    """Mesure la distance cosinus entre 2 dictionnaires.

    Inverse de la similarité cosinus.
    :params: dictionnaires {mot: valeur}
    :cosinus: si vrai, distance cosinus, sinon distance euclidienne (au carré)
    """
    if cosinus:
        num = sum([prm[i] * sec[i] for i in set(prm).intersection(set(sec))])
        norme_prm = sum((x * x for x in prm.values()))
        norme_sec = sum((x * x for x in sec.values()))
        denom = math.sqrt(norme_prm * norme_sec)
        if denom != 0:
            return 1 - num / denom
        return 1
    else:
        return sum([(prm.get(i, 0) - sec.get(i, 0))**2
                    for i in set(prm).union(set(sec))])
