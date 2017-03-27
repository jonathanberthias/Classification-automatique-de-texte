"""Classification non supervisée."""

import random
import distance

def kmeans(k, dico_des_films, associateur):
    centres = random.sample(dico_des_films.keys(), k)
    groupes = {c:[c] for c in centres}
    for film, mots in dico_des_films.items():
        if film not in centres:
            dist = {}
            for c in centres:
                dist[c] = distance.Distance(dico_des_films[film], dico_des_films[c])
            mindist = min(dist.values())
            plus_proche = [c for c in centres if dist[c] == mindist][0]
            groupes[plus_proche].append(associateur.get_titre(film))
    return groupes


