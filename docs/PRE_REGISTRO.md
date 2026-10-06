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
| | | | | | |
