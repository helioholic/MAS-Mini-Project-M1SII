# =============================================================================
# FICHIER : agent_1_reflex.py
# RÔLE    : Agent Réflexe Simple (Simple Reflex Agent)
#
# CONCEPT :
#   L'agent réflexe ne réfléchit pas ! Il suit des règles fixes du type :
#   "SI je perçois X → ALORS je fais Y"
#   Il n'a AUCUNE mémoire : il ne sait pas d'où il vient ni où il est allé.
#
# ANALOGIE :
#   Comme un insecte qui suit toujours la lumière :
#   il ne "pense" pas, il réagit juste à ce qu'il perçoit maintenant.
#
# RÈGLES UTILISÉES (priorité dans l'ordre) :
#   1. Si je peux aller à DROITE  → j'y vais
#   2. Si je peux aller en BAS    → j'y vais
#   3. Si je peux aller en HAUT   → j'y vais
#   4. Si je peux aller à GAUCHE  → j'y vais
#   5. Sinon → je suis bloqué (échec)
#
# PROBLÈME DE CET AGENT :
#   Il peut tourner en rond indéfiniment ! Sans mémoire, il peut revisiter
#   la même case encore et encore → c'est pourquoi on limite à MAX_STEPS.
#
# RÉSULTAT ATTENDU :
#   Peut ÉCHOUER si les règles fixes ne mènent pas à la sortie.
#   Ne garantit PAS de trouver un chemin.
# =============================================================================

import sys
from maze import START, GOAL, is_valid, get_neighbors, print_maze, DIRECTIONS
from visualizer import show_static, show_animated

# Nombre maximum de pas avant d'abandonner (évite la boucle infinie)
MAX_STEPS = 200


def reflex_action(row, col):
    """
    Le "cerveau" de l'agent réflexe : choisit une action selon des règles fixes.
    C'est la CONDITION-ACTION : si la case X est libre → aller en X.

    Ordre de priorité des directions :
        1. DROITE (préférence car le but G est en bas-droite)
        2. BAS
        3. HAUT
        4. GAUCHE

    Paramètres :
        row (int) : ligne actuelle
        col (int) : colonne actuelle

    Retourne :
        (new_row, new_col, direction) si un mouvement est possible
        None si l'agent est complètement bloqué
    """
    # Ordre fixe des directions à essayer (RÈGLES de l'agent réflexe)
    # On essaie toujours dans le MÊME ordre, peu importe le contexte
    priority_order = [
        ( 0,  1, "DROITE"),  # règle 1 : essayer droite en premier
        ( 1,  0, "BAS"),     # règle 2 : essayer bas
        (-1,  0, "HAUT"),    # règle 3 : essayer haut
        ( 0, -1, "GAUCHE"),  # règle 4 : essayer gauche en dernier
    ]

    for dr, dc, direction_name in priority_order:
        new_row = row + dr
        new_col = col + dc
        if is_valid(new_row, new_col):
            # La première direction valide est choisie → pas de "réflexion"
            return (new_row, new_col, direction_name)

    # Aucune direction possible → agent bloqué
    return None


def run_reflex_agent():
    """
    Lance l'agent réflexe depuis la position de départ jusqu'au but (ou échec).

    Processus :
        1. Démarrer à START
        2. À chaque étape : appeler reflex_action() pour choisir où aller
        3. Se déplacer vers la case choisie
        4. Recommencer jusqu'à atteindre GOAL ou dépasser MAX_STEPS

    Retourne :
        path (list) : liste des positions visitées dans l'ordre
        success (bool) : True si le but a été atteint, False sinon
    """
    print("\n" + "="*60)
    print("  AGENT RÉFLEXE SIMPLE - Démarrage")
    print("="*60)
    print(f"  Départ : {START}")
    print(f"  But    : {GOAL}")
    print(f"  Règles : DROITE > BAS > HAUT > GAUCHE (toujours dans cet ordre)")
    print("="*60)

    # Position courante de l'agent
    current_row, current_col = START

    # Historique du chemin parcouru (pour visualisation)
    path = [START]

    # Compteur d'étapes pour éviter la boucle infinie
    steps = 0

    # -------------------------------------------------------------------------
    # BOUCLE PRINCIPALE DE L'AGENT
    # À chaque itération = 1 pas de l'agent
    # -------------------------------------------------------------------------
    while (current_row, current_col) != GOAL:

        # Sécurité : arrêter si trop d'étapes (l'agent tourne peut-être en rond)
        if steps >= MAX_STEPS:
            print(f"\n⚠️  ÉCHEC : L'agent a dépassé {MAX_STEPS} étapes !")
            print("   L'agent réflexe tourne probablement en rond (sans mémoire).")
            return path, False

        # ---- PERCEPTION : l'agent "voit" sa position actuelle ----
        # (Dans un vrai agent réflexe, il percevrait ses capteurs ici)

        # ---- ACTION : choisir la prochaine case selon les règles ----
        result = reflex_action(current_row, current_col)

        if result is None:
            # L'agent est bloqué dans tous les sens
            print(f"\n⚠️  ÉCHEC : L'agent est bloqué en {(current_row, current_col)} !")
            return path, False

        new_row, new_col, direction = result

        # ---- DÉPLACEMENT : l'agent se déplace ----
        current_row, current_col = new_row, new_col
        path.append((current_row, current_col))
        steps += 1

        # Afficher chaque pas dans le terminal (optionnel, décommenter si voulu)
        # print(f"  Étape {steps:3d} : {direction:7s} → position {(current_row, current_col)}")

    # L'agent a atteint le but !
    print(f"\n✅  SUCCÈS ! But atteint en {steps} étapes.")
    print(f"   Chemin parcouru ({len(path)} positions) : {path}")
    return path, True


# =============================================================================
# POINT D'ENTRÉE : ce code s'exécute quand on lance `python agent_1_reflex.py`
# =============================================================================
if __name__ == "__main__":

    # 1. Lancer l'agent et récupérer le chemin
    path, success = run_reflex_agent()

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
        #     title="Agent Réflexe Simple - Chemin trouvé"
        # )

        # =========================================================
        # AFFICHAGE ANIMÉ matplotlib
        # Décommenter pour voir l'agent se déplacer case par case
        # (visited_order = path car l'agent ne "explore" pas, il avance direct)
        # =========================================================
        show_animated(
            path=path,
            visited_order=path,
            title="Agent Réflexe Simple - Animation",
            interval=300   # 300ms entre chaque pas
        )

    else:
        print("\nL'agent réflexe n'a pas pu atteindre le but.")
        print("C'est une limitation connue : sans mémoire, il peut tourner en rond.")

        show_animated(
        path=path,
        visited_order=path,
        title="Agent Réflexe - Chemin partiel",
        interval=300
    )

        # Afficher quand même où il est allé (chemin partiel)
        print_maze(path=path)

