#!/usr/bin/env python3
"""Interpreta a saída do minisat e escreve o plano em português.

Uso:
    python3 interpretar.py resultado1.txt [--mapa ARQ.map] [--verbose] [--ordem='b(1,1)<a(0,1)']

O minisat só devolve números (IDs das variáveis verdadeiras). O arquivo .map, gerado por
gerar_cnf.py, traduz cada ID para o símbolo, por exemplo 50 -> move(d,c,0,0).
Se --mapa não for dado, usa trab01_blocos2SAT_situacaoN.map (N vem do nome resultadoN.txt)
na mesma pasta do resultado. Para a meta alternativa da Situação 1 (resultado1_f1.txt),
usa trab01_blocos2SAT_situacao1_f1.map.
"""
import re
import sys
from pathlib import Path

BLOCKS = {"a": 1, "b": 1, "c": 2, "d": 3}
MAX_POINT = 6
MAX_LEVEL = 2


# ---------------------------------------------------------------- leitura
def ler_mapa(caminho):
    mapa = {}
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        if linha.strip():
            i, simbolo = linha.split("\t")
            mapa[int(i)] = simbolo.strip()
    return mapa


def ler_resultado(caminho):
    """Devolve (status, conjunto de IDs verdadeiros). status: 'SAT', 'UNSAT' ou 'INDET'."""
    linhas = Path(caminho).read_text(encoding="utf-8").split("\n")
    status = linhas[0].strip()
    if status != "SAT":
        return status, set()
    numeros = [int(x) for x in " ".join(linhas[1:]).split() if x != "0"]
    return status, {n for n in numeros if n > 0}


def simbolos_verdadeiros(mapa, ids):
    return [mapa[i] for i in sorted(ids) if i in mapa]


def separar(simbolo):
    nome, resto = simbolo.split("(", 1)
    return nome, resto.rstrip(")").split(",")


# ---------------------------------------------------------------- modelo
def extrair(simbolos):
    at, lev, moves = {}, {}, {}
    for s in simbolos:
        nome, args = separar(s)
        if nome == "at":
            b, p, t = args[0], int(args[1]), int(args[2]); at[(b, t)] = p
        elif nome == "lev":
            b, l, t = args[0], int(args[1]), int(args[2]); lev[(b, t)] = l
        elif nome == "move":
            b, y, p, t = args[0], args[1], int(args[2]), int(args[3]); moves[t] = (b, y, p)
    T = max(t for _, t in at)
    estados = [{b: (at[(b, t)], lev[(b, t)]) for b in BLOCKS} for t in range(T + 1)]
    plano = [moves[t] for t in sorted(moves)]
    return estados, plano


def derivar_on(estado):
    """on(b,y,t) é derivada de at, lev e sobreposição de spans (não é codificada)."""
    on = {}
    for b, (p, l) in estado.items():
        if l == 0:
            on[b] = ["MESA"]
            continue
        apoios = []
        for y, (q, ly) in estado.items():
            if y != b and ly == l - 1 and p < q + BLOCKS[y] and q < p + BLOCKS[b]:
                apoios.append(y)
        on[b] = sorted(apoios)
    return on


# ---------------------------------------------------------------- verificação independente
def validar_plano(estados, plano):
    """Confere cada ação contra as pré-condições P1..P6 do Item 1, sem usar o CNF."""
    erros = []
    for t, (b, y, p) in enumerate(plano):
        est = estados[t]
        pb, lb = est[b]
        L = 0 if y == "T" else est[y][1] + 1
        cobre = lambda x, s, l: est[x][1] == l and est[x][0] <= s < est[x][0] + BLOCKS[x]
        if any(cobre(z, s, lb + 1) for z in BLOCKS if z != b for s in range(pb, pb + BLOCKS[b])):
            erros.append((t, "P1: topo de %s não está livre" % b))
        if not (0 <= p <= MAX_POINT - BLOCKS[b]) or L > MAX_LEVEL or y == b:
            erros.append((t, "P2: posição ou nível fora dos limites"))
        if y != "T":
            q = est[y][0]
            if not (p < q + BLOCKS[y] and q < p + BLOCKS[b]):
                erros.append((t, "P3: %s não se sobrepõe a %s" % (b, y)))
        if any(cobre(z, s, L) for z in BLOCKS if z != b for s in range(p, p + BLOCKS[b])):
            erros.append((t, "P4: slots de destino ocupados"))
        if L > 0:
            apoiados = sum(1 for s in range(p, p + BLOCKS[b])
                           if any(cobre(z, s, L - 1) for z in BLOCKS if z != b))
            if apoiados < -(-BLOCKS[b] // 2):
                erros.append((t, "P5: bloco %s instável (%d slots apoiados)" % (b, apoiados)))
        if (pb, lb) == (p, L):
            erros.append((t, "P6: ação não muda o estado"))
        # o estado seguinte deve ser exatamente o previsto pelo efeito da ação
        previsto = dict(est); previsto[b] = (p, L)
        if estados[t + 1] != previsto:
            erros.append((t, "o estado t+1 do modelo não bate com o efeito da ação"))
    return erros


def verificar_ordem(estados, ordens):
    """phi1 < phi2: em todo t em que phi2 vale, phi1 já valeu em algum t' <= t."""
    msgs = []
    for (b1, p1, l1), (b2, p2, l2) in ordens:
        vale = lambda t, b, p, l: estados[t][b] == (p, l)
        for t in range(len(estados)):
            if vale(t, b2, p2, l2) and not any(vale(u, b1, p1, l1) for u in range(t + 1)):
                msgs.append("ordem %s(%d,%d) < %s(%d,%d) violada em t=%d" % (b1, p1, l1, b2, p2, l2, t))
                break
    return msgs


# ---------------------------------------------------------------- saída
def frase(t, acao):
    b, y, p = acao
    if y == "T":
        return "t=%d: mover bloco '%s' para a MESA em p=%d" % (t, b, p)
    return "t=%d: mover bloco '%s' para CIMA de '%s' em p=%d" % (t, b, y, p)


def descrever_estado(estado):
    return "  ".join("%s(%d,%d)" % (b, *estado[b]) for b in sorted(estado))


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in argv
    if not args:
        print(__doc__); return 2
    resultado = Path(args[0])
    if "--mapa" in argv:
        mapa_arq = Path(argv[argv.index("--mapa") + 1])
    else:
        m = re.match(r"resultado(\d+)(_\w+)?\.txt$", resultado.name)
        if not m:
            print("Não consegui deduzir o .map; use --mapa."); return 2
        mapa_arq = resultado.parent / ("trab01_blocos2SAT_situacao%s%s.map" % (m.group(1), m.group(2) or ""))
    mapa = ler_mapa(mapa_arq)
    status, ids = ler_resultado(resultado)
    if status != "SAT":
        print("Resultado: %s. Não existe plano com esse horizonte." % status)
        return 1
    estados, plano = extrair(simbolos_verdadeiros(mapa, ids))
    print("PLANO ENCONTRADO (%d ações):" % len(plano))
    for t, acao in enumerate(plano):
        print("%d. %s" % (t + 1, frase(t, acao)))
    if verbose:
        print("\nESTADOS (bloco(ponto, nível)):")
        for t, est in enumerate(estados):
            print("  t=%d: %s" % (t, descrever_estado(est)))
    final = estados[-1]
    print("\nESTADO FINAL (t=%d):" % (len(estados) - 1))
    for b in sorted(final):
        print("  %s: ponto inicial p=%d, nivel l=%d" % (b, *final[b]))
    print("\nRELACOES 'on' em t=%d:" % (len(estados) - 1))
    for b, apoios in derivar_on(final).items():
        print("  %s esta sobre: %s" % (b, ", ".join(apoios)))
    ordens = []
    for a in argv:
        if a.startswith("--ordem="):
            g = re.fullmatch(r"([abcd])\((\d),(\d)\)<([abcd])\((\d),(\d)\)", a.split("=", 1)[1].replace(" ", ""))
            ordens.append(((g[1], int(g[2]), int(g[3])), (g[4], int(g[5]), int(g[6]))))
    erros = validar_plano(estados, plano)
    print("\nVERIFICAÇÃO INDEPENDENTE (pré-condições P1..P6 do Item 1): %s"
          % ("plano válido" if not erros else "PLANO INVÁLIDO"))
    for t, msg in erros:
        print("  t=%d: %s" % (t, msg))
    if ordens:
        viol = verificar_ordem(estados, ordens)
        print("VERIFICAÇÃO DA ORDEM PARCIAL ENTRE METAS: %s" % ("respeitada" if not viol else "VIOLADA"))
        for m in viol:
            print("  " + m)
        erros = erros + viol
    return 0 if not erros else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
