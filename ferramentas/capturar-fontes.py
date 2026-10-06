"""Captura as fontes de texto citadas no projeto: URL, hora (UTC), status, tamanho, sha256 e titulo.

O corpo da pagina fica em dados/brutos/fontes/ (fora do git, direitos autorais da imprensa); o que vai para o
git e o registro dados/CAPTURAS.csv. Pagina que recusa o robo (403) fica registrada como tal.

Uso: python ferramentas/capturar-fontes.py
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "dados" / "brutos" / "fontes"
UA = "Mozilla/5.0 (compatible; apuracao-eleicoes-2026; analise aberta)"

FONTES = [
    ("apuracao", "https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/congestionamento-no-sistema-de-dados-gerou-atraso-na-apuracao-diz-tse"),
    ("apuracao", "https://jornaldebrasilia.com.br/noticias/politica-e-poder/sistema-do-tse-trava-durante-apuracao-presidencial-e-deixa-resultados-parados-por-mais-de-uma-hora/"),
    ("apuracao", "https://www.boatos.org/politica/tse-vai-investigar-se-atraso-na-divulgacao-de-resultados-das-eleicoes-tem-relacao-com-fraude-contra-flavio-bolsonaro.html"),
    ("apuracao", "https://www.cnnbrasil.com.br/eleicoes/tse-registrou-congestionamento-no-sistema-de-divulgacao-diz-nunes-marques/"),
    ("apuracao", "https://www.bloomberglinea.com.br/brasil/ao-vivo-brasil-vai-as-urnas-para-eleger-presidente-governadores-e-congresso/"),
    ("apuracao", "https://tribunadonorte.com.br/tn-nas-eleicoes-2026/90-das-urnas-apuradas-flavio-tem-4802-e-lula-chega-a-44/"),
    ("apuracao", "https://www.tribunadosertao.com.br/geral/2026/10/04/990634-com-90-das-urnas-apuradas-lula-segue-atras-de-flavio"),
    ("apuracao", "https://sampi.net.br/ovale/noticias/3009139/geral/2026/10/com-648-de-votos-apurados-flavio-tem-4958-e-lula-tem-4225"),
    ("apuracao", "https://sampi.net.br/ovale/noticias/3009166/geral/2026/10/com-85-de-apuracao-flavio-tem-4847-lula-esta-com-4349"),
    ("apuracao", "https://www.band.com.br/politica/eleicoes/eleicoes-2026-veja-a-diferenca-de-votos-entre-flavio-e-lula-no-1o-turno"),
    ("apuracao", "https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/presidente-do-tse-conclui-1o-turno-das-eleicoes-2026-e-projeta-mesma-tranquilidade-para-segunda-fase-do-pleito"),
    ("apuracao", "https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/flavio-bolsonaro-e-lula-vao-disputar-o-2o-turno-para-a-presidencia-da-republica"),
    ("processo", "https://www.diariodepernambuco.com.br/brasil/2026/08/11721101-totalizacao-dos-votos-e-aberta-auditavel-e-segura-diz-tse.html"),
    ("processo", "https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados"),
    ("apoio", "https://www.cnnbrasil.com.br/eleicoes/governadores-eleitos-flavio-lula/"),
    ("apoio", "https://www.spacemoney.com.br/politica/governadores-eleitos-2026-apoio-flavio-lula"),
    ("apoio", "https://ranking.org.br/en/articles/quem-flavio-bolsonaro-apoia-senado-2026"),
    ("apoio", "https://www.metropoles.com/sao-paulo/tenho-certeza-que-a-vitoria-esta-chegando-diz-tarcisio-sobre-flavio"),
    ("apoio", "https://tribunadejundiai.com.br/politica/eleicoes-2026/tarcisio-apoio-flavio-bolsonaro-2026/"),
    ("apoio", "https://acritica.net/eleicoes-2026/tarcisio-apoio-incondicional-flavio-bolsonaro-sao-paulo/"),
    ("apoio", "https://www.cnnbrasil.com.br/eleicoes/divisao-bancada-senado/"),
    ("apoio", "https://www.cnnbrasil.com.br/politica/oito-governadores-eleitos-se-aliam-a-bolsonaro-e-quatro-apoiam-lula/"),
    ("apoio", "https://www.gazetadopovo.com.br/eleicoes/2022/governadores-eleitos-primeiro-turno-aliados-lula-bolsonaro/"),
    ("apoio", "https://agenciabrasil.ebc.com.br/politica/noticia/2018-10/bolsonaro-recebeu-apoio-de-15-dos-27-governadores-eleitos"),
    ("apoio", "https://www.gazetadopovo.com.br/eleicoes/2022/eleicoes-governador-eleitos-apoios-lula-bolsonaro/"),
    ("apoio", "https://revistaoeste.com/politica/eleicoes-2022/placar-dos-governadores-veja-quem-apoia-bolsonaro-e-lula-no-2o-turno/"),
    ("metodo", "https://en.wikipedia.org/wiki/Election_forensics"),
    ("metodo", "https://arxiv.org/pdf/1410.6059"),
]


def main() -> int:
    PASTA.mkdir(parents=True, exist_ok=True)
    out = RAIZ / "dados" / "CAPTURAS.csv"
    linhas = []
    for tipo, url in FONTES:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
        status, corpo = 0, b""
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                status, corpo = r.status, r.read()
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:  # noqa: BLE001
            status = 0
            corpo = repr(e).encode()
        sha = hashlib.sha256(corpo).hexdigest() if status == 200 and corpo else ""
        titulo = ""
        if status == 200:
            m = re.search(rb"<title[^>]*>(.*?)</title>", corpo[:200000], re.S | re.I)
            titulo = re.sub(r"\s+", " ", m.group(1).decode("utf-8", "ignore")).strip()[:160] if m else ""
            (PASTA / f"{sha[:16]}.bin").write_bytes(corpo)
        linhas.append({"tipo": tipo, "url": url, "consultado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": status, "bytes": len(corpo) if status == 200 else 0, "sha256": sha, "titulo": titulo})
        print(status, url[:90], flush=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"{sum(1 for l in linhas if l['status'] == 200)} de {len(linhas)} capturadas; registro em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
