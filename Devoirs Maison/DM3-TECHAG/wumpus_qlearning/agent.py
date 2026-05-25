import numpy as np
import random

# ============================================================
# CLASSE AGENT Q-LEARNING
# ============================================================
class QLearningAgent:
    def __init__(self):
        """
        Initialise l'agent avec ses paramètres d'apprentissage.
        """

        # ── Paramètres Q-Learning ──────────────────────────

        # Taux d'apprentissage : à quelle vitesse l'agent
        # met à jour ses connaissances
        # 0.1 = apprend lentement mais stable
        self.alpha = 0.1

        # Facteur de discount : est-ce que les récompenses
        # futures comptent autant que les immédiates ?
        # 0.99 = l'agent pense sur le long terme
        self.gamma = 0.99

        # Epsilon : probabilité d'exploration (action aléatoire)
        # On commence à 1.0 = 100% aléatoire au début
        self.epsilon = 1.0

        # Epsilon minimum : on n'arrête jamais complètement
        # d'explorer — même un agent expérimenté teste parfois
        self.epsilon_min = 0.01

        # Epsilon decay : à quelle vitesse on réduit epsilon
        # 0.995 = on réduit de 0.5% après chaque épisode
        self.epsilon_decay = 0.995

        # Nombre d'actions possibles (UP DOWN LEFT RIGHT
        # GRAB SHOOT CLIMB = 7 actions)
        self.n_actions = 7

        # ── La Q-Table ────────────────────────────────────
        # Dictionnaire Python : clé = état, valeur = tableau
        # de 7 valeurs (une par action)
        #
        # Exemple :
        # {
        #   (3,0,False,False,False,False) : [0,0,0,0,0,0,0],
        #   (2,0,False,True,False,False)  : [0,0,0,0,0,0,0],
        #   ...
        # }
        self.q_table = {}

        # ── Statistiques (pour les graphiques après) ──────
        # Historique des récompenses totales par épisode
        self.rewards_history = []

        # Historique du epsilon par épisode
        self.epsilon_history = []

# --------------------------------------------------------
    def get_q_values(self, state):
        """
        Retourne les valeurs Q pour un état donné.
        Si l'état n'existe pas encore dans la Q-table,
        on le crée avec des zéros — l'agent ne sait rien
        sur cet état pour l'instant.

        Exemple :
        state = (3, 0, False, False, False, False)
        → [0. 0. 0. 0. 0. 0. 0.]  (au début)
        → [−5. 2. −1. 8. 0. −10. 0.]  (après apprentissage)
        """
        if state not in self.q_table:
            # Premier passage dans cet état → initialiser à 0
            self.q_table[state] = np.zeros(self.n_actions)

        return self.q_table[state]

    # --------------------------------------------------------
    def choose_action(self, state):
        """
        Choisit une action selon la stratégie epsilon-greedy :

        - Avec probabilité epsilon    → action ALÉATOIRE
          (exploration : l'agent teste quelque chose de nouveau)

        - Avec probabilité 1-epsilon  → meilleure action connue
          (exploitation : l'agent utilise ce qu'il a appris)

        Au début epsilon = 1.0 → tout aléatoire
        Avec le temps epsilon → 0.01 → presque toujours la meilleure action
        """

        if random.random() < self.epsilon:
            # ── EXPLORATION ──
            # random.random() génère un nombre entre 0 et 1
            # si ce nombre est inférieur à epsilon → aléatoire
            action = random.randint(0, self.n_actions - 1)
            # print(f"  [EXPLORATION] action aléatoire : {action}")

        else:
            # ── EXPLOITATION ──
            # Récupérer les valeurs Q de cet état
            q_values = self.get_q_values(state)

            # Choisir l'action avec la valeur Q la plus haute
            action = np.argmax(q_values)
            # print(f"  [EXPLOITATION] meilleure action : {action}")

        return action

    # --------------------------------------------------------
    def decay_epsilon(self):
        """
        Réduit epsilon après chaque épisode.
        L'agent explore de moins en moins avec le temps.

        Formule : epsilon = epsilon * decay
        Exemple après 100 épisodes avec decay=0.995 :
        1.0 → 0.995 → 0.990 → ... → 0.606

        On ne descend jamais en dessous de epsilon_min (0.01)
        pour garder une toute petite part d'exploration.
        """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

            # S'assurer qu'on ne dépasse pas le minimum
            self.epsilon = max(self.epsilon, self.epsilon_min)

    # --------------------------------------------------------
    def learn(self, state, action, reward, next_state, done):
        """
        Met à jour la Q-table après chaque action.
        C'est ici qu'on applique la formule Q-Learning :

        Q(s,a) = Q(s,a) + alpha * [r + gamma * max(Q(s',a')) - Q(s,a)]
                                    └────────────────────────────────┘
                                              la correction

        Paramètres :
        - state      : état AVANT l'action
        - action     : action effectuée
        - reward     : récompense reçue
        - next_state : état APRÈS l'action
        - done       : True si l'épisode est terminé
        """

        # ── Étape 1 : récupérer Q(s, a) ──────────────────
        # La valeur actuelle que l'agent associe à
        # (cet état + cette action)
        current_q = self.get_q_values(state)[action]

        # ── Étape 2 : calculer max Q(s', a') ─────────────
        if done:
            # Si l'épisode est terminé (mort ou victoire),
            # il n'y a pas d'état suivant → pas de futur
            # donc la récompense future = 0
            best_future_q = 0
        else:
            # Sinon, regarder la meilleure valeur Q
            # depuis le prochain état
            # "Quelle est la meilleure action que je pourrais
            #  faire depuis là où je vais atterrir ?"
            best_future_q = np.max(self.get_q_values(next_state))

        # ── Étape 3 : calculer la valeur cible ───────────
        # C'est ce que Q(s,a) DEVRAIT valoir
        # r + gamma * max Q(s', a')
        target = reward + self.gamma * best_future_q

        # ── Étape 4 : calculer la correction ─────────────
        # La différence entre ce qu'on pensait et
        # ce qu'on aurait dû penser
        # Si correction > 0 → c'était mieux que prévu → on monte
        # Si correction < 0 → c'était pire que prévu  → on descend
        correction = target - current_q

        # ── Étape 5 : mettre à jour Q(s, a) ──────────────
        # On ne remplace pas brutalement — on ajuste doucement
        # grâce à alpha (taux d'apprentissage)
        self.q_table[state][action] = current_q + self.alpha * correction

    # --------------------------------------------------------
    def save_stats(self, total_reward):
        """
        Sauvegarde les statistiques de l'épisode terminé.
        Utilisé plus tard pour tracer les graphiques.

        - total_reward : somme de toutes les récompenses
                         reçues pendant l'épisode
        """
        self.rewards_history.append(total_reward)
        self.epsilon_history.append(self.epsilon)

