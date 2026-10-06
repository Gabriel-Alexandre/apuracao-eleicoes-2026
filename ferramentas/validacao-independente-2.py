import json, sqlite3, os, csv, hashlib, glob, re
import pandas as pd
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
con = sqlite3.connect('dados/brutos/oficial.sqlite')
def of(url):
    r = con.execute("select body from raw where url=?", (url,)).fetchone()
    return json.loads(r[0]) if r else None
res = []
def ok(nome, cond, det):
    res.append(bool(cond)); print(('OK    ' if cond else 'FALHA '), nome, '|', det)

def cands(d):
    out = []
    for a in d['carg'][0]['agr']:
        for p in a['par']:
            for c in p['cand']:
                out.append(dict(nome=c['nmu'], n=int(c['n']), v=int(c['vap']), pct=float(str(c['pvap']).replace(',', '.')), e=c.get('e'), sg=p.get('sg')))
    return out

# Sao Paulo
g = of('https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sp/sp-c0003-e006259-u.json')
p = of('https://resultados.tse.jus.br/oficial/ele2026/6257/dados/sp/sp-c0001-e006257-u.json')
cg = sorted(cands(g), key=lambda c: -c['v']); cp = sorted(cands(p), key=lambda c: -c['v'])
tar, hadd = cg[0], cg[1]; fla = cp[0]; lula = cp[1]
print(tar, hadd, fla, lula, sep='\n')
ok('SP: Tarcisio 62,65 e Flavio 51,93', abs(tar['pct'] - 62.65) < 0.006 and abs(fla['pct'] - 51.93) < 0.006, f"{tar['pct']} e {fla['pct']}")
ok("SP: diferenca de votos oficial 1.569.851", tar["v"] - fla["v"] == 1569851, f"{tar['v']-fla['v']:,}")
ok('SP: Haddad 36,42 e Lula 38,20', abs(hadd['pct'] - 36.42) < 0.006 and abs(lula['pct'] - 38.20) < 0.006, f"{hadd['pct']} e {lula['pct']}")
# base de votos: comparecimento no oficial
for nome, d in (('gov', g), ('pres', p)):
    print(nome, {k: d[k] for k in d if k in ('abr', 'ts', 'v', 'vv', 'vb', 'vn', 'c', 'a', 'pvv', 'pvb', 'pvn', 'pc')} if isinstance(d, dict) else '')
# Senado: eleitos do PL e quem liderou
sen = {}
for u, in con.execute("select url from raw where url like '%/6259/dados/%-c0005-%' and url not like '%/br/%'"):
    uf = u.split('/dados/')[1].split('/')[0]
    if len(uf) != 2 or re.search(r'/' + uf + r'\d', u):
        continue
    d = of(u)
    if d: sen[uf] = cands(d)
print(len(sen), 'UFs com senado oficial')
eleitos_pl = [(uf, c['nome']) for uf, cs in sen.items() for c in cs if c['sg'] == 'PL' and str(c['e']).lower().startswith('s')]
print(len(eleitos_pl), eleitos_pl)
lider = {}
for uf in sen:
    pu = of(f'https://resultados.tse.jus.br/oficial/ele2026/6257/dados/{uf}/{uf}-c0001-e006257-u.json')
    cs = sorted(cands(pu), key=lambda c: -c['v'])
    lider[uf] = (cs[0]['nome'], cs[0]['pct'] - cs[1]['pct'])
ok('PL elegeu 19 senadores', len(eleitos_pl) == 19, str(len(eleitos_pl)))
ok('Todos os senadores do PL em UF onde Flavio liderou', all('FLAVIO' in lider[uf][0] for uf, _ in eleitos_pl), str({uf: round(lider[uf][1], 1) for uf, _ in eleitos_pl}))

# Capturas: hash e termos
rows = list(csv.DictReader(open('dados/CAPTURAS.csv', encoding='utf-8')))
bad = 0
for r in rows:
    f = os.path.join('dados/brutos/fontes', r['sha256'][:16] + '.bin')
    if not os.path.exists(f):
        bad += 1; continue
    if hashlib.sha256(open(f, 'rb').read()).hexdigest() != r['sha256']:
        bad += 1
ok('Capturas: hash de cada pagina confere', bad == 0, f"{len(rows)} paginas, {bad} com problema")
def texto(substr):
    for r in rows:
        if substr in r['url']:
            return open(os.path.join('dados/brutos/fontes', r['sha256'][:16] + '.bin'), 'rb').read().decode('utf-8', 'ignore')
    return ''
print(sum(res), 'de', len(res))
