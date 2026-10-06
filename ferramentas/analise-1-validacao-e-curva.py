"""Analises 1: validacao dos dados (P4, T2.x) e curva da noite (P1, P2, P3).

Uso: python ferramentas/analise-1-validacao-e-curva.py [--ufs ac al ...] [--permutacoes 1000]
Saidas em resultados/ (ou na pasta de APURACAO_RESULTADOS, para ensaio).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import analises, coleta, curva, derivar, nacional, oficial, saida, tempo, validar  # noqa: E402


def total_secoes_oficial() -> dict:
    con = oficial.abrir()
    d = json.loads(con.execute("SELECT body FROM raw WHERE url=?", (oficial.url_uf("br", "1", oficial.ELE_FEDERAL),)).fetchone()[0])
    con.close()
    return {k: int(d["s"][k]) for k in ("ts", "st", "si", "sni")} | {"gerado_em": f"{d['dg']} {d['hg']}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ufs", nargs="*")
    ap.add_argument("--permutacoes", type=int, default=1000)
    ap.add_argument("--redigerir", action="store_true", help="refaz os parquet por UF antes de analisar")
    args = ap.parse_args()
    ufs = [u.lower() for u in args.ufs] if args.ufs else coleta.UFS
    for u in ufs:
        if args.redigerir or not (derivar.POR_UF / f"{u}-secoes.parquet").exists():
            print("derivando", u, derivar.derivar_uf(u), flush=True)

    secoes, votos = nacional.carregar(ufs)
    oficial_s = total_secoes_oficial()
    saida.anotar("oficial_secoes", oficial_s)

    # ---- situacao das secoes
    sit = (
        secoes.assign(
            situacao=np.where(secoes["agregada"], "agregada", np.where(secoes["bu_sha256"].notna(), "com_boletim", "sem_boletim"))
        )
        .groupby(["uf", "situacao"]).size().unstack(fill_value=0)
    )
    saida.csv(sit.reset_index(), "t26_situacao_das_secoes.csv")
    saida.anotar("secoes_proprias_com_boletim", int((secoes["bu_sha256"].notna()).sum()))
    saida.anotar("secoes_agregadas", int(secoes["agregada"].sum()))
    saida.anotar("secoes_sem_boletim", int(((~secoes["agregada"]) & secoes["bu_sha256"].isna()).sum()))
    saida.anotar("boletins_por_secao", secoes["n_boletins"].value_counts(dropna=True).to_dict())
    saida.anotar("erros_de_decodificacao", int(secoes.get("erro_decodificacao", pd.Series(dtype=object)).notna().sum()))

    # ---- T2.4 fuso
    fuso = tempo.testar_fuso(secoes)
    saida.csv(fuso, "t24_fuso_por_uf.csv")
    saida.anotar("t24_resumo", {"ufs": len(fuso), "decididas": fuso["fuso_decidido"].value_counts().to_dict(),
                                "viol_BRT_total": int(fuso["viol_BRT"].sum()), "secoes_testadas": int(fuso["secoes"].sum())})
    off = secoes["uf"].map(lambda u: tempo.OFFSET_PARA_BRASILIA.get(u, 0))
    local = secoes["uf"].map(dict(zip(fuso["uf"], fuso["fuso_decidido"]))).eq("LOCAL")
    secoes["recebido_brt"] = secoes["recebido"] + pd.to_timedelta(np.where(local, off, 0), unit="h")

    # ---- P4 validacao
    v_uf = validar.comparar(votos, secoes, "uf")
    saida.csv(v_uf, "p4_validacao_uf.csv")
    v_mun = validar.comparar(votos, secoes, "mun")
    saida.csv(v_mun, "p4_validacao_municipio.csv")
    ok = v_mun[v_mun.situacao == "ok"]
    saida.anotar("p4_uf", {"linhas": len(v_uf), "com_diferenca_em_candidato": int((v_uf.candidatos_com_diferenca > 0).sum()),
                           "votos_nominais_dif_total": int(v_uf.votos_nominais_dif_total.sum()),
                           "nulos_dif_nao_explicada": int((~v_uf.nulos_dif_explicada_por_so_boletim.astype(bool)).sum()),
                           "comparecimento_dif_total": int(v_uf.comparecimento_dif.abs().sum()),
                           "votos_so_no_boletim": int(v_uf.votos_so_no_boletim.sum())})
    saida.anotar("p4_municipio", {"linhas": len(v_mun), "oficial_indisponivel": int((v_mun.situacao != "ok").sum()),
                                  "com_diferenca_em_candidato": int((ok.candidatos_com_diferenca > 0).sum()),
                                  "votos_nominais_dif_total": int(ok.votos_nominais_dif_total.sum()),
                                  "nulos_dif_nao_explicada": int((~ok.nulos_dif_explicada_por_so_boletim.astype(bool)).sum()),
                                  "brancos_dif_total": int(ok.brancos_dif.abs().sum())})

    # ---- curva
    pres = nacional.presidente(secoes, votos)
    pres = pres.merge(secoes[["uf", "mun_cd", "zona", "secao", "recebido_brt"]], on=["uf", "mun_cd", "zona", "secao"], how="left", suffixes=("", "_x"))
    pres["recebido"] = pres["recebido_brt"]
    mun = nacional.municipios()
    pres = pres.merge(mun[["uf", "mun_cd", "capital"]], on=["uf", "mun_cd"], how="left")
    total = oficial_s["ts"] if not args.ufs else len(pres)  # ensaio com subconjunto de UFs usa o total do subconjunto
    cv = curva.curva(pres, total)
    cv_sai = cv.iloc[:: max(1, len(cv) // 5000)]
    saida.csv(cv_sai[["recebido", "n", "pct_secoes", "validos", f"pct_{curva.FLAVIO}", f"pct_{curva.LULA}", "margem_flavio_lula"]], "p3_curva_reconstruida.csv")

    pontos = pd.read_csv(RAIZ / "dados" / "pontos-da-tela.csv")
    cmp_ = curva.comparar_pontos(cv, pontos)
    # latencia entre o instante em que o corte foi recebido e a hora publicada
    hp = pd.to_datetime("2026-10-04 " + cmp_["hora_publicada"].where(cmp_["hora_publicada"].str.contains(":"), None), errors="coerce")
    cmp_["atraso_publicacao_min"] = (hp - pd.to_datetime(cmp_["recebido_no_corte"])).dt.total_seconds() / 60
    # quanto ja tinha chegado na hora publicada
    cmp_["pct_recebido_na_hora_publicada"] = [100 * (cv["recebido"] <= t).sum() / total if pd.notna(t) else np.nan for t in hp]
    cmp_["tela_nao_passa_do_recebido"] = cmp_["pct_secoes"] <= cmp_["pct_recebido_na_hora_publicada"] + 0.5
    saida.csv(cmp_, "p3_pontos_da_tela.csv")
    duas = cmp_[cmp_["fontes"].str.count(";") >= 1]
    saida.anotar("p3_resumo", {
        "pontos": len(cmp_), "encaixam": int(cmp_["encaixa"].sum()),
        "pontos_com_duas_ou_mais_fontes": len(duas), "duas_ou_mais_fontes_encaixam": int(duas["encaixa"].sum()),
        "melhor_erro_max": float(cmp_["melhor_erro_na_janela"].max()), "melhor_erro_mediano": float(cmp_["melhor_erro_na_janela"].median()),
        "pontos_que_nao_encaixam": cmp_.loc[~cmp_["encaixa"], "ponto"].tolist(),
    })

    # ---- P2: a parada
    d = analises.marcar_pct(pres, total)
    p_antes, p_depois = 64.81, 84.96
    corte1 = curva.no_pct(cv, p_antes)["recebido"]
    corte2 = curva.no_pct(cv, p_depois)["recebido"]
    janela = d[(d["recebido"] > pd.Timestamp("2026-10-04 19:06")) & (d["recebido"] <= pd.Timestamp("2026-10-04 20:08"))]
    saida.anotar("p2_parada", {
        "recebido_no_corte_64_81": corte1, "recebido_no_corte_84_96": corte2,
        "boletins_recebidos_19h06_20h08": int(len(janela)),
        "pct_das_secoes_recebido_19h06_20h08": 100 * len(janela) / total,
        "pct_recebido_ate_19h06": 100 * (d["recebido"] <= pd.Timestamp("2026-10-04 19:06")).sum() / total,
        "pct_recebido_ate_20h08": 100 * (d["recebido"] <= pd.Timestamp("2026-10-04 20:08")).sum() / total,
        "margem_do_lote_19h06_20h08": analises.margem(janela) if len(janela) else None,
    })
    saida.csv(analises.taxa_de_chegada(d, "5min").reset_index(), "p2_chegada_a_cada_5min.csv")

    # ---- P1: decomposicao
    base = d.merge(mun[["uf", "mun_cd", "capital"]].rename(columns={"capital": "cap"}), on=["uf", "mun_cd"], how="left")
    base["uf_capital"] = base["uf"] + np.where(base["cap"].fillna(False), "-capital", "-interior")
    resumo_dec = {}
    for chave in ("regiao", "uf", "uf_capital"):
        for rotulo, p0, p1 in (("64_81_a_100", p_antes, 100.0), ("64_81_a_84_96", p_antes, p_depois), ("84_96_a_100", p_depois, 100.0)):
            dec = analises.decompor(base, p0, p1, chave)
            saida.csv(dec, f"p1_decomposicao_{chave}_{rotulo}.csv")
            if chave in ("uf_capital", "regiao"):
                resumo_dec[f"{chave}_{rotulo}"] = {k: float(v) for k, v in dec.attrs.items()}
    saida.anotar("p1_decomposicao_uf_capital", resumo_dec)
    pcts = [10, 20, 30, 40, 50, 60, 64.81, 70, 80, 84.96, 90, 95, 99, 100]
    saida.csv(analises.vantagem_em(base, pcts), "p1_margem_por_pct_de_secoes.csv")
    saida.anotar("p1_troca_de_lideranca", analises.troca_de_lideranca(base))
    saida.csv(analises.chegada_por_regiao(base, "30min").reset_index(), "p1_chegada_por_regiao_30min.csv")

    # permutacoes
    grade = np.arange(1, 101, dtype=float)
    cd = base["dif"].cumsum().to_numpy()
    cvv = base["validos"].cumsum().to_numpy()
    idx = np.clip((grade / 100 * len(base)).astype(int) - 1, 0, len(base) - 1)
    real = 100 * cd[idx] / cvv[idx]
    out = {"grade_pct": grade, "real": real}
    for modo, flag in (("aleatoria", False), ("calendario_por_uf", True)):
        m = curva.permutacoes(pres, grade, n=args.permutacoes, por_uf=flag)
        out[f"{modo}_p05"], out[f"{modo}_p50"], out[f"{modo}_p95"] = np.percentile(m, [5, 50, 95], axis=0)
        fora = (real < out[f"{modo}_p05"]) | (real > out[f"{modo}_p95"])
        saida.anotar(f"p1_permutacao_{modo}", {"n": args.permutacoes, "pontos_da_curva_fora_da_faixa_5_95": int(fora.sum()), "de": len(grade),
                                              "maior_distancia_pontos": float(np.max(np.where(real > out[f"{modo}_p95"], real - out[f"{modo}_p95"], np.where(real < out[f"{modo}_p05"], out[f"{modo}_p05"] - real, 0))))})
    saida.csv(pd.DataFrame(out), "p1_permutacoes.csv")
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
