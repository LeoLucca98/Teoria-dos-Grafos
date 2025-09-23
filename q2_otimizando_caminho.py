# pseudocodigo de Bellman-Ford
#   d11 ← 0
#   d1i ← ∞   ∀ i ∈ V – {1}
#   anterior(i) ← 0   ∀ i
#   enquanto ∃ (j,i) ∈ A | d1j > d1i + vij

from math import inf

def bellman_ford(n, edges, src):
    # d1i ← ∞   ∀ i ∈ V – {1}
    # d11 ← 0
    dist = [inf] * n
    dist[src] = 0

    # anterior(i) ← 0   ∀ i
    anterior = [-1] * n

    # |V|-1 passagens
    for _ in range(n - 1):
        updated = False
    # enquanto ∃ (j,i) ∈ A | d1j > d1i + vij fazer
        for (u, v, w) in edges:
            if dist[u] != inf and dist[v] > dist[u] + w:
    # d1j ← d1i + vij
                dist[v] = dist[u] + w
    # anterior(j) ← i
                anterior[v] = u
                updated = True
        if not updated:
            break 

    return dist, anterior

def reconstrucao_caminho(anterior, src, dest):
    caminho = []
    v = dest
    while v != -1:
        caminho.append(v)
        if v == src:
            break
        v = anterior[v]
    if caminho[-1] != src:
        return []
    caminho.reverse()
    return caminho

if __name__ == "__main__":

# ler arquivo
    with open("graph2.txt", "r", encoding="utf-8") as f:
        first = f.readline().strip().split("\t")
        n, m = map(int, first)

        edges = []
        for _ in range(m):
            u, v, w = f.readline().strip().split("\t")
            edges.append((int(u), int(v), int(w)))

    src = 0
    dest = n-1
    dist, anterior = bellman_ford(n, edges, src)
    caminho = reconstrucao_caminho(anterior, src, dest)

    if not caminho or dist[dest] == inf:
        print("Caminho: (sem caminho)")
        print("Custo total: inf")
    else:
        print("Caminho:", " -> ".join(map(str, caminho)))
        print("Custo total:", dist[dest])
