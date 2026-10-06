"""Teste T2.4 do pre-registro: em que fuso esta a hora de recebimento do boletim?

Hipoteses, por UF:
  BRT    `recebido` esta em horario de Brasilia e `encerramento` (do boletim) em horario local da urna.
  LOCAL  `recebido` e `encerramento` estao os dois em horario local.
Regra pre-registrada: vale a hipotese com zero violacoes (tolerancia de 0,1% das secoes), onde violacao
e o boletim ter sido recebido antes de a urna encerrar. Emenda de 05/out (PRE_REGISTRO.md secao 9): entre as
hipoteses com zero violacoes, vale a que deixa a latencia minima (percentil 0,5) mais proxima da mediana
das UFs que ja estao em horario de Brasilia.
"""

from __future__ import annotations

import pandas as pd

# horas a somar ao horario local para chegar em horario de Brasilia (UTC-3, sem horario de verao desde 2019)
OFFSET_PARA_BRASILIA = {"AC": 2, "AM": 1, "RO": 1, "RR": 1, "MT": 1, "MS": 1}
REGIAO = {
    **dict.fromkeys(["AC", "AP", "AM", "PA", "RO", "RR", "TO"], "Norte"),
    **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
    **dict.fromkeys(["DF", "GO", "MT", "MS"], "Centro-Oeste"),
    **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
    **dict.fromkeys(["PR", "RS", "SC"], "Sul"),
    "ZZ": "Exterior",
}


def testar_fuso(secoes: pd.DataFrame, limite_municipio: float = 0.05, limite_uf: float = 0.01) -> pd.DataFrame:
    """Decide o fuso por UF. A unidade da decisao e o MUNICIPIO (emenda de 05/out, PRE_REGISTRO secao 9).

    Um municipio "falha" numa hipotese se mais de `limite_municipio` das suas secoes tem recebimento antes do encerramento.
    A UF aceita a hipotese se no maximo `limite_uf` das suas secoes estao em municipios que falham. Poucos municipios com o
    relogio da urna fora do padrao (ex.: urnas de Mato Grosso com horario de Brasilia, Fernando de Noronha em Pernambuco)
    nao decidem o fuso do estado inteiro. Esses municipios ficam listados (`municipios_fora_do_padrao`).
    A regra de desempate pela latencia minima continua valendo quando as duas hipoteses passam.
    """
    d = secoes.dropna(subset=["recebido", "encerramento"]).copy()
    d["recebido"] = pd.to_datetime(d["recebido"])
    d["encerramento"] = pd.to_datetime(d["encerramento"])
    linhas = []
    mun_fora = []
    for uf, g in d.groupby("uf"):
        off = pd.to_timedelta(OFFSET_PARA_BRASILIA.get(uf, 0), unit="h")
        lat_brt = (g["recebido"] - (g["encerramento"] + off)).dt.total_seconds() / 60
        lat_loc = (g["recebido"] - g["encerramento"]).dt.total_seconds() / 60
        g = g.assign(vb=lat_brt < 0, vl=lat_loc < 0)
        por_mun = g.groupby("mun_cd").agg(secoes=("vb", "size"), fb=("vb", "mean"), fl=("vl", "mean"))
        ruins_b = por_mun[por_mun.fb > limite_municipio]
        ruins_l = por_mun[por_mun.fl > limite_municipio]
        sec_em_ruins_b = int(ruins_b.secoes.sum())
        sec_em_ruins_l = int(ruins_l.secoes.sum())
        for m, r in ruins_b.iterrows():
            mun_fora.append({"uf": uf, "mun_cd": m, "secoes": int(r.secoes), "pct_violacao_BRT": round(100 * r.fb, 1), "pct_violacao_LOCAL": round(100 * r.fl, 1)})
        linhas.append(
            {
                "uf": uf,
                "secoes": len(g),
                "viol_BRT": int(g["vb"].sum()),
                "viol_LOCAL": int(g["vl"].sum()),
                "pct_viol_BRT": round(100 * g["vb"].mean(), 3),
                "pct_viol_LOCAL": round(100 * g["vl"].mean(), 3),
                "municipios_fora_do_padrao_BRT": len(ruins_b),
                "secoes_em_municipios_fora_do_padrao_BRT": sec_em_ruins_b,
                "secoes_em_municipios_fora_do_padrao_LOCAL": sec_em_ruins_l,
                "latencia_mediana_min_BRT": round(float(lat_brt.median()), 1),
                "latencia_p95_min_BRT": round(float(lat_brt.quantile(0.95)), 1),
                "latencia_min_min_BRT": round(float(lat_brt.min()), 1),
                "p05_BRT": round(float(lat_brt.quantile(0.005)), 1),
                "p05_LOCAL": round(float(lat_loc.quantile(0.005)), 1),
            }
        )
    out = pd.DataFrame(linhas)
    ref = out.loc[~out["uf"].isin(OFFSET_PARA_BRASILIA) & (out["uf"] != "ZZ"), "p05_BRT"].median()
    decididos = []
    for r in out.itertuples():
        candidatos = []
        if r.secoes_em_municipios_fora_do_padrao_BRT <= limite_uf * r.secoes:
            candidatos.append(("BRT", abs(r.p05_BRT - ref)))
        if r.secoes_em_municipios_fora_do_padrao_LOCAL <= limite_uf * r.secoes:
            candidatos.append(("LOCAL", abs(r.p05_LOCAL - ref)))
        decididos.append(min(candidatos, key=lambda c: c[1])[0] if candidatos else "NENHUM")
    out["fuso_decidido"] = decididos
    out["latencia_ref_min"] = round(float(ref), 1)
    out.attrs["municipios_fora_do_padrao"] = pd.DataFrame(mun_fora)
    return out
