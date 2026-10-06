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


def testar_fuso(secoes: pd.DataFrame) -> pd.DataFrame:
    d = secoes.dropna(subset=["recebido", "encerramento"]).copy()
    d["recebido"] = pd.to_datetime(d["recebido"])
    d["encerramento"] = pd.to_datetime(d["encerramento"])
    linhas = []
    for uf, g in d.groupby("uf"):
        off = pd.to_timedelta(OFFSET_PARA_BRASILIA.get(uf, 0), unit="h")
        lat_brt = (g["recebido"] - (g["encerramento"] + off)).dt.total_seconds() / 60
        lat_loc = (g["recebido"] - g["encerramento"]).dt.total_seconds() / 60
        linhas.append(
            {
                "uf": uf,
                "secoes": len(g),
                "viol_BRT": int((lat_brt < 0).sum()),
                "viol_LOCAL": int((lat_loc < 0).sum()),
                "pct_viol_BRT": round(100 * (lat_brt < 0).mean(), 3),
                "pct_viol_LOCAL": round(100 * (lat_loc < 0).mean(), 3),
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
        if r.pct_viol_BRT <= 0.1:
            candidatos.append(("BRT", abs(r.p05_BRT - ref)))
        if r.pct_viol_LOCAL <= 0.1:
            candidatos.append(("LOCAL", abs(r.p05_LOCAL - ref)))
        decididos.append(min(candidatos, key=lambda c: c[1])[0] if candidatos else "NENHUM")
    out["fuso_decidido"] = decididos
    out["latencia_ref_min"] = round(float(ref), 1)
    return out
