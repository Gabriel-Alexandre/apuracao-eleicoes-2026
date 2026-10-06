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
        print(f"[{dt:7.0f}s] {uf}: {feitas}/{total} secoes | taxa {lim.taxa:5.1f}/s teto {lim.teto:.0f} penalizacoes {lim.penalizacoes}", flush=True)

    async def rodar():
        for uf in ufs:
            r = await coleta.coletar_uf(uf, lim, args.concorrencia, rel, args.limite)
            print(r, flush=True)

    asyncio.run(rodar())
    return 0


def cmd_oficial(args) -> int:
    print(asyncio.run(oficial.coletar(args.rps, args.concorrencia)))
    return 0


def cmd_manifesto(args) -> int:
    import hashlib
    import json
    from datetime import datetime, timezone

    ufs = {}
    for uf in coleta.UFS:
        con = coleta.abrir(uf)
        n, ok, nao = con.execute("SELECT COUNT(*), SUM(status=200), SUM(status=404) FROM raw").fetchone()
        ultimo = con.execute("SELECT MIN(fetched_utc), MAX(fetched_utc) FROM raw").fetchone()
        tam = con.execute("SELECT COALESCE(SUM(nbytes),0) FROM raw").fetchone()[0]
        con.close()
        ufs[uf.upper()] = {"arquivos": n, "status_200": ok, "status_404": nao, "bytes": tam, "coleta_utc": list(ultimo), "sha256_resumo": coleta.hash_da_uf(uf)}
    con = oficial.abrir()
    h = hashlib.sha256()
    for url, sha in con.execute("SELECT url, COALESCE(sha256,'-') FROM raw ORDER BY url"):
        h.update((url + chr(9) + sha + chr(10)).encode())
    n = con.execute("SELECT COUNT(*) FROM raw").fetchone()[0]
    con.close()
    dado = {
        "gerado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "como_o_resumo_e_calculado": "sha256 sobre as linhas 'url<TAB>sha256 do corpo' ordenadas por url, de cada banco em dados/brutos/",
        "ufs": ufs,
        "oficial": {"arquivos": n, "sha256_resumo": h.hexdigest()},
        "totais": {"arquivos": sum(u["arquivos"] for u in ufs.values()), "bytes": sum(u["bytes"] for u in ufs.values())},
    }
    (coleta.RAIZ / "dados" / "MANIFESTO.json").write_text(json.dumps(dado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(dado["totais"]), "->", coleta.RAIZ / "dados" / "MANIFESTO.json")
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
    m = sub.add_parser("manifesto", help="grava dados/MANIFESTO.json com o resumo sha256 de cada UF e do oficial")
    m.set_defaults(fn=cmd_manifesto)
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
