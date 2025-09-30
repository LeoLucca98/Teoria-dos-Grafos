# Prática 1

## Q1 - (Floyd_Warshall)
Aqui usamos o Floyd para calcular todas as distâncias entre os vértices, já que a ideia é descobrir qual ponto pode servir de estação central considerando todo o grafo.

Formato de entrada:

```
<num_vertices> <num_arestas>
<u> <v> <w>
...
```
Rodar:
`python q1_floyd_central.py graph1.txt`

## Q2 - (Bellman-Ford)
O Bellman-Ford foi escolhido porque permite lidar com trechos que gastam e outros que devolvem energia, encontrando o caminho de menor consumo líquido mesmo com valores negativos.

Formato de entrada:

```
<num_vertices> <num_arestas>
<u> <v> <w>
...
```
Rodar:
`python q2_otimizando_caminho.py graph2.txt`

## Q3 — (Dijkstra)
No caso do grid, todos os movimentos têm custo positivo, então o Dijkstra é o mais adequado para encontrar o caminho mais curto da origem até o destino no mapa.

Formato de entrada:
```
<linhas> <colunas>
<linha 1 do grid>
...
<linha N do grid>
```
Rodar:
`python q3_grid.py grid_example.txt`
