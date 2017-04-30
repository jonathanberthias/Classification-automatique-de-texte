"""Inférence de la note d'un film grâce à ses voisins les plus proches."""

import math
import random

import distance


def recuperer_moyennes(path_to_moyennes):
    """Lit le fichier des moyennes et récupère les moyennes.

    :param path_to_moyennes: chemin vers le fichier des moyennes.
    """
    moyennes = {}
    with open(path_to_moyennes, 'r') as fichier:
        for ligne in fichier.readlines():
            sep = ligne.find(':')
            film = ligne[:sep]
            note = float(ligne[sep + 1:-2])
            moyennes[film] = note
    return moyennes


def referents(nb_ref, liste_films):
    return random.sample(liste_films, nb_ref)


def plus_proches(film_id, nb_proches, references,
                 mots_pertinents, stockeur_indices):
    """Trouve les plus prohes voisins d'un film."""
    distances = {}
    dict_film = stockeur_indices.get_indices_tfidf_mots_filtres(
        film_id, mots_pertinents)
    for ref in references:
        dict_ref = stockeur_indices.get_indices_tfidf_mots_filtres(
            ref, mots_pertinents)
        distances[ref] = distance.distance_dictionnaires(
            dict_ref, dict_film, True, ref, film_id)
    closest = sorted(distances.keys(), key=distances.get)[:nb_proches]
    return {x: distances[x] for x in closest}


def devine_note(film_id, nb_proches, references, mots_pertinents,
                moyennes, stockeur_indices):
    plus_pres = plus_proches(film_id, nb_proches, references,
                             mots_pertinents, stockeur_indices)
    # Coefficientage
    dist_totale = 0
    score = 0
    for film, dist in plus_pres.items():
        moy_film = moyennes[film]
        score += (1 - dist) * moy_film
        dist_totale += 1 - dist
    if dist_totale == 0:
        return -50
    return score / dist_totale


def devine_toutes_notes(path_to_moyennes, nb_proches, nb_ref, tolerence,
                        liste_films, mots_pertinents, stockeur_indices):
    moyennes = recuperer_moyennes(path_to_moyennes)
    references = referents(nb_ref, liste_films)
    unaccountables = 0
    correct = 0
    for film in liste_films:
        if film not in references:
            guess = devine_note(film, nb_proches, references,
                                mots_pertinents, moyennes, stockeur_indices)
            if guess < 0:
                unaccountables += 1
                continue
            vraie = moyennes[film]
            difference = abs(guess - vraie)
            if difference <= tolerence:
                correct += 1
    vrai_taux = correct / (len(liste_films) - nb_ref)
    taux_corrige = correct / (len(liste_films) - nb_ref - unaccountables)
    return vrai_taux, taux_corrige
