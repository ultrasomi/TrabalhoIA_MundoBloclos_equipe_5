# Execução manual dos cenários

Usa a representação do Item 1 (`poss`, `cov`, `free`, `clr`, `stable`, `overlap`) e os efeitos do Item 2. Nível máximo 2, mesa de 0 a 6. Cada bloco é escrito como `b(p,l)`.

**Pré-condições de `poss(move(b,y,p),t)`** (L = 0 se y = T; L = lev(y)+1 se y é bloco):

1. `clr(b,t)`
2. `y≠b ∧ 0 ≤ p ≤ 6−ℓ(b) ∧ L ≤ 2`
3. `y = T ∨ ∃q. at(y,q,t) ∧ overlap(b,p,y,q)`
4. `∀s∈[p,p+ℓ(b)). free(s,L,b,t)`
5. `stable(b,p,L,t)`
6. `¬(at(b,p,t) ∧ lev(b,L,t))`

**Efeitos** (t → t+1): ADD `at(b,p,t+1)`, `lev(b,L,t+1)`. DELETE da posição anterior `p0` e do nível anterior `l0` **somente se forem diferentes** de `p` e `L` (se `p0 = p` o `at` não é apagado; se `l0 = L` o `lev` não é apagado). Persistência: todo `b' ≠ b` mantém `at` e `lev`. `clr`, `on`, `cov`, `free`, `stable` são recalculados.


## Situação 1: S0 → Sf3

Estado inicial e final conforme o item 1 (Sf3 é o mais curto dos quatro; os outros levam 4, 8 e 9 movimentos).

- Estado inicial: `a(3,0) b(5,0) c(0,0) d(3,1)`
- Estado final: `a(2,0) b(5,0) c(0,0) d(0,1)`

| t | Ação | Pré 1–6 | Add | Delete | Estado em t+1 |
|---|---|---|---|---|---|
| 0 | `move(d,c,0)` | ✓ | `at(d,0,1)`, `lev(d,1,1)` | `at(d,3,1)` | `a(3,0) b(5,0) c(0,0) d(0,1)` |
| 1 | `move(a,T,2)` | ✓ | `at(a,2,2)`, `lev(a,0,2)` | `at(a,3,2)` | `a(2,0) b(5,0) c(0,0) d(0,1)` |

**Verificação da `poss` em cada passo:**

- **t=0: `move(d,c,0)`** (L=1; antes: `d(3,1)`)  
  - (1 clr) nada cobre os slots {3,4,5} no nível 2 ✓
  - (2 limites) y≠d, 0 ≤ 0 ≤ 3, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(d,0) = [0,3) e span(c,0) = [0,2) se sobrepõem ✓
  - (4 free) slots {0,1,2} livres no nível 1 ✓
  - (5 stable) slots {0,1} apoiados: 2 ≥ ⌈3/2⌉ = 2 ✓
  - (6 não é no-op) (3,1) ≠ (0,1) ✓
- **t=1: `move(a,T,2)`** (L=0; antes: `a(3,0)`)  
  - (1 clr) nada cobre os slots {3} no nível 1 ✓
  - (2 limites) y≠a, 0 ≤ 2 ≤ 5, L=0 ≤ 2 ✓
  - (3 apoio/sobreposição) y = T ✓
  - (4 free) slots {2} livres no nível 0 ✓
  - (5 stable) L = 0 (apoio na mesa) ✓
  - (6 não é no-op) (3,0) ≠ (2,0) ✓

**Relações `on` no estado final:** `on(a,T)`, `on(b,T)`, `on(c,T)`, `on(d,a)`, `on(d,c)`


## Situação 1 (extra): S0 → Sf4

Plano de 4 movimentos. Coincide com os estados S0 a S4 da Situação 3.

- Estado inicial: `a(3,0) b(5,0) c(0,0) d(3,1)`
- Estado final: `a(0,1) b(5,0) c(0,0) d(2,0)`

| t | Ação | Pré 1–6 | Add | Delete | Estado em t+1 |
|---|---|---|---|---|---|
| 0 | `move(d,c,0)` | ✓ | `at(d,0,1)`, `lev(d,1,1)` | `at(d,3,1)` | `a(3,0) b(5,0) c(0,0) d(0,1)` |
| 1 | `move(a,b,5)` | ✓ | `at(a,5,2)`, `lev(a,1,2)` | `at(a,3,2)`, `lev(a,0,2)` | `a(5,1) b(5,0) c(0,0) d(0,1)` |
| 2 | `move(d,T,2)` | ✓ | `at(d,2,3)`, `lev(d,0,3)` | `at(d,0,3)`, `lev(d,1,3)` | `a(5,1) b(5,0) c(0,0) d(2,0)` |
| 3 | `move(a,c,0)` | ✓ | `at(a,0,4)`, `lev(a,1,4)` | `at(a,5,4)` | `a(0,1) b(5,0) c(0,0) d(2,0)` |

**Verificação da `poss` em cada passo:**

- **t=0: `move(d,c,0)`** (L=1; antes: `d(3,1)`)  
  - (1 clr) nada cobre os slots {3,4,5} no nível 2 ✓
  - (2 limites) y≠d, 0 ≤ 0 ≤ 3, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(d,0) = [0,3) e span(c,0) = [0,2) se sobrepõem ✓
  - (4 free) slots {0,1,2} livres no nível 1 ✓
  - (5 stable) slots {0,1} apoiados: 2 ≥ ⌈3/2⌉ = 2 ✓
  - (6 não é no-op) (3,1) ≠ (0,1) ✓
- **t=1: `move(a,b,5)`** (L=1; antes: `a(3,0)`)  
  - (1 clr) nada cobre os slots {3} no nível 1 ✓
  - (2 limites) y≠a, 0 ≤ 5 ≤ 5, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(a,5) = [5,6) e span(b,5) = [5,6) se sobrepõem ✓
  - (4 free) slots {5} livres no nível 1 ✓
  - (5 stable) slots {5} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (3,0) ≠ (5,1) ✓
- **t=2: `move(d,T,2)`** (L=0; antes: `d(0,1)`)  
  - (1 clr) nada cobre os slots {0,1,2} no nível 2 ✓
  - (2 limites) y≠d, 0 ≤ 2 ≤ 3, L=0 ≤ 2 ✓
  - (3 apoio/sobreposição) y = T ✓
  - (4 free) slots {2,3,4} livres no nível 0 ✓
  - (5 stable) L = 0 (apoio na mesa) ✓
  - (6 não é no-op) (0,1) ≠ (2,0) ✓
- **t=3: `move(a,c,0)`** (L=1; antes: `a(5,1)`)  
  - (1 clr) nada cobre os slots {5} no nível 2 ✓
  - (2 limites) y≠a, 0 ≤ 0 ≤ 5, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(a,0) = [0,1) e span(c,0) = [0,2) se sobrepõem ✓
  - (4 free) slots {0} livres no nível 1 ✓
  - (5 stable) slots {0} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (5,1) ≠ (0,1) ✓

**Relações `on` no estado final:** `on(a,c)`, `on(b,T)`, `on(c,T)`, `on(d,T)`


## Situação 2: S0 → S5

Plano de 5 movimentos, que passa pelos estados S1 a S4 do slide.

- Estado inicial: `a(0,1) b(1,1) c(0,0) d(3,0)`
- Estado final: `a(4,2) b(5,2) c(4,1) d(3,0)`

| t | Ação | Pré 1–6 | Add | Delete | Estado em t+1 |
|---|---|---|---|---|---|
| 0 | `move(b,T,2)` | ✓ | `at(b,2,1)`, `lev(b,0,1)` | `at(b,1,1)`, `lev(b,1,1)` | `a(0,1) b(2,0) c(0,0) d(3,0)` |
| 1 | `move(a,b,2)` | ✓ | `at(a,2,2)`, `lev(a,1,2)` | `at(a,0,2)` | `a(2,1) b(2,0) c(0,0) d(3,0)` |
| 2 | `move(c,d,4)` | ✓ | `at(c,4,3)`, `lev(c,1,3)` | `at(c,0,3)`, `lev(c,0,3)` | `a(2,1) b(2,0) c(4,1) d(3,0)` |
| 3 | `move(a,c,4)` | ✓ | `at(a,4,4)`, `lev(a,2,4)` | `at(a,2,4)`, `lev(a,1,4)` | `a(4,2) b(2,0) c(4,1) d(3,0)` |
| 4 | `move(b,c,5)` | ✓ | `at(b,5,5)`, `lev(b,2,5)` | `at(b,2,5)`, `lev(b,0,5)` | `a(4,2) b(5,2) c(4,1) d(3,0)` |

**Verificação da `poss` em cada passo:**

- **t=0: `move(b,T,2)`** (L=0; antes: `b(1,1)`)  
  - (1 clr) nada cobre os slots {1} no nível 2 ✓
  - (2 limites) y≠b, 0 ≤ 2 ≤ 5, L=0 ≤ 2 ✓
  - (3 apoio/sobreposição) y = T ✓
  - (4 free) slots {2} livres no nível 0 ✓
  - (5 stable) L = 0 (apoio na mesa) ✓
  - (6 não é no-op) (1,1) ≠ (2,0) ✓
- **t=1: `move(a,b,2)`** (L=1; antes: `a(0,1)`)  
  - (1 clr) nada cobre os slots {0} no nível 2 ✓
  - (2 limites) y≠a, 0 ≤ 2 ≤ 5, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(a,2) = [2,3) e span(b,2) = [2,3) se sobrepõem ✓
  - (4 free) slots {2} livres no nível 1 ✓
  - (5 stable) slots {2} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (0,1) ≠ (2,1) ✓
- **t=2: `move(c,d,4)`** (L=1; antes: `c(0,0)`)  
  - (1 clr) nada cobre os slots {0,1} no nível 1 ✓
  - (2 limites) y≠c, 0 ≤ 4 ≤ 4, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(c,4) = [4,6) e span(d,3) = [3,6) se sobrepõem ✓
  - (4 free) slots {4,5} livres no nível 1 ✓
  - (5 stable) slots {4,5} apoiados: 2 ≥ ⌈2/2⌉ = 1 ✓
  - (6 não é no-op) (0,0) ≠ (4,1) ✓
- **t=3: `move(a,c,4)`** (L=2; antes: `a(2,1)`)  
  - (1 clr) nada cobre os slots {2} no nível 2 ✓
  - (2 limites) y≠a, 0 ≤ 4 ≤ 5, L=2 ≤ 2 ✓
  - (3 apoio/sobreposição) span(a,4) = [4,5) e span(c,4) = [4,6) se sobrepõem ✓
  - (4 free) slots {4} livres no nível 2 ✓
  - (5 stable) slots {4} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (2,1) ≠ (4,2) ✓
- **t=4: `move(b,c,5)`** (L=2; antes: `b(2,0)`)  
  - (1 clr) nada cobre os slots {2} no nível 1 ✓
  - (2 limites) y≠b, 0 ≤ 5 ≤ 5, L=2 ≤ 2 ✓
  - (3 apoio/sobreposição) span(b,5) = [5,6) e span(c,4) = [4,6) se sobrepõem ✓
  - (4 free) slots {5} livres no nível 2 ✓
  - (5 stable) slots {5} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (2,0) ≠ (5,2) ✓

**Relações `on` no estado final:** `on(a,c)`, `on(b,c)`, `on(c,d)`, `on(d,T)`


## Situação 3: S0 → S7

Plano de 6 movimentos: S0→S1→S2→S3→S4→S5→S7 (S6 é igual a S5, sem ação entre eles).

- Estado inicial: `a(3,0) b(5,0) c(0,0) d(3,1)`
- Estado final: `a(0,1) b(1,1) c(0,0) d(3,0)`

| t | Ação | Pré 1–6 | Add | Delete | Estado em t+1 |
|---|---|---|---|---|---|
| 0 | `move(d,c,0)` | ✓ | `at(d,0,1)`, `lev(d,1,1)` | `at(d,3,1)` | `a(3,0) b(5,0) c(0,0) d(0,1)` |
| 1 | `move(a,b,5)` | ✓ | `at(a,5,2)`, `lev(a,1,2)` | `at(a,3,2)`, `lev(a,0,2)` | `a(5,1) b(5,0) c(0,0) d(0,1)` |
| 2 | `move(d,T,2)` | ✓ | `at(d,2,3)`, `lev(d,0,3)` | `at(d,0,3)`, `lev(d,1,3)` | `a(5,1) b(5,0) c(0,0) d(2,0)` |
| 3 | `move(a,c,0)` | ✓ | `at(a,0,4)`, `lev(a,1,4)` | `at(a,5,4)` | `a(0,1) b(5,0) c(0,0) d(2,0)` |
| 4 | `move(b,c,1)` | ✓ | `at(b,1,5)`, `lev(b,1,5)` | `at(b,5,5)`, `lev(b,0,5)` | `a(0,1) b(1,1) c(0,0) d(2,0)` |
| 5 | `move(d,T,3)` | ✓ | `at(d,3,6)`, `lev(d,0,6)` | `at(d,2,6)` | `a(0,1) b(1,1) c(0,0) d(3,0)` |

**Verificação da `poss` em cada passo:**

- **t=0: `move(d,c,0)`** (L=1; antes: `d(3,1)`)  
  - (1 clr) nada cobre os slots {3,4,5} no nível 2 ✓
  - (2 limites) y≠d, 0 ≤ 0 ≤ 3, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(d,0) = [0,3) e span(c,0) = [0,2) se sobrepõem ✓
  - (4 free) slots {0,1,2} livres no nível 1 ✓
  - (5 stable) slots {0,1} apoiados: 2 ≥ ⌈3/2⌉ = 2 ✓
  - (6 não é no-op) (3,1) ≠ (0,1) ✓
- **t=1: `move(a,b,5)`** (L=1; antes: `a(3,0)`)  
  - (1 clr) nada cobre os slots {3} no nível 1 ✓
  - (2 limites) y≠a, 0 ≤ 5 ≤ 5, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(a,5) = [5,6) e span(b,5) = [5,6) se sobrepõem ✓
  - (4 free) slots {5} livres no nível 1 ✓
  - (5 stable) slots {5} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (3,0) ≠ (5,1) ✓
- **t=2: `move(d,T,2)`** (L=0; antes: `d(0,1)`)  
  - (1 clr) nada cobre os slots {0,1,2} no nível 2 ✓
  - (2 limites) y≠d, 0 ≤ 2 ≤ 3, L=0 ≤ 2 ✓
  - (3 apoio/sobreposição) y = T ✓
  - (4 free) slots {2,3,4} livres no nível 0 ✓
  - (5 stable) L = 0 (apoio na mesa) ✓
  - (6 não é no-op) (0,1) ≠ (2,0) ✓
- **t=3: `move(a,c,0)`** (L=1; antes: `a(5,1)`)  
  - (1 clr) nada cobre os slots {5} no nível 2 ✓
  - (2 limites) y≠a, 0 ≤ 0 ≤ 5, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(a,0) = [0,1) e span(c,0) = [0,2) se sobrepõem ✓
  - (4 free) slots {0} livres no nível 1 ✓
  - (5 stable) slots {0} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (5,1) ≠ (0,1) ✓
- **t=4: `move(b,c,1)`** (L=1; antes: `b(5,0)`)  
  - (1 clr) nada cobre os slots {5} no nível 1 ✓
  - (2 limites) y≠b, 0 ≤ 1 ≤ 5, L=1 ≤ 2 ✓
  - (3 apoio/sobreposição) span(b,1) = [1,2) e span(c,0) = [0,2) se sobrepõem ✓
  - (4 free) slots {1} livres no nível 1 ✓
  - (5 stable) slots {1} apoiados: 1 ≥ ⌈1/2⌉ = 1 ✓
  - (6 não é no-op) (5,0) ≠ (1,1) ✓
- **t=5: `move(d,T,3)`** (L=0; antes: `d(2,0)`)  
  - (1 clr) nada cobre os slots {2,3,4} no nível 1 ✓
  - (2 limites) y≠d, 0 ≤ 3 ≤ 3, L=0 ≤ 2 ✓
  - (3 apoio/sobreposição) y = T ✓
  - (4 free) slots {3,4,5} livres no nível 0 ✓
  - (5 stable) L = 0 (apoio na mesa) ✓
  - (6 não é no-op) (2,0) ≠ (3,0) ✓

**Relações `on` no estado final:** `on(a,c)`, `on(b,c)`, `on(c,T)`, `on(d,T)`
