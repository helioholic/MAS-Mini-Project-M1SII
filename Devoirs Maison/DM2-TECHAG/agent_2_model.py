# agent_2_model.py

from maze import START, GOAL, is_valid, print_maze
from visualizer import show_static, show_animated

MAX_STEPS = 200

def model_action(row, col, visited_set):
    # visited_set = la MÉMOIRE de l'agent (passé en paramètre)

    priority_order = [
        ( 0,  1, "DROITE"),
        ( 1,  0, "BAS"),
        (-1,  0, "HAUT"),
        ( 0, -1, "GAUCHE"),
    ]

    # PASSE 1 : chercher une case NON visitée
    for dr, dc, direction in priority_order:
        new_row = row + dr
        new_col = col + dc
        if is_valid(new_row, new_col) and (new_row, new_col) not in visited_set:
            return (new_row, new_col, direction)

    # PASSE 2 : toutes les voisines sont visitées (cul-de-sac)
    # On choisit quand même pour ne pas bloquer totalement
    for dr, dc, direction in priority_order:
        new_row = row + dr
        new_col = col + dc
        if is_valid(new_row, new_col):
            return (new_row, new_col, direction)

    return None  # complètement bloqué

def run_model_agent():

    current_row, current_col = START
    path = [START]
    steps = 0

    # LA MÉMOIRE : on commence avec le départ déjà dedans
    visited_set = {START}

    while (current_row, current_col) != GOAL:

        if steps >= MAX_STEPS:
            print(f"ÉCHEC : {MAX_STEPS} étapes dépassées.")
            return path, visited_set, False

        # CONSULTER LA MÉMOIRE + DÉCIDER
        result = model_action(current_row, current_col, visited_set)

        if result is None:
            print(f"ÉCHEC : bloqué en {(current_row, current_col)}")
            return path, visited_set, False

        # SE DÉPLACER
        new_row, new_col, direction = result
        current_row, current_col = new_row, new_col
        path.append((current_row, current_col))

        # METTRE À JOUR LA MÉMOIRE ← la seule vraie nouveauté
        visited_set.add((current_row, current_col))
        steps += 1

    print(f"SUCCÈS en {steps} étapes !")
    return path, visited_set, True

if __name__ == "__main__":

    # 1. Lancer l'agent et récupérer le chemin
    path, visited_set, success = run_model_agent()

    if success:

        # =========================================================
        # AFFICHAGE TERMINAL
        # Décommenter la ligne ci-dessous pour afficher dans le terminal
        # =========================================================
        print_maze(path=path,  visited=visited_set)

        # =========================================================
        # AFFICHAGE STATIQUE matplotlib
        # Décommenter pour voir le labyrinthe + chemin en image fixe
        # =========================================================
        # show_static(
        #     path=path,
        #     title="Agent Modèle - Chemin trouvé"
        # )

        # =========================================================
        # AFFICHAGE ANIMÉ matplotlib
        # Décommenter pour voir l'agent se déplacer case par case
        # (visited_order = path car l'agent ne "explore" pas, il avance direct)
        # =========================================================
        show_animated(
         path=path,
         visited_order=list(visited_set),  # ← visited_order à la place
         title="Agent Modèle - Animation",
         interval=300
        )

    else:
        print("\nL'agent modèle n'a pas pu atteindre le but.")
        print("C'est une limitation connue : sans mémoire, il peut tourner en rond.")
        show_animated(
         path=path,
         visited_order=list(visited_set),  # ← visited_order à la place
         title="Agent Modèle - Animation",
         interval=300
        )

        # Afficher quand même où il est allé (chemin partiel)
        print_maze(path=path, visited=visited_set)
