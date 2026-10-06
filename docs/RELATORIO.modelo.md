# A noite de 4 de outubro de 2026, refeita com os boletins de urna

**Projeto aberto, escrito com IA e com todos os critérios gravados antes dos testes.** Cada número deste relatório sai de um script rodado sobre arquivo público; a tabela completa está em `resultados/RESUMO.json` e os passos para refazer estão em [`docs/REPLICAR.md`](docs/REPLICAR.md).

> ⚠️ **Quem escreveu:** a análise foi feita por uma IA (Claude) sob a direção do autor do repositório, que definiu o objetivo e a régua. A revisão adversarial é uma segunda passada da própria IA, registrada em [`docs/REVISAO_ADVERSARIAL.md`](docs/REVISAO_ADVERSARIAL.md). **Nenhuma pessoa revisou os resultados antes desta publicação.**

---

## 0. Em resumo

<<RESUMO>>

---

## 1. O que este relatório não consegue dizer

Antes de qualquer número, os limites:

- **Não audita o software nem o hardware da urna.** O projeto começa no boletim de urna que cada urna imprimiu e publicou. Se o voto foi gravado errado dentro da urna, este trabalho não vê.
- **Não vê o sistema interno do TSE.** A causa técnica da parada de cerca de uma hora na tela de Presidente só pode ser confirmada pelo registro interno do sistema de divulgação, que não é público. O projeto mede o **efeito** da parada, não a causa.
- **Não sabe como cada pessoa votou.** O voto é secreto. Toda comparação entre cargos (governador e presidente, senador e presidente) é feita por seção ou município, e o que se conclui sobre "quem votou em quem" é **inferência ecológica**, que pode errar.
- **Não verifica a assinatura digital dos boletins.** Testei a hipótese de que o hash interno do `bu.dat` fosse o SHA-256, o SHA-512 ou o SHA3-512 do conteúdo dos votos, em cinco recortes diferentes, e nenhuma bateu. A especificação pública de verificação de assinatura não foi encontrada. Fica registrado como **não verificado**.
- **Não tem as telas da noite.** O TSE sobrescreve o arquivo a cada atualização. A série de telas foi substituída pela reconstrução com a hora de recebimento, conferida contra {{p3_resumo.pontos}} pontos publicados pela imprensa.
- **Quase todos os pontos publicados têm uma fonte só.** Só {{p3_resumo.pontos_com_duas_ou_mais_fontes}} têm duas ou mais, e um tem os votos absolutos.

**A régua do texto:** "consistente com" e "não explicado por". O relatório não escreve "houve fraude" nem "ficou provado que não houve". Um resultado consistente quer dizer que os dados públicos fecham entre si. Um resultado não explicado vira pergunta específica, com endereço (seção, horário, cargo), para quem tem acesso ao que é interno.

**Como lemos alinhamento político:** por **apoio declarado**, com fonte, e não por partido (correção do autor, 05/out). Tarcísio é do Republicanos e declarou apoio incondicional a Flávio em 31/jul/2026. Uma diferença entre o voto de um aliado e o voto de Flávio **pode indicar** algo, e também pode ser voto dividido, efeito de quem está no cargo ou rejeição diferente de cada nome. O relatório mede o tamanho da diferença contra casos comparáveis e não atribui causa.

---

## 2. Os dados e a verificação

<<DADOS>>

---

## 3. A curva da noite: cada número da tela é a soma de boletins que já tinham chegado?

<<CURVA>>

---

## 4. A parada de cerca de uma hora

<<PARADA>>

---

## 5. Por que a vantagem do primeiro colocado caiu durante a noite

<<QUEDA>>

---

## 6. São Paulo: Tarcísio, Haddad, Flávio e Lula

<<SP>>

---

## 7. Senado e presidente

<<SENADO>>

---

## 8. Testes de anomalia

<<ANOMALIA>>

---

## 9. O que ficou sem explicação

<<SEM_EXPLICACAO>>

---

## 10. Como refazer, e o que mudou ao longo do trabalho

- **Refazer:** [`docs/REPLICAR.md`](docs/REPLICAR.md).
- **Critérios antes dos testes:** [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md), commit `a3b0a66`; as emendas estão na tabela da §9 de lá, cada uma dizendo se foi feita antes ou depois de ver o resultado. Todas foram feitas antes de qualquer resultado de 2026.
- **Erros achados no caminho e já corrigidos:** [`docs/CORRECOES.md`](docs/CORRECOES.md).
- **Fontes capturadas, com hash:** `dados/CAPTURAS.csv`.
