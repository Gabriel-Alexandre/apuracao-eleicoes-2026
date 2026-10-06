# CLAUDE.md: como operar neste repositório

As regras moram em `.cursor/rules/*.mdc`, que o Cursor carrega sozinho e o Claude Code não. Este arquivo é roteador: se um fato aqui contradisser o arquivo dono, o dono ganha.

## Leia antes de qualquer coisa

| Ordem | Arquivo | Para quê |
|---|---|---|
| 1 | `ESTADO.md` | onde o trabalho parou |
| 2 | `.cursor/rules/apuracao-fundamentos.mdc` | a doutrina, sempre |
| 3 | `docs/PLANO.md` | o método e as fases |
| 4 | `docs/PRE_REGISTRO.md` | os critérios; nenhum teste roda antes de ele estar em commit |
| 5 | `docs/FONTES_DE_DADOS.md` | endereços, códigos e o que não existe |

## O que nunca fazer

- Dar número que não saiu de script sobre dado com hash.
- Mudar critério sem registrar na tabela da §9 do pré-registro, dizendo se foi antes ou depois de ver o resultado.
- Escrever número à mão no relatório: ele vem de `resultados/RESUMO.json` pelos modelos `docs/*.modelo.md`.
- Escrever "fraude" ou "provou que não houve fraude".
- Mudar a visibilidade do repositório sem o autor pedir. Ele está **público desde 06/out/2026**, por decisão do autor, e ⚠️ **ainda sem licença** (decisão dele).
- Dizer que o alinhamento de alguém é o do partido: vale o apoio declarado, com fonte (`docs/PRE_REGISTRO.md` §0.1).
- Baixar em massa sem teto de requisições e sem manifesto.
