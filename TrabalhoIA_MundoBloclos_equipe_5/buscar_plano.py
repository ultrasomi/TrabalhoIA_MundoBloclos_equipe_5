#!/usr/bin/env python3
"""Procura o plano mais curto: roda o minisat com T = 1, 2, 3, ... até o primeiro SATISFIABLE.

Uso:
    python3 buscar_plano.py SITUACAO [META] [--tmax N]

    python3 buscar_plano.py 3            # Situação 3
    python3 buscar_plano.py 1 f4         # Situação 1 com a meta S_f4 (f1, f2, f3 ou f4)
    python3 buscar_plano.py 2 --tmax 8
    python3 buscar_plano.py 3 --tmax 8 --ordem='b(1,1)<a(0,1)'   # com ordem parcial entre metas

Precisa do 'minisat' no PATH. Gera trab01_blocos2SAT_situacaoN.cnf/.map e resultadoN.txt
(com o sufixo _fK quando a meta é dada) na pasta deste script. O menor T satisfatível é o
comprimento mínimo do plano, porque os valores menores deram UNSAT.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import gerar_cnf
import interpretar


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); return 2
    if shutil.which("minisat") is None:
        print("minisat não encontrado no PATH."); return 2
    numero = int(args[0])
    meta = args[1] if len(args) > 1 else None
    tmax = int(argv[argv.index("--tmax") + 1]) if "--tmax" in argv else 12
    ordens = [gerar_cnf.ler_ordem(a.split("=", 1)[1]) for a in argv if a.startswith("--ordem=")]
    root = Path(__file__).resolve().parent
    tag = "_%s" % meta if meta and numero == 1 else ""
    if ordens:
        tag += "_ordem"

    for T in range(1, tmax + 1):
        cenario = dict(gerar_cnf.SCENARIOS[numero])
        cenario["horizon"] = T
        if meta and numero == 1:
            cenario["goal"] = gerar_cnf.METAS_SITUACAO1[meta]
        if ordens:
            cenario["ordem"] = ordens
        C = gerar_cnf.write_scenario(root, numero, cenario, tag)
        cnf = root / ("trab01_blocos2SAT_situacao%d%s.cnf" % (numero, tag))
        res = root / ("resultado%d%s.txt" % (numero, tag))
        proc = subprocess.run(["minisat", str(cnf), str(res)], capture_output=True, text=True)
        sat = proc.returncode == 10
        print("T=%d: %s (%d variáveis, %d cláusulas)"
              % (T, "SATISFIABLE" if sat else "UNSATISFIABLE", C.n, len(C.clauses)))
        if sat:
            print("\nMenor horizonte satisfatível: T=%d. Plano mínimo com %d ações.\n" % (T, T))
            extra = ["--ordem=%s(%d,%d)<%s(%d,%d)" % (a + b) for a, b in ordens]
            return interpretar.main(["interpretar.py", str(res), "--verbose"] + extra)
    print("Nenhum plano até T=%d." % tmax)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
