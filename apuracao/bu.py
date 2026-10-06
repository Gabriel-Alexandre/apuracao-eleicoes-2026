"""Decodificador do boletim de urna (bu.dat) do TSE, eleicao de 2026.

Estrutura inferida da leitura de boletins reais e conferida contra o resultado oficial
(ver tests/ e docs/FONTES_DE_DADOS.md). Tipos de voto: 1 nominal, 2 branco, 3 nulo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from . import ber

CARGO = {1: "presidente", 3: "governador", 5: "senador", 6: "dep_federal", 7: "dep_estadual", 8: "dep_distrital"}
MAJORITARIOS = (1, 3, 5)


@dataclass
class Boletim:
    gerado: str | None = None
    emitido: str | None = None
    abertura: str | None = None
    encerramento: str | None = None
    turno_codigo: int | None = None
    municipio: int | None = None
    zona: int | None = None
    local: int | None = None
    secao: int | None = None
    comparecimento: int | None = None
    aptos: int | None = None
    # (cargo, tipo, partido, numero) -> votos ; tipo 1 nominal, 2 branco, 3 nulo
    votos: dict[tuple[int, int, int, int], int] = field(default_factory=dict)


def _conteudo(envelope) -> bytes | None:
    """O boletim de verdade e o OCTET STRING (universal 4) filho do SEQUENCE de nivel mais alto do envelope."""
    if not envelope or not envelope[0][2]:
        return None
    for cls, tag, cons, v in envelope[0][3]:
        if cls == 0 and tag == 4 and not cons and len(v) > 50:
            return v
    return None


def _is_cargo_block(v) -> bool:
    """[ P(2:1) cargo, P(0:2) n, C(0:16) entradas ]"""
    return (
        len(v) == 3
        and v[0][0] == 2 and v[0][1] == 1 and not v[0][2]
        and v[1][0] == 0 and v[1][1] == 2 and not v[1][2]
        and v[2][0] == 0 and v[2][1] == 16 and v[2][2]
    )


def _entrada(e):
    """entrada de votavel: C com P(2:1) tipo, P(2:2) votos, opcional C(2:3) (partido, numero)"""
    tipo = votos = None
    partido = numero = 0
    for cls, tag, cons, v in e:
        if cls == 2 and tag == 1 and not cons:
            tipo = ber.as_int(v)
        elif cls == 2 and tag == 2 and not cons:
            votos = ber.as_int(v)
        elif cls == 2 and tag == 3 and cons and len(v) >= 2:
            partido = ber.as_int(v[0][3])
            numero = ber.as_int(v[1][3])
    return tipo, votos, partido, numero


def _walk(nodes, out: Boletim) -> None:
    for _cls, _tag, cons, v in nodes:
        if not cons:
            continue
        if _is_cargo_block(v):
            cargo = ber.as_int(v[0][3])
            for ecls, etag, econs, ev in v[2][3]:
                if not econs:
                    continue
                tipo, votos, partido, numero = _entrada(ev)
                if tipo is None or votos is None:
                    continue
                if cargo not in MAJORITARIOS:
                    numero = 0 if tipo == 1 else numero  # proporcional: agrega por partido adiante
                key = (cargo, tipo, partido, numero)
                out.votos[key] = out.votos.get(key, 0) + votos
        else:
            _walk(v, out)


def _ts(b: bytes) -> str:
    s = ber.as_text(b)
    return datetime.strptime(s, "%Y%m%dT%H%M%S").isoformat()


def decode(raw: bytes) -> Boletim:
    envelope = ber.parse(raw)
    inner = _conteudo(envelope)
    if inner is None:
        raise ValueError("conteudo do boletim nao encontrado")
    tree = ber.parse(inner)
    top = tree[0][3]
    bu = Boletim()

    # cabecalho: [ (data, 3220), turno, ident..., (muni,zona), ..., emissao, (abertura, encerramento), ... ]
    bu.gerado = _ts(top[0][3][0][3])
    for cls, tag, cons, v in top:
        if cons and cls == 0 and tag == 16 and len(v) == 3 and v[0][2] and len(v[0][3]) == 2:
            # (municipio, zona), local, secao
            try:
                bu.municipio = ber.as_int(v[0][3][0][3])
                bu.zona = ber.as_int(v[0][3][1][3])
                bu.local = ber.as_int(v[1][3])
                bu.secao = ber.as_int(v[2][3])
            except Exception:
                pass
        elif cls == 0 and tag == 27 and not cons and len(v) == 15 and bu.emitido is None:
            bu.emitido = _ts(v)
        elif cls == 2 and tag == 0 and cons and len(v) == 2:
            bu.abertura = _ts(v[0][3])
            bu.encerramento = _ts(v[1][3])
        elif cls == 0 and tag == 2 and not cons and bu.comparecimento is None and bu.encerramento is not None:
            bu.comparecimento = ber.as_int(v)
    # aptos: primeiro inteiro depois do codigo da eleicao no primeiro bloco de eleicao
    for cls, tag, cons, v in top:
        if cons and cls == 0 and tag == 16 and v and v[0][2] and v[0][3] and v[0][3][0][0] == 0 and v[0][3][0][1] == 2:
            first = v[0][3]
            if len(first) >= 3 and not first[1][2]:
                bu.aptos = ber.as_int(first[1][3])
                break
    _walk(top, bu)
    return bu
