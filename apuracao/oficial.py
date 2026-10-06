"""Coleta do resultado OFICIAL (arquivos de totalizacao do TSE) para conferir contra a soma dos boletins.

Guarda em dados/brutos/oficial.sqlite os arquivos do pais, de cada UF e de cada municipio para
Presidente (6257, cargo 1), Governador (6259, cargo 3) e Senador (6259, cargo 5), mais a lista de municipios.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time

import aiohttp

from . import coleta

BASE = coleta.BASE
ELE_FEDERAL, ELE_ESTADUAL = "6257", "6259"
CARGOS = [("1", ELE_FEDERAL), ("3", ELE_ESTADUAL), ("5", ELE_ESTADUAL)]


def url_uf(uf: str, cargo: str, ele: str) -> str:
    return f"{BASE}/{ele}/dados/{uf}/{uf}-c000{cargo}-e00{ele}-u.json"


def url_mun(uf: str, cd: str, cargo: str, ele: str) -> str:
    return f"{BASE}/{ele}/dados/{uf}/{uf}{cd}-c000{cargo}-e00{ele}-u.json"


def url_lista_mun() -> str:
    return f"{BASE}/{ELE_FEDERAL}/config/mun-e00{ELE_FEDERAL}-cm.json"


def abrir() -> sqlite3.Connection:
    coleta.BRUTOS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(coleta.BRUTOS / "oficial.sqlite")
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(coleta.SCHEMA)
    return con


async def coletar(rps: float = 20.0, concorrencia: int = 16) -> dict:
    con = abrir()
    lim = coleta.Limitador(rps)
    timeout = aiohttp.ClientTimeout(total=60, connect=20)
    conector = aiohttp.TCPConnector(limit=concorrencia)
    async with aiohttp.ClientSession(headers={"User-Agent": coleta.UA}, timeout=timeout, connector=conector) as s:
        lu = url_lista_mun()
        if not coleta.salvo(con, lu):
            st, c = await coleta.baixar(s, lim, lu)
            coleta.guardar(con, lu, st, c)
            con.commit()
        lista = json.loads(con.execute("SELECT body FROM raw WHERE url=?", (lu,)).fetchone()[0])
        alvos = [url_uf("br", "1", ELE_FEDERAL)]
        for abr in lista["abr"]:
            uf = abr["cd"].lower()
            for cargo, ele in CARGOS:
                if uf == "zz" and cargo != "1":
                    continue
                alvos.append(url_uf(uf, cargo, ele))
            for mu in abr["mu"]:
                for cargo, ele in CARGOS:
                    if uf == "zz" and cargo != "1":
                        continue
                    alvos.append(url_mun(uf, mu["cd"], cargo, ele))
        alvos = [a for a in alvos if not coleta.salvo(con, a)]
        sem = asyncio.Semaphore(concorrencia)
        feitos = 0
        escrita = asyncio.Lock()
        t0 = time.time()

        async def um(u):
            nonlocal feitos
            async with sem:
                st, c = await coleta.baixar(s, lim, u)
                async with escrita:
                    coleta.guardar(con, u, st, c)
                    feitos += 1
                    if feitos % 1000 == 0:
                        con.commit()
                        print(f"[{time.time()-t0:6.0f}s] oficial {feitos}/{len(alvos)}", flush=True)

        await asyncio.gather(*[um(a) for a in alvos])
        con.commit()
    n = con.execute("SELECT COUNT(*), SUM(status=200), SUM(status=404) FROM raw").fetchone()
    con.close()
    return {"arquivos": n[0], "200": n[1], "404": n[2], "baixados_agora": len(alvos)}
