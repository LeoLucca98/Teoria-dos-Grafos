#!/usr/bin/env python3
import sys
from typing import List, Tuple
import math

INF = math.inf

def read_undirected_graph_from_txt(path: str) -> Tuple[int, List[Tuple[int,int,float]]]:
    """
    Lê grafo não-direcionado no formato:
        <num_vertices> <num_arestas>
        <u> <v> <w>
        ...
    Retorna: (n, edges) com vértices 1..n e edges em ambas as direções.
    """
    edges: List[Tuple[int,int,float]] = []
    with open(path, 'r', encoding='utf-8') as f:
        first = f.readline()
        if not first:
            raise ValueError("Arquivo vazio.")
        parts = first.strip().split()
        if len(parts) < 2:
            raise ValueError("Primeira linha deve conter: <num_vertices> <num_arestas>")
        n, m = int(parts[0]), int(parts[1])
        # m não é usado diretamente; iteramos sobre todas as linhas seguintes

        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            u, v, w = line.split()
            u, v, w = int(u), int(v), float(w)
            edges.append((u, v, w))
            edges.append((v, u, w))  # não-dir

    return n, edges

def floyd_init_with_routing(n: int, edges: List[Tuple[int,int,float]]):
    """
    Inicializa:
      D^0: distâncias diretas (0 na diagonal, ∞ se não há aresta)
      R: matriz de roteamento com r_ij <- j (inclui diagonal para consistência)
    """
    D = [[INF]*(n+1) for _ in range(n+1)]
    for i in range(1, n+1):
        D[i][i] = 0.0

    for u, v, w in edges:
        if w < D[u][v]:
            D[u][v] = w

    R = [[None]*(n+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for j in range(1, n+1):
            if D[i][j] < INF:
                R[i][j] = j
    return D, R

def floyd_warshall_with_routing(n: int, edges: List[Tuple[int,int,float]]):
    """
    Floyd–Warshall completo com matriz de roteamento R,
    inspirado no pseudocódigo visto em sala.
    """
    D, R = floyd_init_with_routing(n, edges)

    for k in range(1, n+1):
        for i in range(1, n+1):
            dik = D[i][k]
            if dik == INF:
                continue
            for j in range(1, n+1):
                alt = dik + D[k][j]
                if alt < D[i][j]:
                    D[i][j] = alt
                    R[i][j] = R[i][k]  # r_ij ← r_ik

    return D, R

def reconstruct_path(R: List[List[int]], i: int, j: int) -> List[int]:
    """
    Reconstrói o caminho i→j usando a matriz de roteamento R (next-hop).
    Retorna [] se não há caminho.
    """
    if i == j:
        return [i]
    if R[i][j] is None:
        return []

    path = [i]
    cur = i
    limit = len(R) * len(R)

    while cur != j and limit > 0:
        nxt = R[cur][j]
        if nxt is None:
            return []
        path.append(nxt)
        cur = nxt
        limit -= 1

    return path if cur == j else []

def choose_central_vertex(D: List[List[float]]) -> Tuple[int, List[float]]:
    """
    Retorna (v_central, vetor_de_distancias).
    v_central minimiza a soma das distâncias aos demais.
    """
    n = len(D) - 1
    best_v, best_sum, best_row = None, INF, None
    for v in range(1, n+1):
        row = D[v][1:]
        s = sum(row)
        if s < best_sum:
            best_sum, best_v, best_row = s, v, row
    return best_v, best_row

def print_dist_matrix(D: List[List[float]]) -> None:
    """Imprime a matriz de distâncias D (1-indexada) com cabeçalho."""
    n = len(D) - 1
    header = "     " + " ".join(f"{j:>4}" for j in range(1, n+1))
    print(header)
    for i in range(1, n+1):
        row_str = []
        for j in range(1, n+1):
            val = D[i][j]
            row_str.append("∞".rjust(4) if val == INF else f"{int(val):4d}")
        print(f"{i:>3} | " + " ".join(row_str))

def main():
    if len(sys.argv) < 2:
        print("Uso: python q1_floyd_central.py <graph1.txt>")
        sys.exit(1)

    path = sys.argv[1]
    n, edges = read_undirected_graph_from_txt(path)
    D, R = floyd_warshall_with_routing(n, edges)

    # (a) estação central e (b) vetor de distâncias
    central, vetor = choose_central_vertex(D)

    # (c) mais distante a partir do central
    max_vert = max(range(1, n+1), key=lambda j: (-1 if j == central else vetor[j-1]))
    max_dist = vetor[max_vert-1]

    print(f"Estação central: {central}")
    print("Vetor de distâncias (a partir da estação central):")
    print(", ".join(f"d({central},{j})={int(vetor[j-1])}" for j in range(1, n+1)))
    print(f"Mais distante a partir do central: vértice {max_vert} com distância {int(max_dist)}")

    print("\nMatriz de distâncias mínimas (D):")
    print_dist_matrix(D)

if __name__ == "__main__":
    main()
