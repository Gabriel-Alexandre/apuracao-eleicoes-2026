# ESTADO: onde o trabalho parou

**Atualizado em:** 05/out/2026.

Uma sessão nova consegue continuar lendo só este arquivo. Ele não guarda método: isso é [`docs/PLANO.md`](docs/PLANO.md).

## Em uma frase

O planejamento está escrito e as fontes foram testadas ao vivo. Nenhum dado por seção foi baixado em massa e nenhuma análise rodou. A execução começa quando o autor pedir.

## O que está pronto

| Peça | Estado |
|---|---|
| Plano e método | ✅ `docs/PLANO.md` |
| Inventário de dados, com sondagem ao vivo de 05/out | ✅ `docs/FONTES_DE_DADOS.md` |
| Pré-registro dos critérios | ⬜ rascunho em `docs/PRE_REGISTRO.md`, **vale só depois de aprovado e gravado em commit** |
| Doutrina | ✅ `.cursor/rules/apuracao-fundamentos.mdc` |
| Sondagem reproduzível | ✅ `ferramentas/sondar-fontes.py` |
| Repositório | git local, sem commit e sem remoto |

## O que falta, em ordem de dependência de dados

1. Pré-registro aprovado e gravado em commit (Fase 0).
2. Coleta com manifesto (Fase 1).
3. Validação, a começar pelo fuso da hora de recebimento (Fase 2, T2.4).
4. Reconstrução da curva (Fase 3), perguntas (Fase 4), revisão adversarial (Fase 5), relatório (Fase 6).

As decisões que são do autor estão em `docs/PLANO.md` §14.

## O que observar ao retomar

- O CSV de boletim de urna de 2026 (`resultados-2026-boletim-de-urna`) não estava publicado em 05/out. `python ferramentas/sondar-fontes.py` mostra se já saiu.
- Os arquivos por seção de 2022 já saíram do ar no site de resultados. Os de 2026 estão no ar; a coleta com hash é o que garante a reprodução depois.
