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

from apuracao import saida  # noqa: E402


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
    df = pd.read_csv(saida.RES / arquivo)
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


def main() -> int:
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
