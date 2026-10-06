# A apuração de 4 de outubro de 2026, em linguagem simples

Este projeto pegou os dados públicos do TSE e refez, boletim por boletim, a noite da apuração do 1º turno. A versão completa, com os números e os testes, está em [`RELATORIO.md`](RELATORIO.md). Este texto é o resumo para quem não quer entrar nos detalhes.

**Quem fez.** Uma IA (Claude), a pedido do autor do repositório. Os critérios dos testes foram escritos e gravados antes de olhar os dados, e toda mudança de critério está registrada. Nenhuma pessoa revisou os resultados antes da publicação.

## O que o projeto responde

**1. Os números do TSE batem com os boletins das urnas?**
Sim. Cada urna imprime um boletim com os votos da sua seção, e o TSE publica esses boletins. Somei os de 499.192 seções e comparei com o resultado oficial, município por município e cargo por cargo. Em 99,96% das comparações a conta fecha exata. A diferença que sobra são 3.935 votos de Presidente (0,0033% do total), que ficam em 15 seções cujos arquivos o TSE não publicou.

**2. Quem estava na frente, e por que a diferença diminuiu?**
Flávio Bolsonaro ficou na frente de Lula durante toda a apuração, depois dos primeiros 0,4% das seções. A diferença chegou a 10,8 pontos no começo da noite e terminou em 1,9. O motivo é a ordem em que os estados terminaram de contar: Sul e Centro-Oeste chegaram primeiro, e o Nordeste, onde Lula teve muito mais votos, chegou por último. Capital ou interior, cidade grande ou pequena, seção grande ou pequena, praticamente não mudam isso. Em 2022 foi igual: a vantagem inicial de Bolsonaro virou vantagem de Lula quando o Nordeste entrou.

**3. O que aconteceu na hora em que a tela parou?**
A tela de Presidente ficou cerca de uma hora sem atualizar. Quando voltou, os números que mostrou batem, com diferença de centésimos de ponto, com a soma dos boletins que já tinham chegado até alguns minutos antes. A mudança que se viu na volta é a que esses boletins somam. Um detalhe ficou sem explicação: no registro de chegada dos boletins há um intervalo de 28 minutos sem nenhum boletim registrado, e logo depois uma enxurrada de 20.171 em 6 minutos, de urnas que tinham fechado horas antes. Isso parece fila, mas só o registro interno do TSE diz o que parou. O projeto não consegue ver isso.

**4. A diferença entre o voto em Tarcísio e o voto em Flávio, em São Paulo, é estranha?**
Tarcísio teve 62,7% dos votos para governador e Flávio 51,9% para presidente. Tarcísio apoia Flávio, então a pergunta é se uma diferença de 11 pontos é comum. Comparei com 30 outros casos de governadores que apoiavam um candidato a presidente, em 2022 e 2026. Quase metade dessa diferença (45%) é uma questão de conta: em São Paulo, mais eleitores votaram em branco ou nulo para governador do que para presidente, e com isso o percentual do governador, que é calculado só sobre os votos válidos, sobe. Medidos sobre quem compareceu, Tarcísio tem 54,8% e Flávio 48,9%. O que sobra está dentro do que aconteceu em outros estados. A diferença aparece em todos os 645 municípios paulistas, e não em poucas seções. A estimativa é que cerca de 87% dos eleitores de Tarcísio votaram em Flávio, e o resto escolheu outros nomes, principalmente Cury, Caiado e Renan Santos. Essa estimativa não é o voto de ninguém, é uma conta feita com totais.

**5. O PL elegeu muitos senadores. Isso virou voto para presidente?**
Os 19 senadores do PL foram eleitos em estados onde Flávio ficou na frente, e nenhum em estado onde Lula ficou na frente ou empatou. Dentro de cada estado, os municípios em que Flávio foi mais votado são os mesmos em que o candidato do PL ao Senado foi mais votado, tanto quanto em eleições anteriores. O critério escrito antes dos testes marcou 8 estados para olhar melhor, porque candidatos do PL e apoiados por Flávio tiveram mais votos do que o partido do presidente costumava ter. O projeto não encontrou a causa. Na Bahia, no Ceará e em Pernambuco, onde os candidatos do PL perderam, o resultado é compatível com eleitores que usaram um dos dois votos do Senado de forma diferente do voto para presidente, mas os dados não separam essa hipótese de outras.

**6. Tem algum município estranho?**
Nenhum município passou nos três testes ao mesmo tempo, nem para Flávio, nem para Lula, nem no teste de comparação com 2022.

## O que o projeto não consegue dizer

- Se a urna gravou corretamente o voto de cada eleitor. O projeto começa no boletim que a urna imprimiu.
- A causa da parada na tela. Só o registro interno do TSE sabe.
- Como cada pessoa votou. O voto é secreto.
- Se as assinaturas digitais dos boletins estão corretas: o projeto não conseguiu verificar.

## Como conferir

Todo o caminho está no repositório, com os dados e os scripts: [`docs/REPLICAR.md`](docs/REPLICAR.md). Qualquer pessoa pode refazer e criticar.
