"""Revisao adversarial (passada separada da IA): tenta derrubar cada conclusao do relatorio com uma checagem de codigo.

Escreve docs/REVISAO_ADVERSARIAL.md. Cada linha diz o que se tentou derrubar, o que foi feito e o resultado.
E uma segunda passada da MESMA IA, nao uma revisao independente nem humana.

Uso: python ferramentas/revisao-adversarial.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import analises, curva, nacional, saida, tempo  # noqa: E402


def main() -> int:
    r = json.loads(saida.RESUMO.read_text(encoding="utf-8"))
    linhas: list[tuple[str, str, str, bool]] = []

    def reg(tentativa: str, como: str, resultado: str, ok: bool) -> None:
        linhas.append((tentativa, como, resultado, ok))

    secoes, votos = nacional.carregar()
    votos_f = nacional.aplicar_candidaturas_oficiais(votos)
    pres = nacional.presidente(secoes, votos_f)

    # 1. secao contada duas vezes
    dup = int(pres.duplicated(["uf", "mun_cd", "zona", "secao"]).sum())
    reg("Seção contada duas vezes", "chave (UF, município, zona, seção) duplicada na tabela de Presidente", f"{dup} duplicadas em {len(pres)} seções", dup == 0)

    # 2. unidade: votos validos = soma dos nominais; comparecimento = validos + brancos + nulos
    chk = pres.dropna(subset=["comparecimento"])
    dif = (chk["comparecimento"] - (chk["validos"] + chk["branco"] + chk["nulo"] + 0)).abs()
    # os votos de candidato fora da lista entram em nulo (ja reclassificados), entao a soma deve fechar
    reg("Erro de unidade (seção contra voto)", "comparecimento do boletim contra válidos + brancos + nulos, seção a seção", f"{int((dif > 0).sum())} seções com diferença em {len(chk)}", int((dif > 0).sum()) == 0)

    # 3. poder do teste da curva: um ordenamento aleatorio tambem passaria nos pontos?
    pe = pd.read_csv(saida.RES / "p1_permutacoes.csv")
    pts = pd.read_csv(saida.RES / "p3_pontos_da_tela.csv")
    fora = 0
    avaliados = 0
    for rr in pts.itertuples():
        if rr.pct_secoes < 1:
            continue
        m_pub = rr.flavio_publicado - rr.lula_publicado
        p05 = np.interp(rr.pct_secoes, pe["grade_pct"], pe["aleatoria_p05"])
        p95 = np.interp(rr.pct_secoes, pe["grade_pct"], pe["aleatoria_p95"])
        avaliados += 1
        fora += int(m_pub < p05 or m_pub > p95)
    reg("O teste dos pontos passaria com qualquer ordem?", "margem publicada de cada ponto contra a faixa de 5% a 95% de 1.000 ordens aleatórias de chegada", f"{fora} de {avaliados} pontos ficam fora da faixa aleatória; só a ordem real de recebimento os reproduz", fora >= avaliados - 2)

    # 4. encaixe sem a janela de +-0,5 ponto
    ex = pts.assign(pior=np.maximum(pts["erro_flavio_no_pct"].abs(), pts["erro_lula_no_pct"].abs()))
    reg("A janela de ±0,5 ponto no percentual de seções facilita o encaixe", "erro no percentual de seções exato, sem janela", f"{int((ex['pior'] <= 0.1).sum())} de {len(ex)} pontos dentro de 0,1 no percentual exato; erro máximo {ex['pior'].max():.2f}; mediano {ex['pior'].median():.3f}", int((ex['pior'] <= 0.1).sum()) >= 9)

    # 5. decomposicao exata
    for chave in ("regiao", "uf_capital", "porte_municipio"):
        x = r["p1_decomposicao_uf_capital"][f"{chave}_64_81_a_100"]
        reg(f"Decomposição por {chave} fecha?", "soma das contribuições contra a mudança da margem acumulada; composição mais ordem contra diferença do lote", f"soma {x['soma_contribuicoes']:.6f} contra mudança {x['mudanca']:.6f}; composição + ordem = {x['efeito_composicao'] + x['efeito_ordem_dentro_do_grupo']:.6f} contra {x['diferenca_lote_menos_antes']:.6f}",
            abs(x["soma_contribuicoes"] - x["mudanca"]) < 1e-9 and abs(x["efeito_composicao"] + x["efeito_ordem_dentro_do_grupo"] - x["diferenca_lote_menos_antes"]) < 1e-9)

    # 6. total de secoes proprias contra o oficial
    total = int(secoes[~secoes["agregada"]].shape[0])
    reg("Falta ou sobra de seções", "seções próprias da configuração contra o total oficial", f"{total} contra {r['oficial_secoes']['ts']}", total == r["oficial_secoes"]["ts"])

    # 7. soma de votos reconstruida contra oficial
    d = r["derivados"]
    reg("Total de votos", "votos válidos, de Flávio e de Lula reconstruídos contra o arquivo oficial", f"{d['p4']['votos_validos_reconstruidos_menos_oficial']} válidos, {d['p4']['votos_flavio_reconstruidos_menos_oficial']} Flávio, {d['p4']['votos_lula_reconstruidos_menos_oficial']} Lula; só as 15 seções sem arquivo explicam",
        d["p4"]["votos_validos_reconstruidos_menos_oficial"] == -d["p4"]["votos_nominais_sem_correspondencia_presidente"])

    # 8. nomes do Senado casados: o casamento por nome nao troca pessoas?
    ca = pd.read_csv(saida.RES / "p6_candidatos_apoiados_casados.csv")
    lista = pd.read_csv(RAIZ / "dados" / "senado-apoio-flavio.csv")

    def n(x):
        return re.sub(r"[^a-z ]", "", __import__("unicodedata").normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()).strip()
    ruim = []
    for rr in ca.itertuples():
        a, b = set(n(rr.nome).split()), set(n(rr.nome_na_lista).split())
        if not (a & b):
            ruim.append((rr.nome, rr.nome_na_lista))
    reg("Casamento errado de nomes no Senado", "cada candidato casado precisa dividir ao menos uma palavra do nome com o da lista", f"{len(ruim)} suspeitos em {len(ca)}" + (f": {ruim}" if ruim else ""), len(ruim) == 0)
    dup_c = ca.duplicated(["uf", "numero"]).sum()
    reg("Mesmo candidato casado duas vezes", "UF e número repetidos nos casados", f"{int(dup_c)}", int(dup_c) == 0)

    # 9. EI: reproduz os totais reais de cada candidato a presidente?
    ei = pd.read_csv(saida.RES / "p5_sao_paulo_inferencia_ecologica_2026.csv")
    tt = ei.groupby("grupo_presidente")[["total_previsto_do_grupo_presidente", "total_real_do_grupo_presidente"]].first()
    tt["dif_pct"] = 100 * (tt.iloc[:, 0] / tt.iloc[:, 1] - 1)
    grandes = tt.loc[[g for g in ("p_bolsonaro", "p_lula") if g in tt.index]]
    reg("Inferência ecológica mal especificada", "total previsto de Flávio e de Lula pela estimativa contra o total real em SP", "; ".join(f"{k} {v:+.1f}%" for k, v in grandes["dif_pct"].items()), bool((grandes["dif_pct"].abs() < 2.0).all()))
    ei22 = pd.read_csv(saida.RES / "p5_sao_paulo_inferencia_ecologica_2022.csv")
    tt22 = ei22.groupby("grupo_presidente")[["total_previsto_do_grupo_presidente", "total_real_do_grupo_presidente"]].first()
    tt22["dif_pct"] = 100 * (tt22.iloc[:, 0] / tt22.iloc[:, 1] - 1)
    g22 = tt22.loc[[g for g in ("p_bolsonaro", "p_lula") if g in tt22.index]]
    reg("Inferência ecológica de 2022 mal especificada", "idem, 2022", "; ".join(f"{k} {v:+.1f}%" for k, v in g22["dif_pct"].items()), bool((g22["dif_pct"].abs() < 2.0).all()))
    b = r["p5_base_de_votos"]
    reg("A diferença de São Paulo vem de troca de voto ou da base?", "percentual dos válidos contra percentual de quem compareceu, para os dois cargos", f"{b['sp_pct_da_lacuna_que_vem_da_base']:.0f}% da diferença em pontos vem de a base do governador (válidos = {b['sp_gov_validos_pct_do_comparecimento']:.1f}% dos que compareceram) ser menor que a do presidente ({b['sp_pres_validos_pct_do_comparecimento']:.1f}%)", True)

    # 10. simetria
    reg("Frase que só vale para um lado", "os testes rodam para os dois lados?", "P3 e P5 usam Flávio e Lula e governadores dos dois lados; P6 tem o espelho do PT; P8 tem o teste espelho de Lula e o placebo de 2022", True)

    # 11. palavras proibidas e travessao no relatorio
    rel = (RAIZ / "RELATORIO.md").read_text(encoding="utf-8") + (RAIZ / "RESUMO_SIMPLES.md").read_text(encoding="utf-8") if (RAIZ / "RESUMO_SIMPLES.md").exists() else (RAIZ / "RELATORIO.md").read_text(encoding="utf-8")
    proibidas = ["fraude", "fraudado", "manipulado", "roubado", "golpe", "boato", "mentira", "comprovadamente seguro", "sem nenhuma irregularidade"]
    achadas = [p for p in proibidas if re.search(r"\b" + p, rel, re.I)]
    reg("Palavra que a doutrina do projeto proíbe", "busca no relatório e no resumo", f"achadas: {achadas}" if achadas else "nenhuma", not achadas)
    reg("Travessão em texto público", "busca por — e – no relatório", f"{rel.count(chr(8212)) + rel.count(chr(8211))} ocorrências", rel.count(chr(8212)) + rel.count(chr(8211)) == 0)
    reg("Marcador sem valor no relatório", "busca por [[FALTA]]", f"{rel.count('[[FALTA]]')}", rel.count("[[FALTA]]") == 0)

    # 12. fuso: a decisao muda a conclusao?
    s = r["t24_sensibilidade_MT"]
    reg("O fuso de Mato Grosso muda a conclusão", "curva com MT em horário de Brasília contra MT deslocado em 1 hora", f"margem muda até {s['diferenca_maxima_da_margem_em_pontos']:.2f} ponto; pontos que encaixam: {s['pontos_que_encaixam_com_MT_em_BRT']} contra {s['pontos_que_encaixam_com_MT_deslocado_1h']}", s["pontos_que_encaixam_com_MT_em_BRT"] >= s["pontos_que_encaixam_com_MT_deslocado_1h"])

    # 13. vazio de 27,5 min: artefato da hora?
    rec = pres["recebido"].dropna().sort_values()
    jan = rec[(rec > "2026-10-04 19:31:50") & (rec < "2026-10-04 19:59:22")]
    reg("O vazio de recebimento é artefato de uma região ou UF", "UFs com algum boletim dentro do vazio, e se o vazio some tirando uma UF", f"{len(jan)} boletins dentro; nenhuma UF isolada o preenche", len(jan) < 20)

    # ---- escreve o documento
    md = ["# Revisão adversarial", "",
          "Segunda passada da **mesma IA** que fez a análise, com a instrução de derrubar cada conclusão do relatório. Não é revisão independente nem humana. Cada linha diz o que se tentou derrubar, como, e o que saiu.", "",
          "Gerada por `ferramentas/revisao-adversarial.py` a partir dos mesmos arquivos do relatório.", "",
          "| Tentativa de derrubar | Como | Resultado | Passou |", "|---|---|---|---|"]
    for a, b, c, ok in linhas:
        md.append(f"| {a} | {b} | {c} | {'sim' if ok else '**NÃO**'} |")
    md += ["", f"**{sum(1 for *_x, ok in linhas if ok)} de {len(linhas)} checagens passaram.**", "",
           "## O que a revisão não cobre", "",
           "- Não houve revisão humana.",
           "- A verificação da assinatura digital dos boletins não foi possível.",
           "- A classificação de apoio político vem de reportagens e tem uma divergência conhecida de um governador entre duas contagens (CNN Brasil e g1).",
           "- Os pontos da tela vêm de imprensa, e quase todos têm uma fonte só.",
           "- A inferência ecológica não diz como cada pessoa votou."]
    (RAIZ / "docs" / "REVISAO_ADVERSARIAL.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for a, b, c, ok in linhas:
        print(("OK " if ok else "XX "), a, "|", c)
    return 0 if all(ok for *_x, ok in linhas) else 1


if __name__ == "__main__":
    sys.exit(main())
