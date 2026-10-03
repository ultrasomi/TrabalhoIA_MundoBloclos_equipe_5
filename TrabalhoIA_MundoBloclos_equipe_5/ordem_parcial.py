#!/usr/bin/env python3
"""Item 4: análise de ordem parcial de um plano (elos causais A_i --fato--> A_j).

Uso:
    python3 ordem_parcial.py --manual 3            # plano manual da Situação 3 (1, 2, 3 ou 1f4)
    python3 ordem_parcial.py resultado3.txt        # plano devolvido pelo minisat (usa o .map)

Para o plano dado, o script:
  1. calcula os ELOS CAUSAIS: um fato (slot s livre/ocupado no nível l) que a ação A_i produz
     e que a ação A_j exige como pré-condição (P1, P4 ou P5);
  2. testa TODAS as ordens de execução das mesmas ações (busca sobre subconjuntos + estado)
     e mantém só as que são executáveis e chegam à meta;
  3. a ordem parcial do plano é o que vale em todas as ordens válidas. Se só existe uma
     ordem válida, o plano é uma cadeia totalmente ordenada.
"""
import re
import sys
from collections import deque
from functools import lru_cache
from pathlib import Path

import gerar_cnf as G
import interpretar as I

BLOCKS = G.BLOCKS
MAXL = G.MAX_LEVEL
# plano manual do item 3 para a meta S_f4 (não está em G.SCENARIOS)
MANUAL_F4 = [("d", "c", 0), ("a", "b", 5), ("d", "T", 2), ("a", "c", 0)]


# ------------------------------------------------------------ simulador das regras P1..P6
def cobre(est, s, l, excl=None):
    return [z for z in BLOCKS if z != excl and est[z][1] == l and est[z][0] <= s < est[z][0] + BLOCKS[z]]


def movimentos(est):
    out = {}
    for b in BLOCKS:
        p0, l0 = est[b]
        if any(cobre(est, s, l0 + 1, b) for s in range(p0, p0 + BLOCKS[b])):
            continue                                            # P1
        for y in list(BLOCKS) + ["T"]:
            if y == b:
                continue
            L = 0 if y == "T" else est[y][1] + 1
            if L > MAXL:
                continue
            for p in range(0, 6 - BLOCKS[b] + 1):
                if y != "T":
                    q = est[y][0]
                    if not (p < q + BLOCKS[y] and q < p + BLOCKS[b]):
                        continue                                # P3
                if any(cobre(est, s, L, b) for s in range(p, p + BLOCKS[b])):
                    continue                                    # P4
                if L > 0:
                    ap = sum(1 for s in range(p, p + BLOCKS[b]) if cobre(est, s, L - 1, b))
                    if ap < -(-BLOCKS[b] // 2):
                        continue                                # P5
                if (p0, l0) == (p, L):
                    continue                                    # P6
                out[(b, y, p)] = L
    return out


def aplicar(est, mv, L):
    n = dict(est); n[mv[0]] = (mv[2], L); return n


def chave(est):
    return tuple(est[b] for b in sorted(BLOCKS))


# ------------------------------------------------------------ fatos e elos causais
def fatos(est):
    return {("livre" if not cobre(est, s, l) else "ocupado", s, l)
            for s in range(6) for l in range(MAXL + 1)}


def pre_fatos(est, mv):
    b, y, p = mv; p0, l0 = est[b]; L = 0 if y == "T" else est[y][1] + 1
    pre = set()
    if l0 + 1 <= MAXL:
        pre |= {("livre", s, l0 + 1) for s in range(p0, p0 + BLOCKS[b])}                  # P1
    pre |= {("livre", s, L) for s in range(p, p + BLOCKS[b]) if not cobre(est, s, L, b)}  # P4
    if L > 0:
        pre |= {("ocupado", s, L - 1) for s in range(p, p + BLOCKS[b]) if cobre(est, s, L - 1, b)}  # P5
    return pre


def elos_causais(estados, plano):
    elos = {}
    for j, mv in enumerate(plano):
        for f in sorted(pre_fatos(estados[j], mv)):
            for i in range(j - 1, -1, -1):
                antes, depois = f in fatos(estados[i]), f in fatos(estados[i + 1])
                if depois and not antes:
                    elos.setdefault((i, j), []).append(f); break
                if antes and not depois:
                    break
    return elos


# ------------------------------------------------------------ ordens válidas
def ordens_validas(s0, plano, meta):
    n = len(plano)
    ini = (frozenset(), chave(s0)); est = {chave(s0): s0}
    alc, fila, arestas = {ini}, deque([ini]), []
    while fila:
        S, k = fila.popleft(); ok = movimentos(est[k])
        for i in range(n):
            if i in S or plano[i] not in ok:
                continue
            ns = aplicar(est[k], plano[i], ok[plano[i]]); nk = chave(ns); est[nk] = ns
            no = (S | {i}, nk); arestas.append(((S, k), no))
            if no not in alc:
                alc.add(no); fila.append(no)
    fim = {x for x in alc if len(x[0]) == n and x[1] == chave(meta)}
    rev = {}
    for a, b in arestas:
        rev.setdefault(b, []).append(a)
    uteis, fila = set(fim), deque(fim)
    while fila:
        x = fila.popleft()
        for a in rev.get(x, []):
            if a not in uteis:
                uteis.add(a); fila.append(a)
    uteis &= alc
    suc = {}
    for a, b in arestas:
        if a in uteis and b in uteis:
            suc.setdefault(a, []).append(b)

    @lru_cache(None)
    def contar(x):
        return 1 if x in fim else sum(contar(y) for y in suc.get(x, []))

    total = contar(ini)
    obrig = {(i, j) for i in range(n) for j in range(n)
             if i != j and not any(j in S and i not in S for S, _ in uteis)}
    red = {(i, j) for (i, j) in obrig if not any((i, k) in obrig and (k, j) in obrig for k in range(n))}
    return total, red


def descrever(f):
    return "%s(s%d,nível %d)" % (f[0], f[1], f[2])


def analisar(s0, meta, plano, titulo):
    estados = [s0]
    for mv in plano:
        ok = movimentos(estados[-1])
        if mv not in ok:
            print("Ação inválida no plano:", mv); return 1
        estados.append(aplicar(estados[-1], mv, ok[mv]))
    if chave(estados[-1]) != chave(meta):
        print("O plano não chega à meta."); return 1
    print("PLANO (%s), %d ações:" % (titulo, len(plano)))
    for i, (b, y, p) in enumerate(plano):
        print("  A%d = move(%s,%s,%d)" % (i + 1, b, y, p))
    elos = elos_causais(estados, plano)
    print("\nELOS CAUSAIS  A_i --fato--> A_j (A_i produz o fato que A_j exige):")
    if not elos:
        print("  (nenhum)")
    for (i, j), fs in sorted(elos.items()):
        print("  A%d --%s--> A%d" % (i + 1, ", ".join(descrever(f) for f in fs), j + 1))
    total, red = ordens_validas(s0, plano, meta)
    print("\nORDENS DE EXECUÇÃO VÁLIDAS das mesmas ações: %d" % total)
    print("RESTRIÇÕES DE ORDEM NECESSÁRIAS (redução transitiva): %s"
          % (", ".join("A%d < A%d" % (i + 1, j + 1) for i, j in sorted(red)) or "nenhuma"))
    if total == 1:
        print("=> o plano é uma cadeia totalmente ordenada: cada ação depende da anterior.")
    else:
        print("=> ordem parcial: ações sem restrição entre si podem ser executadas em qualquer ordem.")
    return 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if "--manual" in argv:
        alvo = args[0]
        if alvo == "1f4":
            cen = dict(G.SCENARIOS[1]); cen["goal"] = G.METAS_SITUACAO1["f4"]; plano = MANUAL_F4
        else:
            cen = G.SCENARIOS[int(alvo)]; plano = cen["plano_manual_ref"]
        return analisar(cen["initial"], cen["goal"], plano, "manual, situação %s" % alvo)
    if not args:
        print(__doc__); return 2
    res = Path(args[0])
    m = re.match(r"resultado(\d+)((?:_\w+)?)\.txt$", res.name)
    n, sufixo = int(m.group(1)), m.group(2)
    mf = re.search(r"_(f\d)", sufixo)
    meta = mf.group(1) if mf else ""
    cen = dict(G.SCENARIOS[n])
    if meta:
        cen["goal"] = G.METAS_SITUACAO1[meta]
    mapa = I.ler_mapa(res.parent / ("trab01_blocos2SAT_situacao%d%s.map" % (n, sufixo)))
    status, ids = I.ler_resultado(res)
    if status != "SAT":
        print("Resultado %s: não há plano." % status); return 1
    _, plano = I.extrair(I.simbolos_verdadeiros(mapa, ids))
    return analisar(cen["initial"], cen["goal"], plano, res.name)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
