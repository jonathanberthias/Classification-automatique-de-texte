"""Classification non supervisée."""

import random

import distance


def kmeans(k, dico_des_films, associateur):
    """Algorithme de k-means simple."""
    centres = random.sample(dico_des_films.keys(), k)
    groupes = {c: [c] for c in centres}
    for film in dico_des_films.keys():
        if film not in centres:
            dist = {}
            for cen in centres:
                dist[cen] = distance.distance_vecteurs(
                    dico_des_films[film], dico_des_films[cen])
            mindist = min(dist.values())
            plus_proche = [c for c in centres if dist[c] == mindist][0]
            groupes[plus_proche].append(associateur.get_titre(film))
    return groupes
