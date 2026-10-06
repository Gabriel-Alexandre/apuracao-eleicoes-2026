"""Analises P1 (queda da vantagem), P2 (a parada) e P7 (comparacao com 2022), sobre a curva reconstruida."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .curva import FLAVIO, LULA, ordenar


def marcar_pct(pres: pd.DataFrame, total_secoes: int, a: str = FLAVIO, b: str = LULA) -> pd.DataFrame:
    d = ordenar(pres)
    d["pct"] = 100 * (np.arange(len(d)) + 1) / total_secoes
    d["dif"] = d[a] - d[b]
    return d


def margem(df: pd.DataFrame) -> float:
    v = df["validos"].sum()
    return 100 * df["dif"].sum() / v if v else np.nan


def decompor(d: pd.DataFrame, p0: float, p1: float, chave: str = "uf") -> pd.DataFrame:
    """Decomposicao exata da mudanca de margem entre o que chegou ate p0 e o lote que chegou entre p0 e p1.

    M_lote - M_antes = (composicao do lote, a margem media de cada grupo no pais inteiro)
                     + (ordem de chegada dentro do grupo: o lote de cada grupo difere do restante do grupo)
    Contribuicao do grupo g para a mudanca da margem acumulada ate p1:  (V_lote_g / V_ate_p1) * (m_lote_g - M_antes).
    """
    antes = d[d["pct"] <= p0]
    lote = d[(d["pct"] > p0) & (d["pct"] <= p1)]
    ate = d[d["pct"] <= p1]
    if lote.empty or antes.empty:
        vazio = pd.DataFrame(columns=[chave, "secoes_no_lote", "peso_no_lote_pct", "margem_do_grupo_no_lote", "margem_do_grupo_antes", "margem_final_do_grupo", "contribuicao_pontos"])
        vazio.attrs.update(M_antes=np.nan, M_ate=np.nan, mudanca=np.nan, soma_contribuicoes=np.nan, M_lote=np.nan, diferenca_lote_menos_antes=np.nan, efeito_composicao=np.nan, efeito_ordem_dentro_do_grupo=np.nan)
        return vazio
    M_antes = margem(antes)
    M_ate = margem(ate)
    m_g = d.groupby(chave).apply(lambda g: 100 * g["dif"].sum() / g["validos"].sum(), include_groups=False)  # margem final do grupo
    linhas = []
    Vl = lote["validos"].sum()
    Va = ate["validos"].sum()
    for g, sub in lote.groupby(chave):
        b = antes[antes[chave] == g]
        mg_lote = 100 * sub["dif"].sum() / sub["validos"].sum() if sub["validos"].sum() else np.nan
        linhas.append(
            {
                chave: g,
                "secoes_no_lote": len(sub),
                "peso_no_lote_pct": 100 * sub["validos"].sum() / Vl,
                "margem_do_grupo_no_lote": mg_lote,
                "margem_do_grupo_antes": margem(b) if len(b) else np.nan,
                "margem_final_do_grupo": m_g[g],
                "contribuicao_pontos": (sub["validos"].sum() / Va) * (mg_lote - M_antes),
            }
        )
    out = pd.DataFrame(linhas).sort_values("contribuicao_pontos")
    out.attrs.update(M_antes=M_antes, M_ate=M_ate, mudanca=M_ate - M_antes, soma_contribuicoes=out["contribuicao_pontos"].sum())
    # composicao x ordem dentro do grupo
    M_lote = margem(lote)
    comp_lote = sum((sub["validos"].sum() / Vl) * m_g[g] for g, sub in lote.groupby(chave))
    comp_antes = sum((sub["validos"].sum() / antes["validos"].sum()) * m_g[g] for g, sub in antes.groupby(chave))
    out.attrs.update(
        M_lote=M_lote,
        diferenca_lote_menos_antes=M_lote - M_antes,
        efeito_composicao=comp_lote - comp_antes,
        efeito_ordem_dentro_do_grupo=(M_lote - comp_lote) - (M_antes - comp_antes),
    )
    return out


def chegada_por_regiao(d: pd.DataFrame, freq: str = "30min") -> pd.DataFrame:
    """Secoes recebidas por regiao em cada faixa de horario (para o grafico de composicao da chegada)."""
    t = d.assign(faixa=d["recebido"].dt.floor(freq))
    return t.pivot_table(index="faixa", columns="regiao", values="secao", aggfunc="count", fill_value=0)


def taxa_de_chegada(d: pd.DataFrame, freq: str = "5min") -> pd.DataFrame:
    """Boletins recebidos por faixa de horario e a margem do lote recebido nessa faixa (para P2)."""
    t = d.assign(faixa=d["recebido"].dt.floor(freq))
    g = t.groupby("faixa")
    out = pd.DataFrame(
        {
            "boletins": g.size(),
            "validos": g["validos"].sum(),
            "margem_flavio_lula_do_lote": g.apply(lambda x: 100 * x["dif"].sum() / x["validos"].sum() if x["validos"].sum() else np.nan, include_groups=False),
        }
    )
    return out


def vantagem_em(d: pd.DataFrame, pcts: list[float]) -> pd.DataFrame:
    linhas = []
    for p in pcts:
        sub = d[d["pct"] <= p]
        linhas.append({"pct_secoes": p, "margem": margem(sub), "recebido_ate": sub["recebido"].iloc[-1] if len(sub) else None})
    return pd.DataFrame(linhas)


def troca_de_lideranca(d: pd.DataFrame) -> dict:
    """Em que % de secoes a margem acumulada muda de sinal (se mudar)."""
    cum = d["dif"].cumsum()
    sinal = np.sign(cum.to_numpy())
    mudancas = np.flatnonzero(np.diff(sinal) != 0)
    return {
        "trocou": bool(len(mudancas)),
        "pct_secoes_da_troca": [float(d["pct"].iloc[i + 1]) for i in mudancas[:5]],
        "margem_final_pontos": margem(d),
    }
