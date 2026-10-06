# A apuração de 4 de outubro de 2026, em linguagem simples

Este projeto pegou os dados públicos do TSE e refez, boletim por boletim, a noite da apuração do 1º turno. A versão completa, com os números e os testes, está em [`RELATORIO.md`](RELATORIO.md). Este texto é o resumo para quem não quer entrar nos detalhes.

**Quem fez.** Uma IA (Claude), a pedido do autor do repositório. Os critérios dos testes foram escritos e gravados antes de olhar os dados, e toda mudança de critério está registrada. Nenhuma pessoa revisou os resultados antes da publicação.

## O que o projeto responde

**1. Os números do TSE batem com os boletins das urnas?**
Sim. Cada urna imprime um boletim com os votos da sua seção, e o TSE publica esses boletins. Somei os de {{secoes_proprias_com_boletim}} seções e comparei com o resultado oficial, município por município e cargo por cargo. Em {{derivados.p4.pct_linhas_municipio_e_cargo_exatas|n=2}}% das comparações a conta fecha exata. A diferença que sobra são {{derivados.p4.votos_nominais_sem_correspondencia_presidente}} votos de Presidente ({{derivados.p4.pct_dos_validos_sem_correspondencia_presidente|n=4}}% do total), que ficam em 15 seções cujos arquivos o TSE não publicou.

**2. Quem estava na frente, e por que a diferença diminuiu?**
Flávio Bolsonaro ficou na frente de Lula durante toda a apuração, depois dos primeiros {{p1_resumo.pct_secoes_da_ultima_troca_de_lideranca|n=1}}% das seções. A diferença chegou a {{p1_resumo.margem_de_pico|n=1}} pontos no começo da noite e terminou em {{p1_resumo.margem_final|n=1}}. O motivo é a ordem em que os estados terminaram de contar: Sul e Centro-Oeste chegaram primeiro, e o Nordeste, onde Lula teve muito mais votos, chegou por último. Capital ou interior, cidade grande ou pequena, seção grande ou pequena, praticamente não mudam isso. Em 2022 foi igual: a vantagem inicial de Bolsonaro virou vantagem de Lula quando o Nordeste entrou.

**3. O que aconteceu na hora em que a tela parou?**
A tela de Presidente ficou cerca de uma hora sem atualizar. Quando voltou, os números que mostrou batem, com diferença de centésimos de ponto, com a soma dos boletins que já tinham chegado até alguns minutos antes. A mudança que se viu na volta é a que esses boletins somam. Um detalhe ficou sem explicação: no registro de chegada dos boletins há um intervalo de {{p2_maiores_vazios_de_recebimento_2026.0.minutos|n=0}} minutos sem nenhum boletim registrado, e logo depois uma enxurrada de {{p2_rajada_depois_do_vazio.boletins_na_rajada_de_6_minutos}} em 6 minutos, de urnas que tinham fechado horas antes. Isso parece fila, mas só o registro interno do TSE diz o que parou. O projeto não consegue ver isso.

**4. A diferença entre o voto em Tarcísio e o voto em Flávio, em São Paulo, é estranha?**
Tarcísio teve {{p5_classe_de_referencia.sp_gov_pct|n=1}}% dos votos para governador e Flávio {{p5_classe_de_referencia.sp_pres_pct|n=1}}% para presidente. Tarcísio apoia Flávio, então a pergunta é se uma diferença de {{p5_classe_de_referencia.sp_2026_lacuna_pontos|n=0}} pontos é comum. Comparei com {{derivados.p5_n.comparados_com_sp}} outros casos de governadores que apoiavam um candidato a presidente, em 2022 e 2026. Quase metade dessa diferença ({{p5_base_de_votos.sp_pct_da_lacuna_que_vem_da_base|n=0}}%) é uma questão de conta: em São Paulo, mais eleitores votaram em branco ou nulo para governador do que para presidente, e com isso o percentual do governador, que é calculado só sobre os votos válidos, sobe. Medidos sobre quem compareceu, Tarcísio tem {{p5_base_de_votos.sp_tarcisio_pct_do_comparecimento|n=1}}% e Flávio {{p5_base_de_votos.sp_flavio_pct_do_comparecimento|n=1}}%. O que sobra está dentro do que aconteceu em outros estados. A diferença aparece em todos os {{p5_sao_paulo_municipios.municipios}} municípios paulistas, e não em poucas seções. A estimativa é que cerca de {{derivados.sp.ei_tarcisio_para_flavio_pct|n=0}}% dos eleitores de Tarcísio votaram em Flávio, e o resto escolheu outros nomes, principalmente Cury, Caiado e Renan Santos. Essa estimativa não é o voto de ninguém, é uma conta feita com totais.

**5. O PL elegeu muitos senadores. Isso virou voto para presidente?**
Os {{p6_senadores_do_pl.total_eleitos}} senadores do PL foram eleitos em estados onde Flávio ficou na frente, e nenhum em estado onde Lula ficou na frente ou empatou. Dentro de cada estado, os municípios em que Flávio foi mais votado são os mesmos em que o candidato do PL ao Senado foi mais votado, tanto quanto em eleições anteriores. O critério escrito antes dos testes marcou {{derivados.p6.a_explicar_n}} estados para olhar melhor, porque candidatos do PL e apoiados por Flávio tiveram mais votos do que o partido do presidente costumava ter. O projeto não encontrou a causa. Na Bahia, no Ceará e em Pernambuco, onde os candidatos do PL perderam, o resultado é compatível com eleitores que usaram um dos dois votos do Senado de forma diferente do voto para presidente, mas os dados não separam essa hipótese de outras.

**6. Tem algum município estranho?**
Nenhum município passou nos três testes ao mesmo tempo, nem para Flávio, nem para Lula, nem no teste de comparação com 2022.

## O que o projeto não consegue dizer

- Se a urna gravou corretamente o voto de cada eleitor. O projeto começa no boletim que a urna imprimiu.
- A causa da parada na tela. Só o registro interno do TSE sabe.
- Como cada pessoa votou. O voto é secreto.
- Se as assinaturas digitais dos boletins estão corretas: o projeto não conseguiu verificar.

## Como conferir

Todo o caminho está no repositório, com os dados e os scripts: [`docs/REPLICAR.md`](docs/REPLICAR.md). Qualquer pessoa pode refazer e criticar.
