"""Testes do nucleo: leitor de BER, decodificador do boletim, decomposicao exata, BH e permutacoes."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from apuracao import analises, anomalia, ber, bu, curva

FIXTURE = Path(__file__).parent / "fixtures" / "bu-ac-porto-walter-z0004-s0077.dat"


def test_ber_inteiro_e_texto():
    nos = ber.parse(bytes([0x02, 0x02, 0x01, 0x00, 0x1B, 0x03, 0x41, 0x42, 0x43]))
    assert ber.as_int(nos[0][3]) == 256
    assert ber.as_text(nos[1][3]) == "ABC"


def test_boletim_real_fecha_a_conta_da_secao():
    b = bu.decode(FIXTURE.read_bytes())
    assert (b.municipio, b.zona, b.secao) == (1066, 4, 77)
    assert b.aptos == 289 and b.comparecimento == 234
    assert b.abertura == "2026-10-04T06:06:52" and b.encerramento == "2026-10-04T15:40:41"
    por_cargo = {}
    for (cargo, tipo, _p, _n), v in b.votos.items():
        por_cargo[cargo] = por_cargo.get(cargo, 0) + v
    assert por_cargo[1] == 234          # presidente: um voto por eleitor
    assert por_cargo[3] == 234          # governador
    assert por_cargo[5] == 2 * 234      # senador: dois votos por eleitor
    assert b.votos[(1, 1, 22, 22)] == 103 and b.votos[(1, 1, 13, 13)] == 99


def test_decomposicao_e_exata():
    rng = np.random.default_rng(1)
    n = 400
    d = pd.DataFrame({
        "uf": rng.choice(["A", "B", "C"], n), "validos": rng.integers(50, 300, n),
        "p22": rng.integers(0, 150, n), "p13": rng.integers(0, 150, n),
        "recebido": pd.date_range("2026-10-04 17:00", periods=n, freq="30s"),
        "mun_cd": "0", "zona": "1", "secao": [str(i) for i in range(n)],
    })
    d["validos"] = np.maximum(d["validos"], d["p22"] + d["p13"])
    d = analises.marcar_pct(d, n)
    dec = analises.decompor(d, 40, 100, "uf")
    assert abs(dec.attrs["soma_contribuicoes"] - dec.attrs["mudanca"]) < 1e-9
    assert abs((dec.attrs["efeito_composicao"] + dec.attrs["efeito_ordem_dentro_do_grupo"]) - dec.attrs["diferenca_lote_menos_antes"]) < 1e-9


def test_bh_controla_a_taxa_de_descoberta():
    p = np.array([0.001, 0.009, 0.04, 0.2, 0.5, 0.9])
    rej = anomalia.bh(p, 0.05)
    assert rej.tolist() == [True, True, False, False, False, False]


def test_permutacao_termina_na_margem_final():
    n = 300
    rng = np.random.default_rng(2)
    f = rng.integers(0, 100, n)
    l = rng.integers(0, 100, n)
    d = pd.DataFrame({"uf": rng.choice(["A", "B"], n), "p22": f, "p13": l, "validos": f + l + 10,
                      "recebido": pd.date_range("2026-10-04 17:00", periods=n, freq="30s"), "mun_cd": "0", "zona": "1", "secao": [str(i) for i in range(n)]})
    final = 100 * (f.sum() - l.sum()) / (f + l + 10).sum()
    r = curva.permutacoes(d, np.array([50.0, 100.0]), n=20, seed=3)
    assert np.allclose(r[:, -1], final)
    r2 = curva.permutacoes(d, np.array([100.0]), n=5, seed=3, por_uf=True)
    assert np.allclose(r2[:, -1], final)
