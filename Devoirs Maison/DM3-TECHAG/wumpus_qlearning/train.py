import numpy as np
from wumpus_env import WumpusWorld, ACTIONS, ACTION_NAMES
from agent import QLearningAgent
from visualize import animate_demo, plot_learning_curve

# ============================================================
# PARAMÈTRES D'ENTRAÎNEMENT
# ============================================================

# Nombre de parties jouées au total
N_EPISODES = 1000

# Nombre maximum de pas par partie
# évite que l'agent tourne en rond indéfiniment
MAX_STEPS = 100

# ============================================================
# INITIALISATION
# ============================================================

# Créer le monde Wumpus (grille 4x4)
world = WumpusWorld(size=4)

# Créer l'agent Q-Learning
agent = QLearningAgent()

# Compteurs pour les statistiques globales
n_wins   = 0  # nombre de victoires sur 1000 parties
n_deaths = 0  # nombre de morts sur 1000 parties

print("=" * 40)
print("   DÉBUT DE L'ENTRAÎNEMENT Q-LEARNING")
print("=" * 40)

# ============================================================
# BOUCLE PRINCIPALE D'ENTRAÎNEMENT
# 1 itération = 1 partie complète (épisode)
# ============================================================
for episode in range(N_EPISODES):

    # Remettre le monde à zéro pour une nouvelle partie
    # retourne l'état initial de l'agent
    state = world.reset()

    # Récompense totale accumulée pendant cette partie
    total_reward = 0

    # La partie est-elle terminée ? (mort ou victoire)
    done = False

    # ── Boucle d'une partie ──────────────────────────────
    for step in range(MAX_STEPS):

        # 1. L'agent choisit une action selon epsilon-greedy
        #    → aléatoire si epsilon élevé (début)
        #    → meilleure action connue si epsilon faible (fin)
        action = agent.choose_action(state)

        # 2. Le monde exécute l'action et retourne :
        #    next_state : nouvel état après l'action
        #    reward     : récompense reçue (+1000, -1000, -1...)
        #    done       : True si mort ou victoire
        #    info       : message texte pour debug
        next_state, reward, done, info = world.step(action)

        # 3. L'agent met à jour sa Q-table avec cette expérience
        #    C'est ici qu'il apprend vraiment
        agent.learn(state, action, reward, next_state, done)

        # 4. Accumuler la récompense de cette partie
        total_reward += reward

        # 5. Avancer vers le nouvel état
        state = next_state

        # 6. Si la partie est terminée → passer à la suivante
        if done:
            break

    # ── Fin de la partie ────────────────────────────────

    # Compter victoires et morts
    if "VICTOIRE" in info:
        n_wins += 1
    elif "MORT" in info:
        n_deaths += 1

    # Sauvegarder les stats pour les graphiques
    agent.save_stats(total_reward)

    # Réduire epsilon → moins d'exploration avec le temps
    agent.decay_epsilon()

    # Afficher un résumé toutes les 100 parties
    if (episode + 1) % 100 == 0:
        avg_reward = np.mean(agent.rewards_history[-100:])
        print(f"\n── Épisode {episode+1}/{N_EPISODES} ──")
        print(f"   Epsilon       : {agent.epsilon:.3f}")
        print(f"   Reward moyen  : {avg_reward:.1f}")
        print(f"   Victoires     : {n_wins}")
        print(f"   Morts         : {n_deaths}")
        print(f"   États connus  : {len(agent.q_table)}")

# ============================================================
# FIN DE L'ENTRAÎNEMENT — statistiques globales
# ============================================================
print("\n" + "=" * 40)
print("   FIN DE L'ENTRAÎNEMENT")
print("=" * 40)
print(f"   Total victoires : {n_wins}")
print(f"   Total morts     : {n_deaths}")
print(f"   États explorés  : {len(agent.q_table)}")
print(f"   Epsilon final   : {agent.epsilon:.3f}")

# ============================================================
# DÉMONSTRATION — l'agent entraîné joue 1 partie
# On met epsilon=0 → plus d'aléatoire, que du savoir acquis
# ============================================================
print("\n" + "=" * 40)
print("   DÉMONSTRATION AGENT ENTRAÎNÉ")
print("=" * 40)

# Désactiver l'exploration complètement
# l'agent utilise uniquement ce qu'il a appris
agent.epsilon = 0.0

# Réinitialiser le monde pour une partie propre
state = world.reset()

# Afficher la grille AVANT que l'agent commence
print("  État INITIAL :")
world.render()

done = False
step = 0

while not done and step < MAX_STEPS:

    # L'agent choisit toujours la meilleure action connue
    action = agent.choose_action(state)

    # Afficher le pas et l'action choisie
    print(f"  → Pas {step+1} : {ACTION_NAMES[action]}")

    # Exécuter l'action
    next_state, reward, done, info = world.step(action)

    state  = next_state
    step  += 1

# Afficher la grille APRÈS la partie
print("\n  État FINAL :")
world.render()
print(f"  Résultat : {info}")
print(f"  Nombre de pas : {step}")

# ============================================================
# VISUALISATION
# ============================================================

# 1. Courbe d'apprentissage
print("\n  Affichage de la courbe d'apprentissage...")
plot_learning_curve(agent.rewards_history, agent.epsilon_history)

# 2. Animation de la démonstration
print("\n  Lancement de l'animation...")
animate_demo(world, agent)


# ── Version détaillée — décommenter pour voir pas à pas ──
# while not done and step < MAX_STEPS:
#     action = agent.choose_action(state)
#     print(f"  → Action : {ACTION_NAMES[action]}")
#     next_state, reward, done, info = world.step(action)
#     world.render()
#     print(f"  Reward : {reward} | {info}")
#     state = next_state
#     step += 1



# si on veut faire une démonstration pas à pas, on peut aussi réutiliser le code de main.py
# import numpy as np
# from wumpus_env import WumpusWorld, ACTIONS, ACTION_NAMES
# from agent import QLearningAgent


# # ============================================================
# # PARAMÈTRES D'ENTRAÎNEMENT
# # ============================================================

# # Nombre d'épisodes = nombre de parties jouées
# # 1 épisode = l'agent joue jusqu'à gagner ou mourir
# N_EPISODES = 1000

# # Nombre maximum de pas par épisode
# # Evite que l'agent tourne en rond indéfiniment
# MAX_STEPS = 100

# # Afficher la grille tous les X épisodes (pour voir la progression)
# RENDER_EVERY = 100

# # ============================================================
# # INITIALISATION
# # ============================================================

# # Créer le monde
# world = WumpusWorld(size=4)

# # Créer l'agent
# agent = QLearningAgent()

# # Compteurs pour les statistiques
# n_wins   = 0  # nombre de victoires
# n_deaths = 0  # nombre de morts

# print("=" * 40)
# print("   DÉBUT DE L'ENTRAÎNEMENT Q-LEARNING")
# print("=" * 40)

# # ============================================================
# # BOUCLE PRINCIPALE D'ENTRAÎNEMENT
# # ============================================================
# for episode in range(N_EPISODES):

#     # ── Réinitialiser le monde pour une nouvelle partie ──
#     state = world.reset()

#     # Récompense totale accumulée pendant cet épisode
#     total_reward = 0

#     # L'épisode est-il terminé ?
#     done = False

#     # ── Boucle d'un épisode ──────────────────────────────
#     for step in range(MAX_STEPS):

#         # 1. L'agent choisit une action (epsilon-greedy)
#         action = agent.choose_action(state)

#         # 2. Le monde exécute l'action et retourne le résultat
#         next_state, reward, done, info = world.step(action)

#         # 3. L'agent apprend de cette expérience
#         agent.learn(state, action, reward, next_state, done)

#         # 4. Accumuler la récompense
#         total_reward += reward

#         # 5. Afficher la grille tous les RENDER_EVERY épisodes
#         if (episode + 1) % RENDER_EVERY == 0:
#             world.render()
#             print(f"  Épisode {episode+1} | Pas {step+1}")
#             print(f"  Action  : {ACTION_NAMES[action]}")
#             print(f"  Reward  : {reward}")
#             print(f"  Info    : {info}")
#             input("  [Entrée pour continuer...]")

#         # 6. Passer à l'état suivant
#         state = next_state

#         # 7. Si l'épisode est terminé → sortir de la boucle
#         if done:
#             break

#     # ── Fin de l'épisode ────────────────────────────────

#     # Mettre à jour les statistiques
#     if "VICTOIRE" in info:
#         n_wins += 1
#     elif "MORT" in info:
#         n_deaths += 1

#     # Sauvegarder les stats de cet épisode
#     agent.save_stats(total_reward)

#     # Réduire epsilon (moins d'exploration avec le temps)
#     agent.decay_epsilon()

#     # Afficher un résumé tous les 100 épisodes
#     if (episode + 1) % 100 == 0:
#         avg_reward = np.mean(agent.rewards_history[-100:])
#         print(f"\n── Épisode {episode+1}/{N_EPISODES} ──")
#         print(f"   Epsilon       : {agent.epsilon:.3f}")
#         print(f"   Reward moyen  : {avg_reward:.1f}")
#         print(f"   Victoires     : {n_wins}")
#         print(f"   Morts         : {n_deaths}")
#         print(f"   États connus  : {len(agent.q_table)}")

# # ============================================================
# # FIN DE L'ENTRAÎNEMENT
# # ============================================================
# print("\n" + "=" * 40)
# print("   FIN DE L'ENTRAÎNEMENT")
# print("=" * 40)
# print(f"   Total victoires : {n_wins}")
# print(f"   Total morts     : {n_deaths}")
# print(f"   États explorés  : {len(agent.q_table)}")
# print(f"   Epsilon final   : {agent.epsilon:.3f}")



    

