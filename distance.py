"""Distance entre textes."""

import math

def pertinence(n, stockeur):
    dico = stockeur.get_tous_idf()
    dicotrie = sorted(dico.keys(), key = dico.get, reverse=True)
    return set(dicotrie[:n])

def pertinence_tfidf(n, stockeur):
    tf_idf = stockeur.indices
    dico = {}
    for film, dic_mots in tf_idf.items():
        for mot, ind in dic_mots.items():
            if mot in dico:
                dico[mot] = max(dico[mot], ind)
            else:
                dico[mot] = ind
    dicotrie = sorted(dico.keys(), key = dico.get, reverse=True)
    return set(dicotrie[:n])


def TransformerTexteVect(film, mots_pertinents, compteur):
    """:param stockeur_frequences: Stockeur de frequences brutes"""
    d = {}
    mots_presents = set(compteur.keys())
    for mot in mots_pertinents:
        if mot in mots_presents:
            d[mot] = compteur[mot]
    return d

def get_dico_des_films(stockeur_frequences, mots_pertinents):
    dico = {}
    for film, occurences in stockeur_frequences.occurences.items():
        dico[film] = TransformerTexteVect(film, mots_pertinents, occurences)
    return dico

def Distance(v1, v2):
    Num = sum([v1[i]*v2[i] for i in set(v1).intersection(set(v2))])
    Denom = math.sqrt(sum([v1[i]**2 for i in v1]))*math.sqrt(sum([v2[i]**2 for i in v2]))
    if Denom != 0:
        return Num / Denom
    return 0


