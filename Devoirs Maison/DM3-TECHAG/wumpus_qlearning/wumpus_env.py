import numpy as np
import random

# ============================================================
# CONSTANTES — ce que peut contenir une case de la grille
# ============================================================
EMPTY   = 0   # case vide
WUMPUS  = 1   # le monstre
PIT     = 2   # le puit (mort instantanée)
GOLD    = 3   # l'or (objectif)
AGENT   = 4   # position actuelle de l'agent


# ============================================================
# RÉCOMPENSES — ce que l'agent gagne ou perd selon la situation
# ============================================================
R_GOLD      = +1000  # trouver l'or
R_WUMPUS    = -1000  # tomber sur le Wumpus
R_PIT       = -1000  # tomber dans un puit
R_STEP      = -1     # chaque mouvement coûte 1 point
R_WIN       = +500   # sortir avec l'or
R_SHOOT     = -10    # tirer la flèche (coût)

# ============================================================
# ACTIONS POSSIBLES — chaque action a un numéro
# ============================================================
UP    = 0
DOWN  = 1
LEFT  = 2
RIGHT = 3
GRAB  = 4
SHOOT = 5
CLIMB = 6

# Liste de toutes les actions (utile pour choisir aléatoirement)
ACTIONS = [UP, DOWN, LEFT, RIGHT, GRAB, SHOOT, CLIMB]

# Noms des actions (utile pour afficher ce que fait l'agent)
ACTION_NAMES = {
    UP:    "UP",
    DOWN:  "DOWN",
    LEFT:  "LEFT",
    RIGHT: "RIGHT",
    GRAB:  "GRAB",
    SHOOT: "SHOOT",
    CLIMB: "CLIMB"
}

# ============================================================
# CLASSE PRINCIPALE — le monde de Wumpus
# ============================================================

class WumpusWorld:
    def __init__(self, size=4):
        """
        Initialise le monde de Wumpus.
        size : taille de la grille (4 = grille 4x4)
        """
        self.size = size

        # Position de départ de l'agent : coin bas-gauche [3,0]
        # (comme dans le cours, l'agent commence en [1,1] 
        #  mais en index Python c'est [3,0])
        self.start_pos = (3, 0)

        # L'agent a une seule flèche au départ
        self.has_arrow = True

        # L'agent n'a pas encore l'or
        self.has_gold = False

        # Le Wumpus est vivant au départ
        self.wumpus_alive = True

        # Construire la grille et placer les éléments
        self._build_world()

    # --------------------------------------------------------
    def _build_world(self):
        """
        Construit la grille 4x4 et place :
        - le Wumpus
        - les Pits
        - l'or
        Les positions sont FIXES comme dans le cours.
        """
        # Créer une grille vide 4x4 remplie de zeros (EMPTY)
        self.grid = np.zeros((self.size, self.size), dtype=int)

        # --- Placer le Wumpus (position fixe comme dans le cours) ---
        # ligne 0, colonne 2 → [0,2] en index Python
        self.wumpus_pos = (0, 2)
        self.grid[0][2] = WUMPUS

        # --- Placer les Pits ---
        # On met 3 pits comme dans l'exemple classique du cours
        self.pit_positions = [(0, 3), (2, 2), (3, 3)]
        for (r, c) in self.pit_positions:
            self.grid[r][c] = PIT

        # --- Placer l'or ---
        # L'or est en [0,3] dans l'exemple classique
        self.gold_pos = (1, 2)
        self.grid[1][2] = GOLD

        # --- Position initiale de l'agent ---
        self.agent_pos = self.start_pos  # (3, 0)

        # --- Calculer les perceptions (breeze, stench) ---
        # Ces listes contiennent les cases où l'agent sentira
        # le stench ou la breeze
        self.stench_cells  = self._get_adjacent(self.wumpus_pos)
        self.breeze_cells  = []
        for pit in self.pit_positions:
            self.breeze_cells += self._get_adjacent(pit)

    # --------------------------------------------------------

    # --------------------------------------------------------
    def _get_adjacent(self, pos):
        """
        Retourne les cases adjacentes (haut, bas, gauche, droite)
        d'une position donnée, sans sortir de la grille.

        Exemple : _get_adjacent((2,2)) 
        → [(1,2), (3,2), (2,1), (2,3)]
        """
        r, c = pos
        adjacent = []

        # Vérifier chaque direction et rester dans la grille
        if r - 1 >= 0:           adjacent.append((r-1, c))  # haut
        if r + 1 < self.size:    adjacent.append((r+1, c))  # bas
        if c - 1 >= 0:           adjacent.append((r, c-1))  # gauche
        if c + 1 < self.size:    adjacent.append((r, c+1))  # droite

        return adjacent
    
    # --------------------------------------------------------
    def get_perceptions(self):
        """
        Retourne ce que l'agent perçoit dans sa case actuelle.
        L'agent ne voit PAS la grille — il ressent juste :
        - stench  : Wumpus adjacent
        - breeze  : Pit adjacent
        - glitter : l'or est ICI (même case)
        - bump    : il a heurté un mur (géré dans step())
        - scream  : le Wumpus est mort (géré dans step())
        """
        r, c = self.agent_pos

        perceptions = {
            "stench"  : self.agent_pos in self.stench_cells,
            "breeze"  : self.agent_pos in self.breeze_cells,
            "glitter" : self.agent_pos == self.gold_pos and not self.has_gold,
            "scream"  : False,  # devient True si la flèche tue le Wumpus
            "bump"    : False   # devient True si l'agent frappe un mur
        }

        return perceptions

    # --------------------------------------------------------
    def get_state(self):
        """
        Retourne l'état actuel sous forme de tuple.
        C'est CE tuple qui sera utilisé comme clé dans la Q-table.

        L'état = position + perceptions + si l'agent a l'or
        Exemple : (3, 0, False, False, False, False)
                   row col stench breeze glitter has_gold
        """
        r, c = self.agent_pos
        p = self.get_perceptions()

        state = (
            r,              # ligne de l'agent
            c,              # colonne de l'agent
            p["stench"],    # sent-il le Wumpus ?
            p["breeze"],    # sent-il un Pit ?
            p["glitter"],   # voit-il l'or ?
            self.has_gold,  # a-t-il déjà l'or ?
            self.has_arrow  # a-t-il encore la flèche ? (utile pour décider de tirer ou pas)
        )

        return state

    # --------------------------------------------------------
    def reset(self):
        """
        Remet le monde à zéro pour un nouvel épisode.
        On repart de la même grille mais l'agent recommence
        depuis le début — comme une nouvelle partie.
        """
        # Remettre l'agent à sa position de départ
        self.agent_pos = self.start_pos

        # L'agent repose sa flèche
        self.has_arrow = True

        # L'agent n'a plus l'or
        self.has_gold = False

        # Le Wumpus ressuscite pour la nouvelle partie
        self.wumpus_alive = True

        # Reconstruire la grille (remet le Wumpus, l'or, les pits)
        self._build_world()

        # Retourner l'état initial
        return self.get_state()
    
    # --------------------------------------------------------
    def step(self, action):
        """
        L'agent effectue une action et le monde répond.
        
        Retourne :
        - next_state : nouvel état après l'action
        - reward     : récompense reçue
        - done       : True si la partie est terminée
        - info       : message explicatif (pour debug)
        """
        r, c = self.agent_pos
        reward = R_STEP  # chaque action coûte -1 par défaut
        done = False
        info = ""
        perceptions = {"scream": False, "bump": False}

        # ====================================================
        # CAS 1 — MOUVEMENTS (UP, DOWN, LEFT, RIGHT)
        # ====================================================
        if action in [UP, DOWN, LEFT, RIGHT]:

            # Calculer la nouvelle position selon l'action
            if action == UP:    new_r, new_c = r - 1, c
            if action == DOWN:  new_r, new_c = r + 1, c
            if action == LEFT:  new_r, new_c = r, c - 1
            if action == RIGHT: new_r, new_c = r, c + 1

            # Vérifier si l'agent sort de la grille (bump)
            if new_r < 0 or new_r >= self.size or \
               new_c < 0 or new_c >= self.size:
                # L'agent frappe un mur — il reste sur place
                perceptions["bump"] = True
                reward = R_STEP  # pénalité normale
                info = "BUMP — mur touché, l'agent reste sur place"

            else:
                # Le mouvement est valide — déplacer l'agent
                self.agent_pos = (new_r, new_c)

                # Vérifier ce qu'il y a dans la nouvelle case
                cell = self.grid[new_r][new_c]

                if cell == WUMPUS and self.wumpus_alive:
                    # L'agent tombe sur le Wumpus vivant → mort
                    reward = R_WUMPUS
                    done = True
                    info = "MORT — le Wumpus a mangé l'agent 💀"

                elif cell == PIT:
                    # L'agent tombe dans un puit → mort
                    reward = R_PIT
                    done = True
                    info = "MORT — l'agent est tombé dans un puit 💀"

                else:
                    # Case normale — rien de dangereux
                    info = f"L'agent se déplace en {self.agent_pos}"

        # ====================================================
        # CAS 2 — GRAB (ramasser l'or)
        # ====================================================
        elif action == GRAB:

            if self.agent_pos == self.gold_pos and not self.has_gold:
                # L'agent est sur la case de l'or et ne l'a pas encore
                self.has_gold = True
                reward = R_GOLD
                info = "OR RAMASSÉ — bien joué ! 🥇"
            else:
                # L'agent essaie de ramasser mais il n'y a rien
                reward = R_STEP
                info = "GRAB raté — pas d'or ici"

        # ====================================================
        # CAS 3 — SHOOT (tirer la flèche)
        # ====================================================
        elif action == SHOOT:

            if self.has_arrow:
                # L'agent utilise sa seule flèche
                self.has_arrow = False
                reward = R_SHOOT  # coût du tir : -10

                # Vérifier si le Wumpus est dans la même ligne
                # (on simplifie : la flèche va vers la droite)
                wr, wc = self.wumpus_pos
                if wr == r and wc > c and self.wumpus_alive:
                    # Le Wumpus est touché !
                    self.wumpus_alive = False
                    self.grid[wr][wc] = EMPTY
                    perceptions["scream"] = True
                    reward = R_SHOOT + 200  # bonus pour avoir tué le Wumpus
                    info = "SCREAM — le Wumpus est mort ! 🎯"
                else:
                    info = "SHOOT raté — flèche perdue"
            else:
                # Plus de flèche disponible
                reward = R_STEP
                info = "SHOOT — plus de flèche !"

        # ====================================================
        # CAS 4 — CLIMB (sortir du monde)
        # ====================================================
        elif action == CLIMB:

            if self.agent_pos == self.start_pos:
                # L'agent est à la sortie (case de départ)
                if self.has_gold:
                    # Il sort avec l'or → VICTOIRE !
                    reward = R_WIN
                    done = True
                    info = "VICTOIRE — l'agent sort avec l'or ! 🏆"
                else:
                    # Il sort sans l'or → partie terminée sans gain
                    reward = R_STEP
                    done = True
                    info = "L'agent sort sans l'or..."
            else:
                # L'agent essaie de sortir mais n'est pas à l'entrée
                reward = R_STEP
                info = "CLIMB raté — pas à la sortie"

        # ====================================================
        # RETOURNER le résultat de l'action
        # ====================================================
        next_state = self.get_state()
        return next_state, reward, done, info

# --------------------------------------------------------
    def render(self):
        """
        Affiche la grille dans le terminal avec des couleurs.
        
        Légende :
        🟦 A = Agent
        🔴 W = Wumpus
        ⚫ P = Pit
        🟡 G = Gold
        ⬜ . = case vide
        ~ = Stench (Wumpus adjacent)
        * = Breeze (Pit adjacent)
        """
        from colorama import Fore, Back, Style, init
        init(autoreset=True)  # reset automatique des couleurs après chaque print

        print("\n" + "=" * 25)
        print("     WUMPUS WORLD")
        print("=" * 25)

        for r in range(self.size):
            row_display = ""

            for c in range(self.size):
                cell = self.grid[r][c]
                pos  = (r, c)

                # ── L'agent est sur cette case ──
                if pos == self.agent_pos:
                    row_display += Fore.BLUE + " A " + Style.RESET_ALL

                # ── Wumpus (vivant) ──
                elif cell == WUMPUS and self.wumpus_alive:
                    row_display += Fore.RED + " W " + Style.RESET_ALL

                # ── Pit ──
                elif cell == PIT:
                    row_display += Fore.BLACK + Back.WHITE + " P " + Style.RESET_ALL

                # ── Or (pas encore ramassé) ──
                elif cell == GOLD and not self.has_gold:
                    row_display += Fore.YELLOW + " G " + Style.RESET_ALL

                # ── Case avec Stench (Wumpus adjacent) ──
                elif pos in self.stench_cells:
                    row_display += Fore.MAGENTA + " ~ " + Style.RESET_ALL

                # ── Case avec Breeze (Pit adjacent) ──
                elif pos in self.breeze_cells:
                    row_display += Fore.CYAN + " * " + Style.RESET_ALL

                # ── Case vide ──
                else:
                    row_display += Fore.WHITE + " . " + Style.RESET_ALL

            # Afficher le numéro de ligne + la rangée
            print(f"  {r} |{row_display}|")

        # Afficher les numéros de colonnes en bas
        print("     " + "   ".join([str(i) for i in range(self.size)]))
        print("=" * 25)

        # Afficher l'état actuel de l'agent
        p = self.get_perceptions()
        print(f"  Position  : {self.agent_pos}")
        print(f"  Or        : {'✅ en main' if self.has_gold else '❌ pas encore'}")
        print(f"  Flèche    : {'✅ disponible' if self.has_arrow else '❌ utilisée'}")
        print(f"  Stench    : {'⚠️  oui' if p['stench'] else 'non'}")
        print(f"  Breeze    : {'⚠️  oui' if p['breeze'] else 'non'}")
        print(f"  Glitter   : {'✨ oui' if p['glitter'] else 'non'}")
        print("=" * 25 + "\n")





