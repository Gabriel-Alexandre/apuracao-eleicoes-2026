"""P5 (governador x presidente, classe de referencia por apoio declarado) e P6 (Senado x presidente)."""

from __future__ import annotations

import json
import unicodedata

import numpy as np
import pandas as pd

from . import coleta, oficial

DADOS = coleta.RAIZ / "dados"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return " ".join(s.replace(".", " ").replace("-", " ").split())


def _mun_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def totais_uf(votos: pd.DataFrame) -> pd.DataFrame:
    """Votos nominais por (uf, cargo, numero), e % dos validos do cargo na UF."""
    nom = votos[votos["tipo"] == 1].groupby(["uf", "cargo", "numero"]).votos.sum().rename("votos").reset_index()
    nom["validos"] = nom.groupby(["uf", "cargo"]).votos.transform("sum")
    nom["pct"] = 100 * nom["votos"] / nom["validos"]
    return nom


def por_secao(votos: pd.DataFrame, cargo: int, numero: int, nome: str) -> pd.Series:
    v = votos[(votos["cargo"] == cargo) & (votos["tipo"] == 1) & (votos["numero"] == numero)]
    return v.groupby(["uf", "mun_cd", "zona", "secao"]).votos.sum().rename(nome)


def vencedor_governador(tot: pd.DataFrame) -> pd.DataFrame:
    g = tot[tot.cargo == 3].sort_values(["uf", "votos"], ascending=[True, False])
    top = g.groupby("uf").head(1).rename(columns={"numero": "gov_numero", "votos": "gov_votos", "pct": "gov_pct"})
    top["venceu_no_1_turno"] = top["gov_pct"] > 50
    return top[["uf", "gov_numero", "gov_votos", "gov_pct", "venceu_no_1_turno"]]


def lacuna_governador_presidente(votos: pd.DataFrame, apoios: pd.DataFrame, ano: int) -> pd.DataFrame:
    """g = % do governador vencedor menos % do candidato a presidente que ele declarou apoiar, por UF."""
    tot = totais_uf(votos)
    ap = apoios[(apoios.ano == ano) & (apoios.candidato_apoiado.notna())].copy()
    ap["candidato_apoiado"] = ap["candidato_apoiado"].astype(int)
    gov = vencedor_governador(tot)
    base = ap.merge(gov, on="uf", how="left")
    pres = tot[tot.cargo == 1][["uf", "numero", "pct", "votos"]].rename(columns={"numero": "candidato_apoiado", "pct": "pres_pct", "votos": "pres_votos"})
    base = base.merge(pres, on=["uf", "candidato_apoiado"], how="left")
    base["lacuna_pontos"] = base["gov_pct"] - base["pres_pct"]
    base["lacuna_votos"] = base["gov_votos"] - base["pres_votos"]
    return base


def concentracao(votos: pd.DataFrame, uf: str, gov_numero: int, pres_numero: int, fracao: float = 0.5) -> dict:
    """Concentracao da diferenca de votos governador - presidente, por secao.

    Medida pre-registrada: quantas secoes (das que mais contribuem) somam `fracao` da diferenca liquida D.
    Refinamento de 05/out (PRE_REGISTRO secao 9): quando |D| e pequeno frente ao fluxo bruto, a medida e instavel
    (poucas secoes grandes ja passam de metade de um D quase zero). Por isso se reporta tambem a razao
    liquido/bruto e o indice de concentracao do 1% de secoes que mais contribuem (1,0 = proporcional ao tamanho).
    """
    v = votos[votos["uf"] == uf]
    g = por_secao(v, 3, gov_numero, "g")
    p = por_secao(v, 1, pres_numero, "p")
    validos_g = v[(v.cargo == 3) & (v.tipo == 1)].groupby(["uf", "mun_cd", "zona", "secao"]).votos.sum().rename("vg")
    t = pd.concat([g, p, validos_g], axis=1).fillna(0)
    t["c"] = t["g"] - t["p"]
    D = float(t["c"].sum())
    n = len(t)
    bruto = float(t["c"].abs().sum())
    out = {"uf": uf, "secoes": n, "diferenca_votos": int(D), "fluxo_bruto": int(bruto), "razao_liquido_bruto": abs(D) / bruto if bruto else np.nan}
    if D == 0 or n == 0:
        return {**out, "secoes_para_metade": np.nan, "fracao_das_secoes": np.nan, "estavel": False, "indice_top1pct": np.nan}
    dirc = np.sign(D)
    a = (dirc * t["c"]).sort_values(ascending=False)
    cum = a.cumsum()
    k = int((cum >= fracao * abs(D)).values.argmax()) + 1
    topn = max(1, int(round(0.01 * n)))
    top_idx = a.index[:topn]
    pos_total = float(a.clip(lower=0).sum())
    share_gross = float(a.iloc[:topn].clip(lower=0).sum() / pos_total) if pos_total else np.nan
    share_votes = float(t.loc[top_idx, "vg"].sum() / t["vg"].sum()) if t["vg"].sum() else np.nan
    return {
        **out, "secoes_para_metade": k, "fracao_das_secoes": k / n, "estavel": abs(D) / bruto >= 0.2,
        "top1pct_parcela_do_fluxo_positivo": share_gross, "top1pct_parcela_dos_votos": share_votes,
        "indice_top1pct": share_gross / share_votes if share_votes else np.nan,
    }


def candidatos_oficiais_senado(uf: str) -> pd.DataFrame:
    con = oficial.abrir()
    row = con.execute("SELECT body FROM raw WHERE url=?", (oficial.url_uf(uf.lower(), "5", oficial.ELE_ESTADUAL),)).fetchone()
    con.close()
    d = json.loads(row[0])
    linhas = []
    for a in d["carg"][0]["agr"]:
        for p in a["par"]:
            for c in p["cand"]:
                linhas.append({"uf": uf.upper(), "numero": int(c["n"]), "nome": c["nmu"], "nome_civil": c.get("nm", ""), "partido": p["sg"], "votos": int(c["vap"]), "pct": float(str(c["pvapn"]).replace(",", ".")), "eleito": c.get("e") == "s"})
    return pd.DataFrame(linhas)


def casar_apoio_flavio(ufs: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Casa a lista de candidatos ao Senado que Flavio declarou apoiar com os candidatos do arquivo oficial."""
    lista = pd.read_csv(DADOS / "senado-apoio-flavio.csv")
    cand = pd.concat([candidatos_oficiais_senado(u) for u in ufs], ignore_index=True)
    cand["nn"] = cand["nome"].map(_norm)
    cand["nc"] = cand["nome_civil"].map(_norm)
    achados, perdidos = [], []
    for r in lista.itertuples():
        alvo = _norm(r.candidato)
        toks = set(alvo.split())
        c = cand[cand.uf == r.uf]
        hit = c[(c.nn == alvo) | (c.nc == alvo) | c.apply(lambda x: toks <= set(x.nn.split()) or toks <= set(x.nc.split()) or set(x.nn.split()) <= toks, axis=1)]
        if len(hit) == 1:
            achados.append({**hit.iloc[0].to_dict(), "apoio_declarado": True, "nome_na_lista": r.candidato})
        elif len(hit) > 1:
            h2 = hit[hit.partido.map(_norm) == _norm(r.partido)]
            if len(h2) == 1:
                achados.append({**h2.iloc[0].to_dict(), "apoio_declarado": True, "nome_na_lista": r.candidato})
            else:
                perdidos.append({"uf": r.uf, "candidato": r.candidato, "motivo": f"{len(hit)} candidatos casam"})
        else:
            perdidos.append({"uf": r.uf, "candidato": r.candidato, "motivo": "nenhum candidato casa"})
    return pd.DataFrame(achados), pd.DataFrame(perdidos)


def senado_vs_presidente(votos: pd.DataFrame, ufs: list[str], flavio: int = 22, lula: int = 13) -> pd.DataFrame:
    """Por UF: voto do campo ao Senado por eleitor, contra % de Flavio. Tres campos: PL, apoiados por Flavio, PT."""
    tot = totais_uf(votos)
    achados, _perdidos = casar_apoio_flavio(ufs)
    linhas = []
    for uf in ufs:
        sen = tot[(tot.uf == uf) & (tot.cargo == 5)]
        pres = tot[(tot.uf == uf) & (tot.cargo == 1)]
        if sen.empty or pres.empty:
            continue
        v_sen = sen.votos.sum()
        eleitores_aprox = v_sen / 2  # dois votos por eleitor
        F = pres[pres.numero == flavio].pct.sum()
        L = pres[pres.numero == lula].pct.sum()
        oc = candidatos_oficiais_senado(uf)
        pl = oc[oc.partido == "PL"]
        pt = oc[oc.partido == "PT"]
        ap = achados[achados.uf == uf] if len(achados) else pd.DataFrame(columns=["votos", "eleito"])
        def bloco(df, prefixo):
            n = len(df)
            vt = int(df.votos.sum()) if n else 0
            return {
                f"{prefixo}_n": n,
                f"{prefixo}_votos": vt,
                f"{prefixo}_eleitos": int(df.eleito.sum()) if n else 0,
                f"{prefixo}_votos_por_eleitor": vt / eleitores_aprox if n else np.nan,
                f"{prefixo}_media_por_candidato_pct_eleitores": 100 * vt / n / eleitores_aprox if n else np.nan,
            }
        linhas.append({"uf": uf, "flavio_pct": F, "lula_pct": L, "validos_senado": int(v_sen), "eleitores_aprox": eleitores_aprox, **bloco(pl, "pl"), **bloco(ap, "apoio_flavio"), **bloco(pt, "pt")})
    out = pd.DataFrame(linhas)
    out["razao_pl_media_sobre_flavio"] = out["pl_media_por_candidato_pct_eleitores"] / out["flavio_pct"]
    out["razao_pt_media_sobre_lula"] = out["pt_media_por_candidato_pct_eleitores"] / out["lula_pct"]
    out["razao_apoio_flavio_media_sobre_flavio"] = out["apoio_flavio_media_por_candidato_pct_eleitores"] / out["flavio_pct"]
    return out


# ---------------------------------------------------------------------------------------------
# P5-b: de onde vem a diferenca entre o voto no governador aliado e o voto no presidente
# ---------------------------------------------------------------------------------------------

def contabilidade(votos: pd.DataFrame, uf: str) -> pd.DataFrame:
    """Contabilidade exata (sem inferencia): % dos validos de cada cargo, candidato a candidato, na UF."""
    tot = totais_uf(votos[votos["uf"] == uf])
    return tot[tot.cargo.isin([1, 3])].sort_values(["cargo", "votos"], ascending=[True, False])


def _tabela_ei(votos: pd.DataFrame, uf: str, gov_cands: dict[str, int], pres_cands: dict[str, int]) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Por secao: votos de cada grupo de governador (colunas) e de cada grupo de presidente (saidas), incluindo branco e nulo."""
    v = votos[votos["uf"] == uf]
    chave = ["mun_cd", "zona", "secao"]

    def grupo(cargo, cands, prefixo):
        sub = v[v.cargo == cargo]
        parts = {}
        nominal = sub[sub.tipo == 1]
        total_nom = nominal.groupby(chave).votos.sum()
        usados = 0
        cols = {}
        for nome, num in cands.items():
            s = nominal[nominal.numero == num].groupby(chave).votos.sum()
            cols[f"{prefixo}_{nome}"] = s
        t = pd.DataFrame(cols).reindex(total_nom.index).fillna(0)
        t[f"{prefixo}_outros_nominais"] = total_nom - t.sum(axis=1)
        nao_val = sub[sub.tipo != 1].groupby(chave).votos.sum()
        t[f"{prefixo}_branco_nulo"] = nao_val.reindex(t.index).fillna(0)
        return t

    g = grupo(3, gov_cands, "g")
    p = grupo(1, pres_cands, "p")
    t = g.join(p, how="inner")
    return t, list(g.columns), list(p.columns)


def inferencia_ecologica(votos: pd.DataFrame, uf: str, gov_cands: dict[str, int], pres_cands: dict[str, int], rodadas: int = 200, semente: int = 20261004) -> pd.DataFrame:
    """Estima, por regressao com restricao, a fracao dos eleitores de cada grupo de governador que votou em cada grupo de presidente.

    ECOLOGICA: usa totais por secao, nao o voto de ninguem. Exploratoria, com intervalo por reamostragem de municipios
    (percentis 5 e 95) e com os limites da falacia ecologica. Cada linha da matriz soma 1 por construcao (normalizacao).
    """
    from scipy.optimize import nnls

    t, gcols, pcols = _tabela_ei(votos, uf, gov_cands, pres_cands)
    t = t.reset_index()
    t = t[t[gcols].sum(axis=1) > 0]
    muns = t["mun_cd"].unique()
    rng = np.random.default_rng(semente)

    def estimar(df: pd.DataFrame) -> np.ndarray:
        X = df[gcols].to_numpy(dtype=float)
        w = 1.0 / np.sqrt(np.maximum(X.sum(axis=1), 1.0))
        B = np.zeros((len(gcols), len(pcols)))
        for k, pc in enumerate(pcols):
            y = df[pc].to_numpy(dtype=float)
            b, _ = nnls(X * w[:, None], y * w)
            B[:, k] = b
        s = B.sum(axis=1, keepdims=True)
        return B / np.where(s == 0, 1, s), s.ravel()

    base, somas = estimar(t)
    por_mun = {m: g for m, g in t.groupby("mun_cd")}
    boot = []
    for _ in range(rodadas):
        amostra = rng.choice(muns, size=len(muns), replace=True)
        df = pd.concat([por_mun[m] for m in amostra], ignore_index=True)
        boot.append(estimar(df)[0])
    boot = np.stack(boot)
    linhas = []
    for i, gc in enumerate(gcols):
        for k, pc in enumerate(pcols):
            linhas.append({
                "grupo_governador": gc, "grupo_presidente": pc, "fracao_estimada": float(base[i, k]),
                "p05": float(np.percentile(boot[:, i, k], 5)), "p95": float(np.percentile(boot[:, i, k], 95)),
                "soma_da_linha_antes_de_normalizar": float(somas[i]),
                "votos_do_grupo_governador": int(t[gc].sum()),
            })
    return pd.DataFrame(linhas)


def alinhamento_municipal(votos: pd.DataFrame, num_partido: int, num_pres: int, votos_por_eleitor: int, min_municipios: int = 10) -> pd.DataFrame:
    """Dentro de cada UF, a correlacao (Spearman, entre municipios) entre o voto no candidato a presidente e o voto
    medio por candidato do mesmo partido ao Senado. Mostra se os dois votos andam juntos no territorio, sem depender do nivel.
    """
    from scipy import stats

    v = votos[(votos.tipo == 1)]
    chave = ["uf", "mun_cd"]
    pres = v[v.cargo == 1].groupby(chave).votos.sum().rename("vp")
    pres_c = v[(v.cargo == 1) & (v.numero == num_pres)].groupby(chave).votos.sum().rename("p")
    sen = v[v.cargo == 5]
    sen_tot = sen.groupby(chave).votos.sum().rename("vs")
    cand = sen[(sen.numero // 10) == num_partido]
    n_cand = cand.groupby("uf").numero.nunique().rename("n")
    sen_c = cand.groupby(chave).votos.sum().rename("s")
    t = pd.concat([pres, pres_c, sen_tot, sen_c], axis=1).fillna(0).reset_index().merge(n_cand.reset_index(), on="uf", how="inner")
    t = t[(t.vp > 0) & (t.vs > 0)]
    t["pct_pres"] = 100 * t["p"] / t["vp"]
    t["pct_sen_por_candidato"] = 100 * (t["s"] / t["n"]) / (t["vs"] / votos_por_eleitor)
    linhas = []
    for uf, g in t.groupby("uf"):
        if len(g) >= min_municipios:
            rho = stats.spearmanr(g["pct_pres"], g["pct_sen_por_candidato"])[0]
            linhas.append({"uf": uf, "municipios": len(g), "n_candidatos_do_partido": int(g["n"].iloc[0]), "spearman_pres_x_senado": rho})
    return pd.DataFrame(linhas)
