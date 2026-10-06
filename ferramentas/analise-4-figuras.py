"""Figuras do relatorio. Le so os CSV de resultados/ (nunca recalcula nada).

Uso: python ferramentas/analise-4-figuras.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from apuracao import saida  # noqa: E402

COR_F, COR_L, COR_CINZA, COR_DEST = "#117a65", "#7d3c98", "#7f8c8d", "#d35400"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 130})


def salvar(fig, nome):
    saida.preparar()
    fig.tight_layout()
    fig.savefig(saida.FIG / nome, bbox_inches="tight")
    plt.close(fig)


def lerc(nome, **kw):
    return pd.read_csv(saida.RES / nome, **kw)


def fig1_curva():
    cv = lerc("p3_curva_reconstruida.csv", parse_dates=["recebido"])
    pt = lerc("p3_pontos_da_tela.csv")
    pe = lerc("p1_permutacoes.csv")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    a = ax[0]
    a.fill_between(pe.grade_pct, pe.aleatoria_p05, pe.aleatoria_p95, color=COR_CINZA, alpha=0.35, label="ordem aleatória (5% a 95%)")
    a.fill_between(pe.grade_pct, pe.calendario_por_uf_p05, pe.calendario_por_uf_p95, color=COR_DEST, alpha=0.25, label="calendário de cada UF, ordem aleatória dentro da UF")
    a.plot(cv.pct_secoes, cv.margem_flavio_lula, color="black", lw=2, label="reconstruída com os boletins")
    duas = pt.fontes.str.count(";") >= 1
    a.scatter(pt.pct_secoes[duas], (pt.flavio_publicado - pt.lula_publicado)[duas], color=COR_F, s=46, zorder=5, label="ponto da tela, 2 ou mais fontes")
    a.scatter(pt.pct_secoes[~duas], (pt.flavio_publicado - pt.lula_publicado)[~duas], facecolors="none", edgecolors=COR_F, s=46, zorder=5, label="ponto da tela, 1 fonte")
    a.set_xlabel("% das seções recebidas"); a.set_ylabel("Flávio menos Lula, em pontos dos votos válidos")
    a.set_title("A curva refeita passa pelos pontos publicados?"); a.legend(fontsize=7.5, loc="upper right")
    b = ax[1]
    b.plot(cv.recebido, cv.margem_flavio_lula, color="black", lw=2, label="reconstruída (hora de recebimento)")
    hora = pd.to_datetime("2026-10-04 " + pt.hora_publicada.where(pt.hora_publicada.str.contains(":"), None), errors="coerce")
    ok = hora.notna()
    b.scatter(hora[duas & ok], (pt.flavio_publicado - pt.lula_publicado)[duas & ok], color=COR_F, s=46, zorder=5, label="tela (hora publicada), 2 ou mais fontes")
    b.scatter(hora[~duas & ok], (pt.flavio_publicado - pt.lula_publicado)[~duas & ok], facecolors="none", edgecolors=COR_F, s=46, zorder=5, label="tela (hora publicada), 1 fonte")
    b.axvspan(pd.Timestamp("2026-10-04 19:06"), pd.Timestamp("2026-10-04 20:08"), color=COR_DEST, alpha=0.15, label="tela de Presidente parada")
    b.set_xlim(pd.Timestamp("2026-10-04 17:00"), pd.Timestamp("2026-10-04 23:00"))
    b.set_xlabel("horário de Brasília"); b.set_title("A mesma curva ao longo do relógio"); b.legend(fontsize=7.5, loc="upper right")
    salvar(fig, "fig1_curva_da_noite.png")


def fig2_regioes():
    t = lerc("p1_chegada_por_regiao_30min.csv", parse_dates=["faixa"]).set_index("faixa")
    t = t[(t.index >= "2026-10-04 17:00") & (t.index <= "2026-10-04 23:30")]
    cores = {"Norte": "#1abc9c", "Nordeste": "#f39c12", "Centro-Oeste": "#8e44ad", "Sudeste": "#2980b9", "Sul": "#16a085", "Exterior": "#7f8c8d"}
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bottom = np.zeros(len(t))
    for c in [c for c in cores if c in t.columns]:
        ax.bar(t.index, t[c], width=0.019, bottom=bottom, label=c, color=cores[c], align="edge")
        bottom += t[c].to_numpy()
    ax.axvspan(pd.Timestamp("2026-10-04 19:06"), pd.Timestamp("2026-10-04 20:08"), color=COR_DEST, alpha=0.12)
    ax.set_ylabel("boletins recebidos por meia hora"); ax.set_xlabel("horário de Brasília (recebimento)")
    ax.set_title("Quem chegou quando: boletins recebidos por região"); ax.legend(fontsize=8)
    salvar(fig, "fig2_chegada_por_regiao.png")


def fig3_parada():
    ch = lerc("p2_chegada_a_cada_5min.csv", parse_dates=["faixa"]).set_index("faixa")
    cv = lerc("p3_curva_reconstruida.csv", parse_dates=["recebido"])
    pt = lerc("p3_pontos_da_tela.csv")
    fig, ax = plt.subplots(2, 1, figsize=(9.5, 6.4), sharex=True)
    ax[0].bar(ch.index, ch.boletins, width=0.0034, color=COR_CINZA, align="edge")
    ax[0].axvspan(pd.Timestamp("2026-10-04 19:06"), pd.Timestamp("2026-10-04 20:08"), color=COR_DEST, alpha=0.15, label="tela de Presidente parada")
    ax[0].set_ylabel("boletins recebidos\npor 5 minutos"); ax[0].legend(fontsize=8); ax[0].set_title("Os boletins continuaram chegando enquanto a tela estava parada?")
    ax[1].plot(cv.recebido, cv.pct_secoes, color="black", lw=2, label="% das seções já recebidas")
    hora = pd.to_datetime("2026-10-04 " + pt.hora_publicada.where(pt.hora_publicada.str.contains(":"), None), errors="coerce")
    ok = hora.notna()
    ax[1].scatter(hora[ok], pt.pct_secoes[ok], color=COR_F, s=40, zorder=5, label="% mostrado na tela (imprensa)")
    ax[1].axvspan(pd.Timestamp("2026-10-04 19:06"), pd.Timestamp("2026-10-04 20:08"), color=COR_DEST, alpha=0.15)
    ax[1].set_xlim(pd.Timestamp("2026-10-04 17:00"), pd.Timestamp("2026-10-04 23:00")); ax[1].set_ylabel("% das seções"); ax[1].set_xlabel("horário de Brasília"); ax[1].legend(fontsize=8)
    salvar(fig, "fig3_parada.png")


def fig4_2022():
    m26 = lerc("p1_margem_por_pct_de_secoes.csv")
    m22 = lerc("p7_margem_2022_por_pct_de_secoes.csv")
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.plot(m26.pct_secoes, m26.margem, "-o", color=COR_F, lw=2, ms=4, label="2026, 1º turno: Flávio menos Lula")
    for turno, estilo, rot in (("1", "-s", "2022, 1º turno: Bolsonaro menos Lula"), ("2", "--^", "2022, 2º turno: Bolsonaro menos Lula")):
        s = m22[m22.turno.astype(str) == turno]
        ax.plot(s.pct_secoes, s.margem, estilo, color=COR_CINZA if turno == "1" else "#bdc3c7", lw=1.8, ms=4, label=rot)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("% das seções recebidas"); ax.set_ylabel("diferença do candidato que começou na frente, em pontos")
    ax.set_title("A vantagem inicial encolhe ao longo da noite também em 2022"); ax.legend(fontsize=8)
    salvar(fig, "fig4_2026_contra_2022.png")


def fig5_lacuna():
    r = lerc("p5_lacuna_governador_presidente.csv")
    r = r[(r.ano.isin([2026, 2022])) & (r.apoio != "neutro")]
    fig, ax = plt.subplots(figsize=(9, 3.9))
    for y, ano in ((1, 2026), (0, 2022)):
        s = r[r.ano == ano]
        ax.scatter(s.lacuna_pontos, np.full(len(s), y) + np.random.default_rng(1).uniform(-0.12, 0.12, len(s)), color=COR_CINZA, s=44, zorder=3)
        for row in s.itertuples():
            if row.uf == "SP" and ano == 2026:
                ax.scatter([row.lacuna_pontos], [y], color=COR_DEST, s=130, zorder=6, label="São Paulo 2026 (Tarcísio menos Flávio)")
            else:
                ax.annotate(row.uf, (row.lacuna_pontos, y), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=6.5, color="#555")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["2022", "2026"]); ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("% do governador eleito menos % do presidente que ele declarou apoiar (pontos)")
    ax.set_title("Quanto o governador aliado costuma ficar acima ou abaixo do candidato a presidente"); ax.legend(fontsize=8, loc="lower right")
    salvar(fig, "fig5_lacuna_governador_presidente.png")


def fig6_sp():
    j = lerc("p5_sao_paulo_por_municipio.csv")
    fig, ax = plt.subplots(figsize=(6.2, 5.6))
    ax.scatter(j.gap_22, j.gap_26, s=np.sqrt(j.vg_26) / 6, alpha=0.5, color=COR_CINZA)
    c = j[j.capital == True]  # noqa: E712
    if len(c):
        ax.scatter(c.gap_22, c.gap_26, s=70, color=COR_DEST, zorder=5, label="capital")
    lim = [min(j.gap_22.min(), j.gap_26.min()), max(j.gap_22.max(), j.gap_26.max())]
    ax.plot(lim, lim, color="black", lw=0.8, ls="--"); ax.axhline(0, color="black", lw=0.5); ax.axvline(0, color="black", lw=0.5)
    ax.set_xlabel("2022: Tarcísio menos Bolsonaro (pontos)"); ax.set_ylabel("2026: Tarcísio menos Flávio (pontos)")
    ax.set_title("São Paulo, por município: a diferença de 2026 repete a de 2022?"); ax.legend(fontsize=8)
    salvar(fig, "fig6_sao_paulo_por_municipio.png")


def fig7_senado():
    s = lerc("p6_senado_vs_presidente_2026.csv")
    h = lerc("p6_referencia_historica_por_partido.csv")
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    for ano, cor in ((2018, "#bdc3c7"), (2022, "#95a5a6")):
        x = h[h.ano == ano]
        ax.scatter(x.flavio_ou_bolsonaro_pct, x.razao_partido_pres * x.flavio_ou_bolsonaro_pct, color=cor, s=28, label=f"{ano}: candidatos do partido do presidente")
    ax.scatter(s.flavio_pct, s.pl_media_por_candidato_pct_eleitores, color=COR_F, s=48, zorder=5, label="2026: candidatos do PL")
    for r in s.itertuples():
        if not np.isnan(r.pl_media_por_candidato_pct_eleitores):
            ax.annotate(r.uf, (r.flavio_pct, r.pl_media_por_candidato_pct_eleitores), textcoords="offset points", xytext=(3, 3), fontsize=7)
    lim = [0, max(s.flavio_pct.max(), 80)]
    ax.plot(lim, lim, color="black", lw=0.8, ls="--", label="igual ao voto no candidato a presidente")
    ax.set_xlabel("% de Flávio (ou do presidente apoiado) nos válidos da UF"); ax.set_ylabel("votos de um candidato do partido ao Senado, em % dos eleitores")
    ax.set_title("Voto no candidato do partido ao Senado contra o voto no presidente"); ax.legend(fontsize=7.5)
    salvar(fig, "fig7_senado_contra_presidente.png")


def fig8_anomalias():
    c = lerc("p8_caudas_dos_z_no_municipio.csv")
    c["rotulo"] = c.ano.astype(str) + " " + c.cargo.str.replace(" (lider da UF)", "", regex=False) + " " + c.candidato
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    cores = [COR_F if a == 2026 else COR_CINZA for a in c.ano]
    ax.barh(c.rotulo, c.pct_abs_gt_4, color=cores)
    ax.set_xlabel("% das seções com |z| maior que 4 contra o resto do município"); ax.invert_yaxis()
    ax.set_title("Caudas parecidas entre anos e cargos: o teste não separa 2026 de 2022")
    salvar(fig, "fig8_caudas_dos_z.png")


def main() -> int:
    for f in (fig1_curva, fig2_regioes, fig3_parada, fig4_2022, fig5_lacuna, fig6_sp, fig7_senado, fig8_anomalias):
        try:
            f()
            print("ok", f.__name__)
        except FileNotFoundError as e:
            print("pulou", f.__name__, e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
