# Como refazer tudo, do zero

Quem quiser conferir ou criticar o projeto consegue chegar aos mesmos números seguindo estes passos. Todo número do relatório sai de um script rodado sobre arquivo público; o `RESUMO.json` de `resultados/` guarda cada um.

## Requisitos

- Python 3.10 ou mais novo.
- Espaço em disco: ~12 GB (≈ 6 GB de boletins de 2026 e do resultado oficial, ≈ 4 GB de CSV de 2014 a 2022 e ≈ 2 GB de tabelas derivadas).
- Internet. A coleta de 2026 faz ≈ 1,0 milhão de requisições e leva de 1 a 3 horas com o teto padrão (120 por segundo).

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

## Passo a passo

| Passo | Comando | O que faz |
|---|---|---|
| 1 | `python ferramentas/sondar-fontes.py` | confere que os endereços do TSE ainda respondem |
| 2 | `python -m apuracao coletar` | baixa a hora de recebimento (`aux.json`) e o boletim (`bu.dat`) de cada seção de 2026 para `dados/brutos/<uf>.sqlite`. Retomável: pode ser interrompido e rodado de novo |
| 3 | `python -m apuracao oficial` | baixa o resultado oficial por país, UF e município (Presidente, Governador, Senador) |
| 3b | `python -m apuracao manifesto` | grava `dados/MANIFESTO.json` com o resumo sha256 de cada UF e do oficial |
| 4 | `python ferramentas/baixar-historico.py --anos 2022 2018` | baixa os CSV de boletim de urna de 2018 e 2022, confere o hash publicado |
| 5 | `python ferramentas/derivar-historico.py` | transforma esses CSV em tabelas por seção |
| 6 | `python ferramentas/capturar-fontes.py` | captura as páginas de imprensa e do TSE citadas, com sha256 |
| 7 | `python ferramentas/analise-1-validacao-e-curva.py` | valida os dados (P4), o fuso (T2.4) e reconstrói a curva (P1, P2, P3) |
| 8 | `python ferramentas/analise-2-historico-uf-senado.py` | 2022 (P7), governador × presidente (P5), Senado × presidente (P6) |
| 9 | `python ferramentas/analise-3-anomalias.py` | testes de anomalia (P8) |
| 10 | `python ferramentas/analise-4-figuras.py` | figuras |
| 11 | `python ferramentas/analise-5-relatorio.py` | escreve `RELATORIO.md` a partir de `RESUMO.json` |

## Como conferir que nada foi alterado

- `dados/pontos-da-tela.csv`, `dados/apoios.csv` e `dados/senado-apoio-flavio.csv` são entradas escritas à mão a partir de fontes capturadas. `dados/CAPTURAS.csv` guarda o hash de cada página.
- `docs/PRE_REGISTRO.md` foi gravado em commit **antes** das análises. O histórico do git mostra a ordem: o commit do pré-registro é anterior ao dos resultados, e toda mudança de critério está na tabela da §9, dizendo se foi feita antes ou depois de ver cada resultado.
- Cada UF tem um resumo sha256 dos arquivos coletados (`dados/MANIFESTO.json`). Quem refizer a coleta compara o seu resumo com o publicado. ⚠️ O TSE pode republicar arquivos por seção; se o resumo diferir, compare por seção antes de concluir qualquer coisa.

## O que não dá para refazer sem o TSE

- A sequência das telas da noite (o TSE sobrescreve o arquivo). O projeto a substitui pela reconstrução e a confere contra os pontos da imprensa.
- O log interno do sistema de divulgação.
- A verificação da assinatura digital de cada boletim (precisa de certificados e especificação do TSE). Ver `RELATORIO.md`, seção de limites.
