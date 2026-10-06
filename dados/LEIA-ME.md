# dados/

| Pasta ou arquivo | No git? | O que guarda |
|---|---|---|
| `brutos/` | não | tudo que veio do TSE e da imprensa, exatamente como chegou |
| `MANIFESTO.json` | sim | para cada arquivo bruto: URL, hora da coleta (UTC), tamanho e sha256 |
| `derivados/` | sim, se leve | votos e hora de recebimento por seção, em formato tabular, gerados por script a partir de `brutos/` |
| `sondas/` | não | saída de `ferramentas/sondar-fontes.py --salvar` |

Nada aqui é editado à mão. Arquivo derivado se regenera pelo script que o produziu.
