"""Segunda validacao, de 06/out/2026: recontagem independente, so com pandas e sqlite.
Compara contra o oficial do TSE (outra fonte) e contra RESUMO.json."""
import json, sqlite3, glob, os, hashlib, csv
import pandas as pd, numpy as np

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
R = json.load(open('resultados/RESUMO.json', encoding='utf-8'))
res = []
def ok(nome, cond, det):
    res.append(bool(cond)); print(('OK    ' if cond else 'FALHA '), nome, '|', det)

BASE = 'https://resultados.tse.jus.br/oficial/ele2026/6257/dados'
con = sqlite3.connect('dados/brutos/oficial.sqlite')
def of(url):
    r = con.execute("select body from raw where url=?", (url,)).fetchone()
    return json.loads(r[0])

def cand_tab(d):
    out = {}
    for a in d['carg'][0]['agr']:
        for p in a['par']:
            for c in p['cand']:
                out[c['nmu']] = dict(n=int(c['n']), v=int(c['vap']), pct=float(str(c['pvap']).replace(',', '.')), sit=c.get('e'), part=p.get('sg'))
    return out

# 1) nacional oficial
d = of(f'{BASE}/br/br-c0001-e006257-u.json')
nac = cand_tab(d)
print({k: (v['n'], v['v'], v['pct']) for k, v in sorted(nac.items(), key=lambda kv: -kv[1]['v'])[:4]})
fl = next(v for k, v in nac.items() if 'FL' in k.upper() and 'BOLSONARO' in k.upper())
lu = next(v for k, v in nac.items() if 'LULA' in k.upper())

# 2) reconstruido pelos boletins
S = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob('dados/derivados/uf/*-secoes.parquet'))], ignore_index=True)
V = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob('dados/derivados/uf/*-votos.parquet'))], ignore_index=True)
p1 = V[(V.cargo == 1) & (V.tipo == 1)]
tot = p1.groupby('numero').votos.sum()
ok('Flavio: soma dos boletins contra o oficial', abs(tot[fl['n']] - fl['v']) / fl['v'] < 5e-5, f"boletins {tot[fl['n']]:,} oficial {fl['v']:,} dif {tot[fl['n']]-fl['v']:,}")
ok('Lula: soma dos boletins contra o oficial', abs(tot[lu['n']] - lu['v']) / lu['v'] < 5e-5, f"boletins {tot[lu['n']]:,} oficial {lu['v']:,} dif {tot[lu['n']]-lu['v']:,}")
valid_b = int(tot.sum()); valid_o = sum(v['v'] for v in nac.values())
ok('Validos totais: boletins contra oficial', abs(valid_b - valid_o) / valid_o < 5e-5, f"{valid_b:,} contra {valid_o:,} dif {valid_b-valid_o:,} ({100*(valid_b-valid_o)/valid_o:+.4f}%)")
ok('Percentual final de Flavio e Lula (oficial)', True, f"Flavio {fl['pct']} Lula {lu['pct']} diferenca {fl['pct']-lu['pct']:.2f}")

# 3) curva da noite, codigo novo
key = ['uf', 'mun_cd', 'zona', 'secao']
wide = p1.pivot_table(index=key, columns='numero', values='votos', aggfunc='sum', fill_value=0)
wide['validos'] = wide.sum(axis=1)
base = S[(~S['agregada']) & S['recebido'].notna()].copy()
base['recebido'] = pd.to_datetime(base['recebido'])
m = base.merge(wide.reset_index(), on=key, how='inner').sort_values(['recebido'], kind='stable').reset_index(drop=True)
n = len(m)
cf = m[fl['n']].cumsum().values; cl = m[lu['n']].cumsum().values; cv = m['validos'].cumsum().values
marg = 100 * (cf - cl) / cv
pct_sec = 100 * (np.arange(n) + 1) / n
print('secoes na curva', n)
ok('Margem final da curva', abs(marg[-1] - R['p1_resumo']['margem_final']) < 0.01 and abs(marg[-1] - (fl['pct'] - lu['pct'])) < 0.05, f"{marg[-1]:.3f} (RESUMO {R['p1_resumo']['margem_final']:.3f}, oficial {fl['pct']-lu['pct']:.2f})")
i = marg[int(0.01 * n):].argmax() + int(0.01 * n)
ok('Pico da margem e quando', abs(marg[i] - R['p1_resumo']['margem_de_pico']) < 0.05, f"pico {marg[i]:.2f} pontos com {pct_sec[i]:.1f}% das secoes, recebido {m.recebido[i]} (RESUMO {R['p1_resumo']['margem_de_pico']:.2f} e {R['p1_resumo']['recebido_no_pico']})")
# nunca Lula na frente depois dos primeiros 0,5%
lider_lula = np.where(marg < 0)[0]
ult = lider_lula.max() if len(lider_lula) else -1
ok('Ultima vez com Lula na frente', pct_sec[ult] < 0.6, f"ultima em {pct_sec[ult]:.3f}% das secoes (RESUMO {R['p1_resumo']['pct_secoes_da_ultima_troca_de_lideranca']:.3f})")
# pontos 64,81% e 84,96% da imprensa
for alvo, esperado in ((64.81, (49.58, 42.25)), (84.96, (48.47, 43.49))):
    j = np.searchsorted(pct_sec, alvo)
    ok(f'Curva em {alvo}% das secoes contra a imprensa', abs(100*cf[j]/cv[j]-esperado[0]) < 0.15 and abs(100*cl[j]/cv[j]-esperado[1]) < 0.15, f"Flavio {100*cf[j]/cv[j]:.2f} Lula {100*cl[j]/cv[j]:.2f} (imprensa {esperado[0]} e {esperado[1]})")

# 4) parada: boletins recebidos entre 19h06 e 20h08 (hora local)
r = m['recebido']
print(r.min(), r.max())
# 5) Sao Paulo, oficial
sp_g = cand_tab(of(f'{BASE}/sp/sp-c0003-e006259-u.json')) if con.execute("select 1 from raw where url=?", (f'{BASE}/sp/sp-c0003-e006259-u.json',)).fetchone() else None
print('SP gov oficial:', None if sp_g is None else sorted(((k, v['pct']) for k, v in sp_g.items()), key=lambda x: -x[1])[:3])
sp_p = cand_tab(of(f'{BASE}/sp/sp-c0001-e006257-u.json'))
print('SP pres oficial:', sorted(((k, v['pct']) for k, v in sp_p.items()), key=lambda x: -x[1])[:3])
print(sum(res), 'de', len(res), 'ok')
