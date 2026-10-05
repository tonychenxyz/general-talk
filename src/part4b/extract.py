"""Extract the practice-game allocations and scores used by build.py into data.json.

Source: ceobench_runs/progress-article/probe/tanks/practice_v1/round_records_v1
  visualization/allocations.json  (week-by-week hours per skill, mean + 5 trials per model)
  results/<model>/<i>.json         (final score per trial)
"""
import json, pathlib, statistics

HERE = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path('/scratch/gpfs/ZHUANGL/hc5019/ceobench_runs/progress-article/probe/tanks/practice_v1/round_records_v1')
A = json.load(open(SRC / 'visualization' / 'allocations.json'))
out = {'skills': A['skills'], 'models': {}}
for m in A['models']:
    runs = [json.load(open(SRC / 'results' / m['model'] / f'{i}.json'))['metrics'] for i in range(5)]
    for i, r in enumerate(runs):   # allocations.json must agree with the raw trial histories
        assert [h for h in r['history']] == [{k: wk[k]['runs'][i] for k in wk} for wk in m['rounds']]
    out['models'][m['name']] = {
        'weeks': [{k: wk[k]['mean'] for k in wk} for wk in m['rounds']],
        'scores': [r['score'] for r in runs],
        'score_mean': statistics.mean(r['score'] for r in runs),
    }
json.dump(out, open(HERE / 'data.json', 'w'), indent=1)
for n, v in out['models'].items():
    w = v['weeks']
    print(f"{n:12s} wk1 B {w[0]['B']:.1f}  share B {sum(x['B'] for x in w) / 200:.1%}  score {v['score_mean']:.1f} {v['scores']}")
    print('   B by week', [round(x['B'], 1) for x in w])
