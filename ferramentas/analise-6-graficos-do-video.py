"""Graficos em 1920x1080 para o video. Le so os CSV de resultados/ e o RESUMO.json (nunca recalcula nada).

Uso: python ferramentas/analise-6-graficos-do-video.py
Saida: resultados/figuras/video/*.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import saida  # noqa: E402

OUT = saida.FIG / "video"
BG, FG, MUTED, GRID = "#0A1630", "#F8FAFC", "#94A3B8", "#1E2D4F"
FLAVIO, LULA, ACENTO, TARC, NEUTRO = "#22D3EE", "#F59E0B", "#FFE500", "#A78BFA", "#64748B"
plt.rcParams.update({
    "figure.figsize": (19.2, 10.8), "figure.dpi": 100, "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID,
    "font.size": 24, "axes.titlesize": 38, "axes.titleweight": "bold", "axes.labelsize": 26, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 1.2, "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "DejaVu Sans", "legend.frameon": False, "legend.fontsize": 24,
})
RES = json.loads((saida.RES / "RESUMO.json").read_text(encoding="utf-8"))
FONTE = "Fonte: boletins de urna e resultados oficiais do TSE · github.com/Gabriel-Alexandre/apuracao-eleicoes-2026"


def v(x, n=1):
    """Numero com virgula decimal."""
    return f"{x:.{n}f}".replace(".", ",")


def milhar(x):
    return f"{int(round(x)):,}".replace(",", ".")


def novo(titulo, sub=None):
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.14)
    fig.text(0.08, 0.945, titulo, fontsize=40, fontweight="bold", va="center", ha="left")
    if sub:
        fig.text(0.08, 0.895, sub, fontsize=24, color=MUTED, va="center", ha="left")
    fig.text(0.08, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    return fig, ax


def salvar(fig, nome):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / nome)
    plt.close(fig)


def hh(ax, d0="2026-10-04 17:00", d1="2026-10-04 23:00"):
    ax.set_xlim(pd.Timestamp(d0), pd.Timestamp(d1))
    ticks = pd.date_range(d0, d1, freq="1h")
    ax.set_xticks(ticks)
    ax.set_xticklabels([t.strftime("%Hh") for t in ticks])


PARADA = (pd.Timestamp("2026-10-04 19:06"), pd.Timestamp("2026-10-04 20:08"))


def g01_noite_em_uma_linha():
    cv = pd.read_csv(saida.RES / "p3_curva_reconstruida.csv", parse_dates=["recebido"])
    cv = cv[cv.pct_secoes >= 1.0]
    fig, ax = novo("A noite de 4 de outubro em uma linha", "Vantagem de Flávio sobre Lula, em pontos dos votos válidos, conforme os boletins chegavam")
    ax.axvspan(*PARADA, color=ACENTO, alpha=0.10, lw=0)
    ax.plot(cv.recebido, cv.margem_flavio_lula, color=FG, lw=5)
    ax.axhline(0, color=MUTED, lw=1.5)
    hh(ax, "2026-10-04 17:10", "2026-10-04 23:00")
    ax.set_ylim(-1.5, 14)
    ax.set_ylabel("Flávio menos Lula (pontos)")
    p = RES["p1_resumo"]
    T = pd.Timestamp
    pts = [(T(p["recebido_no_pico"]), p["margem_de_pico"], f"{v(p['margem_de_pico'])} pontos no pico,\ncom 14% das seções", (T("2026-10-04 17:52"), 12.2)),
           (T("2026-10-04 19:04:09"), 49.58 - 42.25, "tela de 19h06:\n64,81% das seções, 7,3 pontos", (T("2026-10-04 17:20"), 3.4)),
           (T("2026-10-04 19:59:30"), 48.47 - 43.49, "tela de 20h08:\n84,96% das seções, 5,0 pontos", (T("2026-10-04 20:12"), 7.0)),
           (cv.recebido.iloc[-1], p["margem_final"], f"{v(p['margem_final'])} pontos no fim", (T("2026-10-04 21:35"), 4.0))]
    for t, y, txt, (tx, ty) in pts:
        ax.scatter([t], [y], s=260, color=ACENTO, zorder=5, edgecolor=BG, linewidth=3)
        ax.annotate(txt, (t, y), xytext=(tx, ty), fontsize=24, color=FG, ha="left",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.5))
    ax.text(pd.Timestamp("2026-10-04 19:37"), 0.4, "tela de Presidente\nparada", ha="center", fontsize=24, color=ACENTO)
    salvar(fig, "g01_a_noite_em_uma_linha.png")


def g03_quem_chegou_primeiro():
    g = pd.read_csv(saida.RES / "p1_chegada_e_margem_por_grupo.csv")
    g = g[g.tipo_de_grupo == "regiao"].copy()
    g = g.sort_values("pct_ate_19h06", ascending=True)
    fig, (a, b) = plt.subplots(1, 2, sharey=True)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.80, bottom=0.14, wspace=0.10)
    fig.text(0.04, 0.945, "Quem terminou de contar primeiro", fontsize=40, fontweight="bold", va="center", ha="left")
    fig.text(0.04, 0.895, "Cada região: quanto já tinha chegado às 19h06 e para quem ela votou no fim", fontsize=24, color=MUTED, va="center", ha="left")
    fig.text(0.04, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    y = np.arange(len(g))
    a.barh(y, g.pct_ate_19h06, color=NEUTRO, height=0.6)
    for yy, x in zip(y, g.pct_ate_19h06):
        a.text(x - 2, yy, f"{v(x, 0)}%", ha="right", va="center", fontsize=26, color=FG, fontweight="bold")
    a.set_yticks(y); a.set_yticklabels(g.grupo, fontsize=28, color=FG)
    a.set_xlim(0, 100); a.set_title("já recebido às 19h06 (%)", fontsize=26, pad=18, color=FG)
    a.grid(axis="y", visible=False)
    cores = [FLAVIO if m > 0 else LULA for m in g.margem_final_flavio_lula]
    b.barh(y, g.margem_final_flavio_lula, color=cores, height=0.6)
    b.axvline(0, color=MUTED, lw=1.5)
    for yy, x in zip(y, g.margem_final_flavio_lula):
        b.text(x + (1.2 if x > 0 else -1.2), yy, ("+" if x > 0 else "") + v(x), ha="left" if x > 0 else "right", va="center", fontsize=26, fontweight="bold")
    b.set_xlim(-42, 38); b.set_title("resultado: Flávio menos Lula", fontsize=26, pad=18, color=FG)
    b.grid(axis="y", visible=False)
    salvar(fig, "g03_quem_chegou_primeiro.png")


def g04_embaralhando():
    pe = pd.read_csv(saida.RES / "p1_permutacoes.csv")
    fig, ax = novo("E se a ordem de chegada fosse outra?", "Mesmas urnas, mesmos votos. Só muda a ordem em que elas entram na soma")
    ax.fill_between(pe.grade_pct, pe.aleatoria_p05, pe.aleatoria_p95, color=NEUTRO, alpha=0.55, lw=0)
    ax.fill_between(pe.grade_pct, pe.calendario_por_uf_p05, pe.calendario_por_uf_p95, color=ACENTO, alpha=0.35, lw=0)
    ax.plot(pe.grade_pct, pe.real, color=FG, lw=6)
    ax.set_xlim(0, 100); ax.set_ylim(0, 12.5)
    ax.set_xlabel("% das seções somadas"); ax.set_ylabel("Flávio menos Lula (pontos)")
    ax.text(38, 3.1, "ordem sorteada entre todas as urnas:\nquase uma reta, perto do resultado final", color="#CBD5E1", fontsize=24, ha="left")
    ax.text(30, 11.2, "ordem real", color=FG, fontsize=28, fontweight="bold")
    ax.text(40, 8.9, "calendário real de cada estado, urnas sorteadas\ndentro dele: explica a maior parte da queda,\nmas não toda", color=ACENTO, fontsize=24)
    salvar(fig, "g04_embaralhando_a_ordem.png")


def g05_a_tela_parada():
    t = pd.read_csv(saida.RES / "p2_chegada_a_cada_5min.csv", parse_dates=["faixa"])
    cv = pd.read_csv(saida.RES / "p3_curva_reconstruida.csv", parse_dates=["recebido"])
    pt = pd.read_csv(saida.RES / "p3_pontos_da_tela.csv")
    fig, (a, b) = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [1.1, 1]})
    fig.subplots_adjust(left=0.10, right=0.97, top=0.80, bottom=0.12, hspace=0.12)
    fig.text(0.04, 0.945, "A tela parou, os boletins continuaram chegando", fontsize=40, fontweight="bold", va="center", ha="left")
    fig.text(0.04, 0.895, "Boletins recebidos a cada 5 minutos, e % das seções já recebidas", fontsize=24, color=MUTED, va="center", ha="left")
    fig.text(0.04, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    for ax in (a, b):
        ax.axvspan(*PARADA, color=ACENTO, alpha=0.10, lw=0)
    a.bar(t.faixa, t.boletins, width=pd.Timedelta(minutes=4.5), color=NEUTRO, align="edge")
    a.axvspan(pd.Timestamp("2026-10-04 19:31:50"), pd.Timestamp("2026-10-04 19:59:22"), color=LULA, alpha=0.20, lw=0)
    a.text(pd.Timestamp("2026-10-04 19:45"), 17000, "27 min\nsem nenhum\nboletim", ha="center", fontsize=24, color=LULA, fontweight="bold")
    a.annotate("20.171 boletins\nem 6 minutos", (pd.Timestamp("2026-10-04 20:03"), 15500), xytext=(pd.Timestamp("2026-10-04 20:35"), 19500), fontsize=24, color=FG, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.5))
    a.set_ylabel("boletins por 5 min", fontsize=22)
    b.plot(cv.recebido, cv.pct_secoes, color=FG, lw=5)
    hora = pd.to_datetime("2026-10-04 " + pt.hora_publicada.where(pt.hora_publicada.astype(str).str.contains(":"), None), errors="coerce")
    ok = hora.notna()
    b.scatter(hora[ok], pt.pct_secoes[ok], s=210, color=ACENTO, zorder=5, edgecolor=BG, linewidth=2.5, label="o que a tela mostrou (imprensa)")
    b.set_ylabel("% das seções", fontsize=22); b.set_ylim(0, 105)
    b.legend(loc="lower right", fontsize=22)
    hh(b)
    salvar(fig, "g05_a_tela_parada.png")


def g06_tela_contra_boletins():
    pt = pd.read_csv(saida.RES / "p3_pontos_da_tela.csv")
    fig, ax = novo("A curva refeita bate com a imprensa", "Cada ponto é um percentual divulgado na noite, contra o que a soma dos boletins dá no mesmo ponto")
    lim = [38, 52]
    ax.plot(lim, lim, color=MUTED, lw=2, ls="--")
    ax.scatter(pt.flavio_publicado, pt.flavio_reconstruido_no_pct, s=260, color=FLAVIO, label="Flávio", edgecolor=BG, linewidth=2)
    ax.scatter(pt.lula_publicado, pt.lula_reconstruido_no_pct, s=260, color=LULA, label="Lula", edgecolor=BG, linewidth=2)
    ax.set_xlim(38, 52); ax.set_ylim(38, 52)
    ax.set_xlabel("publicado na noite (% dos votos válidos)"); ax.set_ylabel("refeito com os boletins (%)")
    ax.legend(loc="upper left")
    r = RES["p3_resumo"]
    ax.text(51.6, 38.6, f"{r['encaixam']} de {r['pontos']} pontos encaixam\nerro mediano: {v(r['melhor_erro_mediano'] , 2)} ponto", ha="right", fontsize=28, color=ACENTO, fontweight="bold")
    salvar(fig, "g06_imprensa_contra_boletins.png")


def g07_2026_contra_2022():
    a26 = pd.read_csv(saida.RES / "p1_margem_por_pct_de_secoes.csv")
    a22 = pd.read_csv(saida.RES / "p7_margem_2022_por_pct_de_secoes.csv")
    fig, ax = novo("A vantagem inicial também encolheu em 2022", "Diferença do candidato que começou na frente, conforme as seções chegavam")
    ax.axhline(0, color=MUTED, lw=1.5)
    ax.plot(a26.pct_secoes, a26.margem, color=FLAVIO, lw=6, marker="o", ms=11, label="2026, 1º turno: Flávio menos Lula")
    t1 = a22[a22.turno == 1]; t2 = a22[a22.turno == 2]
    ax.plot(t1.pct_secoes, t1.margem, color=FG, lw=5, marker="s", ms=10, label="2022, 1º turno: Bolsonaro menos Lula")
    ax.plot(t2.pct_secoes, t2.margem, color=MUTED, lw=4, ls="--", marker="^", ms=10, label="2022, 2º turno: Bolsonaro menos Lula")
    ax.set_xlabel("% das seções recebidas"); ax.set_ylabel("pontos")
    ax.legend(loc="lower left")
    salvar(fig, "g07_2026_contra_2022.png")


def g08_sao_paulo_base():
    b = RES["p5_base_de_votos"]; c = RES["p5_classe_de_referencia"]
    fig, ax = novo("São Paulo: duas bases de cálculo", "Tarcísio (governador) e Flávio (presidente), em dois jeitos de calcular o percentual")
    x = np.array([0, 1.4])
    w = 0.55
    vals_t = [c["sp_gov_pct"], b["sp_tarcisio_pct_do_comparecimento"]]
    vals_f = [c["sp_pres_pct"], b["sp_flavio_pct_do_comparecimento"]]
    ax.bar(x - w / 2 - 0.02, vals_t, w, color=TARC, label="Tarcísio, governador")
    ax.bar(x + w / 2 + 0.02, vals_f, w, color=FLAVIO, label="Flávio, presidente")
    for xx, a_, b_ in zip(x, vals_t, vals_f):
        ax.text(xx - w / 2 - 0.02, a_ + 1.2, f"{v(a_, 2 if xx == 0 else 1)}%", ha="center", fontsize=34, fontweight="bold")
        ax.text(xx + w / 2 + 0.02, b_ + 1.2, f"{v(b_, 2 if xx == 0 else 1)}%", ha="center", fontsize=34, fontweight="bold")
        ax.text(xx - w / 2 - 0.02, 3, "Tarcísio\ngovernador", ha="center", fontsize=26, fontweight="bold", color=BG)
        ax.text(xx + w / 2 + 0.02, 3, "Flávio\npresidente", ha="center", fontsize=26, fontweight="bold", color=BG)
    ax.set_xticks(x); ax.set_xticklabels(["% dos votos válidos\nde cada cargo", "% de quem votou\n(mesma base nos dois)"], fontsize=28, color=FG)
    ax.set_ylim(0, 78); ax.grid(axis="x", visible=False)
    ax.text(x[0], 71, f"diferença: {v(c['sp_2026_lacuna_pontos'])} pontos", ha="center", fontsize=28, color=ACENTO, fontweight="bold")
    ax.text(x[1], 71, f"diferença: {v(b['sp_lacuna_pct_do_comparecimento'])} pontos", ha="center", fontsize=28, color=ACENTO, fontweight="bold")
    ax.set_ylabel("%")
    salvar(fig, "g08_sao_paulo_base_de_votos.png")


def g09_governadores():
    lr = pd.read_csv(saida.RES / "p5_lacuna_governador_presidente.csv")
    fig, axs = plt.subplots(1, 2, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.14, wspace=0.08)
    fig.text(0.04, 0.945, "São Paulo entre os governadores aliados", fontsize=40, fontweight="bold", va="center", ha="left")
    fig.text(0.04, 0.895, "Governador menos o presidente que ele declarou apoiar, em pontos. Cada ponto é um estado", fontsize=24, color=MUTED, va="center", ha="left")
    fig.text(0.04, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    rng = np.random.default_rng(7)
    for ax, col, tit in ((axs[0], "lacuna_pontos", "% dos votos válidos"), (axs[1], "lacuna_pct_do_comparecimento", "% de quem votou")):
        for i, ano in enumerate((2022, 2026)):
            d = lr[lr.ano == ano]
            y = np.full(len(d), i) + rng.uniform(-0.18, 0.18, len(d))
            ax.scatter(d[col], y, s=190, color=NEUTRO, alpha=0.9, edgecolor=BG)
            sp = d[d.uf == "SP"]
            if len(sp):
                ax.scatter(sp[col], [i], s=520, color=ACENTO, edgecolor=BG, linewidth=3, zorder=6)
                ax.annotate("SP", (float(sp[col].iloc[0]), i), xytext=(0, 34), textcoords="offset points", ha="center", fontsize=28, color=ACENTO, fontweight="bold")
        ax.axvline(0, color=MUTED, lw=1.5)
        ax.set_title(tit, fontsize=26, color=FG, pad=14)
        ax.set_xlim(-22, 22)
        ax.grid(axis="y", visible=False)
    axs[0].set_yticks([0, 1]); axs[0].set_yticklabels(["2022", "2026"], fontsize=30, color=FG); axs[0].set_ylim(-0.6, 1.6)
    axs[0].text(21.5, -0.5, "Goiás (+46,8) fica fora do quadro", ha="right", fontsize=18, color=MUTED)
    salvar(fig, "g09_sao_paulo_entre_os_governadores.png")


def g10_sp_municipios():
    sp = pd.read_csv(saida.RES / "p5_sao_paulo_por_municipio.csv")
    fig, ax = novo("A diferença aparece nos 645 municípios", "Tarcísio menos Flávio nos votos válidos, em cada um dos 645 municípios paulistas")
    bins = np.linspace(-20, 25, 60)
    ax.hist(sp.gap_22.clip(-20, 25), bins=bins, color=NEUTRO, alpha=0.8, label="2022: Tarcísio menos Bolsonaro")
    ax.hist(sp.gap_26.clip(-20, 25), bins=bins, color=TARC, alpha=0.95, label="2026: Tarcísio menos Flávio")
    ax.axvline(0, color=MUTED, lw=1.5)
    ax.set_xlabel("pontos"); ax.set_ylabel("municípios")
    ax.legend(loc="upper left")
    ax.text(26.5, ax.get_ylim()[1] * 0.55, f"menor diferença\nem 2026: {v(sp.gap_26.min())} pontos\n(nenhum município\nabaixo de zero)", ha="right", fontsize=24, color=ACENTO)
    ax.text(-19.5, ax.get_ylim()[1] * 0.50, "em 2022 era o contrário:\nTarcísio ficou atrás de\nBolsonaro em 99% dos municípios", ha="left", fontsize=22, color="#CBD5E1")
    salvar(fig, "g10_sao_paulo_por_municipio.png")


def g11_senado():
    s = pd.read_csv(saida.RES / "p6_senado_vs_presidente_2026.csv")
    h = pd.read_csv(saida.RES / "p6_referencia_historica_por_partido.csv")
    fig, ax = novo("Os senadores do PL e o voto em Flávio", "Votos no candidato do PL ao Senado contra a votação de Flávio, em cada estado")
    x = h[h.ano.isin([2018, 2022])]
    ax.scatter(x.flavio_ou_bolsonaro_pct, x.razao_partido_pres * x.flavio_ou_bolsonaro_pct, s=130, color=NEUTRO, alpha=0.7, label="2018 e 2022: candidatos do partido do presidente")
    d = s.dropna(subset=["pl_media_por_candidato_pct_eleitores"])
    eleito = d[d.pl_eleitos > 0]; perdeu = d[d.pl_eleitos == 0]
    ax.scatter(eleito.flavio_pct, eleito.pl_media_por_candidato_pct_eleitores, s=300, color=FLAVIO, edgecolor=BG, linewidth=2, label="2026: PL elegeu", zorder=5)
    ax.scatter(perdeu.flavio_pct, perdeu.pl_media_por_candidato_pct_eleitores, s=300, color=LULA, edgecolor=BG, linewidth=2, label="2026: PL não elegeu", zorder=5)
    for r in d.itertuples():
        ax.annotate(r.uf, (r.flavio_pct, r.pl_media_por_candidato_pct_eleitores), xytext=(8, 6), textcoords="offset points", fontsize=17, color=FG)
    ax.plot([0, 80], [0, 80], color=MUTED, lw=2, ls="--")
    ax.text(75, 79, "mesmo voto\nno Senado e no presidente", color=MUTED, fontsize=20, ha="right", va="top")
    ax.set_xlim(10, 80); ax.set_ylim(0, 80)
    ax.set_xlabel("% de Flávio nos votos válidos do estado"); ax.set_ylabel("% dos eleitores no candidato do PL")
    ax.legend(loc="lower right", fontsize=20)
    salvar(fig, "g11_senado_e_presidente.png")


def g12_anomalias():
    m = RES["p8_municipios"]
    fig, ax = novo("Procurando município fora do padrão", f"{milhar(m['testados_2026'])} municípios, três testes, e a regra escrita antes de olhar os dados")
    nomes = ["Votos diferentes de 2022", "Votos diferentes do outro cargo", "Comparecimento e voto não combinam", "Nos três ao mesmo tempo"]
    vals = [m["sinal_a_historico"], m["sinal_b_outro_cargo"], m["sinal_c_comparecimento"], m["a_explicar_flavio"]]
    cores = [NEUTRO, NEUTRO, NEUTRO, ACENTO]
    y = np.arange(len(nomes))[::-1]
    ax.barh(y, vals, color=cores, height=0.55)
    for yy, x in zip(y, vals):
        ax.text(x + 1.2, yy, str(x), va="center", fontsize=34, fontweight="bold", color=ACENTO if x == 0 else FG)
    ax.set_yticks(y); ax.set_yticklabels(nomes, fontsize=26, color=FG)
    ax.set_xlim(0, 75); ax.grid(axis="y", visible=False); ax.set_xlabel("municípios sinalizados, para Flávio")
    fig.subplots_adjust(left=0.40)
    ax.text(74, 0.2, f"mesmo teste em 2022: {m['placebo_2022_a_explicar']} nos três", ha="right", fontsize=22, color=MUTED)
    salvar(fig, "g12_municipios_fora_do_padrao.png")


def g13_numeros():
    fig, ax = plt.subplots()
    ax.axis("off"); fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.08)
    fig.text(0.05, 0.93, "O que foi coletado e conferido", fontsize=42, fontweight="bold", va="center")
    cards = [("499.192", "seções com boletim de urna\nbaixadas e lidas"), ("998.468", "arquivos, com sha256\npara conferir depois"), ("99,96%", "das comparações com o oficial\n(município e cargo) fecham exato"),
             ("15", "seções sem arquivo publicado\n(3.935 votos de Presidente)"), ("14", "pontos da tela publicados\npela imprensa, 13 encaixam"), ("0", "municípios nos três testes\nde anomalia ao mesmo tempo")]
    for i, (n, t) in enumerate(cards):
        col, row = i % 3, i // 3
        x0, y0 = 0.05 + col * 0.31, 0.50 - row * 0.40
        fig.add_artist(FancyBboxPatch((x0, y0), 0.29, 0.34, boxstyle="round,pad=0.005,rounding_size=0.02", transform=fig.transFigure, fc="#12244A", ec=GRID, lw=2))
        fig.text(x0 + 0.145, y0 + 0.24, n, fontsize=64, fontweight="bold", color=ACENTO, ha="center", va="center")
        fig.text(x0 + 0.145, y0 + 0.09, t, fontsize=21, color=FG, ha="center", va="center")
    fig.text(0.05, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    salvar(fig, "g13_numeros_da_coleta.png")


def g14_o_caminho():
    fig, ax = plt.subplots()
    ax.axis("off"); fig.subplots_adjust(left=0.04, right=0.96, top=0.9, bottom=0.08)
    fig.text(0.05, 0.93, "Como a noite foi refeita", fontsize=42, fontweight="bold", va="center")
    passos = [("1", "Boletim\nde urna", "cada urna imprime um,\no TSE publica"), ("2", "Hora de\nrecebimento", "o TSE guarda a hora em\nque cada boletim chegou"),
              ("3", "Ordenar", "todas as seções, da\nprimeira à última a chegar"), ("4", "Somar", "votos acumulados,\nminuto a minuto"), ("5", "Conferir", "contra o oficial e contra\no que a imprensa publicou")]
    for i, (n, t, s) in enumerate(passos):
        x0 = 0.045 + i * 0.19
        fig.add_artist(FancyBboxPatch((x0, 0.30), 0.165, 0.40, boxstyle="round,pad=0.004,rounding_size=0.02", transform=fig.transFigure, fc="#12244A", ec=ACENTO if i in (1, 4) else GRID, lw=3))
        fig.text(x0 + 0.0825, 0.62, n, fontsize=56, fontweight="bold", color=ACENTO, ha="center", va="center")
        fig.text(x0 + 0.0825, 0.51, t, fontsize=24, fontweight="bold", ha="center", va="center")
        fig.text(x0 + 0.0825, 0.385, s, fontsize=17, color="#CBD5E1", ha="center", va="center")
        if i < 4:
            fig.text(x0 + 0.1775, 0.50, "›", fontsize=60, color=MUTED, ha="center", va="center")
    fig.text(0.05, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    salvar(fig, "g14_o_caminho.png")



def barras_simples(titulo, sub, rotulos, valores, cores, nome, unidade="", fmt=1, destaque=None, nota=None, xmax=None):
    fig, ax = novo(titulo, sub)
    fig.subplots_adjust(left=0.30)
    y = np.arange(len(rotulos))[::-1]
    ax.barh(y, valores, color=cores, height=0.58)
    for yy, x, c in zip(y, valores, cores):
        ax.text(x + (max(valores) * 0.015), yy, f"{v(x, fmt)}{unidade}", va="center", fontsize=32, fontweight="bold", color=ACENTO if c == ACENTO else FG)
    ax.set_yticks(y); ax.set_yticklabels(rotulos, fontsize=25, color=FG)
    ax.set_xlim(0, xmax or max(valores) * 1.18); ax.grid(axis="y", visible=False)
    if nota:
        fig.text(0.30, 0.09, nota, fontsize=19, color=MUTED, ha="left", va="center")
    salvar(fig, nome)


def g15_queda_comparada():
    p26 = pd.read_csv(saida.RES / "p1_margem_por_pct_de_secoes.csv")
    p22 = pd.read_csv(saida.RES / "p7_margem_2022_por_pct_de_secoes.csv")
    q26 = float(p26[p26.pct_secoes == 10].margem.iloc[0] - RES["p1_resumo"]["margem_final"])
    d = RES["derivados"]["p7"]
    q22a = d["t1_margem_em_10pct"] - d["t1_margem_final"]
    q22b = d["t2_margem_em_10pct"] - d["t2_margem_final"]
    barras_simples("Quanto a vantagem do primeiro colocado encolheu", "Dos 10% das seções recebidas até o fim da contagem, em pontos",
                   ["2022, 1º turno\n(Bolsonaro, virou)", "2026, 1º turno\n(Flávio, não virou)", "2022, 2º turno\n(Bolsonaro, virou)"],
                   [q22a, q26, q22b], [NEUTRO, ACENTO, NEUTRO], "g15_queda_comparada.png", " pts")


def g16_vazio_comparado():
    a = RES["p2_maiores_vazios_de_recebimento_2026"][0]["minutos"]
    b = RES["p7_maiores_vazios_de_recebimento_2022_turno1"][0]["minutos"]
    c = RES["p7_maiores_vazios_de_recebimento_2022_turno2"][0]["minutos"]
    barras_simples("O maior tempo sem nenhum boletim registrado", "Em minutos, na noite inteira de cada apuração",
                   ["2026, 1º turno\n(19:31 às 19:59)", "2022, 1º turno", "2022, 2º turno"], [a, b, c], [ACENTO, NEUTRO, NEUTRO],
                   "g16_vazio_comparado.png", " min")


def g17_governadores_aliados():
    lr = pd.read_csv(saida.RES / "p5_lacuna_governador_presidente.csv")
    escolha = [(2022, "PA"), (2022, "PR"), (2022, "TO"), (2022, "MG"), (2026, "SP"), (2026, "MS"), (2026, "MG"), (2026, "PA")]
    rot, val, cor = [], [], []
    for ano, uf in escolha:
        r = lr[(lr.ano == ano) & (lr.uf == uf)].iloc[0]
        apoio = {"Flavio": "Flávio", "Bolsonaro": "Bolsonaro", "Lula": "Lula"}.get(r.apoio, r.apoio)
        nome = str(r.governador).replace("Tarcisio", "Tarcísio").replace("Ratinho Junior", "Ratinho Júnior")
        rot.append(f"{nome} ({uf}, {ano})\napoiava {apoio}")
        val.append(float(r.lacuna_pontos))
        cor.append(ACENTO if uf == "SP" else NEUTRO)
    barras_simples("Governador aliado acima do presidente que ele apoia", "Em pontos dos votos válidos. As maiores diferenças de 2022 e de 2026",
                   rot, val, cor, "g17_governadores_aliados.png", " pts",
                   nota="Goiás 2026 (+46,8, apoio ao Caiado) fica fora: é um caso à parte")


def g18_o_veredito():
    fig, ax = plt.subplots()
    ax.axis("off"); fig.subplots_adjust(left=0.04, right=0.96, top=0.9, bottom=0.08)
    fig.text(0.05, 0.93, "A leitura da IA, etapa por etapa", fontsize=42, fontweight="bold", va="center")
    linhas = [("A conta", "a soma das urnas bate com o oficial", "resolvido", "#00FF7B"),
              ("A queda da vantagem", "ordem de chegada; caiu menos que em 2022", "normal", "#00FF7B"),
              ("A tela parada", "voltou com a soma de boletins reais", "normal", "#00FF7B"),
              ("O registro de chegada", "27 min sem nenhum boletim; em 2022, 7 min", "pede explicação", ACENTO),
              ("São Paulo", "quase metade é branco e nulo; o resto, voto dividido", "normal", "#00FF7B"),
              ("O Senado", "voto casado com o presidente, como antes", "normal", "#00FF7B"),
              ("As cidades", "nenhuma fora do padrão nos três testes", "normal", "#00FF7B")]
    for i, (a, b, c, cor) in enumerate(linhas):
        y = 0.80 - i * 0.105
        fig.add_artist(FancyBboxPatch((0.05, y - 0.04), 0.90, 0.085, boxstyle="round,pad=0.003,rounding_size=0.015", transform=fig.transFigure, fc="#12244A", ec=cor if cor == ACENTO else GRID, lw=2.5))
        fig.text(0.07, y, a, fontsize=26, fontweight="bold", va="center")
        fig.text(0.33, y, b, fontsize=23, color="#CBD5E1", va="center")
        fig.text(0.93, y, c.upper(), fontsize=24, fontweight="bold", color=cor, va="center", ha="right")
    fig.text(0.05, 0.035, FONTE, fontsize=17, color=MUTED, va="center", ha="left")
    salvar(fig, "g18_a_leitura_da_ia.png")

def trailer_borrado():
    """Versoes borradas dos graficos principais, para o trailer."""
    for nome in ("g01_a_noite_em_uma_linha", "g05_a_tela_parada", "g08_sao_paulo_base_de_votos", "g11_senado_e_presidente"):
        im = Image.open(OUT / f"{nome}.png").convert("RGB").filter(ImageFilter.GaussianBlur(12))
        im.save(OUT / f"{nome.split('_')[0]}_borrado.png")


def main() -> int:
    for f in (g01_noite_em_uma_linha, g03_quem_chegou_primeiro, g04_embaralhando, g05_a_tela_parada, g06_tela_contra_boletins,
              g07_2026_contra_2022, g08_sao_paulo_base, g09_governadores, g10_sp_municipios, g11_senado, g12_anomalias, g13_numeros, g14_o_caminho,
              g15_queda_comparada, g16_vazio_comparado, g17_governadores_aliados, g18_o_veredito):
        f()
        print(f.__name__, "ok")
    trailer_borrado()
    print("borrados ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
