"""Analises 2: curva de 2022 (P7), governador x presidente (P5) e Senado x presidente (P6).

Uso: python ferramentas/analise-2-historico-uf-senado.py [--ufs ...]
Roda depois da coleta completa de 2026 e da derivacao do historico (ferramentas/derivar-historico.py).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import analises, coleta, curva, historico, nacional, saida, tempo, uf as ufm  # noqa: E402

FLAVIO, LULA = 22, 13


def pres_hist(ano: str, turno: str):
    ss, vv = historico.carregar(ano, turno)
    ss["agregada"] = False
    pres = nacional.presidente(ss, vv)
    return ss, vv, pres


def curva_2022():
    out = {}
    for turno in ("1", "2"):
        ss, vv, pres = pres_hist("2022", turno)
        total = len(pres)
        d = analises.marcar_pct(pres, total, "p22", "p13")  # Bolsonaro - Lula
        cvh = curva.curva(pres, total)
        pcts = [10, 20, 30, 40, 50, 60, 64.81, 70, 80, 84.96, 90, 95, 99, 100]
        marg = analises.vantagem_em(d, pcts)
        marg["turno"] = turno
        out[turno] = (marg, analises.troca_de_lideranca(d), d)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ufs", nargs="*")
    args = ap.parse_args()
    ufs = [u.lower() for u in args.ufs] if args.ufs else coleta.UFS
    secoes, votos26 = nacional.carregar(ufs)
    votos26 = nacional.aplicar_candidaturas_oficiais(votos26)
    saida.anotar("votos_de_candidato_fora_da_lista_oficial_como_nulos_2026", votos26.attrs["votos_reclassificados_como_nulos"])

    # ---------------------------------------------------------------- P7: 2022 contra 2026
    h = curva_2022()
    m22 = pd.concat([h["1"][0], h["2"][0]])
    saida.csv(m22, "p7_margem_2022_por_pct_de_secoes.csv")
    saida.anotar("p7_2022_turno1_troca", h["1"][1])
    saida.anotar("p7_2022_turno2_troca", h["2"][1])
    ss22, vv22, pres22 = pres_hist("2022", "1")
    d22 = h["1"][2]
    # o mesmo teste de fuso em 2022, como conferencia do metodo num ano com convencoes conhecidas
    f22 = tempo.testar_fuso(ss22.assign(agregada=False))
    saida.csv(f22, "p7_fuso_2022_por_uf.csv")
    saida.anotar("p7_fuso_2022", {"decididas": f22["fuso_decidido"].value_counts().to_dict(), "viol_BRT_total": int(f22["viol_BRT"].sum()), "secoes_testadas": int(f22["secoes"].sum())})
    # chegada por regiao em 2022
    d22["regiao"] = d22["uf"].map(__import__("apuracao.tempo", fromlist=["REGIAO"]).REGIAO)
    saida.csv(analises.chegada_por_regiao(d22, "30min").reset_index(), "p7_chegada_por_regiao_2022_30min.csv")
    ch22 = analises.taxa_de_chegada(d22, "5min")
    saida.csv(ch22.reset_index(), "p7_chegada_2022_a_cada_5min.csv")
    saida.anotar("p7_maiores_vazios_de_recebimento_2022_turno1", analises.maiores_vazios(d22["recebido"], "2022-10-02 17:00", "2022-10-02 22:00"))
    saida.anotar("p7_maiores_vazios_de_recebimento_2022_turno2", analises.maiores_vazios(h["2"][2]["recebido"], "2022-10-30 17:00", "2022-10-30 22:00"))
    saida.anotar("p7_pico_de_chegada_2022", {"boletins_por_5min_pico": int(ch22["boletins"].max()), "faixa_do_pico": ch22["boletins"].idxmax(), "boletins_por_minuto_no_pico": float(ch22["boletins"].max() / 5)})
    # decomposicao em 2022 (UF e regiao) a partir de 64,81% e entre 84,96 e 100, para comparar com 2026
    d22["uf_x"] = d22["uf"]
    for chave in ("regiao", "uf"):
        for rotulo, p0, p1 in (("64_81_a_100", 64.81, 100.0), ("84_96_a_100", 84.96, 100.0)):
            dec = analises.decompor(d22, p0, p1, chave)
            saida.csv(dec, f"p7_decomposicao_2022_{chave}_{rotulo}.csv")
            if chave == "regiao":
                saida.anotar(f"p7_decomposicao_2022_regiao_{rotulo}", {k: float(v) for k, v in dec.attrs.items()})

    # ---------------------------------------------------------------- P5: governador x presidente
    apoios = pd.read_csv(RAIZ / "dados" / "apoios.csv")
    ss22g, vv22g = historico.carregar("2022", "1")
    ss18g, vv18g = historico.carregar("2018", "1")
    ref = []
    conc = []
    for ano, vv in ((2026, votos26), (2022, vv22g), (2018, vv18g)):
        g = ufm.lacuna_governador_presidente(vv, apoios, ano)
        g = g[g.apoio != "divergente"].copy()
        g["venceu_no_1_turno"] = g["venceu_no_1_turno"].fillna(False)
        ref.append(g)
        for r in g.itertuples():
            if pd.isna(r.gov_numero) or pd.isna(r.candidato_apoiado):
                continue
            c = ufm.concentracao(vv, r.uf, int(r.gov_numero), int(r.candidato_apoiado))
            c["ano"] = ano
            conc.append(c)
    ref = pd.concat(ref, ignore_index=True)
    conc = pd.DataFrame(conc)
    ref = ref.merge(conc[["ano", "uf", "razao_liquido_bruto", "estavel", "fracao_das_secoes", "indice_top1pct"]], on=["ano", "uf"], how="left")
    saida.csv(ref, "p5_lacuna_governador_presidente.csv")

    classe = ref[(ref.ano.isin([2026, 2022])) & (ref.apoio != "neutro")]
    sp = ref[(ref.ano == 2026) & (ref.uf == "SP")].iloc[0]
    outras = classe[~((classe.ano == 2026) & (classe.uf == "SP"))]
    q05, q50, q95 = np.percentile(outras["lacuna_pontos"], [5, 50, 95])
    pct_sp = float(100 * (outras["lacuna_pontos"] < sp["lacuna_pontos"]).mean())
    saida.anotar("p5_classe_de_referencia", {
        "n": len(outras), "q05": q05, "mediana": q50, "q95": q95, "min": float(outras["lacuna_pontos"].min()), "max": float(outras["lacuna_pontos"].max()),
        "sp_2026_lacuna_pontos": float(sp["lacuna_pontos"]), "sp_percentil_na_classe": pct_sp,
        "sp_dentro_de_5_a_95": bool(q05 <= sp["lacuna_pontos"] <= q95),
        "sp_gov_pct": float(sp["gov_pct"]), "sp_pres_pct": float(sp["pres_pct"]),
        "positivas": int((outras["lacuna_pontos"] > 0).sum()), "negativas": int((outras["lacuna_pontos"] < 0).sum()),
    })
    # contabilidade da base (exata, sem inferencia): validos contra comparecimento
    q05c, q95c = np.percentile(outras["lacuna_pct_do_comparecimento"], [5, 95])
    saida.anotar("p5_base_de_votos", {
        "sp_gov_validos_pct_do_comparecimento": float(sp["gov_validos_pct_do_comparecimento"]), "sp_pres_validos_pct_do_comparecimento": float(sp["pres_validos_pct_do_comparecimento"]),
        "sp_tarcisio_pct_do_comparecimento": float(sp["gov_pct_do_comparecimento"]), "sp_flavio_pct_do_comparecimento": float(sp["pres_pct_do_comparecimento"]),
        "sp_lacuna_pct_do_comparecimento": float(sp["lacuna_pct_do_comparecimento"]), "sp_efeito_da_base_pontos": float(sp["efeito_da_base_pontos"]),
        "sp_pct_da_lacuna_que_vem_da_base": float(100 * sp["efeito_da_base_pontos"] / sp["lacuna_pontos"]),
        "sp_comparecimento": int(sp["comparecimento"]),
        "classe_lacuna_pct_do_comparecimento_q05": float(q05c), "classe_lacuna_pct_do_comparecimento_q95": float(q95c),
        "sp_percentil_na_classe_pelo_comparecimento": float(100 * (outras["lacuna_pct_do_comparecimento"] < sp["lacuna_pct_do_comparecimento"]).mean()),
        "sp_dentro_de_5_a_95_pelo_comparecimento": bool(q05c <= sp["lacuna_pct_do_comparecimento"] <= q95c),
        "efeito_da_base_mediano_na_classe": float(outras["efeito_da_base_pontos"].median()),
        "efeito_da_base_mediano_na_classe_2026": float(outras[outras.ano == 2026]["efeito_da_base_pontos"].median()),
        "efeito_da_base_mediano_na_classe_2022": float(outras[outras.ano == 2022]["efeito_da_base_pontos"].median()),
    })
    # sensibilidade: so quem apoiou Flavio/Bolsonaro; so 2026; e sem as UFs onde o governador nao esta no 1o turno
    for rotulo, sub in (("so_apoiadores_do_candidato_do_PL", outras[outras.candidato_apoiado == 22]), ("so_2026", outras[outras.ano == 2026]), ("so_2022", outras[outras.ano == 2022]), ("com_2018", pd.concat([outras, ref[ref.ano == 2018]]))):
        if len(sub) >= 5:
            a, b = np.percentile(sub["lacuna_pontos"], [5, 95])
            saida.anotar(f"p5_sensibilidade_{rotulo}", {"n": len(sub), "q05": a, "q95": b, "sp_dentro": bool(a <= sp["lacuna_pontos"] <= b)})
    # concentracao em SP (2026 e as referencias de 2022 em SP)
    cs = []
    for ano, vv, gnum, pnum, rot in (
        (2026, votos26, 10, 22, "Tarcisio x Flavio"), (2026, votos26, 13, 13, "Haddad x Lula"),
        (2022, vv22g, 10, 22, "Tarcisio x Bolsonaro"), (2022, vv22g, 13, 13, "Haddad x Lula"),
    ):
        c = ufm.concentracao(vv, "SP", gnum, pnum)
        c.update(ano=ano, comparacao=rot)
        cs.append(c)
    cs = pd.DataFrame(cs)
    saida.csv(cs, "p5_sao_paulo_concentracao.csv")

    # SP por municipio: 2026 contra 2022
    def mun_gap(vv, gnum, pnum):
        g = ufm.por_secao(vv[vv.uf == "SP"], 3, gnum, "g").groupby(level=["uf", "mun_cd"]).sum()
        p = ufm.por_secao(vv[vv.uf == "SP"], 1, pnum, "p").groupby(level=["uf", "mun_cd"]).sum()
        vg = vv[(vv.uf == "SP") & (vv.cargo == 3) & (vv.tipo == 1)].groupby(["uf", "mun_cd"]).votos.sum()
        vp = vv[(vv.uf == "SP") & (vv.cargo == 1) & (vv.tipo == 1)].groupby(["uf", "mun_cd"]).votos.sum()
        t = pd.concat([g, p, vg.rename("vg"), vp.rename("vp")], axis=1).fillna(0)
        t["gap"] = 100 * t["g"] / t["vg"] - 100 * t["p"] / t["vp"]
        t = t.reset_index()
        t["mun_int"] = pd.to_numeric(t["mun_cd"], errors="coerce")
        return t[["mun_int", "g", "p", "vg", "vp", "gap"]]
    a26 = mun_gap(votos26, 10, 22)
    a22 = mun_gap(vv22g, 10, 22)
    j = a26.merge(a22, on="mun_int", suffixes=("_26", "_22"))
    mun = nacional.municipios()
    mun["mun_int"] = pd.to_numeric(mun["mun_cd"], errors="coerce")
    j = j.merge(mun[mun.uf == "SP"][["mun_int", "nome", "capital"]], on="mun_int", how="left")
    saida.csv(j, "p5_sao_paulo_por_municipio.csv")
    rho, p = stats.spearmanr(j["gap_26"], j["gap_22"])
    cap = j[j.capital == True]  # noqa: E712
    saida.anotar("p5_sao_paulo_municipios", {
        "municipios": len(j), "spearman_gap2026_x_gap2022": float(rho), "p_valor": float(p),
        "gap_mediano_2026": float(j["gap_26"].median()), "gap_mediano_2022": float(j["gap_22"].median()),
        "gap_2026_sao_paulo_capital": float(cap["gap_26"].iloc[0]) if len(cap) else None,
        "gap_2022_sao_paulo_capital": float(cap["gap_22"].iloc[0]) if len(cap) else None,
        "pct_municipios_com_tarcisio_acima_de_flavio": float(100 * (j["gap_26"] > 0).mean()),
        "pct_municipios_com_tarcisio_acima_de_bolsonaro_2022": float(100 * (j["gap_22"] > 0).mean()),
    })

    # ---------------------------------------------------------------- P5-b: de onde vem a diferenca em Sao Paulo
    cand26 = nacional.candidatos()
    nome_curto = {n: nm.replace("ESCRITOR ", "").split()[-1].lower() for n, nm in cand26.items()}
    for ano, vv, rot in ((2026, votos26, "2026"), (2022, vv22g, "2022")):
        c = ufm.contabilidade(vv, "SP").copy()
        c["candidato"] = [cand26.get(int(n), str(n)) if (ano == 2026 and cg == 1) else str(int(n)) for n, cg in zip(c["numero"], c["cargo"])]
        saida.csv(c, f"p5_sao_paulo_contabilidade_{rot}.csv")
    top26 = [n for n, pct in ufm.totais_uf(votos26[votos26.uf == "SP"]).query("cargo == 1").sort_values("pct", ascending=False)[["numero", "pct"]].itertuples(index=False) if pct >= 1.0]
    pres26 = {nome_curto.get(int(n), str(int(n))): int(n) for n in top26}
    ei26 = ufm.inferencia_ecologica(votos26, "SP", {"tarcisio": 10, "haddad": 13}, pres26, rodadas=200)
    ei22 = ufm.inferencia_ecologica(vv22g, "SP", {"tarcisio": 10, "haddad": 13, "rodrigo": 45}, {"bolsonaro": 22, "lula": 13, "simone": 15, "ciro": 12}, rodadas=200)
    saida.csv(ei26, "p5_sao_paulo_inferencia_ecologica_2026.csv")
    saida.csv(ei22, "p5_sao_paulo_inferencia_ecologica_2022.csv")
    def pega(ei, g, p):
        r = ei[(ei.grupo_governador == g) & (ei.grupo_presidente == p)].iloc[0]
        return {"fracao": float(r.fracao_estimada), "p05": float(r.p05), "p95": float(r.p95)}
    saida.anotar("p5_sao_paulo_ei_2026", {f"tarcisio_para_{p.split('_',1)[1]}": pega(ei26, "g_tarcisio", p) for p in ei26.grupo_presidente.unique()})
    saida.anotar("p5_sao_paulo_ei_2026_haddad", {f"haddad_para_{p.split('_',1)[1]}": pega(ei26, "g_haddad", p) for p in ei26.grupo_presidente.unique()})
    saida.anotar("p5_sao_paulo_ei_2022", {f"tarcisio_para_{p.split('_',1)[1]}": pega(ei22, "g_tarcisio", p) for p in ei22.grupo_presidente.unique()})

    # ---------------------------------------------------------------- P6: Senado x presidente
    sen = ufm.senado_vs_presidente(votos26, [u.upper() for u in ufs if u != "zz"])
    saida.csv(sen, "p6_senado_vs_presidente_2026.csv")
    achados, perdidos = ufm.casar_apoio_flavio([u.upper() for u in ufs if u != "zz"])
    saida.csv(achados[["uf", "numero", "nome", "partido", "votos", "pct", "eleito", "nome_na_lista"]], "p6_candidatos_apoiados_casados.csv")
    saida.csv(perdidos, "p6_candidatos_apoiados_nao_casados.csv")
    saida.anotar("p6_casamento", {"na_lista": 47, "casados": len(achados), "nao_casados": len(perdidos)})

    # referencia: 2018 (dois votos) e 2022 (um voto), definicao por partido
    def razao_historica(ano, vv, flav, lula_num, partido_pres, partido_lula, votos_por_eleitor):
        tot = ufm.totais_uf(vv)
        linhas = []
        for uf_ in sorted(tot.uf.unique()):
            if uf_ == "ZZ":
                continue
            s = tot[(tot.uf == uf_) & (tot.cargo == 5)]
            p = tot[(tot.uf == uf_) & (tot.cargo == 1)]
            if s.empty or p.empty:
                continue
            F = p[p.numero == flav].pct.sum()
            L = p[p.numero == lula_num].pct.sum()
            elei = s.votos.sum() / votos_por_eleitor
            # candidatos ao Senado do partido: numero comeca com o numero do partido (3 digitos, ex. 22x)
            def media(num_partido):
                c = s[s.numero // 10 == num_partido]
                return (100 * c.votos.sum() / len(c) / elei) if len(c) else np.nan, len(c)
            m_pl, n_pl = media(partido_pres)
            m_pt, n_pt = media(partido_lula)
            linhas.append({"ano": ano, "uf": uf_, "flavio_ou_bolsonaro_pct": F, "lula_ou_haddad_pct": L, "n_cand_partido_pres": n_pl, "n_cand_partido_lula": n_pt,
                           "razao_partido_pres": m_pl / F if F else np.nan, "razao_partido_lula": m_pt / L if L else np.nan})
        return pd.DataFrame(linhas)
    # 2018: Bolsonaro 17 (PSL); 2022: Bolsonaro 22 (PL). Lula/Haddad 13 (PT).
    h18 = razao_historica(2018, vv18g, 17, 13, 17, 13, 2)
    h22 = razao_historica(2022, vv22g, 22, 13, 22, 13, 1)
    saida.csv(pd.concat([h18, h22]), "p6_referencia_historica_por_partido.csv")
    hist_all = pd.concat([h18, h22])
    sen["razao_pl_media_sobre_flavio"] = sen["razao_pl_media_sobre_flavio"]
    r_hist = hist_all["razao_partido_pres"].dropna()
    q05, q50, q95 = np.percentile(r_hist, [5, 50, 95]) if len(r_hist) else (np.nan,) * 3
    r26 = sen["razao_pl_media_sobre_flavio"].dropna()
    sen["razao_apoio_flavio_media_sobre_flavio"] = sen["razao_apoio_flavio_media_sobre_flavio"]
    acima = sen["razao_pl_media_sobre_flavio"] > q95
    abaixo = sen["razao_pl_media_sobre_flavio"] < q05
    apoio_acima = sen["razao_apoio_flavio_media_sobre_flavio"] > q95
    apoio_abaixo = sen["razao_apoio_flavio_media_sobre_flavio"] < q05
    sen["a_explicar_literal"] = (acima & apoio_acima) | (abaixo & apoio_abaixo)
    sen["fora_do_intervalo_historico_pl"] = np.where(acima, "acima", np.where(abaixo, "abaixo", ""))
    saida.csv(sen, "p6_senado_vs_presidente_2026.csv")
    saida.anotar("p6_criterio_literal", {
        "ufs_fora_do_intervalo_pelo_PL_acima": sen.loc[acima, "uf"].tolist(), "ufs_fora_do_intervalo_pelo_PL_abaixo": sen.loc[abaixo, "uf"].tolist(),
        "ufs_a_explicar_pelo_criterio_literal": sen.loc[sen["a_explicar_literal"], "uf"].tolist(),
        "dessas_com_senador_do_pl_eleito": sen.loc[sen["a_explicar_literal"] & (sen["pl_eleitos"] > 0), "uf"].tolist(),
    })
    saida.anotar("p6_resumo", {
        "razao_historica_partido_do_presidente": {"n": len(r_hist), "q05": q05, "mediana": q50, "q95": q95},
        "razao_2026_pl": {"n": len(r26), "q05": float(np.percentile(r26, 5)) if len(r26) else None, "mediana": float(r26.median()) if len(r26) else None, "q95": float(np.percentile(r26, 95)) if len(r26) else None},
        "ufs_2026_fora_do_intervalo_historico": sen.loc[(sen["razao_pl_media_sobre_flavio"] < q05) | (sen["razao_pl_media_sobre_flavio"] > q95), "uf"].tolist(),
    })
    # ---- P6 (b): onde o PL elegeu senadores contra quem liderou a eleicao presidencial; e o alinhamento dentro da UF
    sen["flavio_liderou"] = sen["flavio_pct"] > sen["lula_pct"]
    cruz = pd.crosstab(sen["flavio_liderou"].map({True: "Flavio na frente", False: "Lula na frente ou empate"}), sen["pl_eleitos"].clip(upper=2).map({0: "0 senador do PL", 1: "1 senador do PL", 2: "2 senadores do PL"}))
    saida.csv(cruz.reset_index(), "p6_senadores_do_pl_por_quem_liderou.csv")
    pl_total = int(sen["pl_eleitos"].sum())
    saida.anotar("p6_senadores_do_pl", {
        "total_eleitos": pl_total,
        "em_ufs_com_flavio_na_frente": int(sen.loc[sen["flavio_liderou"], "pl_eleitos"].sum()),
        "em_ufs_com_lula_na_frente_ou_empate": int(sen.loc[~sen["flavio_liderou"], "pl_eleitos"].sum()),
        "ufs_com_flavio_na_frente": int(sen["flavio_liderou"].sum()),
        "ufs_com_flavio_na_frente_e_sem_senador_do_pl": sen.loc[sen["flavio_liderou"] & (sen["pl_eleitos"] == 0), "uf"].tolist(),
        "ufs_com_lula_na_frente_ou_empate": sen.loc[~sen["flavio_liderou"], "uf"].tolist(),
    })
    saida.anotar("p6_senadores_do_pt", {"total_eleitos": int(sen["pt_eleitos"].sum()), "em_ufs_com_lula_na_frente_ou_empate": int(sen.loc[~sen["flavio_liderou"], "pt_eleitos"].sum()), "em_ufs_com_flavio_na_frente": int(sen.loc[sen["flavio_liderou"], "pt_eleitos"].sum())})
    com_pl = sen.dropna(subset=["pl_media_por_candidato_pct_eleitores"])
    r_uf = stats.spearmanr(com_pl["flavio_pct"], com_pl["pl_media_por_candidato_pct_eleitores"])[0]
    com_pt = sen.dropna(subset=["pt_media_por_candidato_pct_eleitores"])
    r_uf_pt = stats.spearmanr(com_pt["lula_pct"], com_pt["pt_media_por_candidato_pct_eleitores"])[0]
    saida.anotar("p6_entre_ufs", {"spearman_flavio_x_candidatos_do_pl": float(r_uf), "n_pl": len(com_pl), "spearman_lula_x_candidatos_do_pt": float(r_uf_pt), "n_pt": len(com_pt),
                                  "mediana_razao_pl": float(com_pl["razao_pl_media_sobre_flavio"].median()), "mediana_razao_pt": float(com_pt["razao_pt_media_sobre_lula"].median())})
    alin = []
    for ano, vv, npres, nlula, ve, rot in ((2026, votos26, 22, 13, 2, "2026"), (2022, vv22g, 22, 13, 1, "2022"), (2018, vv18g, 17, 13, 2, "2018")):
        for nome, npart, npc in (("partido_do_candidato_que_liderou_o_1_turno", npres, npres), ("PT", 13, 13)):
            a = ufm.alinhamento_municipal(vv, npart, npc, ve)
            a["ano"], a["partido"] = ano, nome if nome == "PT" else ("PL" if ano != 2018 else "PSL")
            alin.append(a)
    alin = pd.concat(alin, ignore_index=True)
    saida.csv(alin, "p6_alinhamento_entre_municipios_por_uf.csv")
    resumo_alin = {}
    for (ano, partido), g in alin.groupby(["ano", "partido"]):
        resumo_alin[f"{ano}_{partido}"] = {"ufs": len(g), "mediana_spearman": float(g["spearman_pres_x_senado"].median()), "ufs_com_spearman_acima_de_0_8": int((g["spearman_pres_x_senado"] > 0.8).sum())}
    saida.anotar("p6_alinhamento_municipal", resumo_alin)
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
