"""Deriva tabelas por secao a partir dos arquivos brutos coletados (dados/brutos/<uf>.sqlite).

Saidas por UF, em dados/derivados/uf/ (fora do git; regeneravel pelo comando `derivar`):
  <uf>-secoes.parquet  uma linha por secao (inclusive agregadas e sem boletim)
  <uf>-votos.parquet   votos por secao, cargo, tipo, partido e numero (presidente, governador, senador)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import bu as bumod
from . import coleta

DERIVADOS = coleta.RAIZ / "dados" / "derivados"
POR_UF = DERIVADOS / "uf"


def _iso(dr: str | None, hr: str | None) -> str | None:
    if not dr or not hr:
        return None
    return datetime.strptime(f"{dr} {hr}", "%d/%m/%Y %H:%M:%S").isoformat()


def _escolher(hashes: list[dict]) -> dict | None:
    """Entre varios boletins da mesma secao, o ultimo recebido (desempate: o que esta Totalizado)."""
    if not hashes:
        return None
    return sorted(hashes, key=lambda h: (_iso(h.get("dr"), h.get("hr")) or "", h.get("st") == "Totalizado"))[-1]


def derivar_uf(uf: str) -> dict:
    con = coleta.abrir(uf)
    secoes = coleta.secoes_da_uf(con, uf)
    linhas: list[dict] = []
    votos: list[tuple] = []
    erros = 0
    for mun, zona, secao, nsp in secoes:
        base = {"uf": uf.upper(), "mun_cd": mun, "zona": zona, "secao": secao}
        if nsp:
            linhas.append({**base, "agregada": True, "principal": nsp, "status": "agregada"})
            continue
        ua = coleta.url_aux(uf, mun, zona, secao)
        row = con.execute("SELECT status, body FROM raw WHERE url=?", (ua,)).fetchone()
        if row is None or row[0] != 200:
            linhas.append({**base, "agregada": False, "status": f"sem_aux_{row[0] if row else 'nao_coletado'}"})
            continue
        aux = json.loads(row[1])
        hashes = aux.get("hashes", [])
        h = _escolher(hashes)
        linha = {
            **base,
            "agregada": False,
            "status": aux.get("st"),
            "n_boletins": len(hashes),
            "recebido": _iso(h.get("dr"), h.get("hr")) if h else None,
            "status_boletim": h.get("st") if h else None,
            "hash_secao": h.get("hash") if h else None,
        }
        if h:
            arq_bu = next((a for a in h.get("arq", []) if a.get("tp") in ("bu", "busa")), None)
            nome = arq_bu["nm"] if arq_bu else None
            linha["tipo_boletim"] = arq_bu["tp"] if arq_bu else None
            if nome:
                ub = coleta.url_bu(uf, mun, zona, secao, h["hash"], nome)
                r = con.execute("SELECT status, sha256, body FROM raw WHERE url=?", (ub,)).fetchone()
                if r and r[0] == 200:
                    linha["bu_sha256"] = r[1]
                    try:
                        b = bumod.decode(r[2])
                        linha.update(
                            aptos=b.aptos, comparecimento=b.comparecimento,
                            abertura=b.abertura, encerramento=b.encerramento,
                            emitido=b.emitido, gerado=b.gerado, local=b.local,
                            bu_municipio=b.municipio, bu_zona=b.zona, bu_secao=b.secao,
                        )
                        for (cargo, tipo, partido, numero), v in b.votos.items():
                            if cargo in bumod.MAJORITARIOS:
                                votos.append((uf.upper(), mun, zona, secao, cargo, tipo, partido, numero, v))
                    except Exception as e:  # registrado, nao escondido
                        linha["erro_decodificacao"] = repr(e)[:200]
                        erros += 1
                else:
                    linha["erro_decodificacao"] = f"bu_http_{r[0] if r else 'nao_coletado'}"
                    erros += 1
        linhas.append(linha)
    con.close()
    POR_UF.mkdir(parents=True, exist_ok=True)
    ds = pd.DataFrame(linhas)
    dv = pd.DataFrame(votos, columns=["uf", "mun_cd", "zona", "secao", "cargo", "tipo", "partido", "numero", "votos"])
    ds.to_parquet(POR_UF / f"{uf}-secoes.parquet", index=False)
    dv.to_parquet(POR_UF / f"{uf}-votos.parquet", index=False)
    return {"uf": uf, "secoes": len(ds), "com_boletim": int(ds.get("bu_sha256", pd.Series(dtype=object)).notna().sum()), "erros": erros, "linhas_votos": len(dv)}
