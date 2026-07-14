import pennylane as qp
from pennylane import numpy as np
import matplotlib.pyplot as plt

qubs = 20

dev = qp.device("default.qubit", wires=qubs)

@qp.qnode(dev)
def circuit(x):

    for i in range(qubs):
        qp.RX(x, wires=i)

    return qp.probs(wires=[0, 1, 2])

fig, ax = qp.draw_mpl(circuit)([0.0] * 2)
plt.show()
