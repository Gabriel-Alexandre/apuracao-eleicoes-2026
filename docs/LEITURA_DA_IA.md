# A leitura da IA, etapa por etapa

**Escrito em:** 06/out/2026. **O que é:** a opinião da IA que executou o processo sobre o resultado de cada etapa, com a comparação que sustenta cada opinião. É o lastro do que o vídeo diz como *"a leitura da IA"*.

> ⚠️ **Opinião não é prova.** O [`RELATORIO.md`](../RELATORIO.md) diz o que os dados fecham entre si e o que não fecham. Este arquivo vai um passo além: diz **qual é a leitura mais provável** de cada resultado, comparando com 2022 e com outros estados. Onde a opinião não pode ser provada com dado público, isso está dito. Nenhuma opinião aqui afirma que houve ou que não houve irregularidade dentro da urna ou do sistema do TSE, porque nenhum dado público alcança esses dois lugares.

Todo número sai de [`resultados/RESUMO.json`](../resultados/RESUMO.json) e dos CSV de [`resultados/`](../resultados). Os gráficos citados estão em [`resultados/figuras/video/`](../resultados/figuras/video).

---

| # | Etapa | O resultado | A comparação | A leitura da IA |
|---|---|---|---|---|
| 1 | **Os dados** | 499.192 boletins (6,55 GB), cada arquivo com sha256 em `dados/MANIFESTO.json` | · | a base está completa: só 15 seções não têm arquivo publicado pelo TSE |
| 2 | **A soma contra o oficial** | 99,96% das comparações município e cargo iguais voto por voto; sobra de 3.935 votos de presidente nas 15 seções sem arquivo | · | **resolvido.** O número anunciado pelo TSE é a soma das urnas que ele mesmo publicou. Voto que aparecesse no total sem estar em boletim apareceria nessa conta, e não apareceu |
| 3 | **A noite refeita** | 13 dos 14 placares publicados pela imprensa batem com a soma dos boletins, com diferença de centésimos (`g06`) | · | os placares que passaram na televisão saíram de boletins que já tinham chegado |
| 4 | **A queda da vantagem** | de 10,55 pontos (10% das seções) para 1,87 no fim: **8,7 pontos**. A ordem das regiões explica 69% (estado e capital, 78%); com a ordem sorteada a vantagem fica perto de 2 pontos a noite toda (`g03`, `g04`) | 2022, 1º turno: **10,7 pontos**, e virou (Lula passou com 68,2% das seções); 2022, 2º turno: 5,8 e virou (`g15`) | **normal.** É o jeito da apuração brasileira, com Sul e Centro-Oeste chegando antes do Nordeste. A de 2026 caiu **menos** que a do 1º turno de 2022. A queda começou às 17:58, mais de uma hora antes de a tela parar |
| 5 | **A tela parada** | travou às 19h06 (64,81%) e voltou às 20h08 (84,96%); nas duas pontas, o placar é a soma dos boletins recebidos até 1,9 e 8,5 minutos antes | · | **normal.** A tela travou, e o número que voltou era a soma de boletins reais |
| 6 | **O registro de chegada** | nenhum boletim registrado das 19:31:50 às 19:59:22 (**27,5 min**), e depois 20.171 em 6 minutos, de urnas que tinham emitido o boletim em mediana às 17:19 (espera mediana de 162 min); a margem desse lote é a esperada pras regiões dele | maior buraco de 2022: **7,4 min** no 1º turno, 4,6 no 2º (`g16`). Pico de chegada: 5.119 por minuto, contra 3.791 em 2022 | **pede explicação.** Tem cara de fila travada que destravou de uma vez, o que combina com o congestionamento que o TSE declarou. Nenhum boletim sumiu e o lote votou como as regiões dele votam. A causa fica dentro do sistema do TSE, e é a única coisa da noite que, na leitura da IA, merece explicação oficial |
| 7 | **São Paulo** | Tarcísio 62,65%, Flávio 51,93% (10,7 pontos). 12,5% de quem votou anulou ou votou em branco pra governador, contra 5,9% pra presidente; sobre quem votou, a diferença é de 5,9 pontos (45% era base). Aparece nas 645 cidades (a menor, 4,7). Estimativa: 87% dos eleitores do Tarcísio votaram no Flávio; 9,4% no Cury, no Caiado e no Renan Santos | entre os aliados do Flávio em 2026 é a maior; em 2022, Ratinho Júnior (PR) ficou 14,4 pontos acima do Bolsonaro, Zema (MG) 12,6 e Wanderlei Barbosa (TO) 14,1 (`g17`) | **normal.** É voto dividido: eleitor do governador que escolheu outro nome pra presidente. O tamanho já aconteceu com aliados do Bolsonaro em 2022 |
| 8 | **O Senado** | 19 senadores do PL, todos em estados onde o Flávio ganhou; zero nos 12 estados com o Lula na frente ou empate. Ligação por cidade entre o voto no Flávio e no candidato do PL: 0,79 | 2022: 0,65; 2018: 0,70 (`g11`) | **normal, e mais intenso.** É o voto casado de sempre. Nos estados do Nordeste em que o PL foi melhor do que costuma (BA, CE, PE), a explicação mais provável é o segundo voto pro Senado indo pro candidato do PL mesmo de quem votou no Lula |
| 9 | **As cidades** | 5.273 testadas em três testes; nenhuma nos três ao mesmo tempo | o mesmo teste em 2022: nenhuma (`g12`) | **normal.** O tipo de alteração que esses testes procuram não aparece nessa eleição |

---

## O veredito

**Em tudo o que os dados públicos mostram, a apuração de 2026 se comportou como a de 2022.** A soma das urnas bate com o resultado oficial, a vantagem caiu pelo motivo de sempre e caiu menos que em 2022, a tela parada não mudou o número que voltou, São Paulo tem cara de voto dividido e nenhuma cidade ficou fora do padrão.

**O único ponto fora da curva** é o buraco de 27,5 minutos sem nenhum boletim no registro de chegada, quase quatro vezes o maior de 2022. A leitura mais provável é uma fila travada, mas só o registro interno do TSE responde.

**O que a IA não consegue dizer:** o que aconteceu dentro das urnas e dentro do sistema do TSE, porque nenhum dado público mostra esses dois lugares.
