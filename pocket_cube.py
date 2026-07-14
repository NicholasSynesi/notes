"""
Pocket Cube (2x2x2 Rubik's cube): classical state, moves, and a full
breadth-first search that computes the exact distance-to-solved for every
reachable state.

Why this file exists
--------------------
The 2x2x2 has only 3,674,160 reachable states, so we can enumerate the ENTIRE
puzzle by BFS from the solved state. That gives us, for free:
  * perfect ground-truth labels (exact distance-to-solved, 0..11) for every
    state -- an ideal, fully-known dataset for a QML regression/classification
    demo, and
  * the distance histogram (how many states sit at each distance), which is a
    nice figure and a sanity check against known cube math.

Representation
--------------
We fix corner 0 in place as a reference frame (the 2x2x2 has no fixed centres,
so without this the whole cube could be freely rotated in space). That leaves
7 movable corners, and we only ever turn the three faces that do NOT touch the
fixed corner -- these three moves generate the whole reachable group.

A state is (perm, twist):
  * perm  : tuple of length 8. perm[s] = which cubie currently sits in slot s.
  * twist : tuple of length 8, each in {0,1,2}. twist[s] = orientation of the
            cubie in slot s, relative to the solved reference.

The solved state is perm = (0,1,2,3,4,5,6,7), twist = (0,0,0,0,0,0,0,0).
"""

from collections import deque

N_CORNERS = 8

# Slot numbering (a standard corner layout). Corner 0 is the fixed reference
# and is never moved by the three generating turns below.
#
#        top face slots: 0 1 2 3   (0 = fixed reference corner)
#        bottom face   : 4 5 6 7
#
# Each move turns one face: it 4-cycles the four slots on that face and adds a
# twist to each moved cubie. Corner twists change by +1 or +2 (mod 3) depending
# on whether the corner is rotated "forwards" or "backwards" by that face turn;
# the pattern (+1,+2,+1,+2) around a face is the standard corner-orientation
# rule and keeps total twist conserved (mod 3).

SOLVED_PERM = tuple(range(N_CORNERS))
SOLVED_TWIST = (0,) * N_CORNERS


def _make_move(cycle, twists):
    """Build a move from a 4-cycle of slots and the twist added to each.

    cycle  : (a, b, c, d) meaning the cubie in slot a moves to slot b, b->c,
             c->d, d->a (a single quarter turn of one face).
    twists : (ta, tb, tc, td) twist added (mod 3) to the cubie arriving in
             slots (b, c, d, a) respectively.
    Returns a function state -> state.
    """
    a, b, c, d = cycle
    ta, tb, tc, td = twists

    def move(state):
        perm, twist = state
        p = list(perm)
        t = list(twist)
        # cubie in a goes to b, b->c, c->d, d->a
        p[b], p[c], p[d], p[a] = perm[a], perm[b], perm[c], perm[d]
        t[b] = (twist[a] + ta) % 3
        t[c] = (twist[b] + tb) % 3
        t[d] = (twist[c] + tc) % 3
        t[a] = (twist[d] + td) % 3
        return (tuple(p), tuple(t))

    return move


# The three generating face turns (the faces NOT touching fixed corner 0).
# Each turns four of the seven movable corners. The (+1,+2) twist pattern is
# the standard corner-orientation change for a quarter turn.
R = _make_move((1, 2, 6, 5), (1, 2, 1, 2))   # right face  (clockwise)
F = _make_move((2, 3, 7, 6), (1, 2, 1, 2))   # front face  (clockwise)
D = _make_move((4, 5, 6, 7), (0, 0, 0, 0))   # down face   (no twist: axis face)

# Each face turn and its inverse (counter-clockwise) are BOTH single moves.
# We need the inverses as separate edges, otherwise a state one CCW turn away
# would cost three CW turns and every BFS distance would be inflated. A CCW
# turn is just the CW 4-cycle reversed, with the twist added to the reversed
# arrival slots.
Ri = _make_move((5, 6, 2, 1), (2, 1, 2, 1))  # right face  (counter-clockwise)
Fi = _make_move((6, 7, 3, 2), (2, 1, 2, 1))  # front face  (counter-clockwise)
Di = _make_move((7, 6, 5, 4), (0, 0, 0, 0))  # down face   (counter-clockwise)

MOVES = {"R": R, "F": F, "D": D, "R'": Ri, "F'": Fi, "D'": Di}


def neighbours(state):
    """All states reachable from `state` by a single quarter-turn move."""
    return [move(state) for move in MOVES.values()]


def scramble(state, sequence):
    """Apply a sequence of move names, e.g. scramble(solved(), "RFD")."""
    for name in sequence:
        state = MOVES[name](state)
    return state


def solved():
    return (SOLVED_PERM, SOLVED_TWIST)


def bfs_all():
    """Breadth-first search over the ENTIRE reachable state space.

    Returns dist: dict mapping every reachable state -> its exact minimum
    number of quarter-turn moves from solved. Because BFS explores states in
    non-decreasing distance order, the first time we see a state is at its
    true distance.
    """
    start = solved()
    dist = {start: 0}
    frontier = deque([start])
    while frontier:
        state = frontier.popleft()
        d = dist[state]
        for nxt in neighbours(state):
            if nxt not in dist:
                dist[nxt] = d + 1
                frontier.append(nxt)
    return dist


def distance_histogram(dist):
    """Given the BFS dict, return {distance: number_of_states}."""
    hist = {}
    for d in dist.values():
        hist[d] = hist.get(d, 0) + 1
    return hist


if __name__ == "__main__":
    import time

    t0 = time.time()
    dist = bfs_all()
    elapsed = time.time() - t0

    hist = distance_histogram(dist)
    total = len(dist)
    diameter = max(hist)

    print(f"reachable states found : {total:,}")
    print(f"God's number (diameter): {diameter}")
    print(f"BFS time               : {elapsed:.1f}s")
    print("\ndistance : count")
    for d in sorted(hist):
        bar = "#" * (hist[d] * 60 // total + (1 if hist[d] else 0))
        print(f"{d:>7}  : {hist[d]:>9,}  {bar}")