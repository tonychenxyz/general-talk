"""Simulate the 'practice' toy game with its real engine and write data.json for build.py.

Engine + config live in ceobench_runs/progress-article/probe/tanks/practice_v1/ (outside this repo), so the numbers
the slide needs are frozen here. Example strategies are played noise-free (expected path); the 50-seed mean with the
real ±20% noise is stored too, for the speaker notes. On the slide the abstract skills get illustrative names:
C (bar 2, x1) Cooking, E (8, x2) Running, A (18, x4) Guitar, D (28, x7) Spanish, B (34, x20) Coding.
"""
import json, pathlib, statistics, sys

GAME = pathlib.Path('/scratch/gpfs/ZHUANGL/hc5019/ceobench_runs/progress-article/probe/tanks/practice_v1')
sys.path.insert(0, str(GAME))
from config import SPEC, LABELS, KW, containers   # noqa: E402
from engine import Game                             # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent


def run(alloc, noise=0.0, seed=0):
    g = Game(containers(), seed=seed, **{**KW, 'noise': noise})
    weeks = []
    while not g.done():
        before = {i: c['level'] for i, c in g.c.items()}
        pay = g.play(alloc)
        weeks.append({'grown': {i: round(before[i] + (g.c[i]['level'] / (1 - g.leak) - before[i]), 3) for i in g.c},
                      'level': {i: round(c['level'], 3) for i, c in g.c.items()},
                      'pay': {i: round(v, 3) for i, v in pay.items()}, 'total': round(g.score, 3)})
    return weeks


def mean_score(alloc, n=50):
    out = []
    for s in range(n):
        g = Game(containers(), seed=s, **KW)
        while not g.done(): g.play(alloc)
        out.append(g.score)
    return round(statistics.mean(out), 1)


# 'week': the one example week on the slide (4/3/2/1/0 hours), 'easy'/'hard': all 10 h on the x1 / x20 skill
strats = {'week': dict(zip(LABELS, (4, 3, 2, 1, 0))), 'spread': {L: 2 for L in LABELS},
          'easy': {LABELS[0]: 10}, 'hard': {LABELS[-1]: 10}}
D = {'spec': [{'id': L, 'bar': b, 'rate': r} for L, (b, r) in zip(LABELS, SPEC)], 'kw': KW,
     'grow': {h: round(KW['g'] * (1 - __import__('math').exp(-h / KW['k'])), 3) for h in range(11)},
     'runs': {k: run(a) for k, a in strats.items()},
     'mean_score_noisy': {k: mean_score(a) for k, a in strats.items()}}
(HERE / 'data.json').write_text(json.dumps(D, indent=1))
for k in strats:
    w = D['runs'][k]
    print(k, 'total', w[-1]['total'], 'first paying week', next((i + 1 for i, x in enumerate(w) if x['total'] > 0), None),
          'noisy mean', D['mean_score_noisy'][k])
print('grow', D['grow'])
