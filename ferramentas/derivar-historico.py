"""Deriva as tabelas por secao de 2018 e 2022 (1o e 2o turnos) a partir dos zips baixados.

Uso: python ferramentas/derivar-historico.py [--anos 2022 2018] [--turnos 1 2]
2014 fica de fora: o arquivo nao tem cabecalho nem hora de recebimento (ver docs/PRE_REGISTRO.md, secao 9).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import historico  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--anos", nargs="*", default=["2022", "2018"])
    p.add_argument("--turnos", nargs="*", default=["1", "2"])
    args = p.parse_args()
    t0 = time.time()
    for ano in args.anos:
        for turno in args.turnos:
            for zp in sorted((historico.BRUTOS_H / f"{ano}-{turno}").glob("*.zip")):
                r = historico.derivar_zip(zp, ano, turno)
                print(f"[{time.time()-t0:6.0f}s]", r, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
