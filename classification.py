"""Classification non supervisée."""

import random
import distance
import math




def kmeans(k, dictionnaire_des_films, mots_pertinents, centres = {}):

    centres = random.sample(dictionnaire_des_films.keys(), k)

    groupes = {c: [associateur.get_titre(c)] for c in centres}
    for film in dico_des_films.keys():
        if film not in centres:
            dist = {}
            for cen in centres:
                dist[cen] = distance.distance_vecteurs(
                    dico_des_films[film], dico_des_films[cen])
            mindist = min(dist.values())
            plus_proche = [c for c in centres if dist[c] == mindist][0]
            groupes[plus_proche].append(associateur.get_titre(film))

    changements = 1
    while changements != 0:
        changements = 0
        for i in range(k):
            moyenne_centres[i] = mean(mot for mot in groupes[i].values())
            # RAGE
            kmeans(k, groupes, mots_pertinents, centres)
    return groupes, centres


