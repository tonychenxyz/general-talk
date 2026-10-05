"""Part 6c data: Focalboard 056 trajectories (paper Fig. 6) + time-budget pass rates (paper Fig. 9).

Sources (sweeperbench_public):
  sweeper-bench-plotting/assets/focalboard-056/build_stages.py  - generator of the paper figure; its card text was
      verified there against the raw trajectories. We read its literals (rows/names/outcomes/logos) with ast.
  sweeper-bench-plotting/assets/focalboard-056/logo-*.svg        - provider logos used in the figure.
  sweeper-bench-plotting/analysis/time_budget/data/{pass-rates,supplied-pass-rates}.csv - plotted values.
  overleaf/figures/fig_focalboard_056_trajectories.pdf           - every card text is re-checked against the PDF text.
"""
import ast, csv, json, pathlib, re
import fitz

SB = pathlib.Path('/scratch/gpfs/ZHUANGL/hc5019/sweeperbench_public')
PL = SB / 'sweeper-bench-plotting'
HERE = pathlib.Path(__file__).resolve().parent

tree = ast.parse((PL / 'assets/focalboard-056/build_stages.py').read_text())
lit = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
            and node.targets[0].id in ('rows', 'names', 'outcomes', 'logos', 'legend'):
        lit[node.targets[0].id] = ast.literal_eval(node.value)

pdf = ''.join(fitz.open(SB / 'overleaf/figures/fig_focalboard_056_trajectories.pdf')[0].get_text().split())
squash = lambda s: ''.join(s.split())
rows = []
for key, cards in lit['rows'].items():
    name = lit['names'][key]
    tail, tone = lit['outcomes'][key]
    headline = name + tail[len(key):]                      # e.g. "Claude Fable 5.1 treated the empty sidebar ..."
    assert squash(headline) in pdf, headline
    out = []
    for summary, event, quote, is_code, kind in cards:
        assert squash(summary) in pdf, summary
        assert squash(quote) in pdf, quote
        out.append(dict(summary=summary, quote=quote, code=is_code, kind=kind, event=event))
    rows.append(dict(key=key, name=name, headline=headline, fixed=tone == 'pass', logo=lit['logos'][key][0],
                     ring=lit['logos'][key][1], cards=out))
logos = {k: (PL / f'assets/focalboard-056/logo-{k}.svg').read_text().strip() for k in ('claude', 'zai', 'openai')}

tb = PL / 'analysis/time_budget/data'
series = {}
for f in ('pass-rates.csv', 'supplied-pass-rates.csv'):
    for r in csv.DictReader(open(tb / f)):
        series.setdefault(r['model'], {})[int(r['minutes'])] = float(r['pass_rate'])
time_budget = [dict(model=label, color=color, marker=marker, rates=[series[m][t] for t in (20, 40, 60, 80)])
               for m, label, color, marker in [('gpt-5.6-luna', 'GPT-5.6 Luna', '#000000', 'o'),
                                               ('gpt-5.6-terra', 'GPT-5.6 Terra', '#888888', 's'),
                                               ('glm-5.3', 'GLM 5.3', '#BBBBBB', '^')]]
json.dump(dict(trajectories=rows, legend=lit['legend'], logos=logos,
               time_budget=dict(minutes=[20, 40, 60, 80], tasks=40, series=time_budget)),
          open(HERE / 'data.json', 'w'), indent=1, ensure_ascii=False)
print('ok:', [r['name'] for r in rows], [(s['model'], s['rates']) for s in time_budget])
