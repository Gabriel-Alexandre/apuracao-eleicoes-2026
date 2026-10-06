"""Baixa os CSV de boletim de urna (BU na Web) de 2014, 2018 e 2022 dos dados abertos do TSE.

Le dados/fontes-historicas.json (gerado da API CKAN do portal), baixa cada zip por UF com o
arquivo .sha512 publicado ao lado, confere o hash e guarda em dados/brutos/historico/<ano>-<turno>/.
Retomavel: arquivo ja baixado e conferido nao e baixado de novo.

Uso:
    python ferramentas/baixar-historico.py [--anos 2022 2018 2014] [--turnos 1 2]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UA = "apuracao-eleicoes-2026/0.1 (analise aberta; github.com/Gabriel-Alexandre)"


def baixar(url: str, destino: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = destino.with_suffix(destino.suffix + ".part")
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.replace(destino)


def sha(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def hash_publicado(url_zip: str) -> tuple[str, str] | None:
    for suf, algo in ((".sha512", "sha512"), (".sha1", "sha1")):
        try:
            req = urllib.request.Request(url_zip + suf, headers={"User-Agent": UA})
            txt = urllib.request.urlopen(req, timeout=60).read().decode("latin1").strip()
            return algo, txt.split()[0].lower()
        except urllib.error.URLError:
            continue
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--anos", nargs="*", default=["2022", "2018", "2014"])
    p.add_argument("--turnos", nargs="*", default=["1", "2"])
    args = p.parse_args()
    fontes = json.loads((RAIZ / "dados" / "fontes-historicas.json").read_text(encoding="utf-8"))
    registro = []
    for ano in args.anos:
        for turno in args.turnos:
            itens = fontes.get(f"{ano}-{turno}", [])
            pasta = RAIZ / "dados" / "brutos" / "historico" / f"{ano}-{turno}"
            pasta.mkdir(parents=True, exist_ok=True)
            for nome, url in itens:
                destino = pasta / url.rsplit("/", 1)[1]
                esperado = hash_publicado(url)
                if destino.exists() and esperado and sha(destino, esperado[0]) == esperado[1]:
                    registro.append((ano, turno, destino.name, "ja conferido"))
                    continue
                for tentativa in range(4):
                    try:
                        baixar(url, destino)
                        break
                    except (urllib.error.URLError, TimeoutError) as e:
                        print("falha", url, e, flush=True)
                        time.sleep(5 * (tentativa + 1))
                ok = bool(esperado) and sha(destino, esperado[0]) == esperado[1]
                registro.append((ano, turno, destino.name, "conferido" if ok else "HASH NAO CONFERE OU AUSENTE"))
                print(ano, turno, destino.name, registro[-1][3], flush=True)
    ruins = [r for r in registro if r[3].startswith("HASH")]
    print(f"{len(registro)} arquivos, {len(ruins)} com problema")
    return 1 if ruins else 0


if __name__ == "__main__":
    sys.exit(main())
