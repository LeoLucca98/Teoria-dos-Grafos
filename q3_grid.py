#!/usr/bin/env python3
"""
Mapa conciso para o pseudocódigo do livro:
    V -> células transitáveis
    origem (1) -> start (S)
    d_i -> dist (dict; ausência = ∞)
    anterior(i) -> parent
    A (abertos) -> conteúdo vivo do min-heap (heap)
    F (fechados) -> vértices já extraídos com distância consistente (não re-listados)
    r -> vértice u retirado do heap (menor distância)
    N(r) -> neighbors4(r)
    v_{r,l} -> cell_cost(destino)
    p = min[d_l, d_r + v_{r,l}] -> nd = d + w; comparar com dist.get(v, ∞)
    decrease-key -> reinserção (nd, v); entradas antigas descartadas ao checar distância
    parada antecipada -> quando goal sai do heap (dist ótima garantida)

Fases: leitura/modelagem -> dijkstra (inicialização, laço extract-min + relaxamento) -> reconstrução -> visualização.
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import heapq
import sys

# ---------------------------
# [Representação do Grafo]
# ---------------------------
# Cada célula transitável é um vértice (r,c).
# Arestas implícitas ligam (r,c) aos vizinhos N/S/L/O transitáveis.
# O custo da aresta (u -> v) é o custo de ENTRAR em v (definido por COST).
Cell = Tuple[int, int]  # (row, col)

COST = {
    '.': 1, '=': 1,
    '~': 3,
    'S': 1, 'G': 1,
}

OBSTACLE = '#'

# ---------------------------
# [Leitura do Grid]
# ---------------------------
# Apenas constrói a estrutura do problema (não é parte do núcleo do algoritmo).
# Identifica S (origem) e G (alvo) para executar Dijkstra a partir de S.

def read_grid(path: str) -> Tuple[List[str], Cell, Cell]:
    # Pré-processamento: constrói V e identifica origem (start) e objetivo (goal).
    with open(path, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
        if not header:
            raise ValueError("Arquivo vazio ou cabeçalho ausente.")
        try:
            rows, cols = map(int, header.split())
        except Exception as e:
            raise ValueError(f"Primeira linha deve ter 'linhas colunas'. Erro: {e}")

        grid: List[str] = []
        for _ in range(rows):
            line = f.readline()
            if not line:
                raise ValueError("Arquivo terminou antes de ler todas as linhas do grid.")
            line = line.rstrip('\n')
            # Garante largura exata do grid
            if len(line) < cols:
                line = line + ' ' * (cols - len(line))
            elif len(line) > cols:
                line = line[:cols]
            grid.append(line)

    start = find_char(grid, 'S')
    goal = find_char(grid, 'G')
    if start is None or goal is None:
        raise ValueError("Grid deve conter 'S' (início) e 'G' (objetivo).")
    return grid, start, goal


def find_char(grid: List[str], ch: str) -> Optional[Cell]:
    for r, row in enumerate(grid):
        c = row.find(ch)
        if c != -1:
            return (r, c)
    return None


def in_bounds(grid: List[str], r: int, c: int) -> bool:
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def is_passable(ch: str) -> bool:
    return ch != OBSTACLE


def cell_cost(ch: str) -> int:
    # Define o peso não negativo usado por Dijkstra.
    return COST.get(ch, 1)


def neighbors4(grid: List[str], r: int, c: int) -> List[Cell]:
    # Gera N(r): vizinhos em 4 direções (arestas unitárias conceituais com peso definido ao entrar). 
    cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
    out = []
    for nr, nc in cand:
        if in_bounds(grid, nr, nc) and is_passable(grid[nr][nc]):
            out.append((nr, nc))
    return out

# ---------------------------
# [Dijkstra]
# ---------------------------
# Núcleo do algoritmo conforme o anexo:
# - dist[] armazena melhor custo conhecido de S até cada vértice.
# - parent[] armazena o predecessor para reconstrução do caminho mínimo.
# - heap (min-heap) realiza a operação de "extrair o vértice com menor distância"
#   (Extract-Min), central no laço principal.

def dijkstra(grid: List[str], start: Cell, goal: Cell):
    """Dijkstra com lazy decrease-key e parada antecipada.
    Retorna (path, total_cost, expanded_nodes)."""
    dist: Dict[Cell, int] = {start: 0}
    parent: Dict[Cell, Cell] = {}
    expanded = 0
    heap: List[Tuple[int, Cell]] = [(0, start)]  # abertos (A) iniciando pela origem

    while heap:  # laço enquanto A ≠ ∅
        d, u = heapq.heappop(heap)  # extract-min (r)
        expanded += 1
        if d != dist.get(u, float('inf')):
            continue  # descarta entrada antiga (efeito decrease-key)
        if u == goal:  # parada antecipada segura
            path = reconstruct(parent, start, goal)
            return path, dist[goal], expanded
        ur, uc = u
        for v in neighbors4(grid, ur, uc):  # N(r)
            vr, vc = v
            nd = d + cell_cost(grid[vr][vc])  # candidato p = d_r + v_{r,l}
            if nd < dist.get(v, float('inf')):  # relaxamento
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
    return [], float('inf'), expanded  # sem caminho

# ---------------------------
# [Reconstrução do Caminho]
# ---------------------------
# Não é parte do núcleo de Dijkstra no anexo, mas decorre de parent[]
# definido pelas relaxações.

def reconstruct(parent: Dict[Cell, Cell], start: Cell, goal: Cell) -> List[Cell]:
    # Pós-processamento: percorre anterior(i) para formar o caminho.
    if goal not in parent and goal != start:
        return []
    cur = goal
    path = [cur]
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path

# ---------------------------
# [Visualização do Resultado]
# ---------------------------
# Apenas sobrepõe '*' no caminho encontrado; não faz parte do algoritmo em si.

def overlay_path(grid: List[str], path: List[Cell]) -> List[str]:
    # Visualização auxiliar (não faz parte de Dijkstra): sobrepõe '*'.
    g2 = [list(row) for row in grid]
    s = find_char(grid, 'S')
    g = find_char(grid, 'G')
    for (r, c) in path:
        if (r, c) != s and (r, c) != g:
            g2[r][c] = '*'
    return [''.join(row) for row in g2]

# ---------------------------
# [Driver] — encadeia leitura, Dijkstra e impressão do resultado.
# ---------------------------

def solve_file(path: str) -> None:
    grid, s, g = read_grid(path)
    path, cost, expanded = dijkstra(grid, s, g)
    if not path:
        print("Nenhum caminho encontrado.")
        return
    out = overlay_path(grid, path)
    print("Caminho encontrado! [Dijkstra]")
    print(f"Custo total: {cost}")
    print(f"Passos (número de movimentos): {max(0, len(path)-1)}")
    print(f"Nós expandidos: {expanded}")
    print("\nGrid com caminho '*':\n")
    for line in out:
        print(line)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python warehouse_pathfinding_dijkstra.py <arquivo_grid.txt>")
        sys.exit(1)
    solve_file(sys.argv[1])
