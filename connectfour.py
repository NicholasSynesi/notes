import pennylane as qp
from pennylane import numpy as np
import matplotlib.pyplot as plt

# Board geometry: 5 columns x 4 rows, qubit index = row * COLS + col
COLS = 5
ROWS = 4
LINE = 4  # length of a winning line
qubs = COLS * ROWS

# def encode_game():
#     x = (2 * np.pi) / 3

dev = qp.device("default.qubit", wires=qubs)


def winning_lines():
    """Every set of LINE cells that forms a straight line fully on the board.

    A line is only valid if all LINE cells stay within bounds -- this is what
    guarantees we never encode a 3-in-a-row as if it were a win. Directions:
    horizontal, vertical, and both diagonals.
    """
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # (row, col)
    lines = []
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in directions:
                cells = [(r + k * dr, c + k * dc) for k in range(LINE)]
                # Keep the line only if its last cell fit
                if all(0 <= rr < ROWS and 0 <= cc < COLS for rr, cc in cells):
                    lines.append([rr * COLS + cc for rr, cc in cells])
    return lines

@qp.qnode(dev)
def circuit(x, p):

    for i in range(qubs):
        qp.RX(x, wires=i)
        qp.RY(x, wires=i)

    # Entangle each winning line as a chain of CRY gates along its cells.
    for line in winning_lines():
        for control, target in zip(line, line[1:]):
            qp.CRY(x, wires=[control, target])

    return qp.probs(wires=[0, 1, 2])

fig, ax = qp.draw_mpl(circuit)([0.0] * 20, 40 *[0])
plt.show()
