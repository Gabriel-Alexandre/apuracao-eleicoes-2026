"""Refaz a sondagem das fontes de dados descritas em docs/FONTES_DE_DADOS.md.

Faz poucas requisições (uma por endereço), não baixa dado em massa e não grava nada
fora de dados/sondas/ quando chamado com --salvar.

Uso:
    python ferramentas/sondar-fontes.py
    python ferramentas/sondar-fontes.py --salvar
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://resultados.tse.jus.br/oficial"
PLEITO = "3220"
ELEICAO_FEDERAL = "6257"
ELEICAO_ESTADUAL = "6259"
UA = "apuracao-eleicoes-2026/0.1 (sondagem de fontes publicas)"

# Seção de exemplo conferida em 05/out/2026 (AC, Porto Walter, zona 0004, seção 0077).
SECAO_EXEMPLO = ("ac", "01066", "0004", "0077")


def baixar(url: str) -> tuple[int, bytes, dict]:
    pedido = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(pedido, timeout=30) as resposta:
            return resposta.status, resposta.read(), dict(resposta.headers)
    except urllib.error.HTTPError as erro:
        return erro.code, b"", dict(erro.headers or {})
    except urllib.error.URLError as erro:
        return 0, str(erro.reason).encode(), {}


def sondar() -> list[dict]:
    uf, mun, zona, secao = SECAO_EXEMPLO
    alvos = {
        "config_eleicoes": f"{BASE}/comum/config/ele-c.json",
        "presidente_br": f"{BASE}/ele2026/{ELEICAO_FEDERAL}/dados/br/br-c0001-e00{ELEICAO_FEDERAL}-u.json",
        "presidente_sp": f"{BASE}/ele2026/{ELEICAO_FEDERAL}/dados/sp/sp-c0001-e00{ELEICAO_FEDERAL}-u.json",
        "governador_sp": f"{BASE}/ele2026/{ELEICAO_ESTADUAL}/dados/sp/sp-c0003-e00{ELEICAO_ESTADUAL}-u.json",
        "senador_sp": f"{BASE}/ele2026/{ELEICAO_ESTADUAL}/dados/sp/sp-c0005-e00{ELEICAO_ESTADUAL}-u.json",
        "secoes_ac": f"{BASE}/ele2026/arquivo-urna/{PLEITO}/config/{uf}/{uf}-p00{PLEITO}-cs.json",
        "aux_secao_exemplo": (
            f"{BASE}/ele2026/arquivo-urna/{PLEITO}/dados/{uf}/{mun}/{zona}/{secao}/"
            f"p00{PLEITO}-{uf}-m{mun}-z{zona}-s{secao}-aux.json"
        ),
        "aux_2022_exemplo": f"{BASE}/ele2022/arquivo-urna/406/config/ac/ac-p000406-cs.json",
    }

    resultados = []
    for nome, url in alvos.items():
        status, corpo, cabecalho = baixar(url)
        linha = {
            "nome": nome,
            "url": url,
            "status": status,
            "bytes": len(corpo),
            "sha256": hashlib.sha256(corpo).hexdigest() if corpo else None,
            "last_modified": cabecalho.get("Last-Modified"),
        }
        if status == 200 and nome == "aux_secao_exemplo":
            dado = json.loads(corpo)
            hashes = dado.get("hashes", [])
            linha["recebimento"] = [(h.get("dr"), h.get("hr"), h.get("st")) for h in hashes]
        if status == 200 and nome == "presidente_br":
            dado = json.loads(corpo)
            linha["gerado_em"] = f"{dado.get('dg')} {dado.get('hg')}"
            linha["secoes_totalizadas"] = dado.get("s", {}).get("pst")
        resultados.append(linha)

    ckan = "https://dadosabertos.tse.jus.br/api/3/action/package_search?q=resultados%202026&rows=50"
    status, corpo, _ = baixar(ckan)
    conjuntos = []
    if status == 200:
        for pacote in json.loads(corpo)["result"]["results"]:
            if "2026" in pacote["name"]:
                conjuntos.append(pacote["name"])
    resultados.append(
        {
            "nome": "dados_abertos_2026",
            "url": ckan,
            "status": status,
            "conjuntos": conjuntos,
            "boletim_de_urna_publicado": any("boletim-de-urna" in c for c in conjuntos),
        }
    )
    return resultados


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--salvar", action="store_true", help="grava o resultado em dados/sondas/")
    args = parser.parse_args()

    momento = datetime.now(timezone.utc)
    resultados = sondar()
    for linha in resultados:
        extra = {k: v for k, v in linha.items() if k not in ("nome", "url", "status", "sha256")}
        print(f"{linha['status']:>4}  {linha['nome']:<22} {json.dumps(extra, ensure_ascii=False)}")

    if args.salvar:
        pasta = Path(__file__).resolve().parent.parent / "dados" / "sondas"
        pasta.mkdir(parents=True, exist_ok=True)
        arquivo = pasta / f"sondagem-{momento:%Y%m%dT%H%M%SZ}.json"
        arquivo.write_text(
            json.dumps({"momento_utc": momento.isoformat(), "resultados": resultados}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\ngravado em {arquivo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
