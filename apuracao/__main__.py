"""CLI: python -m apuracao <comando>"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from . import coleta, oficial


def cmd_coletar(args) -> int:
    ufs = [u.lower() for u in args.uf] if args.uf else coleta.UFS
    lim = coleta.Limitador(args.rps)
    t0 = time.time()

    def rel(uf, feitas, total):
        dt = time.time() - t0
        print(f"[{dt:7.0f}s] {uf}: {feitas}/{total} secoes", flush=True)

    async def rodar():
        for uf in ufs:
            r = await coleta.coletar_uf(uf, lim, args.concorrencia, rel, args.limite)
            print(r, flush=True)

    asyncio.run(rodar())
    return 0


def cmd_oficial(args) -> int:
    print(asyncio.run(oficial.coletar(args.rps, args.concorrencia)))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="apuracao")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("coletar", help="baixa aux.json e bu.dat de cada secao, por UF")
    c.add_argument("--uf", nargs="*", help="uma ou mais UFs (padrao: todas)")
    c.add_argument("--rps", type=float, default=60.0, help="teto de requisicoes por segundo")
    c.add_argument("--concorrencia", type=int, default=48)
    c.add_argument("--limite", type=int, default=None, help="so as primeiras N secoes (teste)")
    c.set_defaults(fn=cmd_coletar)
    o = sub.add_parser("oficial", help="baixa o resultado oficial por pais, UF e municipio")
    o.add_argument("--rps", type=float, default=20.0)
    o.add_argument("--concorrencia", type=int, default=16)
    o.set_defaults(fn=cmd_oficial)
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
