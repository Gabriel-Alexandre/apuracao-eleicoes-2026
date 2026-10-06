# ESTADO: onde o trabalho parou

**Atualizado em:** 06/out/2026.

Uma sessão nova consegue continuar lendo só este arquivo. Ele não guarda método: isso é [`docs/PLANO.md`](docs/PLANO.md).

## Em uma frase

A execução de ponta a ponta está feita: os boletins de 28 UFs foram coletados, validados contra o resultado oficial, a noite foi reconstruída pela hora de recebimento, as perguntas P1 a P8 foram respondidas, o relatório foi gerado e passou por revisão adversarial (20 de 20 checagens). O repositório é **público desde 06/out/2026** (decisão do autor), ainda **sem licença**. Falta só o que depende do autor: gravar o vídeo e decidir o que publicar. O roteiro e o pacote de publicação do vídeo estão no repositório de documentação dele, e os 17 gráficos do vídeo estão em `resultados/figuras/video/`.

## O que está pronto

| Peça | Estado |
|---|---|
| Plano, método e fontes | ✅ `docs/PLANO.md`, `docs/FONTES_DE_DADOS.md` |
| Pré-registro gravado antes dos resultados, com emendas datadas | ✅ `docs/PRE_REGISTRO.md` (§0.1 alinhamento por apoio declarado, §9 emendas, §10 exploratórias) |
| Coleta de 2026 (499.192 seções, 998.468 arquivos, 6,5 GB) com sha256 | ✅ `dados/MANIFESTO.json` (bruto fora do git, em `dados/brutos/`) |
| Validação aritmética contra o oficial | ✅ conta fecha exata em 99,96% das linhas município × cargo; a sobra são 3.935 votos de Presidente em 15 seções que o TSE não publicou |
| Curva reconstruída e comparada com 14 pontos da imprensa | ✅ 13 encaixam, P02 não encaixa (declarado) |
| Relatório completo e resumo simples | ✅ `RELATORIO.md`, `RESUMO_SIMPLES.md`, gerados por `ferramentas/analise-5-relatorio.py` a partir de `resultados/RESUMO.json` |
| Revisão adversarial | ✅ `docs/REVISAO_ADVERSARIAL.md` (20 de 20) |
| Segunda validação (06/out) | ✅ toda a cadeia refeita do zero sem nenhuma diferença nos resultados, e recontagem independente em `ferramentas/validacao-independente-*.py` (15 de 15). Achou 1 número a corrigir: a diferença de votos em SP agora é a oficial, 1.569.851 |
| Erros achados no caminho | ✅ `docs/CORRECOES.md` |
| Testes | ✅ `python -m pytest -q` |

## O que o projeto concluiu, em resumo

- A ordem de chegada dos estados explica a queda da vantagem (de 10,8 para 1,9 pontos): Sul e Centro-Oeste primeiro, Nordeste por último. Em 2022 foi igual.
- A parada de cerca de uma hora na tela de Presidente é consistente com atraso de exibição; a causa técnica não é verificável com dados públicos.
- A diferença entre Tarcísio (62,65%) e Flávio (51,93%) em São Paulo: 45% dela é diferença de base de votos válidos; o resto fica dentro do que ocorreu em 30 outros casos de governador aliado.
- Os 19 senadores do PL foram eleitos em estados onde Flávio liderou; 8 estados foram marcados pelo critério literal, com ressalvas no relatório.
- Nenhum município passou nos três testes de anomalia ao mesmo tempo.

## Limites declarados

- Sem verificação da assinatura digital dos boletins.
- Causa da parada da tela não é verificável.
- A estimativa de para onde foi o voto é inferência ecológica.
- A maioria dos pontos da imprensa tem uma única fonte.
- A revisão adversarial foi feita pela mesma IA, não por pessoa.

## O que observar ao retomar

- O TSE pode republicar arquivos por seção; compare o `MANIFESTO.json` antes de concluir qualquer coisa.
- O vídeo (vídeo longo 5) só começa por decisão do autor. A doutrina de roteiro mora no repositório de documentação, não aqui.
