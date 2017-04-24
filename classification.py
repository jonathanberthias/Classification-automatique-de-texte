"""Classification non supervisee."""

import random
import distance
import math



def classification(k, dictionnaire_des_films, mots_pertinents, centres):
    groupes = [[] for _ in range(len(centres))]
    for film in dictionnaire_des_films.keys():
        mindist = math.inf
        plus_proche = -1
        for i in range(len(centres)):
            dist = distance.distance_vecteurs(dictionnaire_des_films[film], centres[i])
            if dist <= mindist:
                mindist = dist
                plus_proche = i
        groupes[plus_proche].append(dictionnaire_des_films[film])
    return groupes


def dictionnaire_moyen(liste, mots_pertinents):
    if liste == []:
        return {}
    dico_moyen = {}
    for mot in mots_pertinents:
        moyenne = 0
        for i in range(len(liste)):
            if mot in liste[i]:
                moyenne += liste[i][mot]
        moyenne = moyenne / len(liste)
        dico_moyen[mot] = moyenne
    return dico_moyen


def generer_centres(k, dictionnaire_des_films):
    aleatoire = random.sample(dictionnaire_des_films.keys(), k)
    centres = [dictionnaire_des_films[a] for a in aleatoire]
    for i in range(k):
        trie = sorted(centres[i], key=centres[i].get)
        print(trie[:5])
    return centres

def determiner_nombre_groupes(films):
    """Détermine le nombre de groupes par mn/t (wikipédia)

    :param films: dictionnaire film: dico d'occurences
    """
    m = len(films.keys())
    mots = []
    t = 0
    for film, dico in films.items():
        mots.extend(dico.keys())
        t += len(dico.keys())
    n = len(set(mots))
    return int(m * n / t)



def kmeans(k, dictionnaire_des_films, mots_pertinents):
    # On ne classe que les films qui ont au moins un mot pertinent
    films_a_classer = {film: dico for film, dico in
                                  dictionnaire_des_films.items() if dico != {}}
    groupes_theoriques = determiner_nombre_groupes(films_a_classer)
    print("Nombre de groupes théoriques: %d" % groupes_theoriques)
    print("""Traitement de %d films sur %d au total, soit %.2f%%
          (les autres ne contiennent pas de mot pertinent)"""
          % (len(films_a_classer), len(dictionnaire_des_films),
             100*len(films_a_classer)/len(dictionnaire_des_films)))
    centres = generer_centres(k, films_a_classer)
    groupes = classification(k, films_a_classer, mots_pertinents, centres)
    total_SS = -1
    old_total_SS = math.inf
    moyenne = None
    tours = 0
    while total_SS < old_total_SS:
        if total_SS != -1:
            print("total is %f" % total_SS)
            old_total_SS = total_SS
        moyenne = [0]*k
        for i in range(k):
            moyenne[i] = dictionnaire_moyen(groupes[i], mots_pertinents)
        new_groupes = classification(k, films_a_classer, mots_pertinents, moyenne)
        total_SS = total_sum_of_squares(new_groupes, moyenne)
        tours += 1
        print("current: %f\told: %f" % (total_SS, old_total_SS))
    print("%d boucles" % tours)
    return new_groupes, moyenne


def sum_of_squares(liste_de_films, centre):
    return sum([distance.distance_vecteurs(film, centre) for film in liste_de_films])


def total_sum_of_squares(groupes, centres):
    total = 0
    for i in range(len(groupes)):
        total += sum_of_squares(groupes[i], centres[i])
    return total
