# agent_4_utility_astar.py

import heapq  # file de priorité (tas min) — le plus petit f(n) sort en premier
from maze import START, GOAL, is_valid, get_neighbors, print_maze
from visualizer import show_static, show_animated

def heuristic(pos, goal):
    # |ligne_actuelle - ligne_but| + |colonne_actuelle - colonne_but|
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

def astar(start, goal):

    # File de priorité — format : (f, g, position)
    # heapq trie par le premier élément → f(n)
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    #                          ↑ f=h(start)            ↑ g=0 au départ

    # Mémoire d'où on vient (même principe que BFS)
    parent = {start: None}

    # Coût réel g pour chaque case explorée
    g_score = {start: 0}

    # Cases complètement traitées
    closed_set = set()

    while open_set:

        # Retirer la case avec le plus petit f(n)
        f_current, g_current, current = heapq.heappop(open_set)

        # Déjà traité ? On ignore
        if current in closed_set:
            continue

        closed_set.add(current)

        # But atteint !
        if current == goal:
            return parent

        # Explorer les voisins
        row, col = current
        for new_row, new_col, direction in get_neighbors(row, col):
            neighbor = (new_row, new_col)

            if neighbor in closed_set:
                continue

            # Nouveau coût g pour ce voisin
            new_g = g_current + 1

            # Meilleur chemin trouvé vers ce voisin ?
            if neighbor not in g_score or new_g < g_score[neighbor]:
                g_score[neighbor] = new_g
                parent[neighbor]  = current

                # Calculer f = g + h et ajouter à la file
                new_f = new_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (new_f, new_g, neighbor))

    return None  # aucun chemin trouvé


def reconstruct_path(parent, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path

def run_utility_agent():

    print("Agent Utilité - A*")
    print(f"Départ : {START}  |  But : {GOAL}")
    print(f"h(départ) = {heuristic(START, GOAL)} pas minimum estimés")

    result = astar(START, GOAL)

    if result is None:
        print("ÉCHEC : aucun chemin possible.")
        return [], False

    path = reconstruct_path(result, GOAL)

    print(f"SUCCÈS ! Chemin trouvé en {len(path)-1} étapes.")
    print(f"Chemin : {path}")
    return path, True



if __name__ == "__main__":

    # 1. Lancer l'agent et récupérer le chemin
    path, success = run_utility_agent()

    if success:

        # =========================================================
        # AFFICHAGE TERMINAL
        # Décommenter la ligne ci-dessous pour afficher dans le terminal
        # =========================================================
        #print_maze(path=path)

        #=========================================================
        # AFFICHAGE STATIQUE matplotlib
        #Décommenter pour voir le labyrinthe + chemin en image fixe
        #=========================================================
        show_static(
            path=path,
            title="Agent A* - Chemin trouvé"

        )

        #=========================================================
        # AFFICHAGE ANIMÉ matplotlib
        #Décommenter pour voir l'agent se déplacer case par case
        #(visited_order = path car l'agent ne "explore" pas, il avance direct)
        #=========================================================
        show_animated(
            path=path,
            visited_order=path,
            title="Agent A* - Animation",
            interval=300   # 300ms entre chaque pas
        )

    else:
        print("\nL'agent A* n'a pas pu atteindre le but.")
        print("C'est une limitation connue : sans mémoire, il peut tourner en rond.")

        # Afficher quand même où il est allé (chemin partiel)
        #print_maze(path=path)
        #print_maze(path=path)

