# Planos manuais por situação (referência para a comparação com o SAT)

Notação: `move(b, y, p)` = mover o bloco `b` para cima de `y` (bloco ou mesa `T`), começando no ponto `p`.
Estado: `bloco(ponto, nível)`.

Todos os planos abaixo foram conferidos por um simulador das regras do Item 1 (P1 a P6, nível máximo 2).
O tamanho mínimo (coluna "T mín.") foi obtido por busca em largura sobre os 2032 estados alcançáveis.

| Situação | Meta | Plano manual (item 3) | Nº de ações | T mín. |
|---|---|---|---|---|
| 1 | S_f3 | `move(d,c,0)`, `move(a,T,2)` | 2 | 2 |
| 1 | S_f4 | `move(d,c,0)`, `move(a,b,5)`, `move(d,T,2)`, `move(a,c,0)` | 4 | 4 |
| 1 | S_f1 | não detalhado no item 3 | - | 8 |
| 1 | S_f2 | não detalhado no item 3 | - | 9 |
| 2 | S_5 | `move(b,T,2)`, `move(a,b,2)`, `move(c,d,4)`, `move(a,c,4)`, `move(b,c,5)` | 5 | 5 |
| 3 | S_7 | `move(d,c,0)`, `move(a,b,5)`, `move(d,T,2)`, `move(a,c,0)`, `move(b,c,1)`, `move(d,T,3)` | 6 | 6 |

## Estados

| Situação | Estado inicial | Estado final |
|---|---|---|
| 1 (S_f3) | a(3,0) b(5,0) c(0,0) d(3,1) | a(2,0) b(5,0) c(0,0) d(0,1) |
| 1 (S_f4) | a(3,0) b(5,0) c(0,0) d(3,1) | a(0,1) b(5,0) c(0,0) d(2,0) |
| 2 | a(0,1) b(1,1) c(0,0) d(3,0) | a(4,2) b(5,2) c(4,1) d(3,0) |
| 3 | a(3,0) b(5,0) c(0,0) d(3,1) | a(0,1) b(1,1) c(0,0) d(3,0) |

## Como comparar com a saída do SAT

- Comparar o **tamanho do plano** (menor `T` satisfatível) e a **validade** de cada ação, não a sequência idêntica.
  Pode haver vários planos mínimos. Exemplo na Situação 2, com T=5: o plano manual leva `b` para a mesa, e o CNF corrigido
  devolveu outro plano igualmente válido, `move(a,d,3)`, `move(b,a,3)`, `move(c,d,4)`, `move(b,c,5)`, `move(a,c,4)`.
- Se o SAT for `UNSAT` para `T` menor que a coluna "T mín.", é o esperado. Se der `SAT` com `T` menor, há bug na codificação.
- O plano de exemplo da seção 6 do manual do professor (`d` sobre `c`; `a` para a mesa em 4; `d` para a mesa em 2; `a` sobre `c`) **não é válido**:
  no passo 3, `d` em p=2 cobre os slots 2, 3 e 4, e o slot 4 já está ocupado por `a`. Não usar esse exemplo como gabarito.
