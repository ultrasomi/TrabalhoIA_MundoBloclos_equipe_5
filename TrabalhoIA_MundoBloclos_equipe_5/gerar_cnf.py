#!/usr/bin/env python3
# VERSÃO REVISADA do gerar_cnf.py (Yuri/Gabriel). Mudanças:
#  1. CORREÇÃO DE BUG: mover para cima de um bloco que já está no nível máximo (MAX_LEVEL)
#     não tinha nenhuma cláusula, então o solver podia "teletransportar" o bloco. Agora é proibido.
#  2. O plano manual NÃO é mais fixado no CNF (antes havia uma cláusula unitária por ação).
#     Quem acha o plano agora é o SAT solver.
#  3. O resultado*.txt NÃO é mais gerado pelo script: deve ser a saída real do minisat.
#  4. P6 (no-op) agora testa posição E nível, como na descrição formal.
#  5. Aceita situação, horizonte e (na Situação 1) a meta S_f1..S_f4 pela linha de comando.
#  7. ORDEM PARCIAL (item 4): --ordem='b(1,1)<a(0,1)' acrescenta cláusulas que obrigam a meta
#     da esquerda a valer antes da da direita (grupo ORD).
#  6. CORREÇÃO DE BUG: a estabilidade aceitava como apoio um bloco em QUALQUER nível. Agora o apoio
#     tem que estar no nível imediatamente abaixo (variável nova cov(b,s,l,t)).
import itertools
import math
from pathlib import Path

# Mundo dos Blocos de Tamanho Variável
BLOCKS = {"a": 1, "b": 1, "c": 2, "d": 3}
MAX_POINT = 6
MAX_LEVEL = 2

SCENARIOS = {
    1: {
        "horizon": 2,
        "initial": {"a": (3, 0), "b": (5, 0), "c": (0, 0), "d": (3, 1)},
        "goal":    {"a": (2, 0), "b": (5, 0), "c": (0, 0), "d": (0, 1)},
        "plano_manual_ref": [("d", "c", 0), ("a", "T", 2)],
    },
    2: {
        "horizon": 5,
        "initial": {"a": (0, 1), "b": (1, 1), "c": (0, 0), "d": (3, 0)},
        "goal":    {"a": (4, 2), "b": (5, 2), "c": (4, 1), "d": (3, 0)},
        "plano_manual_ref": [("b", "T", 2), ("a", "b", 2), ("c", "d", 4),
                 ("a", "c", 4), ("b", "c", 5)],
    },
    3: {
        "horizon": 6,
        "initial": {"a": (3, 0), "b": (5, 0), "c": (0, 0), "d": (3, 1)},
        "goal":    {"a": (0, 1), "b": (1, 1), "c": (0, 0), "d": (3, 0)},
        "plano_manual_ref": [("d", "c", 0), ("a", "b", 5), ("d", "T", 2),
                 ("a", "c", 0), ("b", "c", 1), ("d", "T", 3)],
    },
}


# Metas alternativas da Situação 1 (o cenário 1 usa S_f3 por padrão).
METAS_SITUACAO1 = {
    "f1": {"d": (3, 0), "a": (4, 1), "b": (5, 1), "c": (4, 2)},
    "f2": {"d": (3, 0), "c": (4, 1), "a": (4, 2), "b": (5, 2)},
    "f3": {"c": (0, 0), "a": (2, 0), "d": (0, 1), "b": (5, 0)},
    "f4": {"c": (0, 0), "a": (0, 1), "d": (2, 0), "b": (5, 0)},
}


def positions(b):
    return range(MAX_POINT - BLOCKS[b] + 1)


def overlap(b, p, y, q):
    return max(p, q) < min(p + BLOCKS[b], q + BLOCKS[y])


class CNF:
    def __init__(self):
        self.n = 0
        self.var = {}
        self.labels = {}
        self.clauses = []

    def new_var(self, key, label):
        if key not in self.var:
            self.n += 1
            self.var[key] = self.n
            self.labels[self.n] = label
        return self.var[key]

    def add(self, *lits):
        self.clauses.append([x for x in lits if x is not None])

    def unit(self, lit):
        self.add(lit)


def build(scenario):
    T = scenario["horizon"]
    C = CNF()

    at = {(b, p, t): C.new_var(("at", b, p, t), f"at({b},{p},{t})")
          for b in BLOCKS for p in positions(b) for t in range(T + 1)}
    lev = {(b, l, t): C.new_var(("lev", b, l, t), f"lev({b},{l},{t})")
           for b in BLOCKS for l in range(MAX_LEVEL + 1) for t in range(T + 1)}
    clr = {(b, t): C.new_var(("clr", b, t), f"clr({b},{t})")
           for b in BLOCKS for t in range(T + 1)}

    # cov(b,s,l,t): o bloco b cobre o slot s no nível l no instante t (usada na estabilidade).
    cov = {(b, s, l, t): C.new_var(("cov", b, s, l, t), f"cov({b},{s},{l},{t})")
           for b in BLOCKS for s in range(MAX_POINT)
           for l in range(MAX_LEVEL + 1) for t in range(T + 1)}

    mv = {}
    for b in BLOCKS:
        for y in list(BLOCKS) + ["T"]:
            if y == b:
                continue
            for p in positions(b):
                for t in range(T):
                    mv[b, y, p, t] = C.new_var(
                        ("mv", b, y, p, t), f"move({b},{y},{p},{t})")

    # (A,B) exatamente uma posição e um nível por bloco/instante.
    for t in range(T + 1):
        for b in BLOCKS:
            ps = list(positions(b))
            ls = list(range(MAX_LEVEL + 1))
            C.add(*[at[b, p, t] for p in ps])
            for p, q in itertools.combinations(ps, 2):
                C.add(-at[b, p, t], -at[b, q, t])
            C.add(*[lev[b, l, t] for l in ls])
            for l, k in itertools.combinations(ls, 2):
                C.add(-lev[b, l, t], -lev[b, k, t])

    # (COV) definição de cov: cov(b,s,l,t) <-> existe p com s em [p, p+tam(b)) e at(b,p,t), lev(b,l,t).
    for t in range(T + 1):
        for b in BLOCKS:
            for l in range(MAX_LEVEL + 1):
                for s in range(MAX_POINT):
                    ps = [p for p in positions(b) if p <= s < p + BLOCKS[b]]
                    C.add(-cov[b, s, l, t], lev[b, l, t])
                    C.add(-cov[b, s, l, t], *[at[b, p, t] for p in ps])
                    for p in ps:
                        C.add(-at[b, p, t], -lev[b, l, t], cov[b, s, l, t])

    # (C) exclusão horizontal no mesmo nível.
    for t in range(T + 1):
        for b, y in itertools.combinations(BLOCKS, 2):
            for p in positions(b):
                for q in positions(y):
                    if overlap(b, p, y, q):
                        for l in range(MAX_LEVEL + 1):
                            C.add(-at[b, p, t], -lev[b, l, t],
                                  -at[y, q, t], -lev[y, l, t])

    # (E) clear: verdadeiro exatamente quando não existe bloco sobreposto acima.
    for t in range(T + 1):
        for b in BLOCKS:
            for p in positions(b):
                for l in range(MAX_LEVEL):
                    above = []
                    for z in BLOCKS:
                        if z == b:
                            continue
                        for q in positions(z):
                            if overlap(b, p, z, q):
                                C.add(-clr[b, t], -at[b, p, t], -lev[b, l, t],
                                      -at[z, q, t], -lev[z, l + 1, t])
                                above.append((z, q, l + 1))
                    C.add(-at[b, p, t], -lev[b, l, t], clr[b, t],
                          *[x for z, q, ll in above
                            for x in (at[z, q, t], lev[z, ll, t])])

    # Estado inicial e estado meta.
    for b, (p, l) in scenario["initial"].items():
        C.unit(at[b, p, 0])
        C.unit(lev[b, l, 0])
    for b, (p, l) in scenario["goal"].items():
        C.unit(at[b, p, T])
        C.unit(lev[b, l, T])

    # Uma ação por instante + pré-condições e efeitos.
    for t in range(T):
        acts = [k for k in mv if k[3] == t]
        C.add(*[mv[k] for k in acts])
        for x, y in itertools.combinations(acts, 2):
            C.add(-mv[x], -mv[y])

        for (b, y, p, tt), v in mv.items():
            if tt != t:
                continue

            # O bloco movido precisa estar livre.
            C.add(-v, clr[b, t])

            if y == "T":
                # Destino na mesa: nível 0 e posição p.
                C.add(-v, at[b, p, t + 1])
                C.add(-v, lev[b, 0, t + 1])
                C.add(-v, -at[b, p, t], -lev[b, 0, t])
                for z in BLOCKS:
                    if z != b:
                        for q in positions(z):
                            if overlap(b, p, z, q):
                                C.add(-v, -at[z, q, t], -lev[z, 0, t])
            else:
                # Destino sobre y: nível imediatamente acima de y.
                C.add(-v, -lev[y, MAX_LEVEL, t])  # CORRECAO: y no nível máximo => L > MAX_LEVEL
                for ly in range(MAX_LEVEL):
                    L = ly + 1
                    C.add(-v, -lev[y, ly, t], at[b, p, t + 1])
                    C.add(-v, -lev[y, ly, t], lev[b, L, t + 1])

                    # Não coincidir horizontalmente com outro bloco no nível alvo.
                    for q in positions(y):
                        if not overlap(b, p, y, q):
                            C.add(-v, -lev[y, ly, t], -at[y, q, t])
                    for z in BLOCKS:
                        if z != b:
                            for q in positions(z):
                                if overlap(b, p, z, q):
                                    C.add(-v, -lev[y, ly, t],
                                          -at[z, q, t], -lev[z, L, t])

                    # Estabilidade: pelo menos ceil(tamanho(b)/2) slots apoiados.
                    k = math.ceil(BLOCKS[b] / 2)
                    slots = list(range(p, p + BLOCKS[b]))
                    r = len(slots) - k + 1
                    for subset in itertools.combinations(slots, r):
                        # CORRECAO: o apoio precisa estar no nível ly (imediatamente abaixo
                        # de b), por isso usa cov(z,s,ly,t) e não só at(z,q,t).
                        supports = [cov[z, s, ly, t]
                                    for s in subset for z in BLOCKS if z != b]
                        C.add(-v, -lev[y, ly, t], *supports)

                # Evita no-op: mesma posição E mesmo nível de destino (P6).
                for ly in range(MAX_LEVEL):
                    C.add(-v, -at[b, p, t], -lev[y, ly, t], -lev[b, ly + 1, t])

    # (ORD) Ordem parcial entre metas: phi1 < phi2 significa que phi2 só pode valer em t se phi1
    # já valeu em algum t' <= t  (phi2(t) -> existe t' <= t com phi1(t')).
    # Para cada átomo de meta (b,p,l) usa-se ach(b,p,l,t) = "já valeu até t" (só a direção que
    # garante correção: ach(t) -> ach(t-1) ou vale(t)).
    ordem = scenario.get("ordem", [])
    atomos = sorted({a for par in ordem for a in par})
    ach, hold = {}, {}
    for (b, p, l) in atomos:
        for t in range(T + 1):
            ach[b, p, l, t] = C.new_var(("ach", b, p, l, t), f"ach({b},{p},{l},{t})")
            hold[b, p, l, t] = C.new_var(("hold", b, p, l, t), f"hold({b},{p},{l},{t})")
            C.add(-hold[b, p, l, t], at[b, p, t])
            C.add(-hold[b, p, l, t], lev[b, l, t])
            C.add(-at[b, p, t], -lev[b, l, t], hold[b, p, l, t])
        C.add(-ach[b, p, l, 0], hold[b, p, l, 0])
        for t in range(1, T + 1):
            C.add(-ach[b, p, l, t], ach[b, p, l, t - 1], hold[b, p, l, t])
    for phi1, phi2 in ordem:
        for t in range(T + 1):
            C.add(-hold[phi2 + (t,)], ach[phi1 + (t,)])

    # Frame axioms para blocos que não se movem.
    for t in range(T):
        for b in BLOCKS:
            for (bb, y, p, tt), v in mv.items():
                if tt == t and bb != b:
                    for p0 in positions(b):
                        C.add(-v, -at[b, p0, t], at[b, p0, t + 1])
                    for l0 in range(MAX_LEVEL + 1):
                        C.add(-v, -lev[b, l0, t], lev[b, l0, t + 1])

    return C


def write_scenario(root, number, scenario, tag=""):
    C = build(scenario)
    stem = root / f"trab01_blocos2SAT_situacao{number}{tag}"
    stem.with_suffix(".cnf").write_text(
        f"p cnf {C.n} {len(C.clauses)}\n" +
        "".join(" ".join(map(str, clause)) + " 0\n" for clause in C.clauses),
        encoding="utf-8")
    stem.with_suffix(".map").write_text(
        "".join(f"{i}\t{C.labels[i]}\n" for i in range(1, C.n + 1)),
        encoding="utf-8")
    return C


def ler_ordem(texto):
    """'b(1,1)<a(0,1)' -> (('b',1,1), ('a',0,1)): o primeiro átomo deve valer antes do segundo."""
    import re
    m = re.fullmatch(r"\s*([abcd])\((\d),(\d)\)\s*<\s*([abcd])\((\d),(\d)\)\s*", texto)
    if not m:
        raise SystemExit("formato de --ordem: 'b(1,1)<a(0,1)'")
    g = m.groups()
    return ((g[0], int(g[1]), int(g[2])), (g[3], int(g[4]), int(g[5])))


def main():
    import sys
    root = Path(__file__).resolve().parent
    # uso: python3 gerar_cnf.py                 -> as 3 situações, horizonte padrão
    #      python3 gerar_cnf.py 3 6             -> situação 3 com horizonte 6
    #      python3 gerar_cnf.py 1 8 f1          -> situação 1 com a meta S_f1 e horizonte 8
    #      python3 gerar_cnf.py 3 6 --ordem='b(1,1)<a(0,1)'
    #                                           -> com ordem parcial entre metas (pode repetir)
    ordens = [ler_ordem(a.split("=", 1)[1]) for a in sys.argv[1:] if a.startswith("--ordem=")]
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    numeros = [int(pos[0])] if pos else list(SCENARIOS)
    for number in numeros:
        scenario = dict(SCENARIOS[number])
        tag = ""
        if len(pos) > 1:
            scenario["horizon"] = int(pos[1])
        if len(pos) > 2 and number == 1:
            scenario["goal"] = METAS_SITUACAO1[pos[2]]
            tag = f"_{pos[2]}"
        if ordens:
            scenario["ordem"] = ordens
            tag += "_ordem"
        C = write_scenario(root, number, scenario, tag)
        print(f"Situação {number}{tag} (T={scenario['horizon']}): "
              f"{C.n} variáveis, {len(C.clauses)} cláusulas")
    print("Agora rode: minisat trab01_blocos2SAT_situacaoN.cnf resultadoN.txt")


if __name__ == "__main__":
    main()
