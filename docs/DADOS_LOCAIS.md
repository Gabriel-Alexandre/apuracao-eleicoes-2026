# Dados locais: o que foi apagado e como refazer

**14/out/2026, pedido do autor:** depois do vídeo longo 8 pronto, apagar as bases pesadas baixadas para a pesquisa dos vídeos longos, mantendo tudo documentado. Este projeto é o do **vídeo longo 5** (a apuração do 1º turno).

## O que foi apagado

| Pasta ou arquivo | O que tinha | Tamanho | Como refazer (`docs/REPLICAR.md`) |
|---|---|---|---|
| `dados/brutos/<uf>.sqlite` (28) e `dados/brutos/oficial.sqlite` | a hora de recebimento (`aux.json`) e o boletim (`bu.dat`) de cada seção de 2026, e o resultado oficial | ~7,2 GB | passos 2, 3 e 3b: `python -m apuracao coletar`, `python -m apuracao oficial`, `python -m apuracao manifesto` (1 a 3 horas) |
| `dados/brutos/historico/` | os CSV de boletim de urna de 2018 e 2022 do TSE | ~3,6 GB | passo 4: `python ferramentas/baixar-historico.py --anos 2022 2018` |

**Total liberado: ~10,8 GB.** Para conferir um download refeito: o `resumo_sha256` de cada UF tem de bater com o de `dados/MANIFESTO.json`.

## O que ficou no disco, de propósito

| Pasta | Por quê |
|---|---|
| `dados/brutos/fontes/` (11 MB) | as páginas de imprensa e do TSE capturadas; página muda ou sai do ar e não volta igual |
| `dados/derivados/` (~183 MB) | as tabelas por seção que os projetos `presidente-primeiro-turno-2026` (vídeo 7) e `alegacoes-fraude-eleicoes-2026` (vídeo 8) leem; com elas, as análises daqui e de lá rodam sem baixar de novo |
| `dados/logs/` | saídas das execuções, leves |

## O que nunca dependeu dos brutos

`resultados/` inteiro (o `RESUMO.json` com cada número, as figuras e os gráficos do vídeo), o `RELATORIO.md`, o código, o `dados/MANIFESTO.json` e as capturas listadas em `dados/CAPTURAS.csv`: tudo no git.

⚠️ **Risco registrado uma vez:** o TSE já tirou do ar arquivos de eleição anterior (os logs de 2022). Se isso acontecer com os de 2026, o download não volta igual; o `dados/MANIFESTO.json`, que está no git, continua provando o que foi lido (endereço, hora, tamanho e sha256 de cada arquivo).
