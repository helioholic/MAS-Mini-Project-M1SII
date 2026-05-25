# =============================================================================
# FICHIER : maze.py
# RÔLE    : Définit le labyrinthe (la grille), les murs, le départ et l'arrivée
#           Ce fichier est PARTAGÉ par tous les agents — on ne le duplique pas
# =============================================================================

# -----------------------------------------------------------------------------
# Le labyrinthe est une grille 10x10
# Chaque cellule est soit :
#   0  = libre (on peut passer)
#   1  = mur   (bloqué)
# S = départ en (ligne=0, colonne=0)  → position (0,0)
# G = arrivée en (ligne=9, colonne=9) → position (9,9)
# -----------------------------------------------------------------------------

# La grille est lue depuis l'image de l'exercice
# Ligne par ligne, de haut en bas (ligne 0 = en haut)
MAZE = [
    # col: 0  1  2  3  4  5  6  7  8  9
           [0, 1, 0, 0, 1, 0, 0, 0, 0, 1],  # ligne 0  ← S est en (0,0)
           [0, 1, 0, 0, 1, 0, 1, 1, 0, 1],  # ligne 1
           [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # ligne 2
           [1, 0, 0, 0, 0, 0, 1, 0, 0, 1],  # ligne 3
           [0, 0, 0, 1, 0, 0, 1, 0, 1, 1],  # ligne 4
           [0, 0, 1, 1, 0, 0, 1, 0, 1, 0],  # ligne 5
           [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],  # ligne 6
           [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # ligne 7
           [0, 1, 0, 1, 0, 0, 0, 0, 1, 1],  # ligne 8
           [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # ligne 9  ← G est en (9,9)
]

# Taille de la grille
ROWS = len(MAZE)      # 10 lignes
COLS = len(MAZE[0])   # 10 colonnes

# Position de départ (S) et d'arrivée (G)
# Format : (ligne, colonne) → (row, col)
START = (0, 0)   # en haut à gauche
GOAL  = (9, 9)   # en bas à droite

# Les 4 directions possibles pour se déplacer
# Chaque direction = (delta_ligne, delta_colonne, nom_lisible)
DIRECTIONS = [
    (-1,  0, "HAUT"),   # monter   → on soustrait 1 à la ligne
    ( 1,  0, "BAS"),    # descendre → on ajoute 1 à la ligne
    ( 0, -1, "GAUCHE"), # aller à gauche → on soustrait 1 à la colonne
    ( 0,  1, "DROITE"), # aller à droite → on ajoute 1 à la colonne
]


def is_valid(row, col):
    """
    Vérifie si une position (row, col) est valide, c'est-à-dire :
      1. Elle est dans les limites de la grille (pas hors-bords)
      2. Ce n'est pas un mur (valeur = 0)

    Paramètres :
        row (int) : numéro de la ligne
        col (int) : numéro de la colonne

    Retourne :
        True  si on peut aller à cette case
        False si c'est un mur ou hors limites
    """
    # Vérifier les bornes de la grille
    if row < 0 or row >= ROWS:
        return False
    if col < 0 or col >= COLS:
        return False
    # Vérifier que ce n'est pas un mur
    if MAZE[row][col] == 1:
        return False
    return True


def get_neighbors(row, col):
    """
    Retourne la liste des voisins accessibles depuis la position (row, col).
    Un voisin est accessible s'il est valide (pas mur, pas hors-bords).

    Paramètres :
        row (int) : ligne actuelle
        col (int) : colonne actuelle

    Retourne :
        list de tuples (new_row, new_col, direction_name)
    """
    neighbors = []
    for dr, dc, direction_name in DIRECTIONS:
        new_row = row + dr
        new_col = col + dc
        if is_valid(new_row, new_col):
            neighbors.append((new_row, new_col, direction_name))
    return neighbors


def print_maze(path=None, visited=None, current=None):
    """
    Affiche le labyrinthe dans le TERMINAL en ASCII.
    Peut afficher en option :
      - Le chemin trouvé (liste de positions)
      - Les cases visitées
      - La position actuelle de l'agent

    Symboles utilisés :
        S  = départ
        G  = arrivée
        #  = mur
        .  = chemin trouvé
        o  = case visitée
        @  = position actuelle de l'agent
        espace = case libre

    Paramètres :
        path    (list) : liste de (row, col) formant le chemin solution
        visited (set)  : ensemble de (row, col) déjà explorées
        current (tuple): position actuelle (row, col) de l'agent
    """
    # Convertir en sets pour recherche rapide (O(1) au lieu de O(n))
    path_set    = set(path)    if path    else set()
    visited_set = set(visited) if visited else set()

    print("\n" + "=" * (COLS * 2 + 3))  # ligne de séparation

    for row in range(ROWS):
        print("|", end=" ")  # bord gauche
        for col in range(COLS):
            pos = (row, col)

            if pos == START:
                char = "S"          # départ
            elif pos == GOAL:
                char = "G"          # arrivée/but
            elif MAZE[row][col] == 1:
                char = "#"          # mur
            elif pos == current:
                char = "@"          # agent actuellement ici
            elif pos in path_set:
                char = "."          # fait partie du chemin solution
            elif pos in visited_set:
                char = "o"          # a été exploré
            else:
                char = " "          # case libre non visitée

            print(char, end=" ")
        print("|")  # bord droit

    print("=" * (COLS * 2 + 3))
    # Légende
    print("Légende: S=Départ  G=But  #=Mur  .=Chemin  o=Visité  @=Agent\n")

    