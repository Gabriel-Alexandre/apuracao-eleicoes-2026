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
    out["votos_flavio"] = acc[FLAVIO]
    out["votos_lula"] = acc[LULA]
    for c in cols:
        out[f"pct_{c}"] = 100 * acc[c] / out["validos"]
    out["margem_flavio_lula"] = out[f"pct_{FLAVIO}"] - out[f"pct_{LULA}"]
    return out


def no_pct(cv: pd.DataFrame, pct: float) -> pd.Series:
    i = int(np.searchsorted(cv["pct_secoes"].values, pct, side="left"))
    i = min(i, len(cv) - 1)
    return cv.iloc[i]


def comparar_pontos(cv: pd.DataFrame, pontos: pd.DataFrame, tol_pct: float = 0.1, janela: float = 0.5) -> pd.DataFrame:
    """Confere cada ponto publicado contra a curva reconstruida.

    Regra pre-registrada (secao 3): o ponto "encaixa" se, em algum instante da curva com % de secoes a ate `janela`
    (0,5 ponto) do publicado, o % de Flavio e o de Lula estao a ate `tol_pct` (0,1) dos publicados.
    Tambem se reporta o erro no % de secoes exato, e, quando a fonte publicou votos absolutos, a diferenca em votos.
    """
    pct = cv["pct_secoes"].to_numpy()
    F = cv[f"pct_{FLAVIO}"].to_numpy()
    L = cv[f"pct_{LULA}"].to_numpy()
    cf = cv["votos_flavio"].to_numpy()
    cl = cv["votos_lula"].to_numpy()
    linhas = []
    for r in pontos.itertuples():
        i0 = min(int(np.searchsorted(pct, r.pct_secoes, side="left")), len(cv) - 1)
        lo = int(np.searchsorted(pct, r.pct_secoes - janela, side="left"))
        hi = min(int(np.searchsorted(pct, r.pct_secoes + janela, side="right")), len(cv))
        win = slice(lo, max(hi, lo + 1))
        dF_w, dL_w = F[win] - r.flavio_pct, L[win] - r.lula_pct
        pior = np.maximum(np.abs(dF_w), np.abs(dL_w))
        k = int(np.argmin(pior))
        lin = {
            "ponto": r.ponto,
            "hora_publicada": r.hora_publicada_brt,
            "pct_secoes": r.pct_secoes,
            "flavio_publicado": r.flavio_pct,
            "flavio_reconstruido_no_pct": round(F[i0], 2),
            "erro_flavio_no_pct": round(F[i0] - r.flavio_pct, 2),
            "lula_publicado": r.lula_pct,
            "lula_reconstruido_no_pct": round(L[i0], 2),
            "erro_lula_no_pct": round(L[i0] - r.lula_pct, 2),
            "melhor_erro_na_janela": round(float(pior[k]), 3),
            "pct_secoes_do_melhor_encaixe": round(float(pct[win][k]), 2),
            "encaixa": bool(pior[k] <= tol_pct),
            "recebido_no_corte": cv["recebido"].iloc[i0],
            "fontes": r.fontes,
        }
        if pd.notna(getattr(r, "votos_flavio", np.nan)):
            lin["votos_flavio_publicado"] = int(r.votos_flavio)
            lin["votos_flavio_reconstruido_no_pct"] = int(cf[i0])
            lin["dif_votos_flavio"] = int(cf[i0] - r.votos_flavio)
            lin["votos_lula_publicado"] = int(r.votos_lula)
            lin["votos_lula_reconstruido_no_pct"] = int(cl[i0])
            lin["dif_votos_lula"] = int(cl[i0] - r.votos_lula)
        if pd.notna(getattr(r, "margem_votos", np.nan)):
            lin["margem_votos_publicada"] = int(r.margem_votos)
            lin["margem_votos_reconstruida_no_pct"] = int(cf[i0] - cl[i0])
        linhas.append(lin)
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
