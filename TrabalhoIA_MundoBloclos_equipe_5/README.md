# TrabalhoIA_MundoBloclos_equipe_5

Fundamentos de Inteligência Artificial: Mundo dos Blocos de tamanho variável via SAT solver (Prof. Edjard Mota).
Prazo: 02/10/2026.

O problema: quatro blocos `a`, `b`, `c`, `d` com comprimentos 1, 1, 2 e 3 sobre uma mesa com pontos de 0 a 6 (seis slots), empilháveis em até três níveis (0, 1 e 2), com a ação qualitativa `move(b, y, p)`: mover o bloco `b` para cima de `y` (outro bloco ou a mesa `T`), começando no ponto `p`. Um bloco só pode ser colocado se tiver apoio suficiente por baixo (equilíbrio). Os planos são encontrados codificando o problema em CNF e usando o `minisat`.

## Estrutura do repositório

```
TrabalhoIA_MundoBloclos_equipe_5/
├── README.md
├── latex/                      # projeto do Overleaf (main.tex e secoes/)
├── execucao_manual.md          # item 3: execução manual das três situações
├── planos_manuais.md           # tabela dos planos manuais, usada na comparação com o SAT
├── gerar_cnf.py                # gera o .cnf e o .map de uma situação
├── interpretar.py              # traduz a saída do minisat em um plano em português
├── buscar_plano.py             # roda o minisat com T = 1, 2, 3... até o primeiro SAT
├── ordem_parcial.py            # item 4: elos causais e ordem parcial de um plano
├── trab01_blocos2SAT_situacao1.cnf / .map / resultado1.txt
├── trab01_blocos2SAT_situacao2.cnf / .map / resultado2.txt
└── trab01_blocos2SAT_situacao3.cnf / .map / resultado3.txt
```

Os arquivos `.cnf` e `.map` seguem o nome pedido no enunciado (`trab01_blocos2SAT`), com o sufixo da situação. A Situação 1 usa a meta `S_f3` (2 ações) por padrão.

## Como executar

Requisitos: Python 3 e o `minisat` instalado (no PATH).

### Passo a passo (uma situação)

```bash
# 1. gerar o CNF e o mapa (situação, horizonte)
python3 gerar_cnf.py 3 6

# 2. rodar o minisat
minisat trab01_blocos2SAT_situacao3.cnf resultado3.txt

# 3. interpretar o resultado (usa o .map correspondente)
python3 interpretar.py resultado3.txt --verbose
```

O horizonte `T` é o número de ações do plano. Sem argumentos, `python3 gerar_cnf.py` gera as três situações com o horizonte padrão (2, 5 e 6).

### Plano mínimo automático

```bash
python3 buscar_plano.py 1          # Situação 1 (meta S_f3)
python3 buscar_plano.py 2          # Situação 2
python3 buscar_plano.py 3          # Situação 3
python3 buscar_plano.py 1 f4       # Situação 1 com a meta S_f4 (f1, f2, f3 ou f4)
```

O script roda o minisat com `T = 1, 2, 3, ...` e para no primeiro `SATISFIABLE`. Esse `T` é o comprimento mínimo do plano, porque os valores menores deram `UNSATISFIABLE`. Ele grava o `resultadoN.txt` e chama o `interpretar.py`. As metas `f1` e `f2` pedem planos de 8 e 9 ações e podem demorar mais.

### Ordem parcial (item 4)

```bash
# análise dos planos manuais (situação 1, 2, 3 ou 1f4)
python3 ordem_parcial.py --manual 3

# análise do plano devolvido pelo minisat
python3 ordem_parcial.py resultado3.txt

# ordem parcial entre metas: b(1,1) deve valer antes de a(0,1)
python3 buscar_plano.py 3 --tmax 8 --ordem='b(1,1)<a(0,1)'
```

O `ordem_parcial.py` imprime os elos causais `A_i --fato--> A_j`, o número de ordens de execução válidas das mesmas ações e as restrições de ordem necessárias. Com `--ordem`, o gerador acrescenta as cláusulas de ordem entre metas, e o `interpretar.py` confere se a ordem foi respeitada. Os arquivos desse cenário levam o sufixo `_ordem`.

## Resultados

Comprimento mínimo do plano. A coluna "esperado" foi obtida por busca em largura sobre os 2032 estados alcançáveis, com as regras do Item 1.

| Situação | Meta | T mínimo esperado | T mínimo no minisat |
|---|---|---|---|
| 1 | S_f3 | 2 | 2 |
| 1 | S_f4 | 4 | 4 |
| 1 | S_f1 | 8 | 8 |
| 1 | S_f2 | 9 | 9 |
| 2 | S_5 | 5 | 5 |
| 3 | S_7 | 6 | 6 |

Os planos do SAT são comparados com os manuais (`planos_manuais.md`) pelo tamanho e pela validade, não pela sequência idêntica, porque pode haver vários planos mínimos. O `interpretar.py` ainda confere cada ação contra as pré-condições P1 a P6 do Item 1, de forma independente do CNF.

## Observações

- Os `resultado*.txt` devem ser a saída real do `minisat`. Sem o arquivo `.map`, a saída numérica não tem significado.
- A pré-condição de `move` usa `free` por slot no lugar de `clr(y)` do manual, como descrito no Item 1 do documento LaTeX.
- A relação `on(b, y, t)` não é codificada em CNF. Ela é derivada de `at`, `lev` e da sobreposição dos blocos, em `interpretar.py` (função `derivar_on`).
- O plano de exemplo da seção 6 do manual do professor não é válido: no passo 3, o bloco `d` em p=2 cobre o slot 4, que já está ocupado por `a`. Não deve ser usado como gabarito.
- Nos quatro planos manuais, a ordem parcial resulta em uma cadeia totalmente ordenada (uma única ordem de execução válida). Com a ordem entre metas `b(1,1)` antes de `a(0,1)`, o plano mínimo da Situação 3 passa de 6 para 7 ações.

## Documentação em LaTeX

O conteúdo do Overleaf está em `latex/`: introdução, descrição formal (itens 1, 2 e 4), execução manual (item 3), codificação CNF, exemplos, mapeamento formal → código, execução passo a passo e interpretação da saída.

## Responsáveis

| Parte | Responsável |
|---|---|
| Item 1 (LPO) | Fernando |
| Item 2 (adds/deletes) | Luis Felipe |
| Item 3 (execução manual, 3 situações) | Guilherme |
| Item 4 (ordem parcial) | Guilherme |
| Item 5 (codificação SAT) | Yuri e Gabriel |
| Introdução | Guilherme |
