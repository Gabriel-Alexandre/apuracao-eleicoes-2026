# Fontes de dados: o que existe, o que foi testado e o que não existe

**Sondagem feita em:** 05/out/2026, entre 20h50 e 21h05 (horário de Brasília), um dia depois do 1º turno.
**Como refazer a sondagem:** `python ferramentas/sondar-fontes.py`. O script testa os mesmos endereços e imprime o status de cada um.

> Este arquivo é o dono do inventário de dados. O `PLANO.md` aponta para cá e não repete endereço.

Legenda: ✅ testado e respondeu · ⏳ esperado, ainda não publicado · ❌ não existe ou não é público · ⚠️ existe, com ressalva.

---

## 1. Códigos da eleição de 2026

Lidos em `https://resultados.tse.jus.br/oficial/comum/config/ele-c.json` (✅, 22.749 bytes).

| Código | O que é |
|---|---|
| `3220` | pleito do 1º turno de 04/10/2026 (`cdpr` 1219). Campo `dtlim`: **04/10/2034** |
| `6257` | eleição federal, 1º turno: **Presidente** (`cdt2` = 6258, o 2º turno) |
| `6259` | eleição estadual, 1º turno: Governador, Senador, Deputado Federal, Deputado Estadual, Deputado Distrital (`cdt2` = 6260) |
| `6261` | Conselheiro Distrital |

Códigos de cargo usados nos arquivos: `0001` Presidente, `0003` Governador, `0005` Senador (conferidos nos arquivos de SP).

⚠️ O campo `dtlim` é lido como a data até quando os arquivos ficam no ar. **Não há documento que confirme essa leitura.** O que se sabe é que os arquivos por seção de 2022 (`ele2022/arquivo-urna/406/...`) já respondem **404** hoje. Por isso a coleta inclui uma cópia local com hash (Fase 1 do plano).

---

## 2. Resultado oficial por abrangência (país, UF, município)

| Arquivo | Status | O que traz |
|---|---|---|
| `oficial/ele2026/6257/dados/br/br-c0001-e006257-u.json` | ✅ 9.349 bytes | resultado nacional de Presidente |
| `oficial/ele2026/6257/dados/<uf>/<uf>-c0001-e006257-u.json` | ✅ (SP testado) | Presidente na UF |
| `oficial/ele2026/6259/dados/<uf>/<uf>-c0003-e006259-u.json` | ✅ (SP testado) | Governador na UF |
| `oficial/ele2026/6259/dados/<uf>/<uf>-c0005-e006259-u.json` | ✅ (SP testado) | Senador na UF |
| `oficial/ele2026/6257/config/mun-e006257-cm.json` | ✅ 534.025 bytes | lista de municípios |
| `oficial/ele2026/6257/dados-simplificados/...-r.json` | ❌ 404 | o formato simplificado de 2022 não existe com esse nome em 2026 |

**Campos conferidos no arquivo nacional** (gerado em 05/10/2026 12:51:47):

- `s` (seções): `ts` 499.248 seções, `st` 499.248 totalizadas, `si` 499.207 instaladas, `sni` 41 não instaladas.
- `e` (eleitorado): `te` 158.745.502 eleitores, `c` 125.275.835 compareceram (78,92%), `a` 33.469.244 abstenções.
- `v` (votos): `tv` 125.275.835, `vv` 119.300.788 válidos, `vb` 2.300.798 brancos, `tvn` 3.674.249 nulos (2,93%), `van` 0 anulados, `vansj` 0 anulados sub judice.
- `carg` → `agr` → `par` → `cand`: votos (`vap`) e percentual (`pvap`) por candidato. Flávio Bolsonaro 56.104.503 (47,03%), Lula 53.879.538 (45,16%).
- `dg`/`hg` (data e hora de geração do arquivo) e `idg` (um número de geração que cresce a cada atualização).

⚠️ **Estes arquivos guardam só a última versão.** O TSE sobrescreve o mesmo endereço a cada atualização. A série da noite não fica no servidor (ver §6).

---

## 3. 🔑 Por seção: hora de recebimento, boletim de urna, RDV e log

Esta é a fonte que permite reconstruir a apuração **ao longo do tempo**.

| Arquivo | Status | O que traz |
|---|---|---|
| `oficial/ele2026/arquivo-urna/3220/config/<uf>/<uf>-p003220-cs.json` | ✅ (AC: 146.065 bytes, 2.411 seções) | a árvore município → zona → seção da UF. Seção agregada aparece com `nsp` (a seção principal). Cada seção traz `da`/`ha` |
| `oficial/ele2026/arquivo-urna/3220/dados/<uf>/<mun>/<zona>/<secao>/p003220-<uf>-m<mun>-z<zona>-s<secao>-aux.json` | ✅ | **`dr`/`hr`: data e hora de recebimento do boletim**, `st` (`Totalizado`), o `hash` e a lista de arquivos da seção |
| `.../<secao>/<hash>/o03220<uf><mun><zona><secao>-bu.dat` | ✅ 9.019 bytes (1 seção) | o boletim de urna digital, binário |
| `.../-rdv.dat` | ✅ 14.539 bytes | o registro digital do voto (os votos em ordem embaralhada, sem identificação) |
| `.../-vota.vsc` | ✅ 62.605 bytes | arquivo de assinaturas |
| `.../-log.jez` | ✅ 102.203 bytes | o log da urna, compactado (dentro: `logd.dat`, texto) |

**Exemplo real conferido** (AC, Porto Walter, zona 0004, seção 0077):

- `aux.json`: `"dr": "04/10/2026", "hr": "18:34:08", "st": "Totalizado"`.
- `logd.dat`: `15:40:09 Operador selecionou: Encerrar votação` · `15:44:11 Imprimindo relatório [BU]` · `15:44:48 Gerando arquivo de resultado [bu.dat] + [Término]`.

⚠️ **Fuso horário em aberto.** O log da urna está no horário local (Acre, UTC-5). O `hr` do recebimento não diz o fuso. Se for Brasília, o boletim chegou 54 minutos depois de gerado; se for Acre, 2h50. O plano resolve isso com dado, não com suposição (Fase 2, teste T2.4).

⚠️ **O que `da`/`ha` do arquivo de configuração significam não está documentado.** Em AC, 2.270 das 2.411 seções têm `ha` entre 21:08:15 e 21:08:17, horário em que o boletim já tinha chegado. A leitura provável é a hora de publicação do arquivo da seção, mas **não entra como fato** até ser confirmada.

**Tamanho da coleta, calculado sobre a amostra de 1 seção:**

| Item | Conta | Total |
|---|---|---|
| Requisições (aux + bu.dat) | 499.248 × 2 | ~1,0 milhão |
| Espaço só do `bu.dat` | 499.248 × 9.019 bytes | ~4,5 GB |
| Espaço do `log.jez` | 499.248 × 102.203 bytes | ~51 GB |
| Tempo a 20 requisições/s | 1,0 mi ÷ 20 | ~14 h |
| Tempo a 100 requisições/s | 1,0 mi ÷ 100 | ~2,8 h |

O cabeçalho da resposta anuncia `X-RateLimit-Limit: 2000`. Isso é o limite do servidor, não um convite: a coleta roda com teto próprio e conservador.

---

## 4. Dados abertos (CSV): boletim de urna com a hora de recebimento

Portal: `https://dadosabertos.tse.jus.br` (API CKAN, `package_search`).

| Conjunto | Status | Observação |
|---|---|---|
| `resultados-2026-boletim-de-urna` (o CSV `bweb_1t_<UF>_*.zip`) | ⏳ ainda não publicado em 05/out | em 2022 o arquivo do 1º turno saiu com data de 05/10/2022, três dias depois do pleito |
| `resultados-2026-logs-do-sistema-de-preparacao-das-urnas-eletronicas-gedai-1-turno` | ✅ publicado em 04/10/2026 | log do sistema que prepara as urnas, com `.sha512` |
| `resultados-2026-correspondencias-esperadas-e-efetivadas-1-turno` | ✅ publicado em 04/10/2026 | qual urna estava prevista para cada seção e qual foi usada |
| `resultados-2022-boletim-de-urna` | ✅ | 1º e 2º turnos, por UF, com `.sha512` |
| `resultados-2018-boletim-de-urna` | ✅ | idem |
| `resultados-2014-boletim-de-urna` | ✅ | idem, com `.sha1` |

**Colunas do CSV de 2022, conferidas no arquivo do AC** (`bweb_1t_AC_051020221321.csv`):
`DT_BU_RECEBIDO` (a hora em que o boletim chegou) · `DT_ABERTURA` · `DT_ENCERRAMENTO` · `DT_EMISSAO_BU` · `QT_APTOS` · `QT_COMPARECIMENTO` · `QT_ABSTENCOES` · `DS_TIPO_URNA` (`APURADA` etc.) · `NR_VOTAVEL` · `QT_VOTOS` · `NR_URNA_EFETIVADA` · `DS_AGREGADAS` · `NR_JUNTA_APURADORA`.

Exemplo de 2022: `DT_ENCERRAMENTO 02/10/2022 15:01:09` · `DT_EMISSAO_BU 02/10/2022 15:04:15` · `DT_BU_RECEBIDO 02/10/2022 18:45:30`.

🔑 **Consequência para o plano:** a hora de recebimento existe por seção em **2014, 2018, 2022 e 2026**. Dá para reconstruir a curva da apuração das quatro eleições com o mesmo método e comparar. O leia-me do TSE descreve `DT_BU_RECEBIDO` só como *"Data do boletim de urna recebido"*, sem fuso. O fuso é teste, não suposição.

---

## 5. Comunicação oficial e imprensa

| Fonte | Status | O que traz |
|---|---|---|
| Agência Brasil, 05/10: [Congestionamento no sistema de dados gerou atraso na apuração, diz TSE](https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/congestionamento-no-sistema-de-dados-gerou-atraso-na-apuracao-diz-tse) | ✅ lido | Nunes Marques: *"O que ocorreu foi um congestionamento de dados"*; parada por volta das 19h em 64%, retomada por volta das 20h em 84% |
| Jornal de Brasília: [Sistema do TSE trava durante apuração presidencial](https://jornaldebrasilia.com.br/noticias/politica-e-poder/sistema-do-tse-trava-durante-apuracao-presidencial-e-deixa-resultados-parados-por-mais-de-uma-hora/) | ✅ lido | 19h06 com 64,81% das urnas; 20h08 com 84,96%; governador, Senado e Câmara **seguiram atualizando** |
| Boatos.org: [checagem do boato de investigação de fraude](https://www.boatos.org/politica/tse-vai-investigar-se-atraso-na-divulgacao-de-resultados-das-eleicoes-tem-relacao-com-fraude-contra-flavio-bolsonaro.html) | ✅ lido | cita a nota do TSE: a dificuldade ficou *"restrita à conversão de dados pelo programa de divulgação"* |
| OVALE (Sampi): [Com 64,8% de votos apurados, Flávio tem 49,58% e Lula tem 42,25%](https://sampi.net.br/ovale/noticias/3009139/geral/2026/10/com-648-de-votos-apurados-flavio-tem-4958-e-lula-tem-4225) | 🔎 só o título | ponto da curva |
| OVALE (Sampi): [Com 85% de apuração, Flavio tem 48,47%; Lula está com 43,49%](https://sampi.net.br/ovale/noticias/3009166/geral/2026/10/com-85-de-apuracao-flavio-tem-4847-lula-esta-com-4349) | 🔎 só o título | ponto da curva |
| CNN Brasil: [TSE registrou congestionamento no sistema de divulgação, diz Nunes Marques](https://www.cnnbrasil.com.br/eleicoes/tse-registrou-congestionamento-no-sistema-de-divulgacao-diz-nunes-marques/) | 🔎 não lido | |
| TSE: [Informações técnicas sobre a divulgação de resultados 2026](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados) | ⚠️ 403 para o robô | documentação dos arquivos JSON. A coleta tenta pelo navegador |

Toda fonte desta tabela entra no projeto com **captura**: URL, data e hora da consulta, sha256 da página e o trecho copiado. Mesma régua do projeto de checagem.

---

## 6. ❌ O que não existe, e o que fica no lugar

| O que se queria ter | Por que não há | O que fica no lugar |
|---|---|---|
| **A série de telas da noite** (cada versão do JSON nacional entre 17h e 22h) | o TSE sobrescreve o arquivo; o Wayback Machine guardou **1** captura do JSON de Presidente no dia da eleição depois das 17h (04/10, 20:27 UTC, que é 17:27 em Brasília), e nenhuma no intervalo da parada | (a) reconstruir a curva pelos boletins, ordenados pela hora de recebimento; (b) os **pontos publicados pela imprensa**, com hora, como prova externa da tela; (c) pedir publicamente a quem guardou (projetos de painel no GitHub, redações) |
| **A hora em que cada seção foi totalizada** (separada da hora de recebimento) | não aparece em arquivo público conhecido | usar o recebimento como limite inferior e medir o atraso pelo encaixe com os pontos da imprensa |
| **O log interno do sistema de divulgação** (o que travou entre 19h06 e 20h08) | é do TSE, não é público | o pedido pela Lei de Acesso à Informação é possível (ver `PLANO.md` §14). Sem ele, o projeto mede o efeito, não a causa técnica |
| **O voto de cada pessoa em cada cargo** (quem votou em Tarcísio e em Lula) | voto secreto; o RDV embaralha a ordem por cargo, então não liga o voto de governador ao de presidente da mesma pessoa | inferência ecológica por seção, com o limite dito em voz alta |
| **Pesquisa de boca de urna aberta, por seção** | não existe publicamente | fora do escopo |

---

## 7. Projetos de terceiros encontrados

| Projeto | O que faz | Serve para |
|---|---|---|
| [`joonetoo/eleicoes-2026`](https://github.com/joonetoo/eleicoes-2026) | painel ao vivo lendo os JSON do TSE | **não guarda série**: o README diz *"nenhum banco"* |
| [`vfrancisquini/painel-tse-2026`](https://github.com/vfrancisquini/painel-tse-2026) | painel local, atualiza a cada 30 s | a confirmar se alguém guardou o que leu |

---

## 8. Alinhamento político: fontes do critério de apoio (05/out)

Critério de alinhamento = **apoio declarado**, não partido (`PRE_REGISTRO.md` §0.1). Toda linha entra com captura na Fase 1.

| Fonte | O que traz | Observação |
|---|---|---|
| [CNN Brasil, 05/out: Metade dos governadores eleitos apoiaram Flávio no primeiro turno](https://www.cnnbrasil.com.br/eleicoes/governadores-eleitos-flavio-lula/) | tabela dos 20 governadores eleitos no 1º turno com o apoio de cada um: 10 Flávio, 5 Lula, 1 Caiado, 4 sem apoio declarado; 7 UFs vão a 2º turno de governador. O texto traz que Cleitinho (MG) e Pivetta (MT) declararam voto em Flávio **sem apoio oficial** do PL | ✅ capturada e conferida no texto bruto; os 20 nomes e as UFs batem com o resultado oficial do TSE (candidato com mais de 50% e eleito) |
| Space Money: Governadores eleitos em 2026: 11 apoiaram Flávio | outra contagem (11 Flávio, 5 Lula) | ⚠️ 403 para o robô; a divergência com a CNN é registrada e as conclusões são refeitas com as duas |
| [Ranking dos Políticos, 22/set: Quem Flávio Bolsonaro apoia para o Senado em 2026](https://ranking.org.br/en/articles/quem-flavio-bolsonaro-apoia-senado-2026) | 47 candidatos ao Senado em 27 UFs que Flávio declarou apoiar em 06/ago, de vários partidos (PL, PP, Republicanos, Podemos, Novo, PSD, União, PSDB). O texto diz que os palanques estaduais *não reproduzem necessariamente a composição partidária da candidatura presidencial* | ✅ capturada; os 47 nomes de `dados/senado-apoio-flavio.csv` foram conferidos um a um no texto bruto |
| [Metrópoles, 04/out: Tarcísio sobre Flávio](https://www.metropoles.com/sao-paulo/tenho-certeza-que-a-vitoria-esta-chegando-diz-tarcisio-sobre-flavio) | Tarcísio diz ter certeza da vitória e que vai participar da campanha de Flávio no 2º turno | ✅ lida |
| [Tribuna de Jundiaí, 31/07/2026](https://tribunadejundiai.com.br/politica/eleicoes-2026/tarcisio-apoio-flavio-bolsonaro-2026/) e [A Crítica, 31/07/2026](https://acritica.net/eleicoes-2026/tarcisio-apoio-incondicional-flavio-bolsonaro-sao-paulo/) | Tarcísio afirma em entrevista coletiva que o apoio a Flávio será **incondicional**, com presença em todos os eventos do candidato no estado | ✅ capturadas; duas fontes independentes, texto conferido |
| [CNN Brasil: PL elege senadores e terá a maior bancada](https://www.cnnbrasil.com.br/eleicoes/divisao-bancada-senado/) | senadores eleitos por UF e totais por partido | ✅ lida. ⚠️ o texto traz totais de PL diferentes em resumos de outros veículos (19 eleitos em 2026 e 28 na composição de 2027): a conta é refeita com o resultado oficial por UF |

✅ **Capturadas em 05/out:** 2022 ([CNN Brasil](https://www.cnnbrasil.com.br/politica/oito-governadores-eleitos-se-aliam-a-bolsonaro-e-quatro-apoiam-lula/): 9 com Bolsonaro e 6 com Lula entre os 15 eleitos no 1º turno; a [Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2022/eleicoes-governador-eleitos-apoios-lula-bolsonaro/) e a [Revista Oeste](https://revistaoeste.com/politica/eleicoes-2022/placar-dos-governadores-veja-quem-apoia-bolsonaro-e-lula-no-2o-turno/) também colocam Tocantins ao lado de Bolsonaro; a Revista Oeste, de 05/10/2022, dizia que Clécio, do Amapá, ainda não se pronunciara) e 2018 ([Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2018-10/bolsonaro-recebeu-apoio-de-15-dos-27-governadores-eleitos): Caiado, Mendes e Ratinho Júnior, eleitos no 1º turno, ao lado de Bolsonaro **na fase decisiva**, ou seja, no 2º turno).

⚠️ **Lição registrada em 05/out:** um resumo automático de página trouxe horários e decimais que não estavam na página (por exemplo "88,46%" e "90,61%"). Todo número de fonte de texto usado nas análises foi refeito a partir da página capturada (`dados/CAPTURAS.csv`, corpo em `dados/brutos/fontes/`).
