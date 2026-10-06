# A noite de 4 de outubro de 2026, refeita com os boletins de urna

**Projeto aberto, escrito com IA e com os critérios gravados antes dos testes.** Cada número deste relatório sai de um script rodado sobre arquivo público. O conjunto completo está em `resultados/RESUMO.json`, e os passos para refazer estão em [`docs/REPLICAR.md`](docs/REPLICAR.md).

> **Quem escreveu.** A análise foi feita por uma IA (Claude), sob a direção do autor do repositório, que definiu o objetivo e a régua. A revisão adversarial é uma segunda passada da própria IA, registrada em [`docs/REVISAO_ADVERSARIAL.md`](docs/REVISAO_ADVERSARIAL.md). **Nenhuma pessoa revisou os resultados antes desta publicação.**

---

## 0. Em resumo

1. **Os boletins publicados pelo TSE refazem o resultado oficial.** Foram decodificadas {{secoes_proprias_com_boletim}} seções, sem nenhum erro de leitura. Em {{derivados.p4.linhas_municipio_e_cargo_exatas}} das {{p4_municipio.linhas}} comparações por município e cargo ({{derivados.p4.pct_linhas_municipio_e_cargo_exatas|n=2}}%), a soma dos boletins é igual ao resultado oficial, voto por voto. A diferença que sobra vem de 15 seções cujos arquivos o TSE não publicou (3 em Minas Gerais, 12 em São Paulo): {{derivados.p4.votos_nominais_sem_correspondencia_presidente}} votos de Presidente, {{derivados.p4.pct_dos_validos_sem_correspondencia_presidente|n=4}}% dos válidos.
2. **A curva da noite refeita com a hora de recebimento passa pelos pontos que a imprensa publicou.** Encaixam {{p3_resumo.encaixam}} dos {{p3_resumo.pontos}} pontos, o erro mediano é de {{p3_resumo.melhor_erro_mediano|n=3}} ponto percentual, e os três pontos que têm duas ou mais fontes encaixam todos. O ponto que não encaixa, com {{derivados.p3.p02_pct_secoes|n=1}}% das seções, fica a {{p3_resumo.melhor_erro_max|n=2}} ponto.
3. **Não houve troca de liderança.** Depois dos primeiros {{p1_resumo.pct_secoes_da_ultima_troca_de_lideranca|n=2}}% das seções, Flávio Bolsonaro esteve sempre à frente de Lula nos votos válidos. A diferença foi de {{p1_resumo.margem_de_pico|n=2}} pontos no pico (às {{p1_resumo.recebido_no_pico|hm}}, com {{p1_resumo.pct_secoes_no_pico|n=0}}% das seções) até {{p1_resumo.margem_final|n=2}} no fim.
4. **A queda da diferença tem uma causa de calendário: quais regiões chegaram quando.** A composição regional do lote que chegou depois dos 64,81% explica {{derivados.p1.pct_explicado_pela_composicao_regiao|n=0}}% da diferença entre esse lote e o que já tinha chegado ({{derivados.p1.pct_explicado_pela_composicao_uf_capital|n=0}}% por estado e capital). Capital contra interior, porte do município e tamanho da seção explicam praticamente nada. Em 2022, a mesma conta dá {{derivados.p1.pct_explicado_pela_composicao_regiao_2022|n=0}}%.
5. **A parada de cerca de uma hora na tela de Presidente tem duas partes.** A tela congelou às 19h06 e voltou às 20h08, e os boletins refeitos reproduzem o que ela mostrou nos dois momentos. No registro de recebimento existe um vazio de {{p2_maiores_vazios_de_recebimento_2026.0.minutos|n=1}} minutos sem nenhum boletim (das {{p2_maiores_vazios_de_recebimento_2026.0.inicio|hora}} às {{p2_maiores_vazios_de_recebimento_2026.0.fim|hora}}), {{derivados.p2.vazio_minutos_vs_maior_2022|n=1}} vezes o maior vazio de 2022, e uma rajada de {{p2_rajada_depois_do_vazio.boletins_na_rajada_de_6_minutos}} boletins nos 6 minutos seguintes, de urnas que haviam emitido o boletim mais de uma hora antes. **A causa dentro do sistema do TSE não é verificável com dados públicos.**
6. **São Paulo: a diferença entre Tarcísio e Flávio é de {{p5_classe_de_referencia.sp_2026_lacuna_pontos|n=1}} pontos e aparece em todos os {{p5_sao_paulo_municipios.municipios}} municípios.** Tarcísio, apoiador declarado de Flávio, teve {{p5_classe_de_referencia.sp_gov_pct|n=2}}% dos válidos; Flávio, {{p5_classe_de_referencia.sp_pres_pct|n=2}}%. Quase metade dessa diferença ({{p5_base_de_votos.sp_pct_da_lacuna_que_vem_da_base|n=0}}%) vem de uma conta de base: {{p5_base_de_votos.sp_gov_validos_pct_do_comparecimento|n=1}}% de quem compareceu votou em candidato a governador (voto válido), contra {{p5_base_de_votos.sp_pres_validos_pct_do_comparecimento|n=1}}% para presidente. Em percentual de quem compareceu, Tarcísio tem {{p5_base_de_votos.sp_tarcisio_pct_do_comparecimento|n=1}}% e Flávio {{p5_base_de_votos.sp_flavio_pct_do_comparecimento|n=1}}%. Diferenças desse tamanho entre o governador aliado e o candidato a presidente que ele apoia ocorreram em outros estados em 2022 e em 2026. A estimativa ecológica é que cerca de {{derivados.sp.ei_tarcisio_para_flavio_pct|n=0}}% dos eleitores de Tarcísio votaram em Flávio.
7. **Senado: os {{p6_senadores_do_pl.total_eleitos}} senadores eleitos pelo PL estão todos em estados onde Flávio ficou na frente.** Nos {{derivados.p6.ufs_com_lula_na_frente_ou_empate}} estados em que Lula ficou na frente ou empatou, o PL elegeu zero. O voto por município no candidato do PL ao Senado acompanha o voto em Flávio ({{p6_alinhamento_municipal.2026_PL.mediana_spearman|n=2}}) tanto quanto em 2022 ({{p6_alinhamento_municipal.2022_PL.mediana_spearman|n=2}}) e 2018 ({{p6_alinhamento_municipal.2018_PSL.mediana_spearman|n=2}}). O critério escrito antes dos testes marca {{derivados.p6.a_explicar_n}} estados como "a explicar", por motivos que a §7 descreve.
8. **Nenhum município passou nos três testes de anomalia ao mesmo tempo**, para Flávio, para Lula e no placebo de 2022.

---

## 1. O que este relatório não consegue dizer

- **Não audita o software nem o hardware da urna.** O projeto começa no boletim que cada urna imprimiu e publicou. Se o voto foi gravado errado dentro da urna, este trabalho não vê.
- **Não vê o sistema interno do TSE.** A causa técnica da parada só pode ser confirmada pelo registro interno do sistema, que não é público. O projeto mede o efeito da parada, não a causa.
- **Não sabe como cada pessoa votou.** O voto é secreto. Toda comparação entre cargos é feita por seção ou município, e qualquer afirmação sobre "quem votou em quem" é inferência ecológica, que pode errar.
- **Não verifica a assinatura digital dos boletins.** Testei se o hash que vem dentro do `bu.dat` seria o SHA-256, o SHA-512 ou o SHA3-512 do conteúdo dos votos, em cinco recortes diferentes, e nenhum bateu. A especificação pública da verificação não foi encontrada. Fica registrado como **não verificado**.
- **Não tem as telas da noite.** O TSE sobrescreve o arquivo a cada atualização. A série de telas foi substituída pela reconstrução com a hora de recebimento, conferida contra {{p3_resumo.pontos}} pontos publicados pela imprensa. Só {{p3_resumo.pontos_com_duas_ou_mais_fontes}} deles têm duas ou mais fontes, e um traz votos absolutos.
- **A hora de recebimento é a que o TSE registrou, e não sabemos o que ela mede por dentro.** Pode ser a chegada do arquivo ou o momento em que o sistema o processou. A §4 mostra por que isso importa.

**A régua do texto.** "Consistente com" e "não explicado por". O relatório não afirma que houve irregularidade comprovada nem que a ausência dela ficou provada. Um resultado consistente quer dizer que os dados públicos fecham entre si. Um resultado não explicado vira uma pergunta específica, com endereço (seção, horário, cargo), para quem tem acesso ao que é interno.

**Como lemos alinhamento político.** Por **apoio declarado**, com fonte, e não por partido. Tarcísio é do Republicanos e declarou apoio incondicional a Flávio em 31/jul/2026 (duas fontes capturadas). Uma diferença entre o voto de um aliado e o de Flávio pode indicar algo, e também pode ser voto dividido, efeito de quem já está no cargo ou rejeição diferente de cada nome. O relatório mede o tamanho da diferença contra casos comparáveis e não atribui causa.

---

## 2. Os dados e a verificação

**O que foi coletado.** Para cada seção de 2026, o TSE publica a hora em que o boletim foi recebido (`aux.json`) e o boletim em si (`bu.dat`). Foram baixados e guardados com hash {{secoes_proprias_com_boletim}} boletins de seções com votos. O total oficial é de {{oficial_secoes.ts}} seções próprias, das quais {{oficial_secoes.sni}} não foram instaladas (todas no exterior), e {{secoes_agregadas}} seções agregadas têm os votos dentro da seção principal. Nenhuma seção tem mais de um boletim ({{derivados.dados.secoes_com_mais_de_um_boletim}} seções com duplicidade). Em {{derivados.dados.boletins_busa_total}} seções ({{derivados.dados.boletins_busa_por_uf.MG}} em Minas Gerais e {{derivados.dados.boletins_busa_por_uf.ZZ}} no exterior) o arquivo vem como `busa.dat`, o boletim do Sistema de Apuração, e foi lido da mesma forma.

**Decodificação.** Zero erros de leitura. Nas {{t24_resumo.secoes_testadas}} seções com boletim comum, o comparecimento do cabeçalho é igual à soma dos votos de Presidente.

**Confronto com o resultado oficial.**

{{tabela:tabelas/validacao_uf.csv}}

Em nível de município, {{derivados.p4.linhas_municipio_e_cargo_exatas}} de {{p4_municipio.linhas}} linhas são exatas. As diferenças estão em {{derivados.p4.municipios_com_diferenca}} municípios: {{derivados.p4.municipios_com_diferenca_lista.0}} e {{derivados.p4.municipios_com_diferenca_lista.1}}, exatamente onde ficam as {{derivados.dados.secoes_sem_arquivo_publicado}} seções sem arquivo publicado. A soma é consistente: o total de válidos reconstruído fica {{derivados.p4.votos_validos_a_menos}} votos abaixo do oficial ({{p1_resumo.total_de_votos_validos_reconstruidos}} contra {{derivados.oficial.validos}}), e essa é a soma exata das diferenças nominais dos dois municípios. Flávio fica {{derivados.p4.votos_flavio_a_menos}} votos abaixo do oficial e Lula {{derivados.p4.votos_lula_a_menos}}.

**Candidatos fora da lista oficial.** O arquivo oficial trata como nulos os votos de candidaturas sem registro válido. A validação mostrou que o nulo oficial é igual ao nulo dos boletins mais esses votos ({{votos_de_candidato_fora_da_lista_oficial_vistos_como_nulos}} votos nos três cargos). Todas as análises abaixo contam esses votos como nulos, como o TSE.

**Fuso horário.** A hora de recebimento está em horário de Brasília em {{t24_resumo.decididas.BRT}} das 28 unidades; o exterior (seções em vários países) não tem decisão possível. A regra é por município, porque o relógio de poucas urnas está fora do padrão: três municípios de Mato Grosso gravaram o encerramento em horário de Brasília, e Fernando de Noronha usa um fuso à frente. A leitura literal do critério (que moveria todo Mato Grosso uma hora) piora o encaixe dos pontos publicados, de {{t24_sensibilidade_MT.pontos_que_encaixam_com_MT_em_BRT}} para {{t24_sensibilidade_MT.pontos_que_encaixam_com_MT_deslocado_1h}}, e muda a margem em até {{t24_sensibilidade_MT.diferenca_maxima_da_margem_em_pontos|n=2}} ponto. A emenda está em `docs/PRE_REGISTRO.md`, §9.

---

## 3. A curva da noite: cada número da tela é a soma de boletins que já tinham chegado?

Ordenei todas as seções pela hora de recebimento e somei os votos na ordem. Para cada percentual de seções que a imprensa publicou, comparei os percentuais de Flávio e de Lula da tela com os da curva refeita, aceitando qualquer ponto da curva até 0,5 ponto de distância no percentual de seções e 0,1 ponto de diferença nos percentuais dos candidatos.

{{tabela:tabelas/pontos_da_tela.csv|casas=2}}

{{figura:fig1_curva_da_noite.png|A curva refeita com os boletins e os pontos publicados}}

**Leitura.** {{p3_resumo.encaixam}} pontos encaixam, entre eles os três com duas ou mais fontes (P04 e P05, que cercam a parada, e P07). Nos pontos com duas casas decimais publicadas, a curva refeita fica a centésimos de ponto. No único ponto com votos absolutos (P07), a curva refeita tem, no percentual exato de seções, {{derivados.p3.p07_votos_flavio_reconstruidos_menos_publicados}} votos de Flávio a mais que o publicado ({{derivados.p3.p07_pct_flavio_da_diferenca|n=3}}%) e {{derivados.p3.p07_votos_lula_reconstruidos_menos_publicados}} de Lula. No P13, a margem publicada de cerca de 2,4 milhões de votos confere com os {{derivados.p3.p13_margem_reconstruida}} da curva refeita. O ponto que não encaixa é o P02, com {{derivados.p3.p02_pct_secoes|n=1}}% das seções, onde a tela mostrou Flávio {{derivados.p3.p02_flavio_publicado|n=1}} e Lula {{derivados.p3.p02_lula_publicado|n=1}} e a curva dá {{derivados.p3.p02_flavio_refeito|n=2}} e {{derivados.p3.p02_lula_refeito|n=2}}. Nessa faixa a curva muda depressa com a ordem de poucas milhares de seções, e uma diferença de {{p3_resumo.melhor_erro_max|n=2}} ponto é compatível com pequenas diferenças entre a ordem de recebimento e a ordem em que o sistema contou. É o único caso, e fica registrado.

**O que isso mostra e o que não mostra.** Mostra que o que apareceu na tela, nos pontos que temos, é a soma de boletins reais que já tinham chegado, na ordem em que o TSE registrou o recebimento. Não mostra o que a tela exibiu entre os pontos, e nenhum dos pontos, salvo o de 90,56%, traz votos absolutos.

---

## 4. A parada de cerca de uma hora

**O que a imprensa registrou.** A tela de Presidente apontava {{p2_tela_contra_recebido.tela_as_19h06|n=2}}% das seções até as 19h06 e voltou a avançar às 20h08, com {{p2_tela_contra_recebido.tela_as_20h08|n=2}}%. As telas de governador, Senado e Câmara continuaram a atualizar. O presidente do TSE atribuiu a parada a um congestionamento de dados no sistema de divulgação e disse que a totalização não foi comprometida.

**O que os boletins mostram.**

| | |
|---|---|
| Estado da tela às 19h06 | reproduz os boletins recebidos até {{p2_parada.recebido_no_corte_64_81|hora}}, ou seja, {{p2_tela_contra_recebido.minutos_de_defasagem_na_parada_19h06|n=1}} minuto antes |
| Estado da tela às 20h08 | reproduz os boletins recebidos até {{p2_parada.recebido_no_corte_84_96|hora}}, {{p2_tela_contra_recebido.minutos_de_defasagem_na_retomada_20h08|n=1}} minutos antes |
| Seções recebidas segundo o relógio, às 19h06 e às 20h08 | {{p2_tela_contra_recebido.recebido_ate_19h06_pct|n=1}}% e {{p2_tela_contra_recebido.recebido_ate_20h08_pct|n=1}}%, contra {{p2_tela_contra_recebido.tela_as_19h06|n=2}}% e {{p2_tela_contra_recebido.tela_as_20h08|n=2}}% na tela |
| Maior vazio sem nenhum boletim registrado | das {{p2_maiores_vazios_de_recebimento_2026.0.inicio|hora}} às {{p2_maiores_vazios_de_recebimento_2026.0.fim|hora}}, {{p2_maiores_vazios_de_recebimento_2026.0.minutos|n=1}} minutos |
| Maiores vazios em 2022 | {{p7_maiores_vazios_de_recebimento_2022_turno1.0.minutos|n=1}} minutos no 1º turno e {{p7_maiores_vazios_de_recebimento_2022_turno2.0.minutos|n=1}} no 2º |
| Boletins registrados nos 6 minutos seguintes ao vazio | {{p2_rajada_depois_do_vazio.boletins_na_rajada_de_6_minutos}} |
| Hora em que as urnas dessa rajada emitiram o boletim | mediana {{p2_rajada_depois_do_vazio.hora_mediana_de_emissao_na_rajada|hm}}; {{p2_rajada_depois_do_vazio.pct_da_rajada_emitida_pela_urna_antes_das_19h|n=1}}% antes das 19h |
| Tempo entre a emissão na urna e o registro | mediana {{p2_rajada_depois_do_vazio.atraso_mediano_emissao_a_registro_na_rajada_min|n=0}} minutos na rajada, contra {{p2_rajada_depois_do_vazio.atraso_mediano_emissao_a_registro_nos_16_min_antes_do_vazio|n=0}} nos 16 minutos antes do vazio e {{p2_rajada_depois_do_vazio.atraso_mediano_emissao_a_registro_entre_18h_e_19h_min|n=0}} entre 18h e 19h |
| Origem da rajada | Sudeste {{p2_rajada_depois_do_vazio.regioes_da_rajada.Sudeste|x100|n=0}}% das seções, Nordeste {{p2_rajada_depois_do_vazio.regioes_da_rajada.Nordeste|x100|n=0}}% |
| Pico de chegada | {{p2_pico_de_chegada.boletins_por_minuto_no_pico|n=0}} boletins por minuto às 19h, contra {{p7_pico_de_chegada_2022.boletins_por_minuto_no_pico|n=0}} em 2022 |

{{figura:fig3_parada.png|Boletins recebidos por 5 minutos e percentual de seções, com a parada marcada}}

**O que o lote que entrou na parada fez com a margem.** Entre os dois pontos publicados ({{p2_tela_contra_recebido.tela_as_19h06|n=2}}% e {{p2_tela_contra_recebido.tela_as_20h08|n=2}}%), os pontos da tela implicam um lote com margem de {{p2_lote.margem_implicada_pelos_dois_pontos_publicados|n=2}} pontos entre Flávio e Lula, contra {{p2_lote.margem_reconstruida_do_lote|n=2}} no lote reconstruído com os boletins, uma diferença de {{p2_lote.diferenca_pontos|abs|n=2}} ponto. A margem acumulada caiu de {{p1_resumo.margem_em_64_81|n=2}} para {{p1_resumo.margem_em_84_96|n=2}} nesse trecho. A queda por ponto percentual de seções foi de {{derivados.p1.queda_por_ponto_de_secoes_de_20_a_64_81|n=3}} antes, {{derivados.p1.queda_por_ponto_de_secoes_de_64_81_a_84_96|n=3}} nesse trecho e {{derivados.p1.queda_por_ponto_de_secoes_de_84_96_a_100|n=3}} depois, no mesmo sentido e acompanhando a entrada das regiões em que Flávio teve menos votos.

**Critério escrito antes do teste.** O pré-registro dizia que o número de boletins na janela devia ser compatível com os cerca de 20 pontos que a tela acrescentou, com até 2 pontos de diferença. Pelo relógio cru, a janela das 19h06 às 20h08 tem {{derivados.p2.janela_bruta_pct_das_secoes|n=1}}% das seções contra {{derivados.p2.tela_acrescentou_pct|n=1}} acrescentados pela tela, uma diferença de {{derivados.p2.diferenca_vs_janela_bruta|n=1}} pontos, **acima do limite**. A diferença é a defasagem de exibição: a tela às 19h06 estava {{p2_tela_contra_recebido.minutos_de_defasagem_na_parada_19h06|n=1}} minuto atrás do relógio e às 20h08 estava {{p2_tela_contra_recebido.minutos_de_defasagem_na_retomada_20h08|n=1}} atrás. Com a janela medida pelos boletins que cada estado da tela reproduz, a conta fecha por construção. A condição de falha do critério (poucos boletins e, mesmo assim, o salto) não ocorreu: todo o salto da tela corresponde a boletins registrados antes do vazio.

**O que é consistente e o que fica sem resposta.**

- É consistente com um atraso de exibição: a tela parou e depois reproduziu um estado já completo do recebimento.
- O vazio no próprio registro de recebimento é um fato a mais, que a explicação pública (congestionamento no sistema de divulgação) não cobre diretamente. Os boletins da rajada tinham sido emitidos pelas urnas por volta das {{p2_rajada_depois_do_vazio.hora_mediana_de_emissao_na_rajada|hm}} e esperaram, em mediana, {{p2_rajada_depois_do_vazio.atraso_mediano_emissao_a_registro_na_rajada_min|n=0}} minutos até o registro. Isso combina com uma fila de registro que ficou parada e depois foi liberada, e não combina com seções que fecharam tarde. Os dados públicos não dizem se o bloqueio foi na transmissão, no processamento ou na marcação da hora.
- O pico de chegada de 2026 foi {{p2_pico_de_chegada.boletins_por_minuto_no_pico|n=0}} boletins por minuto, contra {{p7_pico_de_chegada_2022.boletins_por_minuto_no_pico|n=0}} em 2022. Isso é compatível com a explicação de volume acima do normal, mas não a prova.
- Todos os boletins chegaram, reconciliam com o resultado oficial e a margem do lote que entrou depois do vazio é a esperada para as regiões que o compõem. **O que ficou sem explicação é o que aconteceu no registro entre {{p2_maiores_vazios_de_recebimento_2026.0.inicio|hm}} e {{p2_maiores_vazios_de_recebimento_2026.0.fim|hm}}.** Só o registro interno do TSE responde.

---

## 5. Por que a vantagem do primeiro colocado caiu durante a noite

**O fato.** A diferença de Flávio sobre Lula nos votos válidos, somando os boletins na ordem de recebimento, chegou ao pico de {{p1_resumo.margem_de_pico|n=2}} pontos às {{p1_resumo.recebido_no_pico|hm}} e terminou em {{p1_resumo.margem_final|n=2}}, uma queda de {{derivados.p1.queda_do_pico_ao_fim_pontos|n=1}} pontos. Em 2022 o primeiro colocado do começo da noite também perdeu a vantagem: a diferença de Bolsonaro sobre Lula foi de {{derivados.p7.t1_margem_em_10pct|n=2}} pontos com 10% das seções para {{derivados.p7.t1_margem_final|n=2}} no fim, e a troca de liderança aconteceu com {{p7_2022_turno1_troca.pct_secoes_da_troca.3|n=1}}% das seções. No 2º turno de 2022 foi de {{derivados.p7.t2_margem_em_10pct|n=2}} para {{derivados.p7.t2_margem_final|n=2}}.

{{figura:fig4_2026_contra_2022.png|A vantagem inicial encolhe ao longo da noite também em 2022}}

**A causa é de calendário.** As regiões chegaram em ordens diferentes, e as margens finais delas são muito diferentes.

{{tabela:tabelas/regioes.csv|casas=1}}

{{figura:fig2_chegada_por_regiao.png|Boletins recebidos por meia hora, por região}}

Às 19h06, {{derivados.p1.sul_pct_ate_19h06|n=1}}% das seções do Sul já tinham chegado e {{derivados.p1.nordeste_pct_ate_19h06|n=1}}% das do Nordeste. A decomposição exata da diferença entre o lote que chegou depois dos 64,81% e o que já tinha chegado mostra o tamanho de cada explicação:

| Agrupamento das seções | Parte da diferença explicada pela composição |
|---|---|
| Região | {{derivados.p1.pct_explicado_pela_composicao_regiao|n=0}}% (2022: {{derivados.p1.pct_explicado_pela_composicao_regiao_2022|n=0}}%) |
| Estado | {{derivados.p1.pct_explicado_pela_composicao_uf|n=0}}% |
| Estado e capital contra interior | {{derivados.p1.pct_explicado_pela_composicao_uf_capital|n=0}}% |
| Capital contra interior (sozinho) | {{derivados.p1.pct_explicado_pela_composicao_capital_ou_interior|n=0}}% |
| Porte do município (em cinco faixas) | {{derivados.p1.pct_explicado_pela_composicao_porte_municipio|n=0}}% |
| Tamanho da seção (em quatro faixas) | {{derivados.p1.pct_explicado_pela_composicao_tamanho_secao|n=0}}% |

Valor perto de zero ou negativo quer dizer que o agrupamento não ajuda a explicar a queda.

O que explica a queda é a geografia. Seções grandes ou pequenas, de capital ou de interior, de município grande ou pequeno, não determinam a ordem de chegada de forma que mude o resultado.

**Teste com embaralhamento.** Embaralhei a ordem de chegada 1.000 vezes. Com ordem totalmente aleatória, a curva real fica fora da faixa de 5% a 95% em {{p1_permutacao_aleatoria.pontos_da_curva_fora_da_faixa_5_95}} de 100 pontos, com distância mediana de {{p1_permutacao_aleatoria.distancia_mediana_pontos|n=1}} pontos. Mantendo o calendário de chegada de cada estado e embaralhando só quais seções ocupam os horários dele, a distância mediana cai {{derivados.p1.reducao_da_distancia_mediana_calendario_por_uf|n=0}}%; com estado e capital, {{derivados.p1.reducao_da_distancia_mediana_calendario_por_uf_e_capital|n=0}}%; com estado, capital e porte, {{derivados.p1.reducao_da_distancia_mediana_calendario_por_uf_capital_e_porte|n=0}}%. O calendário explica a maior parte e deixa uma parte sem explicar, que fica dentro de cada estado e que o agrupamento por capital e porte quase não reduz.

---

## 6. São Paulo: Tarcísio, Haddad, Flávio e Lula

**Os números.** Em São Paulo, Tarcísio (Republicanos) teve {{p5_classe_de_referencia.sp_gov_pct|n=2}}% dos votos válidos para governador, e Flávio {{p5_classe_de_referencia.sp_pres_pct|n=2}}% para presidente: {{derivados.p5.diferenca_de_votos_tarcisio_menos_flavio}} votos a mais para Tarcísio no arquivo oficial. A soma dos boletins dá {{derivados.p5.votos_a_menos_nos_boletins_que_no_oficial_na_diferenca}} votos a menos que isso, porque as seções sem arquivo publicado não entram nela. Haddad teve {{derivados.sp.haddad_pct|n=2}}% e Lula {{derivados.sp.lula_pct|n=2}}%. Os quatro percentuais coincidem com os do arquivo oficial.

**A base dos percentuais não é a mesma.** O percentual de governador é calculado sobre os votos válidos para governador, e o de presidente sobre os votos válidos para presidente. Em São Paulo as duas bases são diferentes, porque muito mais eleitores votaram em branco ou nulo para governador do que para presidente.

| | Governador | Presidente |
|---|---|---|
| Votos válidos, em % de quem compareceu ({{p5_base_de_votos.sp_comparecimento}} pessoas) | {{p5_base_de_votos.sp_gov_validos_pct_do_comparecimento|n=1}}% | {{p5_base_de_votos.sp_pres_validos_pct_do_comparecimento|n=1}}% |
| Tarcísio e Flávio, em % dos votos válidos | {{p5_classe_de_referencia.sp_gov_pct|n=2}}% | {{p5_classe_de_referencia.sp_pres_pct|n=2}}% |
| Tarcísio e Flávio, em % de quem compareceu | {{p5_base_de_votos.sp_tarcisio_pct_do_comparecimento|n=1}}% | {{p5_base_de_votos.sp_flavio_pct_do_comparecimento|n=1}}% |

O arquivo oficial de governador traz o seu próprio total de votos do cargo ({{derivados.p5.oficial_gov_total_do_cargo}}) e dá {{derivados.p5.oficial_gov_validos_pct_do_total_do_cargo|n=1}}% de válidos, e o de presidente dá {{derivados.p5.oficial_pres_validos_pct_do_total_do_cargo|n=1}}%. A tabela acima usa o mesmo denominador para os dois cargos (quem votou para presidente), e por isso o governador aparece com um décimo a menos. A diferença de {{p5_classe_de_referencia.sp_2026_lacuna_pontos|n=1}} pontos entre Tarcísio e Flávio nos votos válidos cai para {{p5_base_de_votos.sp_lacuna_pct_do_comparecimento|n=1}} pontos quando os dois são medidos sobre quem compareceu. Os {{p5_base_de_votos.sp_efeito_da_base_pontos|n=1}} pontos de diferença ({{p5_base_de_votos.sp_pct_da_lacuna_que_vem_da_base|n=0}}%) são a base, e não troca de voto entre candidatos. Esse efeito é comum: a mediana nos {{p5_classe_de_referencia.n}} outros casos é de {{p5_base_de_votos.efeito_da_base_mediano_na_classe|n=1}} pontos ({{p5_base_de_votos.efeito_da_base_mediano_na_classe_2026|n=1}} em 2026 e {{p5_base_de_votos.efeito_da_base_mediano_na_classe_2022|n=1}} em 2022). É conta exata, feita com os totais oficiais, e não inferência.

**Alinhamento.** Tarcísio declarou em 31/jul/2026 apoio "incondicional" a Flávio. A CNN Brasil classificou 10 dos 20 governadores eleitos no 1º turno como apoiadores de Flávio, 5 de Lula, 1 de Caiado e 4 sem apoio declarado; o g1, citado pelo Space Money, contou 11, 5 e 3 sem apoio (e 1 de Caiado). A divergência é de um governador e não envolve São Paulo. Por isso a pergunta não é se o voto em Tarcísio deveria ser igual ao voto em Flávio. A pergunta é quanto uma diferença desse tamanho é comum entre um governador aliado e o candidato a presidente que ele apoia.

**Comparação com casos parecidos.** Comparei a diferença entre o governador eleito e o presidente que ele declarou apoiar em {{derivados.p5_n.casos_total}} casos ({{derivados.p5_n.casos_2026}} de 2026, incluindo São Paulo, e {{derivados.p5_n.casos_2022}} de 2022, todos eleitos no 1º turno e com apoio declarado). São Paulo é comparado com os outros {{derivados.p5_n.comparados_com_sp}}.

{{tabela:tabelas/lacuna_governador_presidente.csv|casas=1}}

{{figura:fig5_lacuna_governador_presidente.png|Diferença entre o governador eleito e o presidente que ele apoia}}

A diferença de São Paulo, {{p5_classe_de_referencia.sp_2026_lacuna_pontos|n=1}} pontos, fica no percentil {{p5_classe_de_referencia.sp_percentil_na_classe|n=0}} das {{p5_classe_de_referencia.n}} comparações, dentro da faixa que vai de {{p5_classe_de_referencia.q05|n=1}} a {{p5_classe_de_referencia.q95|n=1}} pontos (percentis 5 e 95). Entre os 10 governadores aliados de Flávio eleitos em 2026, é a maior diferença. Em 2022, a maior entre aliados de Bolsonaro foi de {{derivados.p5_ref.maior_diferenca_de_aliado_de_bolsonaro_em_2022|n=1}} pontos (Paraná). A conclusão se mantém usando só 2026, só 2022, só aliados do candidato do PL ou acrescentando 2018. Medida sobre quem compareceu, a diferença de São Paulo fica no percentil {{p5_base_de_votos.sp_percentil_na_classe_pelo_comparecimento|n=0}}, entre os limites de {{p5_base_de_votos.classe_lacuna_pct_do_comparecimento_q05|n=1}} e {{p5_base_de_votos.classe_lacuna_pct_do_comparecimento_q95|n=1}}.

**A diferença está espalhada pelo estado, e não concentrada.** Tarcísio ficou à frente de Flávio nos {{p5_sao_paulo_municipios.municipios}} municípios, com diferença entre {{derivados.p5.gap_2026_minimo_entre_municipios|n=1}} e {{derivados.p5.gap_2026_maximo_entre_municipios|n=1}} pontos (percentis 5 e 95: {{derivados.p5.gap_2026_p05|n=1}} e {{derivados.p5.gap_2026_p95|n=1}}); a capital teve {{p5_sao_paulo_municipios.gap_2026_sao_paulo_capital|n=1}}. Em {{derivados.p5.pct_dos_votos_validos_de_governador_em_municipios_com_gap_entre_5_e_15|n=0}}% dos votos válidos para governador a diferença municipal está entre 5 e 15 pontos. Para somar metade da diferença líquida de votos foram necessárias seções que são {{derivados.sp.fracao_das_secoes_para_metade_da_diferenca|n=0}}% do total, sem concentração em poucas seções (o 1% das seções que mais contribuem responde por {{derivados.sp.top1pct_parcela_da_diferenca|n=1}}% da diferença, contra {{derivados.sp.top1pct_parcela_dos_votos|n=1}}% dos votos).

{{figura:fig6_sao_paulo_por_municipio.png|São Paulo por município: 2026 contra 2022}}

**Contra 2022.** Em 2022 Tarcísio ficou abaixo de Bolsonaro em {{derivados.sp.pct_municipios_com_tarcisio_abaixo_de_bolsonaro_em_2022|n=1}}% dos municípios (diferença mediana de {{p5_sao_paulo_municipios.gap_mediano_2022|n=1}} pontos); em 2026, acima de Flávio em todos. A correlação entre as diferenças municipais de um ano e do outro é de {{p5_sao_paulo_municipios.spearman_gap2026_x_gap2022|n=2}}, ou seja, a geografia da diferença não é a mesma. O campo de governador mudou: em 2022 o voto estava dividido entre Tarcísio, Haddad e Rodrigo Garcia ({{derivados.sp.rodrigo_garcia_2022_pct|n=1}}%); em 2026 a disputa foi entre dois nomes, com Tarcísio no cargo.

**Para onde foi o voto (inferência ecológica, exploratória).** O voto é secreto, então isto é uma estimativa feita com os totais por seção, com intervalo por reamostragem de municípios (5% a 95%). A estimativa reproduz os totais reais de Flávio e de Lula em São Paulo com menos de 1% de erro. A primeira versão do cálculo errava 4% para cima o total de Flávio, e a revisão adversarial pegou isso (ver `docs/CORRECOES.md`). Em 2026:

{{tabela:tabelas/ei_sp_2026.csv}}

Cerca de {{derivados.sp.ei_tarcisio_para_flavio_pct|n=1}}% dos eleitores de Tarcísio votaram em Flávio, e o restante se dividiu entre Cury, Caiado, Renan Santos e Lula, nessa ordem de tamanho. Entre os eleitores de Haddad, cerca de {{derivados.sp.ei_haddad_para_lula_pct|n=0}}% votaram em Lula. Em 2022, a mesma estimativa dava {{derivados.sp.ei_2022_tarcisio_para_bolsonaro_pct|n=1}}% de eleitores de Tarcísio votando em Bolsonaro:

{{tabela:tabelas/ei_sp_2022.csv}}

**O que isso pode indicar e o que não diz.** Pela estimativa, o grupo de eleitores de Tarcísio que não votou em Flávio tem cerca de {{derivados.sp.votos_de_tarcisio_que_nao_foram_para_flavio_estimado}} votos. A diferença de {{derivados.p5.diferenca_de_votos_tarcisio_menos_flavio}} votos entre os dois fica menor porque cerca de {{derivados.sp.flavio_votos_de_quem_anulou_ou_deixou_em_branco_para_governador_estimado}} votos de Flávio vieram de quem anulou ou deixou em branco o voto para governador. Dentro desse grupo, Cury, Caiado e Renan Santos somam {{derivados.sp.ei_tarcisio_para_cury_caiado_e_santos|n=1}}% dos eleitores de Tarcísio, e Lula {{p5_sao_paulo_ei_2026.tarcisio_para_lula.fracao|x100|n=1}}%. Isso é consistente com voto dividido: eleitor que escolhe o governador por um motivo e o presidente por outro. Os números não separam essa hipótese de outras, como o efeito de quem já está no cargo ou a rejeição diferente de cada nome. O que os números dizem é que a diferença não é um ponto isolado, é um padrão geral do estado e do tamanho do que aconteceu em outros estados.

---

## 7. Senado e presidente

Eleger muitos senadores de um partido pode indicar apoio a esse campo, e a pergunta do autor foi se esse voto se converteu em voto para presidente. Os números abaixo medem o tamanho dessa relação, sem afirmar que a mesma pessoa votou nos dois cargos.

**Quem elegeu o quê.** O PL elegeu {{p6_senadores_do_pl.total_eleitos}} senadores, e os {{p6_senadores_do_pl.total_eleitos}} estão em estados onde Flávio ficou à frente de Lula ({{p6_senadores_do_pl.ufs_com_flavio_na_frente}} estados). Em estados onde Lula ficou na frente ou empatou, o PL elegeu {{p6_senadores_do_pl.em_ufs_com_lula_na_frente_ou_empate}}. O espelho vale para o PT: elegeu {{p6_senadores_do_pt.total_eleitos}}, {{p6_senadores_do_pt.em_ufs_com_lula_na_frente_ou_empate}} em estados com Lula na frente e {{p6_senadores_do_pt.em_ufs_com_flavio_na_frente}} em um estado em que Flávio ficou na frente. O único estado em que Flávio ficou na frente e o PL não elegeu senador foi o Espírito Santo.

**Os dois votos por eleitor.** Em 2026 cada eleitor votou em dois senadores. Por isso os votos de senador foram divididos por 2 para comparar com o voto presidencial, e a comparação usa o voto médio por candidato como percentual dos eleitores.

{{tabela:tabelas/senado.csv|casas=1}}

{{figura:fig7_senado_contra_presidente.png|Voto no candidato do partido ao Senado contra o voto no presidente}}

**Os dois votos andam juntos no território.** Dentro de cada estado, comparei município a município o voto em Flávio e o voto médio nos candidatos do PL ao Senado. A correlação mediana entre municípios é de {{p6_alinhamento_municipal.2026_PL.mediana_spearman|n=2}} em 2026 (em {{p6_alinhamento_municipal.2026_PL.ufs_com_spearman_acima_de_0_8}} de {{p6_alinhamento_municipal.2026_PL.ufs}} estados ela passa de 0,8), contra {{p6_alinhamento_municipal.2022_PL.mediana_spearman|n=2}} no PL de 2022 e {{p6_alinhamento_municipal.2018_PSL.mediana_spearman|n=2}} no PSL de 2018. Para o PT e Lula, {{p6_alinhamento_municipal.2026_PT.mediana_spearman|n=2}} em 2026. Entre estados, a correlação entre o voto em Flávio e o voto nos candidatos do PL é de {{p6_entre_ufs.spearman_flavio_x_candidatos_do_pl|n=2}} (PT e Lula: {{p6_entre_ufs.spearman_lula_x_candidatos_do_pt|n=2}}). A razão mediana entre o voto médio por candidato e o voto no presidente é de {{p6_entre_ufs.mediana_razao_pl|n=2}} para o PL e {{p6_entre_ufs.mediana_razao_pt|n=2}} para o PT.

**O critério escrito antes dos testes.** Marca como "a explicar" o estado em que o voto médio por candidato do PL, em relação ao voto no presidente, fica acima da faixa de 5% a 95% de 2018 e 2022 (candidatos do partido do presidente) e em que os candidatos apoiados por Flávio ficam também acima. Marca {{derivados.p6.a_explicar_n}} estados: {{p6_criterio_literal.ufs_a_explicar_pelo_criterio_literal|join}}. Em todos eles os candidatos do PL e os apoiados por Flávio receberam mais votos, em relação a Flávio, do que o partido do presidente costumava receber em 2018 e 2022. Em {{p6_criterio_literal.dessas_com_senador_do_pl_eleito|join}} o PL elegeu senador; em {{derivados.p6.a_explicar_sem_senador_do_pl|join}}, não.

**Como ler esse resultado.** A faixa de referência é fraca: o PSL de 2018 e o PL de 2022 tinham candidatos de força muito diferente, e a mediana histórica da razão é de {{p6_resumo.razao_historica_partido_do_presidente.mediana|n=2}}, bem abaixo da de 2026. Um candidato do PL que recebe mais votos que Flávio na Bahia, no Ceará ou em Pernambuco, onde Lula tem mais de 60%, é consistente com eleitor que usou um dos dois votos de Senado para um nome da direita e outro para um da esquerda. Essa leitura não cobre o Distrito Federal, Mato Grosso do Sul, Rio Grande do Sul e São Paulo, onde os candidatos do PL ganharam com mais votos que Flávio nos mesmos estados, nem o Amazonas, onde ficaram acima da faixa sem eleger. O relatório não atribui causa. O endereço da pergunta aberta é: nos {{derivados.p6.a_explicar_n}} estados acima, o que explica o voto no candidato do PL ou apoiado por Flávio acima do que o partido do presidente costumava receber.

**Um dos {{p6_casamento.na_lista}} nomes da lista de apoio não foi casado com o resultado oficial** ({{derivados.p6.nao_casado}}): o nome não aparece na lista de candidatos ao Senado do arquivo oficial. Os outros {{p6_casamento.casados}} foram casados e conferidos.

---

## 8. Testes de anomalia

Os testes têm limite claro: com cerca de {{secoes_proprias_com_boletim}} seções, algumas parecem estranhas por acaso, e a vizinhança dentro de um município produz seções diferentes entre si em qualquer eleição. Por isso a comparação que vale é entre anos e entre cargos, e não o valor absoluto.

{{tabela:tabelas/caudas.csv}}

{{figura:fig8_caudas_dos_z.png|Percentual de seções com z acima de 4 contra o resto do município}}

- **Caudas.** As caudas de 2026 para Flávio e para Lula são iguais ou menores que as de 2022, e as do governador são menores que as do presidente nos dois anos.
- **Impressão digital (comparecimento e voto).** A mudança mediana da correlação entre 2022 e 2026 por estado é de {{p8_impressao_digital.mudanca_spearman_flavio_menos_boso_mediana|n=2}} para Flávio e {{p8_impressao_digital.mudanca_spearman_lula_mediana|n=2}} para Lula. O maior percentual de seções no canto "comparecimento acima de 95% e candidato acima de 90%" em um estado é {{p8_impressao_digital.pct_secoes_no_canto_95_90_2026_max_uf|n=2}}% em 2026 e {{p8_impressao_digital.pct_secoes_no_canto_95_90_2022_max_uf|n=2}}% em 2022.
- **Último dígito (controle).** O teste acusa desvio em todos os anos e candidatos, inclusive em 2018 e 2022. Um teste que acusa tudo não acusa nada, e por isso ele entra só como controle.
- **Lei de Benford.** Não foi usada. A literatura mostra que ela não detecta, de forma confiável, adulteração em dado eleitoral.
- **Municípios nos três testes.** O critério escrito antes dos testes exige que o município seja sinalizado, ao mesmo tempo, na relação entre comparecimento e voto, na comparação com 2022 e na comparação com o outro cargo, depois da correção para muitos testes. Foram testados {{p8_municipios.testados_2026}} municípios. Passaram nos três: {{p8_municipios.a_explicar_flavio}} para Flávio, {{p8_municipios.a_explicar_lula_simetria}} para Lula (teste espelho) e {{p8_municipios.placebo_2022_a_explicar}} no placebo de 2022. Cada teste sozinho sinalizou alguns municípios: {{p8_municipios.sinal_a_historico}} na comparação com 2022, {{p8_municipios.sinal_b_outro_cargo}} na comparação com o outro cargo e {{p8_municipios.sinal_c_comparecimento}} na relação entre comparecimento e voto. A lista completa está em `resultados/p8_municipios_testes.csv`.

---

## 9. O que ficou sem explicação

Cada item tem um endereço, para quem tem acesso ao que é interno ao TSE:

1. **O registro de recebimento entre {{p2_maiores_vazios_de_recebimento_2026.0.inicio|hm}} e {{p2_maiores_vazios_de_recebimento_2026.0.fim|hm}}.** Em {{p2_maiores_vazios_de_recebimento_2026.0.minutos|n=1}} minutos não há nenhum boletim registrado, e {{p2_rajada_depois_do_vazio.boletins_na_rajada_de_6_minutos}} aparecem em 6 minutos depois, de urnas que emitiram o boletim, em mediana, {{p2_rajada_depois_do_vazio.atraso_mediano_emissao_a_registro_na_rajada_min|n=0}} minutos antes. A pergunta é se foi a transmissão, o processamento ou a marcação da hora que parou.
2. **As {{derivados.dados.secoes_sem_arquivo_publicado}} seções sem arquivo publicado.** Minas Gerais: {{derivados.dados.lista_mg}}. São Paulo: {{derivados.dados.lista_sp}}. O resultado oficial inclui os votos delas e os arquivos não estão publicados.
3. **O ponto P02, com {{derivados.p3.p02_pct_secoes|n=1}}% das seções**, onde a tela mostrou Flávio {{derivados.p3.p02_flavio_publicado|n=1}} e Lula {{derivados.p3.p02_lula_publicado|n=1}} e a curva dá {{derivados.p3.p02_flavio_refeito|n=2}} e {{derivados.p3.p02_lula_refeito|n=2}}.
4. **{{derivados.p6.a_explicar_n}} estados no critério do Senado** (a §7).
5. **A assinatura digital dos boletins**, que este projeto não conseguiu verificar.
6. **Os registros internos do sistema de divulgação**, que só o TSE tem, sobre a causa da parada.

---

## 10. Como refazer, e o que mudou ao longo do trabalho

- **Refazer:** [`docs/REPLICAR.md`](docs/REPLICAR.md).
- **Critérios antes dos testes:** [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md), gravado no commit `a3b0a66`. As emendas estão na tabela da §9 de lá, e cada uma diz se foi feita antes ou depois de ver o resultado. **Algumas foram feitas depois de ver resultados parciais de 2026** (o fuso por município, o leitor do `busa.dat`, o tratamento de candidatos fora da lista oficial), e estão marcadas assim. As análises exploratórias, que não decidem nenhum critério, estão na §10 de lá.
- **Erros achados no caminho e corrigidos:** [`docs/CORRECOES.md`](docs/CORRECOES.md).
- **Fontes capturadas, com hash:** `dados/CAPTURAS.csv`.
- **Revisão adversarial:** [`docs/REVISAO_ADVERSARIAL.md`](docs/REVISAO_ADVERSARIAL.md).
