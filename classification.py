"""Classification non supervisee."""

import math
import random

import distance


def filtrer_films_non_vides(liste_films, mots_pertinents, stockeur_indices):
    """Renvoie la liste des films non vides pour les mots donnés."""
    return list(filter(lambda x: stockeur_indices.get_indices_tfidf_mots_filtres
                       (x, mots_pertinents) != {}, liste_films))


def dictionnaire_moyen(liste_films, mots_pertinents, stockeur_indices):
    """Renvoie le centre d'un groupe."""
    nb_films = len(liste_films)
    if nb_films == 0:
        # Aucun film dans la liste
        return {}
    dico_total = {}
    for id_film in liste_films:
        dico_filtre = stockeur_indices.get_indices_tfidf_mots_filtres(
            id_film, mots_pertinents)
        for mot, indice in dico_filtre.items():
            dico_total[mot] = dico_total.get(mot, 0.0) + indice
    return {x: y / nb_films for x, y in dico_total.items()}


def generer_centres(num_gps, liste_films, mots_pertinents, stockeur_indices):
    """Renvoie la liste des dictionnaires des centres."""
    if num_gps > len(liste_films):
        raise ValueError("Impossible de former %d groupes avec %d films." %
                         (num_gps, len(liste_films)))
    films_aleatoires = random.sample(liste_films, num_gps)
    centres = [stockeur_indices.get_indices_tfidf_mots_filtres(
        a, mots_pertinents) for a in films_aleatoires]
    return centres


def classification(films_a_classer, liste_centres, mots_pertinents,
                   distance_cosinus, stockeur_indices):
    """Renvoie une matrice de la composition de chaque groupe."""
    groupes = [[] for _ in range(len(liste_centres))]
    total_ss = 0
    for film_id in films_a_classer:
        mindist = math.inf
        plus_proche = -1
        indices_film = stockeur_indices.get_indices_tfidf_mots_filtres(
            film_id, mots_pertinents)
        for index, dico_centre in enumerate(liste_centres):
            dist = distance.distance_dictionnaires(
                indices_film, dico_centre, distance_cosinus)
            if dist <= mindist:
                mindist = dist
                plus_proche = index
        total_ss += mindist**2
        groupes[plus_proche].append(film_id)
    return groupes, total_ss


def kmeans(nb_groupes, liste_films, mots_pertinents,
           distance_cosinus, stockeur_indices):
    """Effectue le kmeans."""
    films_a_classer = filtrer_films_non_vides(
        liste_films, mots_pertinents, stockeur_indices)
    print("""\nTraitement de %d films sur %d au total, soit %.f%%\
    (les autres ne contiennent pas de mot pertinent)"""
          % (len(films_a_classer), len(liste_films),
             100 * len(films_a_classer) / len(liste_films)))

    centres = generer_centres(
        nb_groupes, films_a_classer, mots_pertinents, stockeur_indices)
    groupes = classification(films_a_classer, centres, mots_pertinents,
                             distance_cosinus, stockeur_indices)
    total_ss = -1
    old_total_ss = math.inf
    tours = 0
    while total_ss < old_total_ss:
        print(".", end="")
        if total_ss != -1:
            old_total_ss = total_ss
            for index_groupe, liste_films_groupe in enumerate(groupes):
                centres[index_groupe] = dictionnaire_moyen(
                    liste_films_groupe, mots_pertinents, stockeur_indices)
        groupes, total_ss = classification(
            films_a_classer, centres, mots_pertinents,
            distance_cosinus, stockeur_indices)
        tours += 1
    print("%d boucles" % tours)
    return groupes, centres
