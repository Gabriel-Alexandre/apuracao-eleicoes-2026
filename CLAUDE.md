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
- Rodar teste antes do pré-registro gravado.
- Escrever "fraude" ou "provou que não houve fraude".
- Fazer commit, criar remoto ou tornar o repositório público sem o autor pedir.
- Baixar em massa sem teto de requisições e sem manifesto.
