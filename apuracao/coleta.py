"""Coleta dos arquivos publicos do TSE (boletim de urna e hora de recebimento) com preservacao.

Cada resposta fica num SQLite por UF (dados/brutos/<uf>.sqlite) com URL, hora da coleta (UTC),
status, tamanho, sha256 e o corpo. Retomavel: o que ja esta salvo nao e baixado de novo.
O teto de requisicoes por segundo e proprio e conservador (o servidor anuncia 2000/s).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

BASE = "https://resultados.tse.jus.br/oficial/ele2026"
PLEITO = "3220"
UA = "apuracao-eleicoes-2026/0.1 (analise aberta, coleta com teto de requisicoes; github.com/Gabriel-Alexandre)"
UFS = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn", "ro", "rr", "rs", "sc", "se", "sp", "to", "zz"]
RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados" / "brutos"

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw (
  url TEXT PRIMARY KEY, status INTEGER NOT NULL, fetched_utc TEXT NOT NULL,
  nbytes INTEGER NOT NULL, sha256 TEXT, body BLOB
);
"""


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def abrir(uf: str) -> sqlite3.Connection:
    BRUTOS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(BRUTOS / f"{uf}.sqlite")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.executescript(SCHEMA)
    return con


def url_config(uf: str) -> str:
    return f"{BASE}/arquivo-urna/{PLEITO}/config/{uf}/{uf}-p00{PLEITO}-cs.json"


def url_aux(uf: str, mun: str, zona: str, secao: str) -> str:
    return f"{BASE}/arquivo-urna/{PLEITO}/dados/{uf}/{mun}/{zona}/{secao}/p00{PLEITO}-{uf}-m{mun}-z{zona}-s{secao}-aux.json"


def url_bu(uf: str, mun: str, zona: str, secao: str, h: str, nome: str) -> str:
    return f"{BASE}/arquivo-urna/{PLEITO}/dados/{uf}/{mun}/{zona}/{secao}/{h}/{nome}"


class Limitador:
    """Teto de requisicoes por segundo (uma reserva de horario por requisicao)."""

    def __init__(self, por_segundo: float):
        self.intervalo = 1.0 / por_segundo
        self._prox = 0.0
        self._lock = asyncio.Lock()

    async def esperar(self) -> None:
        async with self._lock:
            agora_ = time.monotonic()
            if self._prox > agora_:
                await asyncio.sleep(self._prox - agora_)
                agora_ = self._prox
            self._prox = agora_ + self.intervalo


async def baixar(sessao: aiohttp.ClientSession, lim: Limitador, url: str, tentativas: int = 6):
    ultimo = None
    for t in range(tentativas):
        await lim.esperar()
        try:
            async with sessao.get(url) as r:
                corpo = await r.read()
                if r.status in (200, 404, 403):
                    return r.status, corpo
                ultimo = f"HTTP {r.status}"
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            ultimo = repr(e)
        await asyncio.sleep(min(30, 1.5**t))
    return 0, (ultimo or "falha").encode()


def salvo(con: sqlite3.Connection, url: str) -> bool:
    return con.execute("SELECT 1 FROM raw WHERE url=? AND status IN (200,404)", (url,)).fetchone() is not None


def guardar(con: sqlite3.Connection, url: str, status: int, corpo: bytes) -> None:
    sha = hashlib.sha256(corpo).hexdigest() if status == 200 else None
    con.execute(
        "INSERT OR REPLACE INTO raw(url,status,fetched_utc,nbytes,sha256,body) VALUES (?,?,?,?,?,?)",
        (url, status, agora(), len(corpo), sha, corpo if status == 200 else None),
    )


def secoes_da_uf(con: sqlite3.Connection, uf: str):
    """Lista (mun, zona, secao, principal) da config. Secao agregada traz 'nsp' (a secao principal)."""
    row = con.execute("SELECT body FROM raw WHERE url=? AND status=200", (url_config(uf),)).fetchone()
    cfg = json.loads(row[0])
    out = []
    for abr in cfg["abr"]:
        for mu in abr["mu"]:
            for zo in mu["zon"]:
                for se in zo["sec"]:
                    out.append((mu["cd"], zo["cd"], se["ns"], se.get("nsp")))
    return out


async def coletar_uf(uf: str, lim: Limitador, concorrencia: int, relatorio, so_primeiras: int | None = None) -> dict:
    con = abrir(uf)
    timeout = aiohttp.ClientTimeout(total=60, connect=20)
    conector = aiohttp.TCPConnector(limit=concorrencia, ttl_dns_cache=300)
    async with aiohttp.ClientSession(headers={"User-Agent": UA}, timeout=timeout, connector=conector) as sessao:
        cu = url_config(uf)
        if not salvo(con, cu):
            st, corpo = await baixar(sessao, lim, cu)
            guardar(con, cu, st, corpo)
            con.commit()
        if con.execute("SELECT status FROM raw WHERE url=?", (cu,)).fetchone()[0] != 200:
            return {"uf": uf, "erro": "config indisponivel"}
        secoes = secoes_da_uf(con, uf)
        if so_primeiras:
            secoes = secoes[:so_primeiras]
        proprias = [s for s in secoes if not s[3]]
        feitas = 0
        sem = asyncio.Semaphore(concorrencia)
        escrita = asyncio.Lock()

        async def uma(mun, zona, secao):
            nonlocal feitas
            async with sem:
                ua = url_aux(uf, mun, zona, secao)
                if salvo(con, ua):
                    st, corpo = con.execute("SELECT status, body FROM raw WHERE url=?", (ua,)).fetchone()
                else:
                    st, corpo = await baixar(sessao, lim, ua)
                    async with escrita:
                        guardar(con, ua, st, corpo)
                if st == 200:
                    dado = json.loads(corpo)
                    for h in dado.get("hashes", []):
                        for arq in h.get("arq", []):
                            if arq.get("tp") == "bu":
                                ub = url_bu(uf, mun, zona, secao, h["hash"], arq["nm"])
                                if not salvo(con, ub):
                                    stb, cb = await baixar(sessao, lim, ub)
                                    async with escrita:
                                        guardar(con, ub, stb, cb)
                feitas += 1
                if feitas % 500 == 0:
                    async with escrita:
                        con.commit()
                    relatorio(uf, feitas, len(proprias))

        await asyncio.gather(*[uma(*s[:3]) for s in proprias])
        con.commit()
    n = con.execute("SELECT COUNT(*) FROM raw").fetchone()[0]
    con.close()
    return {"uf": uf, "secoes": len(secoes), "proprias": len(proprias), "itens": n}


def hash_da_uf(uf: str) -> str:
    """Resumo da UF: sha256 sobre as linhas 'url<TAB>sha256' ordenadas."""
    con = abrir(uf)
    h = hashlib.sha256()
    for url, sha in con.execute("SELECT url, COALESCE(sha256,'-') FROM raw ORDER BY url"):
        h.update(f"{url}\t{sha}\n".encode())
    con.close()
    return h.hexdigest()
