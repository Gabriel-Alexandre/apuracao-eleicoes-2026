# Revisão adversarial

Segunda passada da **mesma IA** que fez a análise, com a instrução de derrubar cada conclusão do relatório. Não é revisão independente nem humana. Cada linha diz o que se tentou derrubar, como, e o que saiu.

Gerada por `ferramentas/revisao-adversarial.py` a partir dos mesmos arquivos do relatório.

| Tentativa de derrubar | Como | Resultado | Passou |
|---|---|---|---|
| Seção contada duas vezes | chave (UF, município, zona, seção) duplicada na tabela de Presidente | 0 duplicadas em 499191 seções | sim |
| Erro de unidade (seção contra voto) | comparecimento do boletim contra válidos + brancos + nulos, seção a seção | 0 seções com diferença em 499161 | sim |
| O teste dos pontos passaria com qualquer ordem? | margem publicada de cada ponto contra a faixa de 5% a 95% de 1.000 ordens aleatórias de chegada | 14 de 14 pontos ficam fora da faixa aleatória; só a ordem real de recebimento os reproduz | sim |
| A janela de ±0,5 ponto no percentual de seções facilita o encaixe | erro no percentual de seções exato, sem janela | 12 de 14 pontos dentro de 0,1 no percentual exato; erro máximo 0.50; mediano 0.035 | sim |
| Decomposição por regiao fecha? | soma das contribuições contra a mudança da margem acumulada; composição mais ordem contra diferença do lote | soma -5.505194 contra mudança -5.505194; composição + ordem = -15.091385 contra -15.091385 | sim |
| Decomposição por uf_capital fecha? | soma das contribuições contra a mudança da margem acumulada; composição mais ordem contra diferença do lote | soma -5.505194 contra mudança -5.505194; composição + ordem = -15.091385 contra -15.091385 | sim |
| Decomposição por porte_municipio fecha? | soma das contribuições contra a mudança da margem acumulada; composição mais ordem contra diferença do lote | soma -5.505194 contra mudança -5.505194; composição + ordem = -15.091385 contra -15.091385 | sim |
| Falta ou sobra de seções | seções próprias da configuração contra o total oficial | 499248 contra 499248 | sim |
| Total de votos | votos válidos, de Flávio e de Lula reconstruídos contra o arquivo oficial | -3935 válidos, -1757 Flávio, -1746 Lula; só as 15 seções sem arquivo explicam | sim |
| Casamento errado de nomes no Senado | cada candidato casado precisa dividir ao menos uma palavra do nome com o da lista | 0 suspeitos em 46 | sim |
| Mesmo candidato casado duas vezes | UF e número repetidos nos casados | 0 | sim |
| Inferência ecológica mal especificada | total previsto de Flávio e de Lula pela estimativa contra o total real em SP | p_bolsonaro +0.4%; p_lula -0.2% | sim |
| Inferência ecológica de 2022 mal especificada | idem, 2022 | p_bolsonaro +0.1%; p_lula +0.1% | sim |
| A diferença de São Paulo vem de troca de voto ou da base? | percentual dos válidos contra percentual de quem compareceu, para os dois cargos | 45% da diferença em pontos vem de a base do governador (válidos = 87.5% dos que compareceram) ser menor que a do presidente (94.1%) | sim |
| Frase que só vale para um lado | os testes rodam para os dois lados? | P3 e P5 usam Flávio e Lula e governadores dos dois lados; P6 tem o espelho do PT; P8 tem o teste espelho de Lula e o placebo de 2022 | sim |
| Palavra que a doutrina do projeto proíbe | busca no relatório e no resumo | nenhuma | sim |
| Travessão em texto público | busca por — e – no relatório | 0 ocorrências | sim |
| Marcador sem valor no relatório | busca por [[FALTA]] | 0 | sim |
| O fuso de Mato Grosso muda a conclusão | curva com MT em horário de Brasília contra MT deslocado em 1 hora | margem muda até 0.87 ponto; pontos que encaixam: 13 contra 10 | sim |
| O vazio de recebimento é artefato de uma região ou UF | UFs com algum boletim dentro do vazio, e se o vazio some tirando uma UF | 0 boletins dentro; nenhuma UF isolada o preenche | sim |

**20 de 20 checagens passaram.**

## O que a revisão não cobre

- Não houve revisão humana.
- A verificação da assinatura digital dos boletins não foi possível.
- A classificação de apoio político vem de reportagens e tem uma divergência conhecida de um governador entre duas contagens (CNN Brasil e g1).
- Os pontos da tela vêm de imprensa, e quase todos têm uma fonte só.
- A inferência ecológica não diz como cada pessoa votou.
