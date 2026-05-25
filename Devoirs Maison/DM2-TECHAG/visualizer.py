# =============================================================================
# FICHIER : visualizer.py
# RÔLE    : Affichage graphique du labyrinthe avec matplotlib
#           Ce fichier gère DEUX modes d'affichage :
#             1. Statique  → montre le labyrinthe + chemin final
#             2. Animé     → montre l'agent se déplacer case par case
#
# COMMENT ACTIVER/DÉSACTIVER :
#   Dans chaque fichier agent (ex: reflex_agent.py), tu trouveras :
#
#   # ---- AFFICHAGE TERMINAL (décommenter pour activer) ----
#   # print_maze(path=solution)
#
#   # ---- AFFICHAGE STATIQUE matplotlib (décommenter pour activer) ----
#   # show_static(path=solution)
#
#   # ---- AFFICHAGE ANIMÉ matplotlib (décommenter pour activer) ----
#   # show_animated(path=solution)
#
#   Il suffit d'enlever le # devant la ligne que tu veux utiliser !
# =============================================================================

import matplotlib.pyplot as plt          # bibliothèque de graphiques
import matplotlib.patches as mpatches    # pour créer les légendes colorées
import matplotlib.animation as animation # pour animer l'agent
import numpy as np                       # pour créer la matrice de couleurs

from maze import MAZE, START, GOAL, ROWS, COLS  # on importe le labyrinthe


# -----------------------------------------------------------------------------
# Palette de couleurs utilisée dans les graphiques
# Chaque couleur correspond à un type de case
# -----------------------------------------------------------------------------
COLORS = {
    "wall":    [0.40, 0.10, 0.15],  # bordeaux foncé  → mur
    "free":    [1.00, 1.00, 1.00],  # blanc           → case libre
    "start":   [0.20, 0.80, 0.20],  # vert vif        → départ S
    "goal":    [1.00, 0.30, 0.10],  # orange-rouge    → arrivée G
    "path":    [0.30, 0.60, 1.00],  # bleu clair      → chemin solution
    "visited": [0.85, 0.85, 0.95],  # gris très clair → cases explorées
    "agent":   [1.00, 0.85, 0.00],  # jaune vif       → position de l'agent
}


def build_color_grid(path=None, visited=None, current=None):
    """
    Construit une matrice numpy de couleurs RGB pour matplotlib.
    Chaque case (row, col) reçoit une couleur selon son type.

    Paramètres :
        path    (list)  : liste ordonnée de (row, col) = chemin solution
        visited (set)   : cases déjà explorées par l'agent
        current (tuple) : position actuelle (row, col) de l'agent

    Retourne :
        grid (numpy array) de forme (ROWS, COLS, 3) → image RGB
    """
    # Créer une grille vide (toutes les cases blanches par défaut)
    grid = np.ones((ROWS, COLS, 3))

    # Convertir en sets pour accès rapide
    path_set    = set(path)    if path    else set()
    visited_set = set(visited) if visited else set()

    for row in range(ROWS):
        for col in range(COLS):
            pos = (row, col)

            if MAZE[row][col] == 1:
                grid[row, col] = COLORS["wall"]       # mur
            elif pos == START:
                grid[row, col] = COLORS["start"]      # départ
            elif pos == GOAL:
                grid[row, col] = COLORS["goal"]       # arrivée
            elif pos == current:
                grid[row, col] = COLORS["agent"]      # agent ici
            elif pos in path_set:
                grid[row, col] = COLORS["path"]       # chemin solution
            elif pos in visited_set:
                grid[row, col] = COLORS["visited"]    # exploré

    return grid


def show_static(path=None, visited=None, title="Labyrinthe"):
    """
    AFFICHAGE STATIQUE : montre le labyrinthe avec le chemin final.
    Utile pour voir le résultat d'un algorithme après exécution.

    ╔══════════════════════════════════════════════╗
    ║  Pour utiliser : décommenter dans l'agent    ║
    ║  # show_static(path=mon_chemin)              ║
    ╚══════════════════════════════════════════════╝

    Paramètres :
        path    (list) : chemin solution à afficher
        visited (set)  : cases explorées (optionnel)
        title   (str)  : titre du graphique
    """
    # Construire la grille de couleurs
    grid = build_color_grid(path=path, visited=visited)

    # Créer la figure matplotlib
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(grid, interpolation='nearest')  # afficher comme image

    # Dessiner la grille (lignes entre les cases)
    ax.set_xticks(np.arange(-0.5, COLS, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, ROWS, 1), minor=True)
    ax.grid(which='minor', color='gray', linewidth=0.5)
    ax.tick_params(which='minor', size=0)

    # Numéroter les axes (0 à 9)
    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.set_xticklabels(range(COLS))
    ax.set_yticklabels(range(ROWS))

    # Ajouter les labels S et G sur le graphique
    ax.text(START[1], START[0], 'S', ha='center', va='center',
            fontsize=12, fontweight='bold', color='black')
    ax.text(GOAL[1],  GOAL[0],  'G', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')

    # Titre et légende
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    _add_legend(ax, show_visited=(visited is not None), show_path=(path is not None))

    plt.tight_layout()
    plt.show()


def show_animated(path, visited_order=None, title="Agent en mouvement", interval=200):
    """
    AFFICHAGE ANIMÉ : montre l'agent se déplacer case par case.
    Utile pour comprendre comment l'agent explore le labyrinthe.

    ╔══════════════════════════════════════════════╗
    ║  Pour utiliser : décommenter dans l'agent    ║
    ║  # show_animated(path=mon_chemin,            ║
    ║  #               visited_order=mes_visités)  ║
    ╚══════════════════════════════════════════════╝

    Paramètres :
        path          (list) : chemin solution (positions dans l'ordre)
        visited_order (list) : ordre d'exploration (pour montrer BFS/A*)
        title         (str)  : titre du graphique
        interval      (int)  : délai entre frames en millisecondes
    """
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

    # Paramètres de la grille
    ax.set_xticks(np.arange(-0.5, COLS, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, ROWS, 1), minor=True)
    ax.grid(which='minor', color='gray', linewidth=0.5)
    ax.tick_params(which='minor', size=0)
    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))

    # Affichage initial (labyrinthe vide)
    img = ax.imshow(build_color_grid(), interpolation='nearest')

    # Labels S et G fixes
    ax.text(START[1], START[0], 'S', ha='center', va='center',
            fontsize=12, fontweight='bold', color='black', zorder=5)
    ax.text(GOAL[1],  GOAL[0],  'G', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white', zorder=5)

    # Compteur d'étapes
    step_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                        fontsize=10, va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # -------------------------------------------------------------------------
    # Logique d'animation :
    # Phase 1 → montrer l'exploration (cases visitées une par une)
    # Phase 2 → montrer le chemin final (positions du path)
    # -------------------------------------------------------------------------
    visited_so_far = []
    explored = visited_order if visited_order else []

    def update(frame):
        """
        Fonction appelée à chaque frame de l'animation.
        frame = numéro de la frame actuelle (0, 1, 2, ...)
        """
        n_explore = len(explored)

        if frame < n_explore:
            # ---- PHASE 1 : Exploration ----
            visited_so_far.append(explored[frame])
            grid = build_color_grid(visited=visited_so_far,
                                    current=explored[frame])
            step_text.set_text(f"Exploration: étape {frame + 1}/{n_explore}")

        else:
            # ---- PHASE 2 : Affichage du chemin final ----
            path_idx = frame - n_explore
            partial_path = path[:path_idx + 1]
            current_pos  = path[path_idx] if path_idx < len(path) else None
            grid = build_color_grid(path=partial_path,
                                    visited=visited_so_far,
                                    current=current_pos)
            step_text.set_text(f"Chemin: étape {path_idx + 1}/{len(path)}")

        img.set_data(grid)
        return [img, step_text]

    # Nombre total de frames = exploration + chemin
    total_frames = len(explored) + len(path)

    # Créer l'animation
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=total_frames,
        interval=interval,   # millisecondes entre chaque frame
        blit=True,
        repeat=False         # ne pas reboucler
    )

    _add_legend(ax, show_visited=True, show_path=True)
    plt.tight_layout()
    plt.show()


def _add_legend(ax, show_visited=False, show_path=False):
    """
    Fonction interne : ajoute une légende colorée au graphique.
    Le _ au début du nom indique que c'est une fonction privée (usage interne).
    """
    handles = [
        mpatches.Patch(color=COLORS["wall"],  label="Mur"),
        mpatches.Patch(color=COLORS["start"], label="Départ (S)"),
        mpatches.Patch(color=COLORS["goal"],  label="But (G)"),
    ]
    if show_visited:
        handles.append(mpatches.Patch(color=COLORS["visited"], label="Exploré"))
    if show_path:
        handles.append(mpatches.Patch(color=COLORS["path"], label="Chemin solution"))
    handles.append(mpatches.Patch(color=COLORS["agent"], label="Agent"))

    ax.legend(handles=handles, loc='upper right',
              bbox_to_anchor=(1.35, 1.0), fontsize=9)
    
