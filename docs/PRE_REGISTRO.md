# Pré-registro: os testes e os critérios, escritos antes de olhar os dados

**Estado:** versão 2, de 05/out/2026 (noite), com a correção do autor sobre alinhamento político (§0.1). O autor mandou executar de ponta a ponta, o que aprova o plano. **Este arquivo é gravado em commit antes de qualquer análise**, e o relatório cita o hash desse commit como prova de que os critérios vieram antes dos resultados.

**Regra de mudança:** depois do commit, um critério só muda com uma entrada na §9, com o antes, o depois, o motivo e a declaração de se a mudança foi feita **antes ou depois** de ver o resultado do teste. Mudança depois de ver o resultado vai para o relatório com o mesmo destaque do resultado.

---

## 0. O que já foi visto antes deste registro (declaração)

Honestidade sobre o ponto de partida. Antes de escrever este arquivo, foram vistos:

- os totais finais oficiais de Presidente no Brasil e de Presidente, Governador e Senador em SP;
- os dois pontos da imprensa: 19h06 com 64,81% (Flávio 49,58%, Lula 42,25%) e 20h08 com 84,96% (Flávio 48,47%, Lula 43,49%);
- **uma** seção do AC (Porto Walter, zona 0004, seção 0077): `aux.json`, tamanho dos arquivos e o log;
- a primeira linha do CSV de 2022 do AC.

**Também visto antes deste registro (declaração adicional):** um boletim de urna decodificado à mão para conferir o formato (a mesma seção do AC), e as tabelas públicas de apoio de governadores e de candidatos ao Senado (CNN Brasil, 05/out; Ranking dos Políticos, 22/set).

**Não foi visto:** nenhum dado por seção além dessa, nenhuma curva, nenhum resultado por município.

### 0.1 Correção do autor sobre alinhamento político (05/out)

> O autor corrigiu uma leitura que a primeira versão deste plano deixou passar. Palavras dele: *"Tarcísio ele é do Republicanos. Sim, mas ele é apoiador de Flávio"*, *"não indica que não há um apoio"*, *"isso vai muito além do apenas do partido"*, *"não seja tão taxativo"*.

O que muda, e vale para P5, P6 e para qualquer frase do relatório:

1. **Partido não é o critério de alinhamento. Apoio declarado é.** Tarcísio é do Republicanos e declarou apoio incondicional a Flávio em 31/jul (fonte a capturar: Tribuna de Jundiaí e A Crítica, ver `FONTES_DE_DADOS.md` §8). A CNN Brasil de 05/out classifica 10 dos 20 governadores eleitos no 1º turno como apoiadores de Flávio, 5 de Lula, 1 de Caiado e 4 sem apoio declarado; os apoiadores de Flávio incluem PL, Republicanos, PP e Podemos.
2. **Diferença entre cargos de um mesmo campo não é, por si, anomalia nem prova de normalidade.** Ela pode indicar voto dividido (eleitor escolhe o governador por um motivo e o presidente por outro), efeito de quem já está no cargo, rejeição diferente de cada nome, ou algo que os dados públicos não separam. O relatório mede **quanto** da diferença cabe no que já aconteceu em casos comparáveis e diz que o **resto** é uma pergunta aberta, sem concluir causa.
3. **A régua de comparação é a classe de referência, não a ausência de diferença.** Para cada UF cujo governador eleito (ou candidato competitivo) declarou apoio a um candidato a presidente, mede-se a diferença entre o voto dele e o voto do candidato que ele apoia. A distribuição dessa diferença nas UFs de 2026 e nos casos equivalentes de 2018 e 2022 é o que diz se São Paulo está dentro do que costuma acontecer ou fora dele.
4. **Duas classificações públicas de apoio divergem** (CNN Brasil: 10 apoiaram Flávio; Space Money: 11). Toda conclusão que depende da classificação é refeita com as duas, e só vale se resistir às duas.
5. **Três fontes independentes do próprio critério de apoio** (apoio declarado do governador, lista de candidatos ao Senado que Flávio declarou apoiar em 06/ago, e partido) são usadas como variáveis separadas. Se o resultado muda conforme a definição, o relatório diz que o resultado depende da definição.

---

## 1. Fuso horário (T2.4), porque todo o resto depende dele

- **Teste:** para cada UF, converter o encerramento registrado no log da urna para horário de Brasília em cada fuso candidato, e contar quantas seções teriam o recebimento (`hr`) **antes** do encerramento.
- **Decisão:** o fuso do `hr` é o que dá **zero** violações em todas as UFs (tolerância: 0,1% das seções, para erro de relógio de urna, listadas uma a uma).
- **Se nenhum fuso der zero:** a hora de recebimento não é usada como relógio, as perguntas P1 a P3 e P7 ficam sem resposta temporal, e o relatório diz isso.

---

## 2. Integridade aritmética (P4)

| Teste | Explicado | Não explicado |
|---|---|---|
| Soma dos boletins = total oficial, por município, UF e cargo | diferença **zero** votos, ou diferença igual a votos com status declarado (anulado, sub judice, seção com boletim substituído) e documentado | qualquer outra diferença, com o município e o cargo |
| Assinatura do boletim | confere em todas as seções, ou as que não conferem têm explicação documentada | assinatura que não confere sem explicação |
| Recebimento × encerramento | recebimento sempre depois do encerramento, no fuso decidido no §1 | recebimento antes do encerramento |
| `aux.json` × CSV `bweb` | mesma hora (até 1 segundo) e mesmos votos | qualquer divergência |

---

## 3. A curva da noite (P1 e P3)

- **Modelo:** a tela exibida no instante *t* é a soma dos boletins recebidos até *t − d*, com **um único** atraso *d* para o país inteiro, estimado pelos pontos publicados.
- **Tolerância de encaixe por ponto:** percentual de seções a até **0,5 ponto** do publicado, e percentual de cada um dos dois primeiros colocados a até **0,1 ponto**, no mesmo instante da curva.
- **Explicado:** todos os pontos com duas fontes independentes dentro da tolerância, com o mesmo *d*.
- **Não explicado:** um ponto com duas fontes fora da tolerância com qualquer *d* entre 0 e 60 minutos. Teste extra para esse ponto: existe **algum** subconjunto de seções recebidas até *t* que produz o percentual publicado? Se nem isso existir, o achado é forte e vai para o topo do relatório.
- **Ponto com uma fonte só:** entra no gráfico marcado, fora da decisão.

---

## 4. A parada de 19h06 a 20h08 (P2)

| Medida | Explicado | Não explicado |
|---|---|---|
| Boletins recebidos na janela (ajustada por *d*) | número compatível com os ~20% de seções que a tela acrescentou (até 2 pontos de diferença) | nenhum ou poucos boletins chegando, e mesmo assim o salto |
| Composição do lote da janela | Flávio e Lula no lote reconstruído a até **0,3 ponto** do lote implícito pelos dois pontos da imprensa | diferença maior |
| Outros cargos no mesmo intervalo | atualizaram, como a imprensa relatou | |

O que este teste **não** decide: a causa técnica dentro do TSE.

---

## 5. A queda da vantagem (P1 e P7)

- **Medida:** a vantagem de Flávio sobre Lula em 25%, 50%, 64,81%, 84,96% e 100% das seções.
- **Contrafactual:** 10.000 ordens de chegada aleatórias (semente declarada no código).
- **Leitura:** a decomposição por região, porte de município, capital × interior e exterior tem de **fechar** a mudança total (resíduo declarado).
- **Histórico:** a mesma medida em 2014, 2018 e 2022. 2026 é descrito pela posição dentro desse conjunto, sem rótulo de "normal" ou "anormal" fora do que o número diz.

---

## 6. São Paulo e a diferença entre governador e presidente (P5)

- **Classe de referência (definida antes de ver o resultado):** as UFs de 2026 em que o governador eleito no 1º turno tem apoio declarado a um candidato a presidente na tabela da CNN Brasil de 05/out (20 UFs), mais, para 2022 e 2018, os governadores que concorreram com apoio declarado a um dos dois primeiros colocados da eleição presidencial. A fonte de 2022 e 2018 é capturada na Fase 1; UF sem fonte fica fora.
- **Medida:** `g = % válidos do governador − % válidos do presidente que ele apoia`, por UF, e a mesma diferença por seção e por município dentro de São Paulo.
- **Em São Paulo:** onde `g` se concentra (por município, por porte, capital × interior, perfil da seção), quantas seções somam metade da diferença, e como se compara com 2022 (governador × presidente).
- **Explicado:** `g` de São Paulo dentro do intervalo de 5% a 95% da classe de referência, e a distribuição por seção parecida com a de outras UFs com governador no cargo e apoio declarado.
- **A explicar (pergunta aberta, não conclusão):** `g` fora desse intervalo, **ou** metade da diferença em menos de **1%** das seções, **ou** padrão que não existe nas UFs comparáveis.
- **O que o resultado NÃO diz:** não diz por que os eleitores dividiram o voto. O relatório lista as hipóteses possíveis (voto dividido, efeito de quem está no cargo, rejeição diferente, composição do eleitorado que votou) como hipóteses, e só afirma a parte que os números separam.
- **Limite dito no relatório:** inferência ecológica não diz o que cada eleitor fez.

---

## 7. Senado e presidente (P6)

- **Normalização obrigatória:** em 2026 cada eleitor vota em dois senadores. O voto de senador é dividido por 2 para ser comparado com o de presidente, e cada cargo usa os próprios brancos e nulos.
- **Três definições de "campo", usadas separadas e depois comparadas:** (a) candidatos do PL; (b) candidatos que Flávio declarou apoiar em 06/ago (Ranking dos Políticos, 22/set, 47 candidatos); (c) candidatos de partidos que tiveram apoio declarado do governador apoiador de Flávio na mesma UF (classe da §6).
- **Medidas, por UF:** soma dos votos do campo ao Senado (por eleitor) sobre os válidos de Senador, contra o `% de Flávio`; número de candidatos competitivos ao Senado; margem do 2º eleito sobre o 3º; quantos senadores do campo venceram em UFs onde Flávio perdeu e o inverso.
- **Explicado:** a diferença entre o campo no Senado e Flávio cabe na distribuição observada em 2022 e 2018 para o mesmo tipo de comparação (campo do presidente × campo no Senado), com o mesmo ajuste de voto duplo.
- **A explicar:** UF fora do intervalo de 5% a 95% dessa distribuição histórica em pelo menos duas das três definições de campo.
- **Leitura que o relatório faz e a que não faz:** eleger muitos senadores de um partido **pode indicar** apoio ao campo, e a diferença para o voto presidencial **pode indicar** algo; os números dizem o tamanho da diferença e se ela é incomum, nunca a causa.

---

## 8. Testes de anomalia (P8)

- **Testes:** comparecimento × voto por seção (impressão digital, Klimek e outros, 2012); último dígito (como controle); distribuição de votos por seção contra 2018 e 2022 e contra o outro cargo da mesma urna.
- **Correção:** Benjamini-Hochberg, taxa de falsa descoberta de 5%.
- **Uma seção ou município só é "a explicar" se** passar a correção **e** destoar do próprio histórico **e** destoar do outro cargo da mesma urna. Os três ao mesmo tempo.
- **Benford:** não é teste deste projeto (ver `PLANO.md` §7).
- **Simetria:** todo teste roda para todos os candidatos com mais de 1% dos válidos.

---

## 9. Registro de mudanças nos critérios

| Data | Critério | Antes | Depois | Motivo | Antes ou depois de ver o resultado |
|---|---|---|---|---|---|
| 05/out | T2.4 (fuso): regra de decisão | "vale o fuso que dá zero violações" | acrescenta desempate: entre as hipóteses com zero violações, vale a que deixa a **latência mínima** (percentil 0,5 de recebimento menos encerramento) mais próxima da mediana das UFs que já estão em horário de Brasília | no Acre as duas hipóteses dão zero violação (a de horário local é mais frouxa), então a regra original não decide. Latência mínima no Acre: 7 min em BRT e 127 min em horário local, contra 5 min em Alagoas | **depois** de ver AC e AL (as duas primeiras UFs derivadas), **antes** do teste com o país inteiro |
| 05/out | P7: anos do histórico | 2014, 2018 e 2022 | **só 2022** para a curva por ordem de chegada. 2018 entra só com votos finais (P5, P6). 2014 sai | o CSV de 2018 não tem `DT_BU_RECEBIDO` e o de 2014 não tem cabeçalho nem hora de recebimento. É limitação dos dados, não escolha | **antes** de ver qualquer resultado de 2026; depois de abrir os cabeçalhos dos arquivos |
| 05/out | P5: classe de referência | UFs de 2026, 2022 e 2018 com governador de apoio declarado | 2026 (20 UFs, CNN Brasil) e 2022 (15 UFs eleitos no 1º turno; ver a correção abaixo sobre Tocantins). 2018 entra só como sensibilidade, com 3 UFs (GO, MT, PR: eleitos no 1º turno, apoio declarado) | em 2018 a maior parte do apoio foi declarada depois do 1º turno e para governadores eleitos no 2º, o que não é comparável ao apoio de 2026 e 2022, declarado antes | **antes** de ver 2026; **depois** de ver a lacuna de 2022 por UF (variou de −17,5 a +18,2 pontos) |
| 05/out | P5: medida de concentração | "metade da diferença em menos de 1% das seções" | mantém a medida, e acrescenta a razão entre diferença líquida e fluxo bruto (`estavel` quando ≥ 0,2) e o índice de concentração do 1% de seções que mais contribuem (1,0 = proporcional ao tamanho). A medida literal só decide nas UFs `estavel` | com diferença líquida pequena perto do fluxo bruto (MT 2022: 0,06; RJ 2022: 0,19), poucas seções grandes já passam de metade de um valor quase zero, e a medida acusa concentração que não existe | **antes** de ver 2026; **depois** de ver a medida literal em 2022 |
| 05/out | P6: definições de campo | três: PL, candidatos apoiados por Flávio, partidos do governador aliado | **duas**: PL e candidatos que Flávio declarou apoiar (47, Ranking dos Políticos). A terceira sai | não foi achada fonte pública do apoio dos governadores aos candidatos ao Senado por UF. Sem fonte, não entra | **antes** de ver qualquer resultado de 2026 |
| 05/out | P6: referência histórica | "2018 e 2022 para o mesmo tipo de comparação" | referência de 2018 (também com dois votos por eleitor) e de 2022 (um voto), só pela definição por **partido** do presidente apoiado (PSL e PL em 2018 e 2022; PT para Lula/Haddad). A definição por apoio declarado só existe para 2026 | não há lista pública de apoio a candidatos ao Senado equivalente à de 2026 para 2018 e 2022. O critério "fora do intervalo em pelo menos duas definições" passa a ser: fora do intervalo histórico na definição por partido **e** o campo apoiado por Flávio diferente do PL no mesmo sentido | **antes** de ver qualquer resultado de 2026 |
| 05/out | P3: pontos da tela | tabela com 14 pontos montada a partir de um resumo automático da página do blog ao vivo | tabela refeita **só com o que está escrito nas páginas capturadas** (`dados/CAPTURAS.csv`): 14 pontos, dos quais 3 com duas ou mais fontes e 1 com votos absolutos. Pontos como "21,96%" e "88,46%", que estavam no resumo, **não existem na página** e saíram | a conferência com o texto bruto mostrou que o resumo trazia decimais e horários inventados. Tolerância passa a valer por instante da curva dentro de ±0,5 ponto no % de seções, como já estava escrito | **antes** de reconstruir qualquer curva de 2026 (a coleta ainda estava no início) |
| 05/out | P5: Tocantins em 2022 | fora da classe de referência, "porque a CNN e a Gazeta do Povo divergem" | **dentro**, ao lado de Bolsonaro | erro meu: a divergência vinha de um trecho de resultado de busca, não da página. Lidas as páginas capturadas, CNN Brasil, Gazeta do Povo e Revista Oeste colocam Tocantins ao lado de Bolsonaro. A classe de 2022 volta a ter 15 UFs | **antes** de ver qualquer resultado de 2026 |
| 06/out | T2.4 (fuso): unidade da decisão | por seção: a UF tem a hipótese se no máximo 0,1% das seções violam | por **município**: um município falha numa hipótese se mais de 5% das suas seções violam, e a UF aceita a hipótese se no máximo 1% das suas seções estão em municípios que falham. Municípios que falham ficam listados | com a regra por seção, Mato Grosso saiu "LOCAL" por 47 seções (0,57% das 8.287). Essas 47 estão em 3 municípios (31, 13 e 3 seções) onde o **encerramento na própria urna já está em horário de Brasília** (17:00), e as 10 de Pernambuco são todas de Fernando de Noronha (UTC-2). É relógio de urna fora do padrão em poucos municípios, e a regra por seção moveria 8.287 seções em uma hora por causa de 47 | **depois** de ver o resultado nacional do T2.4 (26 UFs BRT, MT LOCAL, ZZ sem decisão). A leitura literal é refeita como sensibilidade: `RESUMO.json`, chave `t24_sensibilidade_MT` |
| 06/out | Leitor do boletim | só `bu.dat` | `bu.dat` e `busa.dat` (boletim gerado pelo Sistema de Apuração, publicado no lugar do `bu.dat` em 31 seções: 2 de MG e 29 do exterior) | a coleta completa mostrou 87 seções sem boletim; 31 delas tinham `busa.dat`. O leitor também não achava o conteúdo em boletins pequenos (20 do exterior) | **depois** de ver a primeira validação (que acusou diferença só nesses lugares), **antes** de olhar curva ou qualquer análise com o boletim corrigido |
| 06/out | Todas as análises de 2026: voto de candidato fora da lista oficial | contado como voto válido, como saiu do boletim | contado como **nulo**, como no resultado oficial. Pares (UF, cargo, número) vêm do arquivo oficial de cada UF | a validação (P4) mostrou que o nulo oficial é igual ao nulo dos boletins mais os votos desses candidatos (candidatura sem registro válido: 154.719 votos em SP, 131.000 só no Senado). Sem o ajuste, o percentual de Tarcísio saía 62,59% contra 62,65% oficiais | **depois** de ver a primeira rodada completa (que já tinha P3, P5 e P6 com a regra antiga). Os números mudam na casa dos centésimos de ponto; os critérios de decisão não mudam |

## 10. Análises exploratórias acrescentadas depois de ver a primeira rodada de resultados

Estas **não** estavam no pré-registro e **não decidem** nenhum critério dele. Entram no relatório marcadas como exploratórias, para responder perguntas que o autor fez ou que os primeiros resultados levantaram.

| Análise | Por que entrou | Onde está |
|---|---|---|
| Calendário de chegada por UF e capital, e por UF, capital e porte do município (mais duas variantes de permutação) | com o calendário só por UF, a curva real ficou fora da faixa em 99 de 100 pontos; faltava saber quanto o calendário mais fino explica | `p1_permutacoes.csv` |
| Decomposição da queda por porte do município, tamanho da seção e capital × interior | pergunta do autor sobre colégios maiores e menores | `p1_decomposicao_*.csv` |
| Diferença entre o lote que chegou na parada e o lote implicado pelos pontos da imprensa; atraso de exibição na parada e na retomada | critério da §4 só pedia a contagem | `RESUMO.json`, chaves `p2_*` |
| Contabilidade exata e inferência ecológica em São Paulo (para onde foi o voto de quem votou em Tarcísio e em Haddad) | pergunta direta do autor sobre a diferença entre Tarcísio e Flávio | `p5_sao_paulo_*` |
| Senadores do PL por quem liderou a eleição presidencial na UF; alinhamento entre municípios do voto presidencial e do voto no partido ao Senado, com PT como espelho | a comparação histórica por partido (P6) é fraca: o PSL de 2018 e o PL de 2022 tinham candidatos de força muito diferente | `p6_senadores_do_pl_*`, `p6_alinhamento_*` |
| Contabilidade da base em São Paulo e nos outros casos (percentual dos válidos contra percentual de quem compareceu) | a revisão adversarial mostrou que a estimativa ecológica não explicava sozinha a diferença, e a conta exata da base separa o que é troca de voto do que é diferença de base | `p5_base_de_votos` no `RESUMO.json` |
| Estimativa ecológica com as duas restrições juntas | a primeira versão não conservava os totais (erro de 4% para Flávio) | `apuracao/uf.py`, `inferencia_ecologica` |

