#!/usr/bin/env python3
import sys
from typing import List, Tuple

def read_undirected_graph_from_txt(path: str) -> Tuple[int, List[Tuple[int,int,float]]]:
    edges: List[Tuple[int,int,float]] = []
    with open(path, 'r', encoding='utf-8') as f:
        first = f.readline()
        n, m = map(int, first.strip().split())
        for line in f:
            u, v, w = line.split()
            u, v, w = int(u), int(v), float(w)
            edges.append((u, v, w))
            edges.append((v, u, w))  # não-dir
    return n, edges

def main():
    if len(sys.argv) < 2:
        print("Uso: python q1_floyd_central.py <graph1.txt>")
        sys.exit(1)
    n, edges = read_undirected_graph_from_txt(sys.argv[1])
    print(f"OK: lidos {n} vértices e {len(edges)//2} arestas.")

if __name__ == "__main__":
    main()