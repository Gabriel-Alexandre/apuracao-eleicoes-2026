"""Carrega as tabelas derivadas de todas as UFs e monta a tabela nacional por secao (presidente)."""

from __future__ import annotations

import json

import pandas as pd

from . import coleta, derivar, oficial
from .tempo import REGIAO

CANDIDATOS = {}  # numero -> nome, preenchido por candidatos()


def candidatos() -> dict[int, str]:
    """Numero -> nome de urna dos candidatos a presidente, lidos do arquivo oficial do pais."""
    if CANDIDATOS:
        return CANDIDATOS
    con = oficial.abrir()
    row = con.execute("SELECT body FROM raw WHERE url=?", (oficial.url_uf("br", "1", oficial.ELE_FEDERAL),)).fetchone()
    con.close()
    d = json.loads(row[0])
    for a in d["carg"][0]["agr"]:
        for p in a["par"]:
            for c in p["cand"]:
                CANDIDATOS[int(c["n"])] = c["nmu"]
    return CANDIDATOS


def carregar(ufs: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    ufs = ufs or coleta.UFS
    ss, vv = [], []
    for uf in ufs:
        ss.append(pd.read_parquet(derivar.POR_UF / f"{uf}-secoes.parquet"))
        vv.append(pd.read_parquet(derivar.POR_UF / f"{uf}-votos.parquet"))
    secoes = pd.concat(ss, ignore_index=True)
    votos = pd.concat(vv, ignore_index=True)
    secoes["regiao"] = secoes["uf"].map(REGIAO)
    for c in ("recebido", "encerramento", "abertura", "emitido", "gerado"):
        if c in secoes:
            secoes[c] = pd.to_datetime(secoes[c])
    return secoes, votos


def presidente(secoes: pd.DataFrame, votos: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por secao propria com boletim: colunas p<numero> (nominais), branco, nulo, validos."""
    chave = ["uf", "mun_cd", "zona", "secao"]
    v = votos[votos.cargo == 1]
    nom = v[v.tipo == 1].pivot_table(index=chave, columns="numero", values="votos", aggfunc="sum", fill_value=0)
    nom.columns = [f"p{int(c)}" for c in nom.columns]
    outros = v[v.tipo != 1].pivot_table(index=chave, columns="tipo", values="votos", aggfunc="sum", fill_value=0)
    outros = outros.rename(columns={2: "branco", 3: "nulo"})
    wide = nom.join(outros, how="outer").fillna(0).astype(int)
    wide["validos"] = wide[[c for c in wide.columns if c.startswith("p")]].sum(axis=1)
    base = secoes[(~secoes["agregada"]) & secoes["recebido"].notna()]
    out = base.merge(wide.reset_index(), on=chave, how="left")
    faltantes = int(out["validos"].isna().sum())
    out = out[out["validos"].notna()].copy()
    for c in wide.columns:
        out[c] = out[c].astype(int)
    out.attrs["secoes_recebidas_sem_votos_decodificados"] = faltantes
    return out


def municipios() -> pd.DataFrame:
    """uf, mun_cd (codigo do TSE), nome, capital (bool), cdi (codigo IBGE)."""
    con = oficial.abrir()
    row = con.execute("SELECT body FROM raw WHERE url=?", (oficial.url_lista_mun(),)).fetchone()
    con.close()
    lista = json.loads(row[0])
    linhas = []
    for abr in lista["abr"]:
        for mu in abr["mu"]:
            linhas.append({"uf": abr["cd"].upper(), "mun_cd": mu["cd"], "nome": mu["nm"], "capital": mu.get("c") == "s", "cdi": mu.get("cdi")})
    return pd.DataFrame(linhas)


def candidaturas_oficiais() -> pd.MultiIndex:
    """Pares (UF, cargo, numero) dos candidatos que aparecem no resultado OFICIAL (arquivo de totalizacao da UF)."""
    con = oficial.abrir()
    pares = []
    for uf in coleta.UFS:
        for cargo, ele in ((1, oficial.ELE_FEDERAL), (3, oficial.ELE_ESTADUAL), (5, oficial.ELE_ESTADUAL)):
            if uf == "zz" and cargo != 1:
                continue
            row = con.execute("SELECT body FROM raw WHERE url=?", (oficial.url_uf(uf, str(cargo), ele),)).fetchone()
            if row is None:
                continue
            d = json.loads(row[0])
            for carg in d.get("carg", []):
                for a in carg.get("agr", []):
                    for p in a.get("par", []):
                        for c in p.get("cand", []):
                            pares.append((uf.upper(), cargo, int(c["n"])))
    con.close()
    return pd.MultiIndex.from_tuples(pares, names=["uf", "cargo", "numero"])


def aplicar_candidaturas_oficiais(votos: pd.DataFrame) -> pd.DataFrame:
    """Voto de candidato que nao esta na lista oficial vira nulo, como no resultado oficial do TSE.

    Conferido na validacao (P4): o total de nulos do arquivo oficial e igual aos nulos dos boletins mais os votos
    desses candidatos (candidatura sem registro valido). Sem isto os percentuais saem diferentes dos oficiais.
    """
    validos = candidaturas_oficiais()
    idx = pd.MultiIndex.from_arrays([votos["uf"], votos["cargo"], votos["numero"]])
    nominal = votos["tipo"] == 1
    fora = nominal & ~idx.isin(validos)
    v = votos.copy()
    v.loc[fora, "tipo"] = 3
    v.loc[fora, "partido"] = 0
    v.loc[fora, "numero"] = 0
    v.attrs["votos_reclassificados_como_nulos"] = int(votos.loc[fora, "votos"].sum())
    return v
