# Plano e método: a apuração do 1º turno de 2026, medida ao longo do tempo

**Escrito em:** 05/out/2026, um dia depois do 1º turno. **Estado:** planejamento. Nenhuma análise foi rodada.
**Dono deste arquivo:** o método. O inventário de dados mora em [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md); os testes com o critério de cada um, escritos antes de olhar os dados, moram em [`PRE_REGISTRO.md`](PRE_REGISTRO.md).

---

## 0. Em uma frase

Pegar os boletins de urna de todas as seções do país, ordenar cada um pela hora em que chegou ao TSE, refazer a apuração da noite de 04/10 minuto a minuto, e conferir se cada número que apareceu na tela, inclusive antes e depois da parada de uma hora, é a soma de boletins reais que já tinham chegado naquele momento. Em cima dessa base, responder as perguntas sobre estados, cargos e partidos com estatística, contra o histórico de 2014, 2018 e 2022.

---

## 1. Por que o projeto existe, e o que ele não promete

**A motivação** (palavras do autor, 05/out): muita gente questiona a contagem. O projeto usa IA de forma metodológica para medir, com número e fonte, se o que pareceu estranho tem explicação nos dados.

**O que o projeto consegue responder**, porque os dados existem:

1. Se o total divulgado bate com a soma dos boletins de urna publicados, seção por seção.
2. Se cada ponto da curva da noite é explicado pela ordem em que os boletins chegaram.
3. O que entrou no intervalo da parada e se a mudança de percentual depois dela é explicada pelo que entrou.
4. Onde estão, no mapa e no tipo de seção, as diferenças entre cargos (governador × presidente, senador × presidente).
5. Se o padrão de 2026 cabe no padrão das eleições anteriores.

**O que o projeto NÃO consegue responder, e diz isso no relatório:**

- Se a urna registrou corretamente o voto de cada eleitor. Isso é auditoria de software e hardware (testes públicos de segurança, teste de integridade no dia da eleição), e este projeto não tem acesso a ela. O projeto começa no boletim que a urna imprimiu e publicou.
- A causa técnica da parada dentro do sistema do TSE. O projeto mede o efeito; a causa só com o log interno, que não é público.
- Como cada pessoa votou em cada cargo. O voto é secreto, então toda conclusão sobre "quem votou em Tarcísio e em Lula" é inferência sobre seções, nunca sobre pessoas.

🔴 **A régua do relatório:** o projeto escreve "consistente com" e "não explicado por". Ele não escreve "provou que não houve fraude" nem "houve fraude". Um resultado consistente diz que os dados públicos fecham entre si; um resultado não explicado vira uma pergunta específica, com endereço (seção, horário, cargo), para quem tem acesso ao que é interno.

---

### 1.1 Alinhamento político se mede por apoio, não por partido

Correção do autor em 05/out: Tarcísio é do Republicanos e declarou apoio incondicional a Flávio. Dizer que "não é do mesmo partido, então não é do mesmo campo" é um erro de método. O projeto trata alinhamento como **apoio declarado**, com fonte, em três definições separadas (partido, candidatos que Flávio declarou apoiar, apoio do governador), e refaz as conclusões com todas. Uma diferença entre o voto de um aliado e o de Flávio **pode indicar** algo, e **também pode** ser voto dividido ou efeito de quem está no cargo: o relatório mede o tamanho dela contra casos comparáveis e não atribui causa. Detalhe em `PRE_REGISTRO.md` §0.1, §6 e §7.

---

## 2. Os fatos de partida, conferidos em 05/out

Antes de formular as perguntas, os números que motivaram o projeto foram conferidos na fonte. Dois deles chegaram ao autor diferentes do que os dados mostram, e a pergunta muda por causa disso.

| O que circulou | O que os dados mostram | Fonte |
|---|---|---|
| Depois da parada, "um candidato subiu e o que estava na frente desceu" | **Não houve troca de liderança.** Flávio liderava antes da parada (49,58% × 42,25% com 64,81% das seções), depois (48,47% × 43,49% com 84,96%) e no fim (47,03% × 45,16%). A vantagem diminuiu; ela não se inverteu | imprensa com hora (FONTES §5) e arquivo oficial (FONTES §2) |
| "Um candidato em São Paulo teve 64%" | Tarcísio (Republicanos, apoiador declarado de Flávio), governador, teve **62,65%** dos válidos (14.491.874 votos). Em SP, Flávio teve **51,93%** (12.922.023) e Lula **38,20%** (9.505.413) | `sp-c0003-e006259-u.json` e `sp-c0001-e006257-u.json` |
| Parada de uma hora | Confirmada: 19h06 com 64,81%, 20h08 com 84,96%. Os outros cargos seguiram atualizando. O TSE atribuiu a parada a congestionamento no programa de divulgação, sem efeito na totalização | FONTES §5 |
| Muitos senadores do PL eleitos e o presidente sem o mesmo voto | A ser medido. ⚠️ Em SP, os votos válidos de Senador somam **43.377.903** e os de Presidente **24.882.948**: em 2026 cada eleitor vota em **dois** senadores. Comparar a contagem de voto de senador com a de presidente, sem ajustar isso, gera a impressão errada por construção | `sp-c0005-e006259-u.json` |

**Conta preliminar, que o projeto vai substituir pela reconstrução** (decidir × calcular: a conta entra sem ser pedida):

Se os pontos da imprensa forem fiéis, o lote que entrou entre 64,81% e 84,96% das seções (20,15% das seções) tinha, em média, **Flávio ~44,9% e Lula ~47,5%**. O lote final, de 84,96% a 100% (15,04%), tinha **Flávio ~38,9% e Lula ~54,6%**. A queda da vantagem é o que acontece quando os últimos lotes vêm de lugares onde Lula vai melhor. ⚠️ A conta trata "percentual de seções" como se fosse "percentual de votos válidos", o que não é exato (seções têm tamanhos diferentes). É uma ordem de grandeza, não um resultado.

Em SP, Tarcísio teve **1.569.851** votos a mais que Flávio, e Lula **1.081.757** a mais que Haddad. Os votos válidos de Presidente em SP superam os de Governador em **1.752.435**, porque o número de brancos e nulos muda de um cargo para outro. Isso também entra na comparação.

---

## 3. As perguntas, escritas de forma que dá para testar

| Nº | Pergunta | Dado principal |
|---|---|---|
| **P1** | Por que a vantagem de Flávio caiu ao longo da noite, de 7,33 pontos (64,81%) para 1,87 ponto (100%)? Quanto disso é explicado pela ordem de chegada por região, por porte de município, por capital × interior e pelo exterior? | boletim por seção + hora de recebimento |
| **P2** | O que aconteceu entre 19h06 e 20h08? Os boletins continuaram chegando? O que entrou no intervalo explica a mudança de 49,58/42,25 para 48,47/43,49? | idem, com a janela da parada |
| **P3** | Cada número exibido na noite é a soma de boletins reais que já tinham chegado? | boletins + pontos com hora (imprensa, Wayback, terceiros) |
| **P4** | A soma dos boletins publicados bate com o total oficial, por município, UF e cargo? O boletim publicado bate com o CSV de dados abertos e com o próprio log da urna? | `bu.dat`, CSV `bweb`, JSON oficial, `log.jez` |
| **P5** | Em SP, onde está a diferença entre Tarcísio e Flávio, e entre Lula e Haddad? Ela cabe no que acontece nas outras UFs em que o governador declarou apoio ao candidato a presidente, em 2026 e em 2018 e 2022? Dentro de SP, ela está espalhada ou concentrada? | boletim por seção, 2026 e 2022; apoio declarado (`FONTES_DE_DADOS.md` §8) |
| **P6** | O PL e aliados elegeram muitos senadores. Isso aparece como voto em Flávio na mesma UF, ou há diferença? Se há, ela é do tamanho do que ocorreu em 2018 e 2022 (campo do presidente × campo no Senado), depois de ajustar o voto duplo, o branco e nulo por cargo e a fragmentação dos adversários? O campo é medido de três formas: partido, candidatos que Flávio declarou apoiar e apoio do governador aliado | resultado por UF e por seção, Senador × Presidente |
| **P7** | A curva de 2026 tem formato e tamanho de "virada" parecidos com os de 2014, 2018 e 2022 (1º e 2º turnos)? | CSV `bweb` históricos, com `DT_BU_RECEBIDO` |
| **P8** | Os testes estatísticos usados na literatura para achar irregularidade apontam alguma seção ou município fora do padrão de 2026 **e** das eleições anteriores **e** dos outros cargos da mesma urna? | boletim por seção, todos os anos |

Cada pergunta tem, no `PRE_REGISTRO.md`, o teste, o resultado que a explica e o resultado que fica sem explicação.

---

## 4. Como a apuração funciona, no que importa para o método

O caminho de um voto até a tela tem quatro relógios diferentes. Misturar esses relógios é o erro que mais produz suspeita falsa.

```
URNA                         TRANSMISSÃO              TSE                          TELA
encerra (log da urna)  ──►   boletim enviado    ──►   recebido (dr/hr)      ──►    arquivo JSON publicado
imprime o BU                                          validado e totalizado        (dg/hg, idg)
gera bu.dat, rdv, log                                 (status "Totalizado")
```

| Relógio | Onde está | O que mede |
|---|---|---|
| Encerramento e emissão do BU | `log.jez` da urna; `DT_ENCERRAMENTO` e `DT_EMISSAO_BU` no CSV | quando a seção terminou. ⚠️ horário local da urna |
| Recebimento | `dr`/`hr` no `aux.json`; `DT_BU_RECEBIDO` no CSV | quando o boletim chegou à Justiça Eleitoral |
| Totalização | não publicado por seção | quando o boletim passou a contar no total |
| Divulgação | `dg`/`hg` e `idg` no JSON oficial | quando o número foi publicado para o público |

Fatos já conferidos: o boletim sai da urna com assinatura digital e é publicado por seção (FONTES §3); o TSE diz que só incorpora o boletim depois de checar se ele veio da urna daquela seção e se a assinatura confere (ver [Diário de Pernambuco, ago/2026](https://www.diariodepernambuco.com.br/brasil/2026/08/11721101-totalizacao-dos-votos-e-aberta-auditavel-e-segura-diz-tse.html), a capturar na Fase 1); a parada de 04/10 foi atribuída à divulgação, não à totalização (FONTES §5).

⬜ **A documentar com fonte na Fase 1, antes de qualquer texto público:** horário oficial de votação em 2026 e se ele é unificado em horário de Brasília; o caminho da transmissão (pontos de transmissão, satélite, juntas); o que é seção agregada, urna substituída, seção não instalada, voto em separado e votação por cédula; quais verificações existem e quem pode fazê-las (teste de integridade, Boletim na Mão, auditoria de fiscais). Nada disto entra no relatório a partir da memória do modelo.

---

## 5. O que dá para ter e o que não dá (resumo)

O detalhe, com endereço e status testado, está em [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md).

| Dado | Situação | Uso |
|---|---|---|
| Resultado oficial final por país, UF e cargo | ✅ no ar | ponto de chegada, total a conferir |
| Hora de recebimento por seção, 2026 | ✅ no ar (`aux.json`) | **a espinha da reconstrução** |
| Boletim, RDV, assinatura e log de cada seção, 2026 | ✅ no ar | votos por seção, integridade, encerramento |
| CSV de boletim de urna 2026 (`bweb`) | ⏳ não publicado em 05/out | segunda via independente dos votos e da hora |
| CSV de boletim de urna 2014, 2018, 2022 | ✅ | a curva histórica, com o mesmo método |
| Série das telas da noite | ❌ não guardada pelo TSE | substituída pela reconstrução + pontos da imprensa |
| Log interno da divulgação | ❌ não público | pedido por LAI é possível; sem ele, mede-se o efeito |
| Voto individual por cargo | ❌ secreto | inferência ecológica por seção, com limite declarado |

---

## 6. O método, fase a fase

Cada fase tem entrada, saída e critério de pronto. A ordem entre as fases é dependência de dados, não prioridade.

### Fase 0 · Pré-registro (antes de olhar qualquer dado por seção)

- **Entrada:** este plano e as perguntas.
- **Saída:** `PRE_REGISTRO.md` aprovado pelo autor e gravado em commit. O hash do commit é o carimbo de que os critérios vieram antes dos resultados.
- **Pronto quando:** cada pergunta tem teste, tolerância e o que conta como "não explicado".
- **Declaração obrigatória:** o que já foi visto antes do registro (os totais finais, os pontos 64,81% e 84,96% da imprensa e a amostra de 1 seção do AC). Ver `PRE_REGISTRO.md` §0.

### Fase 1 · Coleta e preservação

1. Baixar a configuração de seções de todas as UFs e do exterior (`<uf>-p003220-cs.json`).
2. Para cada seção: `aux.json` (hora de recebimento, status, hash) e `bu.dat`. `rdv.dat`, `vota.vsc` e `log.jez` entram numa **amostra estratificada** e nas seções que a análise apontar (ver o custo em FONTES §3).
3. Baixar os JSON oficiais de Presidente, Governador e Senador de todas as UFs, e do Brasil.
4. Baixar o CSV `bweb` de 2014, 2018 e 2022 (1º e 2º turnos) e, quando publicado, o de 2026.
5. Capturar as fontes de texto (TSE, imprensa, documentação), com URL, hora, sha256 e trecho.
6. Juntar os pontos da curva publicados com hora: matérias "com X% apurado", ao vivo de portais, publicações oficiais do TSE nas redes. Cada ponto entra com a fonte capturada.

- **Saída:** `dados/brutos/` (fora do git, pesado) e `dados/MANIFESTO.json` (dentro do git): para cada arquivo, URL, hora da coleta, tamanho e sha256.
- **Pronto quando:** 499.248 seções com `aux.json` lido (ou a falta de cada uma registrada com o código HTTP), e todos os JSON oficiais baixados.
- **Regras da coleta:** teto de requisições próprio e baixo, retomada sem rebaixar o que já está salvo, nenhum arquivo sobrescrito sem guardar o hash anterior.

### Fase 2 · Validação dos dados (antes de qualquer conclusão)

| Teste | O que confere | Se falhar |
|---|---|---|
| T2.1 | o `bu.dat` decodifica e a soma por cargo fecha com o comparecimento da seção | a seção vai para a lista de exceções, com o motivo |
| T2.2 | a assinatura do boletim confere com a chave publicada | idem; o relatório publica a contagem |
| T2.3 | soma de todos os boletins = total oficial, por município, UF e cargo | diferença diferente de zero vira achado com endereço |
| T2.4 | **o fuso do `hr`**: para cada UF, a hora de recebimento tem de ser posterior ao encerramento do log da urna convertido para Brasília; o fuso certo é o que nunca viola isso | se nenhum fuso for coerente, o tempo não serve e a Fase 3 para |
| T2.5 | `aux.json` × CSV `bweb` (quando sair): mesma hora e mesmos votos por seção | divergência vira achado |
| T2.6 | seções agregadas, não instaladas (41), urnas substituídas e seções com mais de um boletim: contadas e explicadas com fonte | |

O decodificador do `bu.dat` segue a especificação publicada pelo TSE (a localizar e capturar na Fase 1). Se não houver especificação pública utilizável, a via principal dos votos passa a ser o CSV `bweb`, e o `bu.dat` fica para a conferência das assinaturas.

### Fase 3 · Reconstrução da curva da noite

1. Ordenar todas as seções pela hora de recebimento validada.
2. Somar os votos de cada candidato em ordem, gerando a curva: a cada minuto, % de seções recebidas, % de cada candidato, vantagem.
3. Para cada ponto publicado com hora (imprensa, Wayback, terceiros), achar o momento da curva com o mesmo % de seções e comparar os percentuais dos candidatos.
4. Estimar um único atraso entre recebimento e divulgação (um parâmetro só, para o país todo) que melhor encaixa todos os pontos.

🔑 **Por que este é o teste mais forte do projeto:** um número exibido na tela, se for honesto, é a soma de um conjunto de boletins reais. Se a curva reconstruída passa por todos os pontos publicados com um atraso só, a tela da noite foi a soma progressiva dos boletins. Se algum ponto não puder ser alcançado por nenhuma ordem plausível de chegada, esse ponto vira o achado mais importante do relatório. O teste corta para os dois lados.

### Fase 4 · As perguntas

| Pergunta | Como se responde |
|---|---|
| **P1** (queda da vantagem) | decompor a mudança da vantagem em contribuições: região, UF, porte do município, capital × interior, exterior, urna substituída, horário de encerramento. Contrafactual: se todas as seções tivessem chegado em ordem aleatória, como seria a curva? (permutação, 10.000 ordens) |
| **P2** (a parada) | contar boletins recebidos entre 19h06 e 20h08 menos o atraso estimado; comparar a composição desse lote com o lote implícito pelos dois pontos da imprensa; mostrar a curva dos outros cargos no mesmo intervalo |
| **P3** (cada número da tela) | o encaixe da Fase 3, ponto a ponto, com o erro de cada um |
| **P4** (integridade aritmética) | os testes T2.1 a T2.6, publicados como tabela completa |
| **P5** (SP) | diferença Tarcísio − Flávio e Lula − Haddad por seção; mapa por município; concentração (quantas seções fazem metade da diferença); comparação com 2022; inferência ecológica (King, ou regressão por seção) com o intervalo de incerteza e o aviso de falácia ecológica |
| **P6** (Senado × Presidente) | por UF: votos do candidato do PL ao Senado sobre votos válidos de Senador **por eleitor** (dividido por 2), contra o voto de Flávio; fragmentação dos adversários; branco e nulo por cargo; quantos senadores do PL venceram com menos voto que Flávio no estado e quantos com mais |
| **P7** (histórico) | a mesma reconstrução para 2014, 2018 e 2022: tamanho da mudança de vantagem entre 60%, 85% e 100% das seções, e se houve troca de liderança. Coloca 2026 na distribuição histórica |
| **P8** (testes de anomalia) | ver §7 |

### Fase 5 · Revisão adversarial

Uma passada separada da IA, com a instrução de derrubar cada conclusão: procurar o erro de fuso, o erro de unidade (seção × voto), a seção contada duas vezes, a conclusão que vai além do dado e a frase que só vale para um lado. Cada conclusão sai com `revisao_ia` registrada: mantida, alterada ou retirada, e por quê. Mesma regra do projeto de checagem.

### Fase 6 · Relatório

- `RELATORIO.md` (técnico, completo) e um resumo em linguagem simples.
- Toda figura com o script que a gera e o número que ela mostra em tabela ao lado.
- Achados que dão "consistente" e achados que dão "não explicado" com o mesmo destaque.
- A seção "O que este projeto não consegue dizer" no começo, não no fim.
- **Replicação:** um comando que refaz tudo a partir dos dados brutos e confere os hashes do manifesto.

---

## 7. Estatística: o que usar, o que evitar e por quê

| Técnica | Para quê | Cuidado registrado |
|---|---|---|
| Soma progressiva ordenada por tempo | P1, P2, P3 | a unidade é seção; percentual da tela pode ser de seção ou de voto, e isso se confere na fonte |
| Permutação da ordem de chegada | contrafactual de P1 e P7 | 10.000 ordens; o resultado é uma faixa, não um número |
| Decomposição da mudança de vantagem | P1 | contribuição = peso do grupo × diferença de comportamento; somar e fechar com o total |
| Regressão por seção e inferência ecológica | P5, P6 | **falácia ecológica**: relação entre seções não é relação entre pessoas. Sempre com intervalo e com o aviso |
| Impressão digital de comparecimento × voto (Klimek e outros, 2012) | P8 | sensível à composição social das seções. Só vale **comparado** com 2014, 2018, 2022 e com os outros cargos da mesma seção |
| Teste do último dígito (Beber e Scacco) | P8 | só faz sentido em contagem digitada à mão; em urna eletrônica, o resultado esperado é que não aponte nada. Entra como controle |
| Lei de Benford | ⛔ **não usar como evidência** | a literatura mostra que ela não detecta fraude de forma confiável em dado eleitoral (Deckert, Myagkov e Ordeshook, *Political Analysis*, 2011). Entra só para explicar por que gráficos de Benford que circulam não provam nada |
| Correção para muitos testes | P8 | com ~500 mil seções, algumas vão parecer estranhas por acaso. Benjamini-Hochberg com taxa de falsa descoberta de 5%, declarada antes |
| Placebo | todas | o mesmo teste em 2022, no outro cargo da mesma urna e com a ordem embaralhada. Um teste que acusa tudo não acusa nada |

As referências desta tabela entram com captura na Fase 1, com pelo menos duas fontes por afirmação de método.

---

## 8. Validação cruzada: cada número por dois caminhos

| Número | Caminho 1 | Caminho 2 | Caminho 3 |
|---|---|---|---|
| Total por candidato e UF | JSON oficial | soma dos `bu.dat` | soma do CSV `bweb` |
| Votos de uma seção | `bu.dat` | CSV `bweb` | foto do BU impresso (amostra pública, se houver) |
| Hora de chegada | `aux.json` | `DT_BU_RECEBIDO` do CSV | limite inferior pelo log da urna |
| Ponto da curva às 19h06 | reconstrução | matéria com hora | segunda matéria de outro veículo |
| Fala do TSE sobre a parada | nota oficial | duas reportagens que citam a nota | |

Duas matérias com o mesmo parágrafo contam como uma fonte.

---

## 9. Onde a IA entra, e como ela é controlada

| A IA faz | A IA não faz |
|---|---|
| escreve e testa o código de coleta, decodificação e análise | ⛔ dá número de memória. Todo número sai de script rodado sobre dado com hash |
| lê a documentação técnica do TSE e resume, com o trecho copiado | ⛔ afirma como funciona o sistema sem fonte capturada |
| propõe testes e acha furos no próprio raciocínio (Fase 5) | ⛔ muda critério depois de ver o resultado sem registrar o antes e o depois |
| redige o relatório a partir das tabelas geradas | ⛔ escreve conclusão que a tabela não sustenta |
| varre as ~500 mil seções em busca do que destoa | ⛔ trata seção apontada como irregular antes de olhar o boletim, o log e o histórico dela |

O registro da sessão e o histórico do git são a prova do que a IA fez e do que o autor fez. O vídeo depois usa essa matriz (mesma regra de autoria do projeto de checagem).

---

## 10. Reprodutibilidade

- Todo dado bruto entra no `MANIFESTO.json` com sha256. O relatório cita o hash do manifesto.
- Scripts determinísticos: mesma entrada, mesma saída. Aleatoriedade (permutações) com semente fixa e declarada.
- Versões das bibliotecas fixadas em `requirements.txt`.
- O dado pesado não vai para o git. O repositório tem o script que baixa e confere, e um pacote compacto dos dados derivados (votos por seção e hora, em CSV ou Parquet) para quem não quer baixar 500 mil arquivos.
- `CORRECOES.md`: todo erro achado depois da publicação, com o antes e o depois.

---

## 11. O que seria suspeito, e o que não seria

O critério exato de cada teste está no `PRE_REGISTRO.md`. Em linhas gerais:

| Não é sinal de problema (e o relatório explica por quê) | Seria um achado a explicar |
|---|---|
| a vantagem mudar ao longo da noite | um ponto da tela que nenhuma soma de boletins chegados alcança |
| a parada da tela, se os boletins continuaram chegando e o lote que entrou explica a mudança | boletins sem chegada registrada na janela e, mesmo assim, o salto |
| um candidato a governador ter mais voto que o candidato a presidente do mesmo campo | soma dos boletins diferente do total oficial |
| seções com 100% para um candidato em lugar pequeno e homogêneo, se isso já acontecia em 2018 e 2022 | o mesmo padrão aparecendo só em 2026, só num cargo e só num lado |
| percentuais que "parecem redondos" | boletim com assinatura que não confere, ou chegada antes do encerramento da urna |
| um gráfico de Benford "fora da curva" | |

---

## 12. Travas do assunto

Valem para o código, o relatório e qualquer peça de conteúdo feita a partir dele. São as mesmas do projeto de checagem.

- ⛔ Nada de "fraude" ou "prova de que não houve fraude" como conclusão. Ver §1.
- ⛔ Nada de recomendação de voto, de avaliação de candidato ou de governo.
- ⛔ Nada de julgar intenção de quem quer que seja (TSE, campanhas, eleitores, quem compartilhou boato).
- ⛔ Nada de testar um lado só. Todo teste roda para todos os candidatos, e a tabela mostra os dois.
- ⛔ Nada de chamar quem levantou a suspeita de mentiroso. O projeto responde à pergunta, não às pessoas.

---

## 13. Riscos e o que já se sabe sobre eles

| Risco | Medida |
|---|---|
| Os arquivos por seção saírem do ar (os de 2022 já saíram) | coleta com hash na Fase 1; o CSV `bweb` é a cópia permanente |
| O fuso da hora de recebimento estar errado | teste T2.4, decidido por dado |
| Os pontos da imprensa terem sido digitados com erro | dois veículos por ponto; ponto com uma fonte só fica marcado |
| O percentual da tela ser por seção e a conta ser por voto | conferir no JSON (`pst` é de seções) e trabalhar sempre na mesma unidade |
| Limite de requisições do servidor | teto próprio baixo e retomada |
| Muitos testes produzirem falso alarme | correção de falsa descoberta e placebo |
| Leitura política do resultado, a três semanas do 2º turno | as travas do §12 e o "não consegue dizer" no topo |

---

## 14. ⬜ Decisões que são do autor

Registro, não pendência. Nenhuma delas trava o planejamento.

| Decisão | Por que importa |
|---|---|
| Nome definitivo do repositório | o provisório é `apuracao-eleicoes-2026` |
| Remoto no GitHub, privado ou público, e quando | o projeto de checagem nasceu privado e ficou público em 18/set, por decisão dele |
| Licença do código e do conteúdo | o projeto de checagem usa MIT no código e uma licença separada no conteúdo |
| Baixar o `log.jez` de todas as seções (~51 GB) ou só da amostra | custo de disco e de tempo contra a força do teste de encerramento × chegada |
| Anos do histórico: 2014, 2018 e 2022, ou também os 2ºs turnos | cada turno a mais é uma curva a mais no gráfico de comparação |
| Pedir ao TSE, por Lei de Acesso à Informação, o registro da parada | é a única via para a causa técnica; resposta não tem prazo garantido para o vídeo |
| Pedir publicamente a quem guardou a série da noite (painéis, redações) | mais pontos de tela deixam o teste da Fase 3 mais forte |
| Quando publicar o relatório, e se antes ou depois do 2º turno (25/10) | decisão editorial |
| Como identificar o uso de IA no relatório e no vídeo | o projeto de checagem registrou a mesma questão (`docs/DEBATES.md` §7 de lá) como decisão dele |
| Repetir o método no 2º turno | o mesmo código serve, com o pleito novo |
