"""P8: testes de anomalia, com placebo (2022, outros cargos) e correcao para muitos testes (Benjamini-Hochberg).

Regra pre-registrada: um municipio so e "a explicar" se passar a correcao no teste de comparecimento x voto,
E destoar do proprio historico (2022), E destoar do outro cargo da mesma urna (governador), os tres ao mesmo tempo.
Todo teste roda para todos os candidatos com mais de 1% dos validos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

CHAVE_SEC = ["uf", "mun_cd", "zona", "secao"]


def _mun_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def bh(p: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg: devolve booleano 'rejeita H0' com taxa de falsa descoberta q."""
    p = np.asarray(p, dtype=float)
    n = len(p)
    ordem = np.argsort(p)
    lim = q * (np.arange(1, n + 1) / n)
    ok = p[ordem] <= lim
    k = np.max(np.flatnonzero(ok)) + 1 if ok.any() else 0
    rej = np.zeros(n, dtype=bool)
    rej[ordem[:k]] = True
    return rej


def secao_candidato(votos: pd.DataFrame, cargo: int, numero: int, nome: str) -> pd.Series:
    v = votos[(votos["cargo"] == cargo) & (votos["tipo"] == 1) & (votos["numero"] == numero)]
    return v.groupby(CHAVE_SEC).votos.sum().rename(nome)


def tabela_secao(secoes: pd.DataFrame, votos: pd.DataFrame, cargo: int, numeros: dict[str, int]) -> pd.DataFrame:
    """Uma linha por secao: aptos, comparecimento, validos do cargo e votos de cada candidato pedido."""
    v = votos[(votos["cargo"] == cargo) & (votos["tipo"] == 1)]
    validos = v.groupby(CHAVE_SEC).votos.sum().rename("validos")
    t = pd.concat([validos] + [secao_candidato(votos, cargo, n, nome) for nome, n in numeros.items()], axis=1).fillna(0).reset_index()
    base = secoes[~secoes.get("agregada", pd.Series(False, index=secoes.index))][CHAVE_SEC + ["aptos", "comparecimento"]]
    t = t.merge(base, on=CHAVE_SEC, how="left")
    t["mun_int"] = _mun_int(t["mun_cd"])
    t["comparecimento_pct"] = 100 * t["comparecimento"] / t["aptos"]
    return t


def z_na_cidade(t: pd.DataFrame, col: str, min_validos: int = 30, min_secoes: int = 10) -> pd.Series:
    """z binomial de cada secao contra o resto do proprio municipio (sem a propria secao)."""
    g = t.groupby(["uf", "mun_int"])
    F_m = g[col].transform("sum")
    V_m = g["validos"].transform("sum")
    n_m = g[col].transform("size")
    V_s = t["validos"]
    p = (F_m - t[col]) / (V_m - V_s).replace(0, np.nan)
    z = (t[col] - p * V_s) / np.sqrt((V_s * p * (1 - p)).replace(0, np.nan))
    z[(V_s < min_validos) | (n_m < min_secoes)] = np.nan
    return z


def cauda(z: pd.Series, limites=(4, 5, 6)) -> dict:
    z = z.dropna()
    out = {"n": int(len(z)), "sd": float(z.std()), "q001": float(z.quantile(0.001)), "q999": float(z.quantile(0.999))}
    for L in limites:
        out[f"pct_abs_gt_{L}"] = float(100 * (z.abs() > L).mean())
    return out


def ultimo_digito(valores: pd.Series, minimo: int = 100) -> dict:
    v = valores[valores >= minimo].astype(int)
    cont = np.bincount(v % 10, minlength=10)
    chi2, p = stats.chisquare(cont)
    return {"n": int(len(v)), "chi2": float(chi2), "p_valor": float(p), "maior_desvio_pct": float(100 * np.abs(cont / cont.sum() - 0.1).max())}


def impressao_digital(t: pd.DataFrame, col: str) -> pd.DataFrame:
    """Por UF: correlacao entre comparecimento e % do candidato, e a fracao de secoes no canto 'alto comparecimento e alto voto'."""
    t = t[(t["validos"] >= 30) & t["comparecimento_pct"].notna()].copy()
    t["pct"] = 100 * t[col] / t["validos"]
    linhas = []
    for uf, g in t.groupby("uf"):
        r = stats.spearmanr(g["comparecimento_pct"], g["pct"])[0] if len(g) > 10 else np.nan
        canto = ((g["comparecimento_pct"] >= 95) & (g["pct"] >= 90)).mean() * 100
        linhas.append({"uf": uf, "secoes": len(g), "spearman_comparecimento_x_pct": r, "pct_secoes_no_canto_95_90": canto, "comparecimento_medio": g["comparecimento_pct"].mean()})
    return pd.DataFrame(linhas)


def municipios_tabela(t: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    g = t.groupby(["uf", "mun_int"])
    out = g[["validos", "aptos", "comparecimento"] + cols].sum()
    out["comparecimento_pct"] = 100 * out["comparecimento"] / out["aptos"]
    for c in cols:
        out[f"pct_{c}"] = 100 * out[c] / out["validos"]
    return out.reset_index()


def z_robusto_por_uf(df: pd.DataFrame, col: str) -> pd.Series:
    def f(x):
        med = x.median()
        mad = (x - med).abs().median() * 1.4826
        return (x - med) / mad if mad > 0 else x * np.nan
    return df.groupby("uf")[col].transform(f)


def sinalizar_municipios(m26: pd.DataFrame, m22: pd.DataFrame, gov26: pd.DataFrame, flavio_col: str, boso_col: str,
                         gov_col: str, min_validos: int = 2000, q: float = 0.05) -> pd.DataFrame:
    """Tres testes por municipio (todos corrigidos por BH):
       (a) historico: mudanca de % do candidato 2022->2026 contra a distribuicao da propria UF;
       (b) outro cargo: lacuna entre % do presidente e % do governador contra a distribuicao da propria UF;
       (c) comparecimento x voto: residuo da regressao de % do candidato sobre comparecimento, dentro da UF.
    """
    d = m26.merge(m22[["uf", "mun_int", f"pct_{boso_col}", "comparecimento_pct"]].rename(columns={"comparecimento_pct": "comp22"}), on=["uf", "mun_int"], how="inner")
    d = d.merge(gov26[["uf", "mun_int", f"pct_{gov_col}"]], on=["uf", "mun_int"], how="inner")
    d = d[d["validos"] >= min_validos].copy()
    d["mudanca_vs_2022"] = d[f"pct_{flavio_col}"] - d[f"pct_{boso_col}"]
    d["lacuna_gov_pres"] = d[f"pct_{gov_col}"] - d[f"pct_{flavio_col}"]
    # residuo comparecimento x voto por UF
    res = []
    for uf, g in d.groupby("uf"):
        if len(g) < 12:
            res.append(pd.Series(np.nan, index=g.index))
            continue
        b = np.polyfit(g["comparecimento_pct"], g[f"pct_{flavio_col}"], 1)
        res.append(g[f"pct_{flavio_col}"] - np.polyval(b, g["comparecimento_pct"]))
    d["residuo_comp_voto"] = pd.concat(res)
    for nome, col in (("a", "mudanca_vs_2022"), ("b", "lacuna_gov_pres"), ("c", "residuo_comp_voto")):
        d[f"z_{nome}"] = z_robusto_por_uf(d, col)
        p = 2 * stats.norm.sf(d[f"z_{nome}"].abs().fillna(0))
        p = np.where(d[f"z_{nome}"].isna(), 1.0, p)
        d[f"sinal_{nome}"] = bh(p, q)
    d["a_explicar"] = d["sinal_a"] & d["sinal_b"] & d["sinal_c"]
    return d
