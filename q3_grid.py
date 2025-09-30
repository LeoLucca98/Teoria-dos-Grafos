#!/usr/bin/env python3
"""Implementação de Dijkstra sobre grid alinhada ao pseudocódigo fornecido.

Pseudocódigo (rotulado) para referência:
    (P1) d_{1,1} ← 0
    (P2) d_{1,i} ← ∞, ∀ i ≠ origem
    (P3) A ← V
    (P4) F ← ∅
    (P5) anterior(i) ← 0, ∀ i
    (P6) enquanto A ≠ ∅:
                (P6.1) r ← vértice em A com menor d
                (P6.2) mover r: F ← F ∪ {r}; A ← A − {r}
                (P6.3) S ← sucessores abertos de r (N⁺(r) ∩ A)
                (P6.4) para cada i ∈ S:
                             (P6.4.1) p ← min(d_{1,i}, d_{1,r} + v_{r,i})
                             (P6.4.2) se p < d_{1,i}: d_{1,i} ← p; anterior(i) ← r

Mapeamento sintético neste arquivo:
    - V: células transitáveis (tuplas (r,c)) implícitas em 'grid' + função neighbors4.
    - Custos v_{r,i}: função cell_cost ao ENTRAR na célula destino.
    - Estruturas dist (d_{1,i}) e parent (anterior(i)). Ausência em dist => ∞ (P2).
    - Conjunto A (aberto) representado pelo min-heap 'heap'; vértices fora dele ou com entrada obsoleta são tratados ao comparar dist (lazy decrease-key). (P3)
    - Conjunto F (fechado) não é armazenado explicitamente; equivalem os vértices para os quais retiramos a entrada válida (quando d == dist[u]) — isto realiza (P4).
    - Laço principal e relaxamento: função dijkstra (ver comentários pontuais (P1..)).
    - Parada antecipada: quando extraímos 'goal' (garantia de otimalidade após (P6.1)).
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import heapq
import sys

## Representação do Grafo
# V: conjunto implícito das células transitáveis (tuplas (r,c)).
# Arestas direcionais de custo >= 0 para vizinhos em 4 direções.
# v_{r,i}: custo de entrar em i (cell_cost destino).
Cell = Tuple[int, int]  # (row, col)

## Tabela de custos (define v_{r,i})
COST = {'.': 1, '=': 1, '~': 3, 'S': 1, 'G': 1}

OBSTACLE = '#'

## Leitura / Modelagem (pré Dijkstra)
# Identifica origem (start) e objetivo (goal) para aplicação do algoritmo.

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
    return COST.get(ch, 1)  # v_{r,i}


def neighbors4(grid: List[str], r: int, c: int) -> List[Cell]:
    # N⁺(r) (P6.3): sucessores transitáveis.
    cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
    out: List[Cell] = []
    for nr, nc in cand:
        if in_bounds(grid, nr, nc) and is_passable(grid[nr][nc]):
            out.append((nr, nc))
    return out

# ---------------------------
# [Dijkstra]
# ---------------------------
# Núcleo do algoritmo conforme o anexo:
# - dist[] armazena o melhor custo conhecido de S até cada vértice.
# - parent[] armazena o predecessor para reconstrução do caminho mínimo.
# - heap (min-heap) realiza a operação de "extrair o vértice com menor distância"
#   (Extract-Min), central no laço principal.

def dijkstra(grid: List[str], start: Cell, goal: Cell):
    """Executa Dijkstra alinhado ao pseudocódigo (P1..P6.4.2). Retorna (path, total_cost, expanded_nodes)."""
    dist: Dict[Cell, int] = {start: 0}          # (P1) d_{1,1} ← 0  | (P2) implícito: demais ausentes => ∞
    parent: Dict[Cell, Cell] = {}               # (P5) anterior(i) ← 0 (aqui: ausência => indefinido)
    expanded = 0
    heap: List[Tuple[int, Cell]] = [(0, start)] # (P3) A ← V (representação implícita: só inserimos alcançáveis) + origem
    # (P4) F ← ∅ implícito: nenhum extraído ainda

    while heap:                                  # (P6) enquanto A ≠ ∅
        d, u = heapq.heappop(heap)              # (P6.1) r ← vértice com menor d (extract-min)
        expanded += 1
        if d != dist.get(u, float('inf')):      # entradas velhas simulam decrease-key (descartadas)
            continue
        if u == goal:                           # Parada antecipada após (P6.1) ao retirar objetivo
            path = reconstruct(parent, start, goal)
            return path, dist[goal], expanded
        ur, uc = u
        for v in neighbors4(grid, ur, uc):      # (P6.3) S: sucessores ainda "abertos" (não extraídos com dist consistente)
            vr, vc = v
            nd = d + cell_cost(grid[vr][vc])    # (P6.4.1) p candidato = d_{1,r} + v_{r,i}
            if nd < dist.get(v, float('inf')):  # (P6.4.1) p < d_{1,i} ?
                dist[v] = nd                    # (P6.4.2) d_{1,i} ← p
                parent[v] = u                   # (P6.4.2) anterior(i) ← r
                heapq.heappush(heap, (nd, v))   # reinserção = efeito de atualizar A
        # (P6.2) r passa a compor F: fato implícito ao não voltar ao heap com mesma dist
    return [], float('inf'), expanded            # nenhum caminho (distância ∞)

## Reconstrução (após término: percorre anterior(i))

def reconstruct(parent: Dict[Cell, Cell], start: Cell, goal: Cell) -> List[Cell]:
    if goal not in parent and goal != start:
        return []
    cur = goal
    path = [cur]
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path

## Visualização (não faz parte do pseudocódigo; apenas output)

def overlay_path(grid: List[str], path: List[Cell]) -> List[str]:
    g2 = [list(row) for row in grid]
    s = find_char(grid, 'S')
    g = find_char(grid, 'G')
    for (r, c) in path:
        if (r, c) != s and (r, c) != g:
            g2[r][c] = '*'
    return [''.join(row) for row in g2]

## Driver: orquestra leitura -> Dijkstra -> reconstrução -> visualização

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
        print("Uso: python q3_grid.py <arquivo_grid.txt>")
        sys.exit(1)
    solve_file(sys.argv[1])
