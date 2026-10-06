# Apuração 2026: a noite do 1º turno, medida com os dados públicos

Projeto aberto que usa os boletins de urna publicados pelo TSE para refazer a apuração do 1º turno da eleição presidencial de 04/10/2026 ao longo do tempo, e responder com número e fonte às perguntas que a noite levantou:

- por que a vantagem do primeiro colocado diminuiu durante a contagem;
- o que entrou no intervalo de cerca de uma hora em que a tela de Presidente ficou parada;
- se cada número exibido naquela noite é a soma de boletins reais que já tinham chegado;
- por que o voto de governador e de senador não se converteu da mesma forma no voto de presidente;
- como 2026 se compara com 2014, 2018 e 2022.

> **Estado:** planejamento. Nenhuma análise foi rodada. O método está em [`docs/PLANO.md`](docs/PLANO.md), os critérios em [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md) e o inventário de dados em [`docs/FONTES_DE_DADOS.md`](docs/FONTES_DE_DADOS.md).

## O que este projeto não consegue dizer

Ele começa no boletim que cada urna imprimiu e publicou. Não audita o software da urna, não vê o sistema interno do TSE e não sabe como cada pessoa votou. Onde os dados públicos fecham entre si, o relatório diz "consistente com". Onde não fecham, diz "não explicado por", com o endereço exato (seção, horário, cargo).

## Mapa

| Caminho | O que tem |
|---|---|
| `docs/PLANO.md` | o método, fase a fase |
| `docs/PRE_REGISTRO.md` | os testes e os critérios, escritos antes de olhar os dados |
| `docs/FONTES_DE_DADOS.md` | o que existe, o que foi testado e o que não existe |
| `ferramentas/` | scripts (hoje: `sondar-fontes.py`) |
| `dados/` | manifesto e dados derivados; o dado bruto pesado fica fora do git |
| `ESTADO.md` | onde o trabalho parou |
| `.cursor/rules/` | a doutrina do projeto |

## Refazer a sondagem das fontes

```bash
python ferramentas/sondar-fontes.py
```

Só a biblioteca padrão do Python 3.10 ou mais novo.
