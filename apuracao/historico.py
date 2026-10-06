"""Leitura dos CSV de boletim de urna (BU na Web) de 2014, 2018 e 2022 dos dados abertos do TSE.

Mantem so Presidente (1), Governador (3) e Senador (5). Saidas em dados/derivados/historico/:
  <ano>-<turno>-<uf>-secoes.parquet  uma linha por secao (hora de recebimento so existe em 2022)
  <ano>-<turno>-<uf>-votos.parquet   votos por secao, cargo, tipo (nominal, branco, nulo) e numero
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

from . import coleta

BRUTOS_H = coleta.BRUTOS / "historico"
DERIV_H = coleta.RAIZ / "dados" / "derivados" / "historico"

QUERIDAS = {
    "SG_UF": "uf", "SG_ UF": "uf", "CD_MUNICIPIO": "mun", "NR_ZONA": "zona", "NR_SECAO": "secao",
    "CD_CARGO_PERGUNTA": "cargo", "NR_PARTIDO": "partido", "DS_TIPO_VOTAVEL": "tipo_txt", "NR_VOTAVEL": "numero",
    "QT_VOTOS": "votos", "DT_BU_RECEBIDO": "recebido", "DT_ENCERRAMENTO": "encerramento", "DT_ABERTURA": "abertura",
    "QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "DS_TIPO_URNA": "tipo_urna",
}
TIPO = {"nominal": 1, "branco": 2, "nulo": 3, "legenda": 4}


def _tipo(txt: pd.Series) -> pd.Series:
    t = txt.str.lower().str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
    return t.map(lambda x: TIPO.get(x, 0))


def derivar_zip(path: Path, ano: str, turno: str) -> dict:
    DERIV_H.mkdir(parents=True, exist_ok=True)
    uf = path.name.split("_")[2].lower()
    z = zipfile.ZipFile(path)
    nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
    votos, secoes = [], []
    with z.open(nome) as fh:
        for chunk in pd.read_csv(
            fh, sep=";", encoding="latin1", dtype=str, usecols=lambda c: c in QUERIDAS, chunksize=1_500_000,
            na_values=["#NULO#", "#NE#"], keep_default_na=False,
        ):
            chunk = chunk.rename(columns=QUERIDAS)
            chunk = chunk[chunk["cargo"].isin(["1", "3", "5"])]
            if chunk.empty:
                continue
            chunk["tipo"] = _tipo(chunk["tipo_txt"])
            chave = ["uf", "mun", "zona", "secao"]
            sec_cols = [c for c in ("recebido", "encerramento", "abertura", "aptos", "comparecimento", "tipo_urna") if c in chunk]
            secoes.append(chunk[chave + sec_cols].drop_duplicates(subset=chave))
            v = chunk[chave + ["cargo", "tipo", "partido", "numero", "votos"]].copy()
            v["votos"] = pd.to_numeric(v["votos"], errors="coerce").fillna(0).astype("int32")
            votos.append(v)
    dv = pd.concat(votos, ignore_index=True)
    ds = pd.concat(secoes, ignore_index=True).drop_duplicates(subset=["uf", "mun", "zona", "secao"])
    for c in ("recebido", "encerramento", "abertura"):
        if c in ds:
            ds[c] = pd.to_datetime(ds[c], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    for c in ("aptos", "comparecimento"):
        if c in ds:
            ds[c] = pd.to_numeric(ds[c], errors="coerce")
    base = DERIV_H / f"{ano}-{turno}-{uf}"
    ds.to_parquet(f"{base}-secoes.parquet", index=False)
    dv.to_parquet(f"{base}-votos.parquet", index=False)
    return {"ano": ano, "turno": turno, "uf": uf, "secoes": len(ds), "linhas_votos": len(dv), "tem_recebido": "recebido" in ds and ds["recebido"].notna().any()}


def carregar(ano: str, turno: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabelas por secao e de votos de todas as UFs de um ano e turno (ja derivadas)."""
    ss, vv = [], []
    for f in sorted(DERIV_H.glob(f"{ano}-{turno}-*-secoes.parquet")):
        ss.append(pd.read_parquet(f))
        vv.append(pd.read_parquet(str(f).replace("-secoes", "-votos")))
    secoes = pd.concat(ss, ignore_index=True)
    votos = pd.concat(vv, ignore_index=True)
    secoes = secoes.rename(columns={"mun": "mun_cd"})
    votos = votos.rename(columns={"mun": "mun_cd"})
    for t in (secoes, votos):
        t["uf"] = t["uf"].str.upper()
    votos["numero"] = pd.to_numeric(votos["numero"], errors="coerce")
    votos["partido"] = pd.to_numeric(votos["partido"], errors="coerce")
    votos["cargo"] = votos["cargo"].astype(int)
    return secoes, votos
