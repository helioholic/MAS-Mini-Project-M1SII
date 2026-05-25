import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import time

# ============================================================
# COULEURS DE LA GRILLE
# ============================================================
# Chaque type de case a une couleur
COLORS = {
    "empty"   : "#F5F5F5",   # gris clair
    "wumpus"  : "#E74C3C",   # rouge
    "pit"     : "#2C3E50",   # noir/bleu foncé
    "gold"    : "#F1C40F",   # jaune
    "agent"   : "#3498DB",   # bleu
    "start"   : "#ECF0F1",   # blanc cassé (case de départ)
    "stench"  : "#F8C471",   # orange clair
    "breeze"  : "#AED6F1",   # bleu clair
}

# ============================================================
# FONCTION — Dessiner une case de la grille
# ============================================================
def draw_cell(ax, row, col, color, text="", text_color="black", fontsize=12):
    """
    Dessine une case colorée à la position (row, col).
    ax    : l'axe matplotlib
    text  : texte affiché au centre de la case (A, W, P, G...)
    """
    # Dessiner le rectangle coloré
    rect = mpatches.FancyBboxPatch(
        (col + 0.05, row + 0.05),   # position
        0.9, 0.9,                    # taille
        boxstyle="round,pad=0.05",
        facecolor=color,
        edgecolor="#CCCCCC",
        linewidth=1.5
    )
    ax.add_patch(rect)

    # Afficher le texte au centre
    if text:
        ax.text(
            col + 0.5, row + 0.5, text,
            ha="center", va="center",
            fontsize=fontsize,
            color=text_color,
            fontweight="bold"
        )

# ============================================================
# FONCTION — Dessiner la grille entière à un instant T
# ============================================================
def draw_grid(ax, world, step_num, action_name, reward, info):
    """
    Dessine l'état complet de la grille à un instant donné.
    Appelée à chaque pas de la démonstration.
    """
    ax.clear()

    size = world.size

    # ── Dessiner chaque case ─────────────────────────────
    for r in range(size):
        for c in range(size):
            pos  = (r, c)
            cell = world.grid[r][c]

            # Déterminer la couleur et le texte de la case
            if pos == world.agent_pos:
                # L'agent est ici
                color = COLORS["agent"]
                text  = "A"
                text_color = "white"

            elif cell == 1 and world.wumpus_alive:
                # Wumpus vivant
                color = COLORS["wumpus"]
                text  = "W"
                text_color = "white"

            elif cell == 2:
                # Pit
                color = COLORS["pit"]
                text  = "P"
                text_color = "white"

            elif cell == 3 and not world.has_gold:
                # Or pas encore ramassé
                color = COLORS["gold"]
                text  = "G"
                text_color = "black"

            elif pos == world.start_pos and pos != world.agent_pos:
                # Case de départ (sortie)
                color = COLORS["start"]
                text  = "↩"
                text_color = "gray"

            elif pos in world.stench_cells:
                # Stench — Wumpus adjacent
                color = COLORS["stench"]
                text  = "~"
                text_color = "#E67E22"

            elif pos in world.breeze_cells:
                # Breeze — Pit adjacent
                color = COLORS["breeze"]
                text  = "*"
                text_color = "#2980B9"

            else:
                # Case vide
                color = COLORS["empty"]
                text  = ""
                text_color = "black"

            draw_cell(ax, r, c, color, text, text_color)

    # ── Numéros de lignes et colonnes ────────────────────
    for i in range(size):
        ax.text(-0.3, i + 0.5, str(i), ha="center", va="center",
                fontsize=10, color="gray")
        ax.text(i + 0.5, -0.3, str(i), ha="center", va="center",
                fontsize=10, color="gray")

    # ── Infos en bas de la grille ────────────────────────
    perceptions = world.get_perceptions()
    status = (
        f"Or : {'✅' if world.has_gold else '❌'}   "
        f"Flèche : {'✅' if world.has_arrow else '❌'}   "
        f"Stench : {'⚠️' if perceptions['stench'] else '—'}   "
        f"Breeze : {'⚠️' if perceptions['breeze'] else '—'}"
    )

    # ── Titre avec infos du pas actuel ───────────────────
    ax.set_title(
        f"Pas {step_num} — Action : {action_name}\n"
        f"Reward : {reward}   |   {info}",
        fontsize=11, pad=10
    )

    # ── Légende en bas ───────────────────────────────────
    ax.text(
        size / 2, -0.7, status,
        ha="center", va="center",
        fontsize=9, color="#333333"
    )

    # ── Paramètres de l'axe ──────────────────────────────
    ax.set_xlim(-0.5, size)
    ax.set_ylim(-1, size)
    ax.set_aspect("equal")
    ax.axis("off")


# ============================================================
# FONCTION — Animer la démonstration pas à pas
# ============================================================
def animate_demo(world, agent, max_steps=100):
    """
    Joue 1 partie avec l'agent entraîné et anime chaque pas.
    L'agent utilise epsilon=0 → uniquement ce qu'il a appris.
    """
    from wumpus_env import ACTION_NAMES

    # Désactiver l'exploration
    agent.epsilon = 0.0

    # Réinitialiser le monde
    state = world.reset()
    done  = False
    step  = 0

    # ── Créer la fenêtre matplotlib ──────────────────────
    fig, ax = plt.subplots(figsize=(6, 7))
    fig.patch.set_facecolor("#FAFAFA")
    plt.suptitle("Wumpus World — Démonstration Q-Learning",
                 fontsize=13, fontweight="bold", color="#2C3E50")

    # Afficher l'état initial
    draw_grid(ax, world, step_num=0,
              action_name="—", reward=0, info="État initial")
    plt.pause(2)

    # ── Boucle de démonstration ──────────────────────────
    while not done and step < max_steps:

        # L'agent choisit la meilleure action connue
        action = agent.choose_action(state)

        # Exécuter l'action
        next_state, reward, done, info = world.step(action)

        step += 1

        # Mettre à jour l'affichage
        draw_grid(ax, world,
                  step_num=step,
                  action_name=ACTION_NAMES[action],
                  reward=reward,
                  info=info)

        # Pause entre chaque pas (en secondes)
        plt.pause(1.5)

        state = next_state

    # Message final
    color  = "#27AE60" if "VICTOIRE" in info else "#E74C3C"
    result = "🏆 VICTOIRE !" if "VICTOIRE" in info else "💀 MORT"
    fig.text(0.5, 0.02, f"{result} — {step} pas",
             ha="center", fontsize=12,
             fontweight="bold", color=color)
    
    plt.show()

# ============================================================
# FONCTION — Courbe d'apprentissage
# ============================================================
def plot_learning_curve(rewards_history, epsilon_history):
    """
    Affiche deux graphiques :
    1. Évolution des rewards moyens par épisode
    2. Évolution de epsilon (exploration vs exploitation)
    """

    # Calculer la moyenne glissante sur 50 épisodes
    # pour lisser la courbe et mieux voir la tendance
    window    = 50
    smoothed  = np.convolve(
        rewards_history,
        np.ones(window) / window,
        mode="valid"
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
    fig.patch.set_facecolor("#FAFAFA")
    plt.suptitle("Courbe d'apprentissage — Q-Learning Wumpus",
                 fontsize=13, fontweight="bold", color="#2C3E50")

    # ── Graphique 1 : Rewards ────────────────────────────
    ax1.plot(rewards_history, alpha=0.3,
             color="#3498DB", linewidth=0.8, label="Reward par épisode")
    ax1.plot(range(window - 1, len(rewards_history)), smoothed,
             color="#E74C3C", linewidth=2,
             label=f"Moyenne glissante ({window} épisodes)")

    ax1.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax1.set_ylabel("Reward total", fontsize=11)
    ax1.set_xlabel("Épisode", fontsize=11)
    ax1.legend(fontsize=9)
    ax1.set_facecolor("#F8F9FA")
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Évolution des récompenses", fontsize=11)

    # ── Graphique 2 : Epsilon ────────────────────────────
    ax2.plot(epsilon_history, color="#27AE60",
             linewidth=2, label="Epsilon (exploration)")

    ax2.axhline(y=0.01, color="#E74C3C", linestyle="--",
                linewidth=1, label="Epsilon minimum (0.01)")

    ax2.set_ylabel("Epsilon", fontsize=11)
    ax2.set_xlabel("Épisode", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#F8F9FA")
    ax2.grid(True, alpha=0.3)
    ax2.set_title("Évolution de l'exploration (epsilon decay)", fontsize=11)

    plt.tight_layout()
    plt.savefig("learning_curve.png", dpi=150,
                bbox_inches="tight", facecolor="#FAFAFA")
    print("  Courbe sauvegardée : learning_curve.png")
    plt.show()


