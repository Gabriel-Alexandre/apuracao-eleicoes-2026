"""Analises 3: testes de anomalia (P8), sempre com placebo (2022 e 2018) e correcao para muitos testes.

Uso: python ferramentas/analise-3-anomalias.py [--ufs ...]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import anomalia as an, coleta, historico, nacional, saida, uf as ufm  # noqa: E402


def tabela_governador(secoes, votos, cargo=3):
    """Por secao: votos do candidato lider de cada UF ao governo (o lider no total da UF)."""
    tot = ufm.totais_uf(votos)
    gov = ufm.vencedor_governador(tot).set_index("uf")["gov_numero"].to_dict()
    v = votos[(votos.cargo == cargo) & (votos.tipo == 1)]
    validos = v.groupby(an.CHAVE_SEC).votos.sum().rename("validos")
    v = v.assign(lider=v["uf"].map(gov))
    lider = v[v["numero"] == v["lider"]].groupby(an.CHAVE_SEC).votos.sum().rename("lider")
    t = pd.concat([validos, lider], axis=1).fillna(0).reset_index()
    base = secoes[~secoes.get("agregada", pd.Series(False, index=secoes.index))][an.CHAVE_SEC + ["aptos", "comparecimento"]]
    t = t.merge(base, on=an.CHAVE_SEC, how="left")
    t["mun_int"] = an._mun_int(t["mun_cd"])
    t["comparecimento_pct"] = 100 * t["comparecimento"] / t["aptos"]
    return t, gov


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ufs", nargs="*")
    args = ap.parse_args()
    ufs = [u.lower() for u in args.ufs] if args.ufs else coleta.UFS
    s26, v26 = nacional.carregar(ufs)
    s22, v22 = historico.carregar("2022", "1")
    s18, v18 = historico.carregar("2018", "1")
    for s in (s22, s18):
        s["agregada"] = False
    if args.ufs:
        ufs_up = {u.upper() for u in ufs}
        s22, v22 = s22[s22.uf.isin(ufs_up)], v22[v22.uf.isin(ufs_up)]
        s18, v18 = s18[s18.uf.isin(ufs_up)], v18[v18.uf.isin(ufs_up)]

    t26 = an.tabela_secao(s26, v26, 1, {"flavio": 22, "lula": 13})
    t22 = an.tabela_secao(s22, v22, 1, {"boso": 22, "lula": 13})
    t18 = an.tabela_secao(s18, v18, 1, {"boso": 17, "haddad": 13})

    # ---------------- A2: caudas dos z-scores dentro do municipio (todos os candidatos acima de 1%)
    linhas = []
    for ano, t, cols in ((2026, t26, ["flavio", "lula"]), (2022, t22, ["boso", "lula"]), (2018, t18, ["boso", "haddad"])):
        for c in cols:
            linhas.append({"ano": ano, "cargo": "presidente", "candidato": c, **an.cauda(an.z_na_cidade(t, c))})
    g26, gov26 = tabela_governador(s26, v26)
    g22, gov22 = tabela_governador(s22, v22)
    for ano, t in ((2026, g26), (2022, g22)):
        linhas.append({"ano": ano, "cargo": "governador (lider da UF)", "candidato": "lider", **an.cauda(an.z_na_cidade(t, "lider"))})
    saida.csv(pd.DataFrame(linhas), "p8_caudas_dos_z_no_municipio.csv")

    # ---------------- A3: ultimo digito (controle)
    ld = []
    for ano, t, cols in ((2026, t26, ["flavio", "lula"]), (2022, t22, ["boso", "lula"]), (2018, t18, ["boso", "haddad"])):
        for c in cols:
            ld.append({"ano": ano, "candidato": c, **an.ultimo_digito(t[c])})
    saida.csv(pd.DataFrame(ld), "p8_ultimo_digito.csv")

    # ---------------- A1: impressao digital por UF
    f26 = an.impressao_digital(t26, "flavio").assign(ano=2026, candidato="flavio")
    l26 = an.impressao_digital(t26, "lula").assign(ano=2026, candidato="lula")
    f22 = an.impressao_digital(t22, "boso").assign(ano=2022, candidato="bolsonaro")
    l22 = an.impressao_digital(t22, "lula").assign(ano=2022, candidato="lula")
    fp = pd.concat([f26, l26, f22, l22])
    saida.csv(fp, "p8_impressao_digital_por_uf.csv")
    # a mudanca da correlacao 2022 -> 2026 por UF, contra a distribuicao entre UFs
    a = f26.set_index("uf")["spearman_comparecimento_x_pct"] - f22.set_index("uf")["spearman_comparecimento_x_pct"]
    b = l26.set_index("uf")["spearman_comparecimento_x_pct"] - l22.set_index("uf")["spearman_comparecimento_x_pct"]
    saida.anotar("p8_impressao_digital", {
        "mudanca_spearman_flavio_menos_boso_mediana": float(a.median()), "mudanca_spearman_lula_mediana": float(b.median()),
        "pct_secoes_no_canto_95_90_2026_max_uf": float(max(f26["pct_secoes_no_canto_95_90"].max(), l26["pct_secoes_no_canto_95_90"].max())),
        "pct_secoes_no_canto_95_90_2022_max_uf": float(max(f22["pct_secoes_no_canto_95_90"].max(), l22["pct_secoes_no_canto_95_90"].max())),
    })

    # ---------------- A4: municipios sinalizados nos tres testes
    m26 = an.municipios_tabela(t26, ["flavio", "lula"])
    m22 = an.municipios_tabela(t22, ["boso", "lula"])
    mg26 = an.municipios_tabela(g26.rename(columns={"lider": "gov"}), ["gov"])
    d = an.sinalizar_municipios(m26, m22, mg26, "flavio", "boso", "gov")
    mun = nacional.municipios()
    mun["mun_int"] = pd.to_numeric(mun["mun_cd"], errors="coerce")
    d = d.merge(mun[["uf", "mun_int", "nome", "capital"]], on=["uf", "mun_int"], how="left")
    saida.csv(d.sort_values("z_c"), "p8_municipios_testes.csv")
    saida.csv(d[d["a_explicar"]], "p8_municipios_a_explicar.csv")
    # placebo: o mesmo procedimento com Lula no lugar de Flavio (simetria) e com 2022 contra 2018
    d_l = an.sinalizar_municipios(m26.assign(pct_flavio=m26["pct_lula"]), m22.assign(pct_boso=m22["pct_lula"]), mg26, "flavio", "boso", "gov")
    d_22 = an.sinalizar_municipios(m22.rename(columns={"boso": "flavio", "pct_boso": "pct_flavio"}), an.municipios_tabela(t18, ["boso", "haddad"]),
                                   an.municipios_tabela(tabela_governador(s22, v22)[0].rename(columns={"lider": "gov"}), ["gov"]), "flavio", "boso", "gov")
    saida.anotar("p8_municipios", {
        "testados_2026": len(d), "sinal_a_historico": int(d.sinal_a.sum()), "sinal_b_outro_cargo": int(d.sinal_b.sum()), "sinal_c_comparecimento": int(d.sinal_c.sum()),
        "a_explicar_flavio": int(d.a_explicar.sum()),
        "a_explicar_lula_simetria": int(d_l.a_explicar.sum()), "sinal_a_lula": int(d_l.sinal_a.sum()), "sinal_b_lula": int(d_l.sinal_b.sum()), "sinal_c_lula": int(d_l.sinal_c.sum()),
        "placebo_2022_testados": len(d_22), "placebo_2022_a_explicar": int(d_22.a_explicar.sum()),
        "placebo_2022_sinal_a": int(d_22.sinal_a.sum()), "placebo_2022_sinal_b": int(d_22.sinal_b.sum()), "placebo_2022_sinal_c": int(d_22.sinal_c.sum()),
    })
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
