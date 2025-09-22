#!/usr/bin/env python3
import sys
from typing import List, Tuple
import math

INF = math.inf

def read_undirected_graph_from_txt(path: str) -> Tuple[int, List[Tuple[int,int,float]]]:
    edges: List[Tuple[int,int,float]] = []
    with open(path, 'r', encoding='utf-8') as f:
        first = f.readline()
        if not first:
            raise ValueError("Arquivo vazio.")
        parts = first.strip().split()
        if len(parts) < 2:
            raise ValueError("Primeira linha deve conter: <num_vertices> <num_arestas>")
        n, m = int(parts[0]), int(parts[1])
        #não estamos usando m por conta da iteração ser feita até o fim do arquivo

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
    # Matriz de distâncias 1-indexada
    D = [[INF]*(n+1) for _ in range(n+1)]
    for i in range(1, n+1):
        D[i][i] = 0.0

    # Preenche com o menor peso direto conhecido (pode haver paralelas)
    for u, v, w in edges:
        if w < D[u][v]:
            D[u][v] = w

    # Matriz de roteamento (next-hop): r_ij <- j se existe caminho direto (ou i==j)
    R = [[None]*(n+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for j in range(1, n+1):
            if D[i][j] < INF:
                R[i][j] = j
    return D, R


def main():
    if len(sys.argv) < 2:
        print("Uso: python q1_floyd_central.py <graph1.txt>")
        sys.exit(1)

    n, edges = read_undirected_graph_from_txt(sys.argv[1])
    print(f"OK: lidos {n} vértices e {len(edges)//2} arestas (não-dir).")

if __name__ == "__main__":
    main()
