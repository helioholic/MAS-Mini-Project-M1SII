from wumpus_env import WumpusWorld

# Créer le monde
world = WumpusWorld(size=4)

# Afficher la grille initiale
world.render()

# Tester quelques actions manuellement
print("→ L'agent essaie d'aller UP")
state, reward, done, info = world.step(0)  # 0 = UP
print(f"  Info    : {info}")
print(f"  Reward  : {reward}")
print(f"  Done    : {done}")
world.render()

