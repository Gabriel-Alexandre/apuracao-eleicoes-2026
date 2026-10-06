"""Monta RELATORIO.md e RESUMO_SIMPLES.md a partir dos textos-modelo e dos resultados.

Marcadores aceitos nos modelos (docs/RELATORIO.modelo.md e docs/RESUMO_SIMPLES.modelo.md):
  {{chave.subchave}}                    numero (ou texto) do RESUMO.json; falha se a chave nao existir
  {{chave.subchave|n=1}}                formata com 1 casa decimal e virgula
  {{chave.subchave|pct}}                formata como percentual (so acrescenta o sinal, sem multiplicar)
  {{tabela:arquivo.csv|colunas=a,b,c|linhas=10|ordem=coluna|desc}}   tabela em Markdown a partir de um CSV
  {{figura:arquivo.png|legenda}}        imagem

Nenhum numero do relatorio e digitado a mao: o que nao esta no RESUMO.json ou num CSV nao entra.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import nacional, saida  # noqa: E402


def br(x, casas=None):
    if isinstance(x, bool):
        return "sim" if x else "não"
    if isinstance(x, int):
        return f"{x:,}".replace(",", ".")
    if isinstance(x, float):
        if casas is None:
            casas = 0 if abs(x) >= 1000 else 2
        s = f"{x:,.{casas}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    return str(x)


def pega(resumo, caminho):
    cur = resumo
    for parte in caminho.split("."):
        if isinstance(cur, dict) and parte in cur:
            cur = cur[parte]
        elif isinstance(cur, list) and parte.isdigit() and int(parte) < len(cur):
            cur = cur[int(parte)]
        else:
            raise KeyError(f"chave ausente no RESUMO.json: {caminho}")
    return cur


def tabela(arquivo, opcoes):
    df = pd.read_csv(saida.RES / arquivo, dtype={"Ano": str})
    if "colunas" in opcoes:
        df = df[opcoes["colunas"].split(",")]
    if "ordem" in opcoes:
        df = df.sort_values(opcoes["ordem"], ascending="desc" not in opcoes)
    if "linhas" in opcoes:
        df = df.head(int(opcoes["linhas"]))
    casas = int(opcoes.get("casas", 2))
    cab = "| " + " | ".join(df.columns) + " |\n|" + "|".join("---" for _ in df.columns) + "|\n"
    corpo = ""
    for _, r in df.iterrows():
        cel = []
        for v in r:
            if isinstance(v, float):
                cel.append("" if pd.isna(v) else br(float(v), casas))
            elif isinstance(v, (int,)) and not isinstance(v, bool):
                cel.append(br(int(v)))
            else:
                cel.append("" if pd.isna(v) else str(v))
        corpo += "| " + " | ".join(cel) + " |\n"
    return cab + corpo


def renderizar(modelo: Path, destino: Path, resumo: dict) -> list[str]:
    texto = modelo.read_text(encoding="utf-8")
    faltas: list[str] = []

    def troca(m):
        corpo = m.group(1).strip()
        try:
            if corpo.startswith("tabela:"):
                partes = corpo[len("tabela:"):].split("|")
                opcoes = {}
                for p in partes[1:]:
                    k, _, v = p.partition("=")
                    opcoes[k.strip()] = v.strip()
                return tabela(partes[0].strip(), opcoes)
            if corpo.startswith("figura:"):
                partes = corpo[len("figura:"):].split("|")
                return f"![{partes[1].strip() if len(partes) > 1 else ''}](resultados/figuras/{partes[0].strip()})"
            partes = corpo.split("|")
            v = pega(resumo, partes[0].strip())
            fmt = {}
            for p in partes[1:]:
                k, _, val = p.partition("=")
                fmt[k.strip()] = val.strip()
            if "abs" in fmt and isinstance(v, (int, float)):
                v = abs(v)
            if "x100" in fmt and isinstance(v, (int, float)):
                v = 100 * v
            if "join" in fmt and isinstance(v, list):
                return ", ".join(str(x) for x in v)
            if "hora" in fmt and isinstance(v, str) and "T" in v:
                return v[11:19]
            if "hm" in fmt and isinstance(v, str) and "T" in v:
                return v[11:16]
            if "n" in fmt and isinstance(v, (int, float)):
                return br(float(v), int(fmt["n"]))
            if isinstance(v, float):
                return br(v)
            return br(v)
        except Exception as e:  # noqa: BLE001
            faltas.append(f"{corpo}: {e}")
            return "[[FALTA]]"

    saida_txt = re.sub(r"\{\{(.+?)\}\}", troca, texto)
    destino.write_text(saida_txt, encoding="utf-8")
    return faltas


def derivar_numeros() -> None:
    """Percentuais derivados e tabelas legiveis. Tudo vem de RESUMO.json e dos CSV; nada e digitado a mao."""
    import numpy as np

    from apuracao import oficial

    r = json.loads(saida.RESUMO.read_text(encoding="utf-8"))
    dec = r["p1_decomposicao_uf_capital"]
    der: dict = {"p1": {}, "p4": {}, "oficial": {}}
    for chave in ("regiao", "uf", "uf_capital", "capital_ou_interior", "porte_municipio", "tamanho_secao"):
        x = dec[f"{chave}_64_81_a_100"]
        der["p1"][f"pct_explicado_pela_composicao_{chave}"] = 100 * x["efeito_composicao"] / x["diferenca_lote_menos_antes"]
    x22 = r["p7_decomposicao_2022_regiao_64_81_a_100"]
    der["p1"]["pct_explicado_pela_composicao_regiao_2022"] = 100 * x22["efeito_composicao"] / x22["diferenca_lote_menos_antes"]
    base = r["p1_permutacao_aleatoria"]["distancia_mediana_pontos"]
    for k in ("calendario_por_uf", "calendario_por_uf_e_capital", "calendario_por_uf_capital_e_porte"):
        der["p1"][f"reducao_da_distancia_mediana_{k}"] = 100 * (1 - r[f"p1_permutacao_{k}"]["distancia_mediana_pontos"] / base)
    der["p1"]["queda_do_pico_ao_fim_pontos"] = r["p1_resumo"]["perda_do_pico_ao_fim"]
    # oficial
    con = oficial.abrir()
    d = json.loads(con.execute("SELECT body FROM raw WHERE url=?", (oficial.url_uf("br", "1", oficial.ELE_FEDERAL),)).fetchone()[0])
    con.close()
    cand = {int(c["n"]): int(c["vap"]) for a in d["carg"][0]["agr"] for p in a["par"] for c in p["cand"]}
    der["oficial"] = {"validos": int(d["v"]["vv"]), "flavio": cand[22], "lula": cand[13], "comparecimento": int(d["e"]["c"]), "secoes_totalizadas_pct": d["s"]["pst"]}
    uf = pd.read_csv(saida.RES / "p4_validacao_uf.csv")
    pres = uf[uf.cargo == 1]
    der["p4"]["votos_nominais_sem_correspondencia_presidente"] = int(pres["votos_nominais_dif_total"].sum())
    der["p4"]["pct_dos_validos_sem_correspondencia_presidente"] = 100 * der["p4"]["votos_nominais_sem_correspondencia_presidente"] / der["oficial"]["validos"]
    der["p4"]["votos_validos_reconstruidos_menos_oficial"] = int(r["p1_resumo"]["total_de_votos_validos_reconstruidos"] - der["oficial"]["validos"])
    der["p4"]["votos_flavio_reconstruidos_menos_oficial"] = int(r["p1_resumo"]["votos_flavio_reconstruidos"] - der["oficial"]["flavio"])
    der["p4"]["votos_lula_reconstruidos_menos_oficial"] = int(r["p1_resumo"]["votos_lula_reconstruidos"] - der["oficial"]["lula"])
    der["p4"]["votos_validos_a_menos"] = -der["p4"]["votos_validos_reconstruidos_menos_oficial"]
    der["p4"]["votos_flavio_a_menos"] = -der["p4"]["votos_flavio_reconstruidos_menos_oficial"]
    der["p4"]["votos_lula_a_menos"] = -der["p4"]["votos_lula_reconstruidos_menos_oficial"]
    mun = pd.read_csv(saida.RES / "p4_validacao_municipio.csv", dtype={"mun_cd": str})
    com_dif = mun[(mun.candidatos_com_diferenca > 0) | (~mun.nulos_dif_explicada_por_so_boletim)]
    der["p4"]["municipios_com_diferenca"] = com_dif.groupby(["uf", "mun_cd"]).ngroups
    der["p4"]["municipios_com_diferenca_lista"] = sorted({f"{a}-{b}" for a, b in zip(com_dif.uf, com_dif.mun_cd)})
    der["p4"]["linhas_municipio_e_cargo_exatas"] = int(len(mun) - len(com_dif))
    der["p4"]["pct_linhas_municipio_e_cargo_exatas"] = 100 * der["p4"]["linhas_municipio_e_cargo_exatas"] / len(mun)
    pts = pd.read_csv(saida.RES / "p3_pontos_da_tela.csv").set_index("ponto")
    der["p3"] = {
        "p07_votos_flavio_reconstruidos_menos_publicados": int(pts.loc["P07", "dif_votos_flavio"]), "p07_votos_lula_reconstruidos_menos_publicados": int(pts.loc["P07", "dif_votos_lula"]),
        "p07_pct_flavio_da_diferenca": 100 * float(pts.loc["P07", "dif_votos_flavio"]) / float(pts.loc["P07", "votos_flavio_publicado"]),
        "p13_margem_publicada": int(pts.loc["P13", "margem_votos_publicada"]), "p13_margem_reconstruida": int(pts.loc["P13", "margem_votos_reconstruida_no_pct"]),
        "p02_flavio_publicado": float(pts.loc["P02", "flavio_publicado"]), "p02_flavio_refeito": float(pts.loc["P02", "flavio_reconstruido_no_pct"]),
        "p02_lula_publicado": float(pts.loc["P02", "lula_publicado"]), "p02_lula_refeito": float(pts.loc["P02", "lula_reconstruido_no_pct"]),
    }
    par = r["p2_parada"]
    der["p2"] = {"janela_bruta_pct_das_secoes": par["pct_das_secoes_recebido_19h06_20h08"], "tela_acrescentou_pct": 84.96 - 64.81,
                 "diferenca_vs_janela_bruta": par["pct_das_secoes_recebido_19h06_20h08"] - (84.96 - 64.81),
                 "vazio_minutos_vs_maior_2022": r["p2_maiores_vazios_de_recebimento_2026"][0]["minutos"] / r["p7_maiores_vazios_de_recebimento_2022_turno1"][0]["minutos"]}
    lr = pd.read_csv(saida.RES / "p5_lacuna_governador_presidente.csv")
    sp_l = float(lr[(lr.ano == 2026) & (lr.uf == "SP")]["lacuna_pontos"].iloc[0])
    der["p5_ref"] = {"posicao_de_sp_entre_os_governadores_aliados_de_flavio_em_2026_da_maior_diferenca": int((lr[(lr.ano == 2026) & (lr.apoio == "Flavio")]["lacuna_pontos"] > sp_l).sum()) + 1,
                     "governadores_aliados_de_flavio_em_2026": int(((lr.ano == 2026) & (lr.apoio == "Flavio")).sum()),
                     "maior_diferenca_de_aliado_de_bolsonaro_em_2022": float(lr[(lr.ano == 2022) & (lr.apoio == "Bolsonaro")]["lacuna_pontos"].max())}
    sp = pd.read_csv(saida.RES / "p5_sao_paulo_por_municipio.csv")
    der["p5"] = {
        "gap_2026_minimo_entre_municipios": float(sp["gap_26"].min()), "gap_2026_maximo_entre_municipios": float(sp["gap_26"].max()),
        "gap_2026_p05": float(sp["gap_26"].quantile(0.05)), "gap_2026_p95": float(sp["gap_26"].quantile(0.95)),
        "gap_2022_p05": float(sp["gap_22"].quantile(0.05)), "gap_2022_p95": float(sp["gap_22"].quantile(0.95)),
        "pct_dos_votos_validos_de_governador_em_municipios_com_gap_entre_5_e_15": float(100 * sp.loc[(sp.gap_26 >= 5) & (sp.gap_26 <= 15), "vg_26"].sum() / sp["vg_26"].sum()),
        "diferenca_de_votos_dos_boletins": int(sp["g_26"].sum() - sp["p_26"].sum()),
    }
    # numeros de SP no arquivo oficial do TSE (a fonte que quem confere vai abrir)
    _con = oficial.abrir()
    def _of(url):
        return json.loads(_con.execute("SELECT body FROM raw WHERE url=?", (url,)).fetchone()[0])
    _g = _of(oficial.url_uf("sp", "3", oficial.ELE_ESTADUAL))
    _p = _of(oficial.url_uf("sp", "1", oficial.ELE_FEDERAL))
    _con.close()
    def _votos(d, nome):
        for ag in d["carg"][0]["agr"]:
            for pa in ag["par"]:
                for c in pa["cand"]:
                    if c["nmu"].upper().startswith(nome):
                        return int(c["vap"])
    _tar, _fla = _votos(_g, "TARC"), _votos(_p, "FLAVIO")
    der["p5"]["diferenca_de_votos_tarcisio_menos_flavio"] = _tar - _fla
    der["p5"]["votos_a_menos_nos_boletins_que_no_oficial_na_diferenca"] = (_tar - _fla) - der["p5"]["diferenca_de_votos_dos_boletins"]
    der["p5"]["oficial_gov_validos_pct_do_total_do_cargo"] = float(str(_g["v"]["pvvc"]).replace(",", "."))
    der["p5"]["oficial_pres_validos_pct_do_total_do_cargo"] = float(str(_p["v"]["pvvc"]).replace(",", "."))
    der["p5"]["oficial_gov_total_do_cargo"] = int(_g["v"]["tv"])
    # contagens e listas que o texto usa
    sit = pd.read_csv(saida.RES / "t26_situacao_das_secoes.csv")
    sem = r["secoes_sem_boletim"]
    der["dados"] = {"secoes_sem_arquivo_publicado": int(sem - r["oficial_secoes"]["sni"]), "secoes_com_um_boletim": int(r["boletins_por_secao"]["1.0"]), "secoes_com_mais_de_um_boletim": int(sum(v for k, v in r["boletins_por_secao"].items() if k != "1.0"))}
    from apuracao import coleta as _co, derivar as _dv
    for _uf in ("MG", "SP"):
        _t = pd.read_parquet(_dv.POR_UF / f"{_uf.lower()}-secoes.parquet")
        _t = _t[(~_t["agregada"]) & _t["bu_sha256"].isna()]
        der["dados"][f"n_{_uf.lower()}"] = int(len(_t))
        der["dados"][f"lista_{_uf.lower()}"] = "; ".join(f"município {m}, zona {int(z)}, seção {int(sc)}" for m, z, sc in zip(_t["mun_cd"], _t["zona"], _t["secao"]))
    busa = 0
    busa_uf = {}
    for _uf in _co.UFS:
        _t = pd.read_parquet(_dv.POR_UF / f"{_uf}-secoes.parquet")
        n = int((_t["tipo_boletim"] == "busa").sum()) if "tipo_boletim" in _t else 0
        if n:
            busa_uf[_uf.upper()] = n
        busa += n
    der["dados"]["boletins_busa_total"] = busa
    der["dados"]["boletins_busa_por_uf"] = busa_uf
    nc = pd.read_csv(saida.RES / "p6_candidatos_apoiados_nao_casados.csv")
    der["p6"] = {"ufs_com_lula_na_frente_ou_empate": len(r["p6_senadores_do_pl"]["ufs_com_lula_na_frente_ou_empate"]),
                 "nao_casado": "; ".join(f"{a}, {b}" for a, b in zip(nc["candidato"], nc["uf"])),
                 "a_explicar_n": len(r["p6_criterio_literal"]["ufs_a_explicar_pelo_criterio_literal"]),
                 "a_explicar_sem_senador_do_pl": [u for u in r["p6_criterio_literal"]["ufs_a_explicar_pelo_criterio_literal"] if u not in r["p6_criterio_literal"]["dessas_com_senador_do_pl_eleito"]]}
    ref_all = pd.read_csv(saida.RES / "p5_lacuna_governador_presidente.csv")
    ref_cls = ref_all[(ref_all.ano.isin([2026, 2022])) & (ref_all.apoio != "neutro")]
    der["p5_n"] = {"casos_total": int(len(ref_cls)), "casos_2026": int((ref_cls.ano == 2026).sum()), "casos_2022": int((ref_cls.ano == 2022).sum()),
                   "comparados_com_sp": int(len(ref_cls)) - 1,
                   "todas_as_sensibilidades_com_sp_dentro": bool(all(r[k]["sp_dentro"] for k in r if k.startswith("p5_sensibilidade_")))}
    cont = pd.read_csv(saida.RES / "p5_sao_paulo_contabilidade_2026.csv")
    cont22 = pd.read_csv(saida.RES / "p5_sao_paulo_contabilidade_2022.csv")
    def pct_gov(df, num):
        return float(df[(df.cargo == 3) & (df.numero == num)]["pct"].iloc[0])
    def pct_pres(df, num):
        return float(df[(df.cargo == 1) & (df.numero == num)]["pct"].iloc[0])
    der["sp"] = {"haddad_pct": pct_gov(cont, 13), "lula_pct": pct_pres(cont, 13), "rodrigo_garcia_2022_pct": pct_gov(cont22, 45),
                 "pct_municipios_com_tarcisio_abaixo_de_bolsonaro_em_2022": 100 - r["p5_sao_paulo_municipios"]["pct_municipios_com_tarcisio_acima_de_bolsonaro_2022"]}
    cc = pd.read_csv(saida.RES / "p5_sao_paulo_concentracao.csv")
    t_f = cc[(cc.ano == 2026) & (cc.comparacao == "Tarcisio x Flavio")].iloc[0]
    der["sp"].update({"fracao_das_secoes_para_metade_da_diferenca": 100 * float(t_f["fracao_das_secoes"]), "top1pct_parcela_da_diferenca": 100 * float(t_f["top1pct_parcela_do_fluxo_positivo"]),
                      "top1pct_parcela_dos_votos": 100 * float(t_f["top1pct_parcela_dos_votos"])})
    ei = r["p5_sao_paulo_ei_2026"]
    der["sp"]["ei_tarcisio_para_cury_caiado_e_santos"] = 100 * (ei["tarcisio_para_cury"]["fracao"] + ei["tarcisio_para_caiado"]["fracao"] + ei["tarcisio_para_santos"]["fracao"])
    der["sp"]["ei_tarcisio_para_flavio_pct"] = 100 * ei["tarcisio_para_bolsonaro"]["fracao"]
    votos_t = float(cont[(cont.cargo == 3) & (cont.numero == 10)]["votos"].iloc[0])
    der["sp"]["votos_de_tarcisio"] = int(votos_t)
    der["sp"]["votos_de_tarcisio_que_nao_foram_para_flavio_estimado"] = int(votos_t * (1 - ei["tarcisio_para_bolsonaro"]["fracao"]))
    ei_csv = pd.read_csv(saida.RES / "p5_sao_paulo_inferencia_ecologica_2026.csv")
    bn = ei_csv[(ei_csv.grupo_governador == "g_branco_nulo") & (ei_csv.grupo_presidente == "p_bolsonaro")].iloc[0]
    der["sp"]["flavio_votos_de_quem_anulou_ou_deixou_em_branco_para_governador_estimado"] = int(bn["fracao_estimada"] * bn["votos_do_grupo_governador"])
    der["sp"]["ei_tarcisio_para_flavio_ic"] = f"{100*ei['tarcisio_para_bolsonaro']['p05']:.1f} a {100*ei['tarcisio_para_bolsonaro']['p95']:.1f}".replace(".", ",")
    der["sp"]["ei_haddad_para_lula_pct"] = 100 * r["p5_sao_paulo_ei_2026_haddad"]["haddad_para_lula"]["fracao"]
    der["sp"]["ei_2022_tarcisio_para_bolsonaro_pct"] = 100 * r["p5_sao_paulo_ei_2022"]["tarcisio_para_bolsonaro"]["fracao"]
    m22 = pd.read_csv(saida.RES / "p7_margem_2022_por_pct_de_secoes.csv")
    def m22v(turno, pc):
        return float(m22[(m22.turno.astype(str) == turno) & (m22.pct_secoes == pc)]["margem"].iloc[0])
    der["p7"] = {"t1_margem_em_10pct": m22v("1", 10.0), "t2_margem_em_10pct": m22v("2", 10.0),
                 "t1_margem_final": r["p7_2022_turno1_troca"]["margem_final_pontos"], "t2_margem_final": r["p7_2022_turno2_troca"]["margem_final_pontos"]}
    m26 = pd.read_csv(saida.RES / "p1_margem_por_pct_de_secoes.csv").set_index("pct_secoes")["margem"]
    der["p1"]["queda_por_ponto_de_secoes_de_20_a_64_81"] = float((m26[20.0] - m26[64.81]) / (64.81 - 20.0))
    der["p1"]["queda_por_ponto_de_secoes_de_64_81_a_84_96"] = float((m26[64.81] - m26[84.96]) / (84.96 - 64.81))
    der["p1"]["queda_por_ponto_de_secoes_de_84_96_a_100"] = float((m26[84.96] - m26[100.0]) / (100.0 - 84.96))
    rg = pd.read_csv(saida.RES / "p1_chegada_e_margem_por_grupo.csv")
    rg = rg[rg.tipo_de_grupo == "regiao"].set_index("grupo")
    der["p1"]["sul_pct_ate_19h06"] = float(rg.loc["Sul", "pct_ate_19h06"])
    der["p1"]["nordeste_pct_ate_19h06"] = float(rg.loc["Nordeste", "pct_ate_19h06"])
    pt_ = pd.read_csv(saida.RES / "p3_pontos_da_tela.csv").set_index("ponto")
    der["p3"]["p02_pct_secoes"] = float(pt_.loc["P02", "pct_secoes"])
    cau = pd.read_csv(saida.RES / "p8_caudas_dos_z_no_municipio.csv")
    def cauda(ano, cargo, cand):
        return float(cau[(cau.ano == ano) & (cau.cargo.str.startswith(cargo)) & (cau.candidato == cand)]["pct_abs_gt_4"].iloc[0])
    der["p8"] = {"flavio_2026_menor_ou_igual_a_bolsonaro_2022": cauda(2026, "presidente", "flavio") <= cauda(2022, "presidente", "boso"),
                 "lula_2026_menor_ou_igual_a_lula_2022": cauda(2026, "presidente", "lula") <= cauda(2022, "presidente", "lula"),
                 "governador_menor_que_presidente_2026": cauda(2026, "governador", "lider") < min(cauda(2026, "presidente", "flavio"), cauda(2026, "presidente", "lula")),
                 "governador_menor_que_presidente_2022": cauda(2022, "governador", "lider") < min(cauda(2022, "presidente", "boso"), cauda(2022, "presidente", "lula"))}

    # asserções: se uma frase do texto deixar de ser verdadeira, o relatório não é gerado
    def ok(cond, msg):
        if not cond:
            raise AssertionError("frase do relatório deixou de ser verdadeira: " + msg)
    ok(r["p6_senadores_do_pl"]["em_ufs_com_lula_na_frente_ou_empate"] == 0, "o PL nao elegeu senador onde Lula liderou")
    ok(r["p6_senadores_do_pl"]["total_eleitos"] == r["p6_senadores_do_pl"]["em_ufs_com_flavio_na_frente"], "todos os senadores do PL estao em UFs com Flavio na frente")
    ok(r["p6_senadores_do_pl"]["ufs_com_flavio_na_frente_e_sem_senador_do_pl"] == ["ES"], "so o Espirito Santo teve Flavio na frente sem senador do PL")
    ok(r["p6_senadores_do_pt"]["em_ufs_com_flavio_na_frente"] == 1, "1 senador do PT em UF com Flavio na frente (Minas Gerais)")
    ok(r["p5_classe_de_referencia"]["sp_dentro_de_5_a_95"], "SP entre os percentis 5 e 95")
    ok(der["p5_n"]["todas_as_sensibilidades_com_sp_dentro"], "a conclusao de SP se mantem nas sensibilidades")
    ok(der["p5_ref"]["posicao_de_sp_entre_os_governadores_aliados_de_flavio_em_2026_da_maior_diferenca"] == 1, "SP e a maior diferenca entre aliados de Flavio em 2026")
    ok(r["p5_sao_paulo_municipios"]["pct_municipios_com_tarcisio_acima_de_flavio"] == 100.0, "Tarcisio a frente de Flavio em todos os municipios")
    ok(r["p3_resumo"]["duas_ou_mais_fontes_encaixam"] == r["p3_resumo"]["pontos_com_duas_ou_mais_fontes"], "todos os pontos com 2+ fontes encaixam")
    ok(r["p3_resumo"]["pontos_que_nao_encaixam"] == ["P02"], "so o ponto P02 nao encaixa")
    ok(der["p2"]["diferenca_vs_janela_bruta"] > 2.0, "a janela bruta passa do limite de 2 pontos")
    ok(all(der["p8"].values()), "afirmacoes sobre as caudas dos z")
    ok(r["p8_municipios"]["a_explicar_flavio"] == 0 and r["p8_municipios"]["a_explicar_lula_simetria"] == 0 and r["p8_municipios"]["placebo_2022_a_explicar"] == 0, "nenhum municipio passou nos tres testes")
    ok(r["p1_resumo"]["menor_margem_depois_de_1pct"] > 0, "Flavio sempre a frente depois do primeiro 1% das secoes")
    ok(set(r["p6_criterio_literal"]["dessas_com_senador_do_pl_eleito"]) == {"DF", "MS", "RS", "SP"}, "UFs do criterio do Senado com senador do PL")
    ok(der["p6"]["a_explicar_sem_senador_do_pl"] == ["AM", "BA", "CE", "PE"], "UFs do criterio do Senado sem senador do PL")
    ok(r["t24_resumo"]["decididas"].get("BRT") == 27, "27 unidades em BRT")
    ok(der["p4"]["municipios_com_diferenca_lista"] == ["MG-41335", "SP-63134"], "os dois municipios com diferenca")
    ok(busa_uf == {"MG": 2, "ZZ": 29}, "31 boletins busa: 2 em MG e 29 no exterior")
    ok(der["dados"]["secoes_sem_arquivo_publicado"] == 15 and der["dados"]["n_mg"] == 3 and der["dados"]["n_sp"] == 12, "15 secoes sem arquivo: 3 em MG e 12 em SP")
    saida.anotar("derivados", der)

    # tabelas legiveis
    T = saida.RES / "tabelas"
    T.mkdir(exist_ok=True)
    pt = pd.read_csv(saida.RES / "p3_pontos_da_tela.csv")
    pd.DataFrame({
        "Ponto": pt["ponto"], "% das seções": pt["pct_secoes"], "Flávio publicado": pt["flavio_publicado"], "Flávio refeito": pt["flavio_reconstruido_no_pct"],
        "Lula publicado": pt["lula_publicado"], "Lula refeito": pt["lula_reconstruido_no_pct"], "Melhor erro na janela (pontos)": pt["melhor_erro_na_janela"],
        "Encaixa": pt["encaixa"].map({True: "sim", False: "não"}), "Fontes": pt["fontes"].str.count(";") + 1,
    }).to_csv(T / "pontos_da_tela.csv", index=False)
    g = pd.read_csv(saida.RES / "p1_chegada_e_margem_por_grupo.csv")
    rg = g[g.tipo_de_grupo == "regiao"].copy()
    pd.DataFrame({"Região": rg["grupo"], "Seções": rg["secoes"], "Já recebidas às 19h06 (%)": rg["pct_ate_19h06"], "Mediana de recebimento": rg["recebido_mediana"].str[11:16],
                  "Margem final, Flávio menos Lula (pontos)": rg["margem_final_flavio_lula"]}).sort_values("Mediana de recebimento").to_csv(T / "regioes.csv", index=False)
    ref = pd.read_csv(saida.RES / "p5_lacuna_governador_presidente.csv")
    ref = ref[(ref.ano.isin([2026, 2022])) & (ref.apoio != "neutro")].sort_values(["ano", "lacuna_pontos"], ascending=[False, False])
    pd.DataFrame({"Ano": ref["ano"].astype(str), "UF": ref["uf"], "Governador": ref["governador"], "Apoio declarado": ref["apoio"], "Governador (% dos válidos)": ref["gov_pct"],
                  "Presidente apoiado (% dos válidos)": ref["pres_pct"], "Diferença (pontos)": ref["lacuna_pontos"]}).to_csv(T / "lacuna_governador_presidente.csv", index=False)
    sn = pd.read_csv(saida.RES / "p6_senado_vs_presidente_2026.csv")
    pd.DataFrame({"UF": sn["uf"], "Flávio (%)": sn["flavio_pct"], "Lula (%)": sn["lula_pct"], "PL: candidatos": sn["pl_n"], "PL: eleitos": sn["pl_eleitos"],
                  "PL: voto por candidato (% dos eleitores)": sn["pl_media_por_candidato_pct_eleitores"], "Apoiados por Flávio: eleitos": sn["apoio_flavio_eleitos"],
                  "PT: eleitos": sn["pt_eleitos"], "PL fora da faixa histórica": sn["fora_do_intervalo_historico_pl"].fillna("")}).to_csv(T / "senado.csv", index=False)
    ca = pd.read_csv(saida.RES / "p8_caudas_dos_z_no_municipio.csv")
    pd.DataFrame({"Ano": ca["ano"].astype(str), "Cargo": ca["cargo"].str.replace(" (lider da UF)", " (líder da UF)", regex=False), "Candidato": ca["candidato"], "Seções": ca["n"],
                  "% com |z| acima de 4": ca["pct_abs_gt_4"], "% com |z| acima de 6": ca["pct_abs_gt_6"]}).to_csv(T / "caudas.csv", index=False)
    def ei_tabela(arq, grupos, rot_pres):
        e = pd.read_csv(saida.RES / arq)
        linhas = []
        for gname, rot in grupos:
            sub = e[e.grupo_governador == gname].set_index("grupo_presidente")
            linha = {"Voto para governador": rot}
            for pg, pr in rot_pres.items():
                if pg in sub.index:
                    r_ = sub.loc[pg]
                    linha[pr] = f"{100*r_.fracao_estimada:.1f}% ({100*r_.p05:.1f} a {100*r_.p95:.1f})".replace(".", ",")
            linhas.append(linha)
        return pd.DataFrame(linhas)
    ei_tabela("p5_sao_paulo_inferencia_ecologica_2026.csv", [("g_tarcisio", "Tarcísio"), ("g_haddad", "Haddad")],
              {"p_bolsonaro": "Flávio", "p_lula": "Lula", "p_caiado": "Caiado", "p_cury": "Cury", "p_santos": "Renan Santos", "p_outros_nominais": "Outros", "p_branco_nulo": "Branco ou nulo"}) if False else None
    cand26 = nacional.candidatos()
    ei26 = pd.read_csv(saida.RES / "p5_sao_paulo_inferencia_ecologica_2026.csv")
    rot26 = {f"p_{c}": c for c in sorted(set(x.split("_", 1)[1] for x in ei26.grupo_presidente))}
    ei_tabela("p5_sao_paulo_inferencia_ecologica_2026.csv", [("g_tarcisio", "Tarcísio"), ("g_haddad", "Haddad")], {k: v.capitalize() if v not in ("branco_nulo", "outros_nominais") else {"branco_nulo": "Branco ou nulo", "outros_nominais": "Outros"}[v] for k, v in rot26.items()}).to_csv(T / "ei_sp_2026.csv", index=False)
    ei22 = pd.read_csv(saida.RES / "p5_sao_paulo_inferencia_ecologica_2022.csv")
    rot22 = {f"p_{c}": c for c in sorted(set(x.split("_", 1)[1] for x in ei22.grupo_presidente))}
    ei_tabela("p5_sao_paulo_inferencia_ecologica_2022.csv", [("g_tarcisio", "Tarcísio"), ("g_haddad", "Haddad"), ("g_rodrigo", "Rodrigo Garcia")], {k: v.capitalize() if v not in ("branco_nulo", "outros_nominais") else {"branco_nulo": "Branco ou nulo", "outros_nominais": "Outros"}[v] for k, v in rot22.items()}).to_csv(T / "ei_sp_2022.csv", index=False)
    cont = pd.read_csv(saida.RES / "p5_sao_paulo_contabilidade_2026.csv")
    cont["candidato"] = cont["candidato"].where(cont["cargo"] == 1, "gov " + cont["numero"].astype(int).astype(str))
    un = pd.read_csv(saida.RES / "p4_validacao_uf.csv")
    cargo_nome = {1: "Presidente", 3: "Governador", 5: "Senador"}
    v = un.groupby("cargo").agg(linhas=("uf", "size"), com_diferenca=("candidatos_com_diferenca", lambda x: int((x > 0).sum())), votos_sem_correspondencia=("votos_nominais_dif_total", "sum")).reset_index()
    v["cargo"] = v["cargo"].map(cargo_nome)
    v.columns = ["Cargo", "UFs comparadas", "UFs com diferença", "Votos sem correspondência"]
    v.to_csv(T / "validacao_uf.csv", index=False)


def main() -> int:
    derivar_numeros()
    resumo = json.loads(saida.RESUMO.read_text(encoding="utf-8"))
    ok = True
    for modelo, destino in (("RELATORIO.modelo.md", "RELATORIO.md"), ("RESUMO_SIMPLES.modelo.md", "RESUMO_SIMPLES.md")):
        m = RAIZ / "docs" / modelo
        if not m.exists():
            print("sem modelo:", m)
            continue
        faltas = renderizar(m, RAIZ / destino, resumo)
        print(destino, "ok" if not faltas else f"{len(faltas)} marcadores sem valor")
        for f in faltas:
            print("  FALTA:", f)
        ok = ok and not faltas
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
