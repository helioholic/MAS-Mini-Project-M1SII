# agent_3_goal_bfs.py

from collections import deque  # la file FIFO pour BFS
from maze import START, GOAL, is_valid, get_neighbors, print_maze
from visualizer import show_static, show_animated

def bfs(start, goal):

    # La file FIFO — on commence avec uniquement le départ
    queue = deque()
    queue.append(start)

    # La mémoire "d'où je viens" — le départ n'a pas de parent
    parent = {start: None}

    # Les cases déjà visitées — pour ne pas repasser deux fois
    visited = {start}

    # Tant que la file n'est pas vide
    while queue:

        # Retirer la case la plus ancienne (FIFO)
        current = queue.popleft()

        # Est-ce qu'on a atteint le but ?
        if current == goal:
            return parent  # on retourne parent pour reconstruire le chemin

        # Explorer tous les voisins accessibles
        row, col = current
        for new_row, new_col, direction in get_neighbors(row, col):
            neighbor = (new_row, new_col)

            # On n'explore que les cases pas encore visitées
            if neighbor not in visited:
                visited.add(neighbor)         # marquer comme visité
                parent[neighbor] = current    # mémoriser d'où on vient
                queue.append(neighbor)        # ajouter à la file

    # File vide → aucun chemin n'existe
    return None


def reconstruct_path(parent, goal):

    path = []
    current = goal

    # Remonter de G → S en suivant les parents
    while current is not None:
        path.append(current)
        current = parent[current]

    # On a le chemin à l'envers → on inverse
    path.reverse()
    return path

def run_goal_agent():

    print("Agent But - BFS")
    print(f"Départ : {START}  |  But : {GOAL}")

    # PHASE 1 : BFS calcule le chemin AVANT de bouger
    result = bfs(START, GOAL)

    if result is None:
        print("ÉCHEC : aucun chemin possible.")
        return [], False

    # PHASE 2 : reconstruire le chemin depuis le dictionnaire parent
    path = reconstruct_path(result, GOAL)

    print(f"SUCCÈS ! Chemin trouvé en {len(path)-1} étapes.")
    print(f"Chemin : {path}")
    return path, True

if __name__ == "__main__":

    # 1. Lancer l'agent et récupérer le chemin
    path, success = run_goal_agent()

    if success:

        # =========================================================
        # AFFICHAGE TERMINAL
        # Décommenter la ligne ci-dessous pour afficher dans le terminal
        # =========================================================
        print_maze(path=path)

        # =========================================================
        # AFFICHAGE STATIQUE matplotlib
        # Décommenter pour voir le labyrinthe + chemin en image fixe
        # =========================================================
        # show_static(
        #     path=path,
        #     title="Agent But - Chemin trouvé"

        # )

        # =========================================================
        # AFFICHAGE ANIMÉ matplotlib
        # Décommenter pour voir l'agent se déplacer case par case
        # (visited_order = path car l'agent ne "explore" pas, il avance direct)
        # =========================================================
        show_animated(
            path=path,
            visited_order=path,
            title="Agent But - Animation",
            interval=300   # 300ms entre chaque pas
        )

    else:
        print("\nL'agent réflexe n'a pas pu atteindre le but.")
        print("C'est une limitation connue : sans mémoire, il peut tourner en rond.")

        # Afficher quand même où il est allé (chemin partiel)
        print_maze(path=path)
