import numpy as np
np.random.seed(2)

NODES = 5

list = [0, 1, 2, 3, 4]

# Match all available pairs
def map():
    maps = set()
    list = [0, 1, 2, 3, 4]
    for i in range(len(list)):
        for j in range(i + 1):
            if i != j:
                maps.add((list[i], list[j]))
    return maps

a = map()
edges = sorted(a)

edge_to_qubit = {e: k for k, e in enumerate(edges)}
# print(edge_to_qubit)

# Build a graph using these connections
qubs = len(edges)
a = np.random.random(size=10)

for i in range(len(a)):
    if a[i] < 0.5:
        a[i] = 1
    else:
        a[i] = 0

def create_mapper():
    mapper = np.random.random(size=10)
    for i in range(len(mapper)):
        if mapper[i] < 0.5:
            mapper[i] = 1
        else:
            mapper[i] = 0
    return mapper

def has_triangle():
    # A graph has a triangle if 
    triangles = set()
    mapping = create_mapper()
    mapping_dict = dict(zip(edges, mapping))
    for i in range(len(edges)):
        a, b = edges[i]
        # Both values in a, b need to connect to the same number
        if mapping[i] == 1:
            #print(edges[i])
            key = (max(a, b), min(a, b))
            #print(key)
            for x in range(5):
                if x != a and x != b:
                    key_a = (max(a, x), min(a, x))
                    key_b = (max(b, x), min(b, x))
                    if mapping_dict[key_a] == 1 and mapping_dict[key_b] == 1:
                        print(a, b)
                        triangles.add((a, b))
    # print(triangles)
    # print(mapping_dict)

has_triangle()