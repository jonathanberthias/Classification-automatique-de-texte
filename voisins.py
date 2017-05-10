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
            sep = ligne.strip().split(':')
            film = sep[0]
            note = float(sep[1])
            moyennes[film] = note
    return moyennes


def referents(nb_ref, liste_films):
    """Renvoie une liste de films choisis au hasard."""
    return random.sample(liste_films, nb_ref)


def plus_proches(film_id, nb_proches, references,
                 mots_pertinents, stockeur_indices):
    """Trouve les plus proches voisins d'un film."""
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
    """Essaye de deviner la note d'un film à partir de ses voisins.

    Coefficiente les voisins par leur distance.
    """
    plus_pres = plus_proches(film_id, nb_proches, references,
                             mots_pertinents, stockeur_indices)
    dist_totale = 0
    score = 0
    for film, dist in plus_pres.items():
        moy_film = moyennes[film]
        score += (1 - dist) * moy_film
        dist_totale += 1 - dist
    if dist_totale == 0:
        return -1
    return score / dist_totale


def devine_toutes_notes(path_to_moyennes, nb_proches, nb_ref, tolerence,
                        liste_films, mots_pertinents, stockeur_indices, asso):
    """Essaye de prédire la note de tous les films."""
    moyennes = recuperer_moyennes(path_to_moyennes)
    references = referents(nb_ref, liste_films)
    unaccountables = 0
    correct = 0
    diff_totale = 0.0
    for film in liste_films:
        if film not in references:
            guess = devine_note(film, nb_proches, references,
                                mots_pertinents, moyennes, stockeur_indices)
            if guess < 0:
                unaccountables += 1
                continue
            vraie = moyennes[film]
            difference = abs(guess - vraie)
            diff_totale += difference ** 2
            if correct < 10:
                print("%-50s\tPrediction: %.2f\tVraie: %.2f\tDiff: %.2f" %
                      (asso.get_titre(film), guess, vraie, difference))
            if difference <= tolerence:
                correct += 1
    vrai_taux = correct / (len(liste_films) - nb_ref)
    taux_corrige = correct / (len(liste_films) - nb_ref - unaccountables)
    diff_moyenne = math.sqrt(diff_totale / (len(liste_films) - nb_ref))
    return vrai_taux, taux_corrige, diff_moyenne
