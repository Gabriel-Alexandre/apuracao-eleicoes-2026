"""Reconstrucao da curva da apuracao (P1, P2, P3): soma dos boletins na ordem em que chegaram."""

from __future__ import annotations

import numpy as np
import pandas as pd

FLAVIO, LULA = "p22", "p13"


def ordenar(pres: pd.DataFrame) -> pd.DataFrame:
    d = pres.dropna(subset=["recebido"]).copy()
    d = d.sort_values(["recebido", "uf", "mun_cd", "zona", "secao"], kind="mergesort").reset_index(drop=True)
    return d


def curva(pres: pd.DataFrame, total_secoes: int) -> pd.DataFrame:
    """Curva acumulada: apos cada secao recebida, % de secoes, % de cada candidato nos validos."""
    d = ordenar(pres)
    cols = [c for c in d.columns if c.startswith("p") and c[1:].isdigit()]
    acc = d[cols].cumsum()
    out = pd.DataFrame({"recebido": d["recebido"], "n": np.arange(1, len(d) + 1)})
    out["pct_secoes"] = 100 * out["n"] / total_secoes
    out["validos"] = acc.sum(axis=1)
    for c in cols:
        out[f"pct_{c}"] = 100 * acc[c] / out["validos"]
    out["margem_flavio_lula"] = out[f"pct_{FLAVIO}"] - out[f"pct_{LULA}"]
    return out


def no_pct(cv: pd.DataFrame, pct: float) -> pd.Series:
    i = int(np.searchsorted(cv["pct_secoes"].values, pct, side="left"))
    i = min(i, len(cv) - 1)
    return cv.iloc[i]


def comparar_pontos(cv: pd.DataFrame, pontos: pd.DataFrame, tol_pct=0.1) -> pd.DataFrame:
    linhas = []
    for r in pontos.itertuples():
        x = no_pct(cv, r.pct_secoes)
        dF = x[f"pct_{FLAVIO}"] - r.flavio_pct
        dL = x[f"pct_{LULA}"] - r.lula_pct
        linhas.append(
            {
                "ponto": r.ponto,
                "hora_publicada": r.hora_brt_publicada,
                "pct_secoes": r.pct_secoes,
                "flavio_publicado": r.flavio_pct,
                "flavio_reconstruido": round(x[f"pct_{FLAVIO}"], 2),
                "erro_flavio": round(dF, 2),
                "lula_publicado": r.lula_pct,
                "lula_reconstruido": round(x[f"pct_{LULA}"], 2),
                "erro_lula": round(dL, 2),
                "recebido_no_corte": x["recebido"],
                "dentro_da_tolerancia": bool(abs(dF) <= tol_pct and abs(dL) <= tol_pct),
                "fontes": r.fontes,
            }
        )
    return pd.DataFrame(linhas)


def permutacoes(pres: pd.DataFrame, grade_pct: np.ndarray, n: int = 1000, seed: int = 20261004, por_uf: bool = False):
    """Contrafactual da P1. Devolve matriz (n, len(grade)) da margem Flavio-Lula em cada % de secoes.

    por_uf=False: ordem de chegada totalmente aleatoria.
    por_uf=True : mantem o calendario de chegada de cada UF (os instantes que ela ocupou na fila) e embaralha
                  QUAIS secoes da UF ocupam esses instantes. Mostra o que o calendario por UF explica sozinho.
    """
    d = ordenar(pres)
    f = d[FLAVIO].to_numpy(dtype=np.int64)
    l = d[LULA].to_numpy(dtype=np.int64)
    v = d["validos"].to_numpy(dtype=np.int64)
    uf = d["uf"].to_numpy()
    N = len(d)
    idx_grade = np.clip((grade_pct / 100 * N).astype(int) - 1, 0, N - 1)
    rng = np.random.default_rng(seed)
    resultados = np.empty((n, len(grade_pct)))
    grupos = [np.flatnonzero(uf == u) for u in np.unique(uf)] if por_uf else None
    for k in range(n):
        if por_uf:
            ordem = np.arange(N)
            for g in grupos:
                ordem[g] = rng.permutation(g)
        else:
            ordem = rng.permutation(N)
        cf = np.cumsum(f[ordem])[idx_grade]
        cl = np.cumsum(l[ordem])[idx_grade]
        val = np.cumsum(v[ordem])[idx_grade]
        resultados[k] = 100 * (cf - cl) / np.maximum(val, 1)
    return resultados
