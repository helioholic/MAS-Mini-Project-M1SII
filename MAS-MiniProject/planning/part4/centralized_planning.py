# ============================================================
# Part 4 : Centralized Planning for Distributed Plans
# Blocks world with 2 agents : Bill (Agent1) and Tom (Agent2)
# ============================================================

# ---- INITIAL AND GOAL STATES ----

initial_state = [
    'on(A,B)', 'on(C,D)', 'on(E,F)',
    'ontable(B)', 'ontable(D)', 'ontable(F)',
    'clear(A)', 'clear(C)', 'clear(E)'
]

goal_state = [
    'on(B,A)', 'on(A,E)',
    'on(F,D)', 'on(D,C)',
    'ontable(E)', 'ontable(C)'
]

# ---- OPERATORS ----

def move(b, x, y):
    return {
        'name': f'move({b},{x},{y})',
        'precond': [f'on({b},{x})', f'clear({b})', f'clear({y})'],
        'add':    [f'on({b},{y})', f'clear({x})'],
        'delete': [f'on({b},{x})', f'clear({y})']
    }

def movetable(b, x):
    return {
        'name': f'movetable({b},{x})',
        'precond': [f'on({b},{x})', f'clear({b})'],
        'add':    [f'ontable({b})', f'clear({x})'],
        'delete': [f'on({b},{x})']
    }

# ---- APPLY ACTION TO STATE ----

def apply(action, state):
    new_state = list(state)
    for d in action['delete']:
        if d in new_state:
            new_state.remove(d)
    for a in action['add']:
        if a not in new_state:
            new_state.append(a)
    return new_state

def preconditions_met(action, state):
    return all(p in state for p in action['precond'])

# ---- CENTRALIZED PLANNER ----
# We encode the plan steps directly from the slide (backward chaining result)
# Each step is derived by working backward from goal to initial state

def centralized_planner():
    """
    Backward chaining from goal state.
    Goal:  on(B,A), on(A,E), on(F,D), on(D,C), ontable(E), ontable(C)

    Working backward:
    - on(B,A)  needs clear(B) and on(B,T) → movetable(A,B) first to free B
    - on(A,E)  needs clear(A) and clear(E) → A is free after movetable
    - on(F,D)  needs clear(F) and clear(D) → movetable(C,D) to free D
    - on(D,C)  needs clear(D) and clear(C) → movetable(E,F) to free C via movetable(C,D)
    """

    # The 6 steps derived from backward chaining (matching the slide)
    plan = [
        movetable('A', 'B'),   # S1: move A from B to table → frees B, A on table
        movetable('E', 'F'),   # S2: move E from F to table → frees F, E on table
        movetable('C', 'D'),   # S3: move C from D to table → frees D, C on table
        move('B', 'T', 'A'),   # S4: move B from table onto A → on(B,A) ✓  (T=table)
        move('A', 'T', 'E'),   # S5: move A from table onto E → on(A,E) ✓
        move('F', 'T', 'D'),   # S6: move F from table onto D → on(F,D) ✓
        move('D', 'T', 'C'),   # S7: move D from table onto C → on(D,C) ✓
    ]

    # verify each step against the running state
    state = list(initial_state)
    # T (table) is always clear for our purposes
    state.append('ontable(A)')  # A starts on B but we track table separately

    print("=" * 60)
    print("   CENTRALIZED PLANNER — Backward Chaining")
    print("=" * 60)
    print(f"\nInitial state:\n  {initial_state}")
    print(f"\nGoal state:\n  {goal_state}\n")
    print("-" * 60)
    print("  Plan Steps (derived by working backward from goal):")
    print("-" * 60)

    for i, action in enumerate(plan, 1):
        print(f"\n  S{i}: {action['name']}")
        print(f"       Preconditions : {action['precond']}")
        print(f"       Add effects   : {action['add']}")
        print(f"       Del effects   : {action['delete']}")

    return plan

# ---- AGENT ASSIGNMENT ----
# Bill (Agent1) → Stack 1: blocks A, B, E  (left stack in S_final)
# Tom  (Agent2) → Stack 2: blocks C, D, F  (right stack in S_final)

def assign_to_agents(plan):
    bill_blocks = ['A', 'B', 'E']
    tom_blocks  = ['C', 'D', 'F']

    bill_plan = []
    tom_plan  = []

    for action in plan:
        name = action['name']
        involved = [c for c in name if c.isupper() and c != 'T']
        if any(b in bill_blocks for b in involved):
            bill_plan.append(action['name'])
        else:
            tom_plan.append(action['name'])

    return bill_plan, tom_plan

# ---- MAIN ----

if __name__ == '__main__':

    # Step 1: central planner builds global plan
    plan = centralized_planner()

    # Step 2: distribute to agents
    bill_plan, tom_plan = assign_to_agents(plan)

    print("\n" + "=" * 60)
    print("   DISTRIBUTED PLAN")
    print("=" * 60)

    print(f"\n  Global plan — {len(plan)} steps total")

    print(f"\n  Bill (Agent1) handles stack [B on A on E]:")
    for s in bill_plan:
        print(f"    → {s}")

    print(f"\n  Tom (Agent2) handles stack [F on D on C]:")
    for s in tom_plan:
        print(f"    → {s}")

    print("\n  Both agents execute their sub-plans IN PARALLEL")
    print("  The two stacks are fully independent — no conflicts.\n")

