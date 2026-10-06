"""P4 / T2.3: a soma dos boletins bate com o resultado oficial, por municipio, UF e cargo?

Compara, para Presidente, Governador e Senador:
  - votos nominais por candidato (soma dos boletins x campo `vap` do arquivo oficial);
  - brancos (`vb`) e nulos (`tvn`: nulos mais votos anulados de candidatos sem registro);
  - comparecimento (`c`).
Candidato que aparece nos boletins e nao aparece no oficial tem os votos somados aos nulos no oficial; isso e
conferido e registrado (ex.: candidato com candidatura indeferida). Diferenca que sobra e achado.
"""

from __future__ import annotations

import json

import pandas as pd

from . import oficial

CARGOS = {1: ("1", oficial.ELE_FEDERAL), 3: ("3", oficial.ELE_ESTADUAL), 5: ("5", oficial.ELE_ESTADUAL)}


def _ler_oficial(con, url: str):
    row = con.execute("SELECT status, body FROM raw WHERE url=?", (url,)).fetchone()
    if row is None or row[0] != 200:
        return None
    return json.loads(row[1])


def _cand_votos(d: dict) -> dict[int, int]:
    out = {}
    for carg in d.get("carg", []):
        for a in carg.get("agr", []):
            for p in a.get("par", []):
                for c in p.get("cand", []):
                    out[int(c["n"])] = int(c["vap"])
    return out


def _to_int(x) -> int:
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


def _tup(k):
    return k if isinstance(k, tuple) else (k,)


def comparar(votos: pd.DataFrame, secoes: pd.DataFrame, nivel: str = "uf") -> pd.DataFrame:
    """nivel: 'uf' ou 'mun'. Devolve uma linha por (unidade, cargo) com as diferencas (boletins menos oficial)."""
    con = oficial.abrir()
    chave = ["uf"] if nivel == "uf" else ["uf", "mun_cd"]
    nom_g: dict = {}
    for key, v in votos[votos.tipo == 1].groupby(chave + ["cargo", "numero"]).votos.sum().items():
        nom_g.setdefault((key[:-2], key[-2]), {})[key[-1]] = int(v)
    bra = {(_tup(k[:-1]), k[-1]): int(v) for k, v in votos[votos.tipo == 2].groupby(chave + ["cargo"]).votos.sum().items()}
    nul = {(_tup(k[:-1]), k[-1]): int(v) for k, v in votos[votos.tipo == 3].groupby(chave + ["cargo"]).votos.sum().items()}
    # comparecimento do boletim = soma de todos os votos de Presidente (nominais, brancos e nulos); em todas as secoes
    # com boletim comum ele e igual ao campo de comparecimento do cabecalho (conferido: 499.161 de 499.161)
    comp = {_tup(k): int(v) for k, v in votos[votos.cargo == 1].groupby(chave).votos.sum().items()}
    unidades = sorted({u for (u, _c) in nom_g})
    linhas = []
    for un in unidades:
        uf = un[0].lower()
        mun = un[1] if nivel == "mun" else None
        for cargo, (cod, ele) in CARGOS.items():
            if uf == "zz" and cargo != 1:
                continue
            if (un, cargo) not in nom_g:
                continue
            url = oficial.url_uf(uf, cod, ele) if nivel == "uf" else oficial.url_mun(uf, mun, cod, ele)
            d = _ler_oficial(con, url)
            if d is None:
                linhas.append({"uf": un[0], "mun_cd": mun, "cargo": cargo, "situacao": "oficial_indisponivel"})
                continue
            of = _cand_votos(d)
            mine = nom_g[(un, cargo)]
            dif_cand = {n: mine.get(n, 0) - of.get(n, 0) for n in set(of) | set(mine)}
            so_boletim = sum(mine[n] for n in mine if n not in of)
            so_oficial = sum(of[n] for n in of if n not in mine)
            v = d["v"]
            dif_nulos = nul.get((un, cargo), 0) - _to_int(v.get("tvn"))
            linhas.append(
                {
                    "uf": un[0], "mun_cd": mun, "cargo": cargo, "situacao": "ok",
                    "candidatos_com_diferenca": sum(1 for n, x in dif_cand.items() if x != 0 and n in of),
                    "votos_nominais_dif_total": sum(abs(x) for n, x in dif_cand.items() if n in of),
                    "votos_so_no_boletim": so_boletim,
                    "votos_so_no_oficial": so_oficial,
                    "brancos_dif": bra.get((un, cargo), 0) - _to_int(v.get("vb")),
                    "nulos_dif": dif_nulos,
                    "nulos_dif_explicada_por_so_boletim": dif_nulos + so_boletim == 0,
                    "comparecimento_dif": (comp.get(un, 0) - _to_int(d["e"].get("c"))) if cargo == 1 else None,
                }
            )
    con.close()
    return pd.DataFrame(linhas)
