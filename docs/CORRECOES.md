# Correções: erros achados no caminho

Registro de tudo que estava errado no projeto e foi corrigido, com o antes, o depois e como foi achado. Erro que fica em silêncio é erro que volta.

| Quando | O que estava errado | Como foi achado | O que mudou |
|---|---|---|---|
| 05/out, noite | O texto do planejamento e da primeira resposta tratavam Tarcísio como "do Republicanos e não do PL", como se o partido separasse o campo político dele do de Flávio | o autor corrigiu: Tarcísio é apoiador declarado de Flávio e o alinhamento vai além do partido | alinhamento passa a ser **apoio declarado, com fonte**, em definições separadas; ver `PRE_REGISTRO.md` §0.1. O relatório descreve diferenças como "pode indicar", sem atribuir causa |
| 05/out | A tabela de 14 pontos da tela vinha de um resumo automático da página de um blog ao vivo, e trazia decimais e horários que não existem na página (por exemplo "21,96%", "88,46%", "90,61%") | captura da página e leitura do texto bruto | tabela refeita só com o que está escrito nas páginas capturadas; os pontos inventados saíram; cada ponto tem a precisão da fonte. `PRE_REGISTRO.md` §9 |
| 05/out | Tocantins em 2022 estava fora da classe de referência "porque as fontes divergem" | leitura das páginas capturadas: CNN Brasil, Gazeta do Povo e Revista Oeste colocam Tocantins ao lado de Bolsonaro. A "divergência" vinha de um trecho de resultado de busca | Tocantins entra; a classe de 2022 volta a ter 15 UFs. `PRE_REGISTRO.md` §9 |
| 05/out | A coleta com três processos juntos passou do limite do servidor (HTTP 429) e deixou itens com `status 0` | os testes de carga e o log | um coletor só, com limitador adaptativo (cai a 60% ao receber 429, sobe 8% a cada 150 sucessos) e teto de 90 por segundo; item com falha não conta como salvo e é refeito. Nada foi perdido |
| 05/out | A medida de concentração "metade da diferença em menos de 1% das seções" acusava concentração onde ela não existe quando a diferença líquida é pequena perto do fluxo bruto | a medida literal em 2022 (MT, RJ) | acrescentadas a razão líquido/bruto e o índice do 1% de seções; a medida literal só decide quando `estavel`. `PRE_REGISTRO.md` §9 |
| 05/out | O teste de fuso (T2.4) não decidia no Acre, onde as duas hipóteses dão zero violação | primeiro teste em AC e AL | acrescentado o desempate pela latência mínima. `PRE_REGISTRO.md` §9 |
| 05/out | O plano dizia que a curva histórica sairia de 2014, 2018 e 2022 | abertura dos arquivos: 2018 não tem `DT_BU_RECEBIDO`, 2014 não tem cabeçalho nem hora | só 2022 tem a curva por ordem de chegada. `PRE_REGISTRO.md` §9 |
