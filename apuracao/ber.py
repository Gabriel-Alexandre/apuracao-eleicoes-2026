"""Leitor minimo de BER (ASN.1), o formato do boletim de urna (bu.dat).

Nao conhece o esquema: devolve a arvore de (classe, tag, construido, valor).
O esquema e inferido em apuracao/bu.py e conferido contra o total oficial.
"""

from __future__ import annotations

Node = tuple[int, int, bool, "list[Node] | bytes"]


def parse(b: bytes, i: int = 0, end: int | None = None) -> list[Node]:
    end = len(b) if end is None else end
    out: list[Node] = []
    while i < end:
        t0 = b[i]
        i += 1
        cls = t0 >> 6
        cons = bool((t0 >> 5) & 1)
        tag = t0 & 0x1F
        if tag == 0x1F:
            tag = 0
            while True:
                x = b[i]
                i += 1
                tag = (tag << 7) | (x & 0x7F)
                if not x & 0x80:
                    break
        length = b[i]
        i += 1
        if length & 0x80:
            n = length & 0x7F
            if n == 0:
                raise ValueError("comprimento indefinido nao suportado")
            length = int.from_bytes(b[i : i + n], "big")
            i += n
        if i + length > end:
            raise ValueError("TLV maior que o contêiner")
        if cons:
            out.append((cls, tag, True, parse(b, i, i + length)))
        else:
            out.append((cls, tag, False, bytes(b[i : i + length])))
        i += length
    return out


def as_int(v: bytes) -> int:
    return int.from_bytes(v, "big")


def as_text(v: bytes) -> str:
    return v.decode("latin1")
