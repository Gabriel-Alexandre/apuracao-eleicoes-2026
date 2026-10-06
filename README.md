# Apuração 2026: a noite do 1º turno, medida com os dados públicos

Projeto aberto que usa os boletins de urna publicados pelo TSE para refazer a apuração do 1º turno da eleição presidencial de 04/10/2026 ao longo do tempo, e responder com número e fonte às perguntas que a noite levantou:

- por que a vantagem do primeiro colocado diminuiu durante a contagem;
- o que entrou no intervalo de cerca de uma hora em que a tela de Presidente ficou parada;
- se cada número exibido naquela noite é a soma de boletins reais que já tinham chegado;
- por que o voto de governador e de senador não se converteu da mesma forma no voto de presidente;
- como 2026 se compara com 2014, 2018 e 2022.

> **Estado:** executado. Resultados em [`RELATORIO.md`](RELATORIO.md) (completo), [`RESUMO_SIMPLES.md`](RESUMO_SIMPLES.md) (linguagem simples) e [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md) (a opinião da IA sobre cada etapa, com a comparação com 2022 e com outros estados). Método em [`docs/PLANO.md`](docs/PLANO.md), critérios gravados antes dos resultados em [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md), erros achados no caminho em [`docs/CORRECOES.md`](docs/CORRECOES.md) e como refazer tudo em [`docs/REPLICAR.md`](docs/REPLICAR.md).

## O que este projeto não consegue dizer

Ele começa no boletim que cada urna imprimiu e publicou. Não audita o software da urna, não vê o sistema interno do TSE e não sabe como cada pessoa votou. Onde os dados públicos fecham entre si, o relatório diz "consistente com". Onde não fecham, diz "não explicado por", com o endereço exato (seção, horário, cargo).

## Mapa

| Caminho | O que tem |
|---|---|
| `RELATORIO.md`, `RESUMO_SIMPLES.md` | os resultados (gerados de `resultados/RESUMO.json`) |
| `docs/` | plano, pré-registro, fontes, correções, revisão adversarial, como replicar |
| `apuracao/` | biblioteca: coletor, decodificador de boletim, curva, análises |
| `ferramentas/` | scripts numerados na ordem de execução |
| `resultados/` | tabelas CSV, figuras e `RESUMO.json` |
| `dados/` | entradas escritas à mão, manifesto com sha256 e dados derivados; o bruto pesado fica fora do git |
| `tests/` | testes do decodificador e das contas |
| `ESTADO.md` | onde o trabalho parou |
| `.cursor/rules/` | a doutrina do projeto |

## Refazer

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

Passo a passo completo, com espaço em disco e tempo: [`docs/REPLICAR.md`](docs/REPLICAR.md).
