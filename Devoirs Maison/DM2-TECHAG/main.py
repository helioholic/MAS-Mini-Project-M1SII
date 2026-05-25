# main.py
# Lance tous les agents et affiche un tableau comparatif

from agent_1_reflex       import run_reflex_agent
from agent_2_model        import run_model_agent
from agent_3_goal_bfs     import run_goal_agent
from agent_4_utility_astar import run_utility_agent
from maze import print_maze

if __name__ == "__main__":

    print("\n" + "="*50)
    print("   COMPARAISON DES 4 AGENTS - EXERCICE 2")
    print("="*50)

    # Lancer les 4 agents
    path1, success1                = run_reflex_agent()
    path2, visited2, success2      = run_model_agent()
    path3, success3                = run_goal_agent()
    path4, success4                = run_utility_agent()

    # Tableau comparatif
    print("\n" + "="*50)
    print(f"  {'Agent':<20} {'Résultat':<10} {'Étapes'}")
    print("  " + "-"*40)
    print(f"  {'Réflexe Simple':<20} {'❌ ÉCHEC' if not success1 else '✅':<10} {len(path1)-1 if success1 else 'N/A'}")
    print(f"  {'Basé sur Modèle':<20} {'❌ ÉCHEC' if not success2 else '✅':<10} {len(path2)-1 if success2 else 'N/A'}")
    print(f"  {'But - BFS':<20} {'❌ ÉCHEC' if not success3 else '✅':<10} {len(path3)-1 if success3 else 'N/A'}")
    print(f"  {'Utilité - A*':<20} {'❌ ÉCHEC' if not success4 else '✅':<10} {len(path4)-1 if success4 else 'N/A'}")
    print("="*50)

    