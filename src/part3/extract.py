"""Collect the numbers behind the part-3 slides ("What improved?") into data.json.

Sources are local analysis outputs on della (not in this repo); data.json is committed so build.py runs anywhere.
  RUNS  progress-article: metrics.json, series.json, parsed lever calls, DB extractions (db/out, db/out2), fig12.py
  VIEW  trajectory viewer data (per-run daily actions + rationales, customers by group)
  WEB   ceo-bench-webpage assets/runs.json (best-run cash curves, same as the leaderboard slide)
"""
import collections, json, os, re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get('CEO_ROOT', '/scratch/gpfs/ZHUANGL/hc5019'))
RUNS = ROOT / 'ceobench_runs/progress-article'
VIEW = ROOT / 'ceobench-website-details/trajectory-viewer/data'
WEB = ROOT / 'ceobench-website-preview/assets'

sys.path.insert(0, str(RUNS / 'process/fig12'))
import fig12 as F  # forecast error exactly as in the paper's Fig. 12b (mean abs % error of 4-week forecasts, weeks 1-4)

M = {r['run_id']: r for r in json.load(open(RUNS / 'generations/metrics.json'))['runs']}
S = {r['run_id']: r for r in json.load(open(RUNS / 'generations/series.json'))['runs']}
P = json.load(open(RUNS / 'process/latency/cache/parsed.json'))
view = lambda rid: json.load(open(VIEW / f'runs/{rid}.json'))

BEST = {'Claude Opus 4.7': 'c2b8b65e', 'Claude Fable 5': '2c0aeba9', 'GPT-5.6 Sol': 'd1834c32',
        'GPT-6 Sol': 'native-80fbf4bdb641', 'Claude Fable 5.1': 'native-00af2b447bfc'}
DBFILE = {'native-80fbf4bdb641': 'sol-hc5019-a', 'native-00af2b447bfc': 'fable-hc5019-cs'}
out = {'best_runs': BEST}

# ---- 1. forecast error vs best-run cash, models on the June leaderboard ----
JUNE = ['GPT-5.5', 'Claude Opus 4.7', 'Claude Sonnet 4.6', 'Claude Haiku 4.5', 'Kimi K2.6', 'GLM-5.1', 'DeepSeek V4 Pro',
        'Gemini 3 Flash', 'Grok 4.20', 'Claude Opus 4.8', 'Claude Fable 5']
fc = {}
for m in JUNE:
    rids = [r for r, x in M.items() if x['model_display'] == m]
    errs = {r: F.fc_err(r) for r in rids}
    v = [e for e in errs.values() if e is not None]
    fc[m] = dict(best_cash_db=max(M[r]['final_cash'] for r in rids), err=sum(v) / len(v), per_run=errs,
                 bankrupt_runs=sum(1 for r in rids if M[r]['bankrupt']), n_runs=len(rids))
# displayed cash uses the leaderboard's numbers (website runs.json) so every slide agrees
WEBNAME = {'GLM-5.1': 'GLM 5.1'}
web = {r['pretty']: r for r in json.load(open(WEB / 'runs.json'))}
for m in fc: fc[m]['best_cash'] = web[WEBNAME.get(m, m)]['final_cash']
out['forecast'] = fc

# ---- 2. weekly rationales + activity, Opus 4.7 vs Fable 5 best runs ----
act = {}
for m in ['Claude Opus 4.7', 'Claude Fable 5']:
    rid = BEST[m]; d = view(rid); s = S[rid]
    act[m] = dict(rationale={k: v.get('rationale') or '' for k, v in d['days'].items()},
                  tool_calls=sum(x or 0 for x in s['tool_calls']),
                  weeks_config_changed=sum(1 for x in s['core_config_changed'] if x),
                  weeks_total=sum(1 for x in s['core_config_changed'] if x is not None),
                  mutation_call_sites=s['cum_mutation_call_sites'][-1])
    # SDK functions called from the agent's shell commands (nm.<module>.<fn>(...)); raw SQL queries excluded
    c = collections.Counter()
    for day in d['days'].values():
        for a in day['actions']:
            if a['tool'] == 'bash':
                c.update(re.findall(r'\bnm\.(?:\w+\.)?(\w+)\s*\(', a['arguments'].get('command', '')))
    c.pop('query', None)
    act[m]['sdk_calls'] = dict(c.most_common())
    # number of weekly turns (days 0, 7, ..., 504) in which each SDK function was called at least once
    wk = collections.Counter()
    for day in d['days'].values():
        used = set()
        for a in day['actions']:
            if a['tool'] == 'bash':
                used.update(re.findall(r'\bnm\.(?:\w+\.)?(\w+)\s*\(', a['arguments'].get('command', '')))
        used.discard('query'); wk.update(used)
    act[m]['sdk_weeks'] = dict(wk.most_common())
out['activity'] = act

# ---- 3. best-run cash curves (same source as the leaderboard slide) ----
runs = {r['pretty']: r for r in json.load(open(WEB / 'runs.json'))}
out['curves'] = {m: dict(final=runs[m]['final_cash'], points=runs[m]['points'])
                 for m in ['Claude Fable 5', 'Claude Fable 5.1', 'GPT-5.6 Sol', 'GPT-6 Sol']}
out['rule_based_final'] = float(open(WEB / 'rule_based_baseline_day_vs_cash.csv').read().split()[-1].split(',')[1])

# ---- 4. paying customers by group category over time; revenue by category (DB runs only) ----
def cat(g):
    if g in ('S1', 'S2', 'S3'): return g
    if g.startswith('D_S'): return 'D'
    return 'E'
groups, revenue, groups_by_id = {}, {}, {}
for m in ['GPT-5.6 Sol', 'GPT-6 Sol', 'Claude Fable 5', 'Claude Fable 5.1']:
    rid = BEST[m]; d = view(rid)
    by = collections.defaultdict(collections.Counter)
    for x in d['customer_series_by_group']:
        by[x['day']][cat(x['group_id'])] += x['count']
    if rid in DBFILE:   # enterprise seats paying in the trailing 30 days (DB); dashboard seat counts stop at day 315 in Fable 5.1
        seats = json.load(open(RUNS / f'db/out2/{DBFILE[rid]}.json'))['paying_base_30d']['ent_seats_billed']
        ent = lambda day: seats[min(day, len(seats) - 1)]
        pay = json.load(open(RUNS / f'db/out/{DBFILE[rid]}.json'))['payments_by_group']
        rv = collections.Counter()
        for g, v in pay.items(): rv[cat(g)] += v
        revenue[m] = dict(rv)
    else:
        ent = lambda day, w=S[rid]['ent_seats']: (w[min(day // 7, len(w) - 1)] or 0)
    groups[m] = [dict(day=day, **{k: by[day].get(k, 0) for k in ('S1', 'S2', 'S3', 'D')}, E=ent(day))
                 for day in range(0, 505, 7) if day in by]
    # same, but every individual group on its own (S1..S3, D_S01..D_S10); enterprise seats only exist as one total
    byg = collections.defaultdict(collections.Counter)
    for x in d['customer_series_by_group']:
        byg[x['day']][x['group_id']] += x['count']
    gids = sorted({x['group_id'] for x in d['customer_series_by_group']})
    groups_by_id[m] = [dict(day=day, **{g: byg[day].get(g, 0) for g in gids}, E=ent(day))
                       for day in range(0, 505, 7) if day in byg]
out['groups'], out['revenue'], out['groups_by_id'] = groups, revenue, groups_by_id

# ---- 5. targeted development (quality bought for a specific group), daily budget by category ----
def dev_series(rid):
    if rid in DBFILE:   # DB override history is exact for the native runs
        calls = [dict(day=d_, state=json.loads(js)['targeted_spend'])
                 for d_, tool, _, js in json.load(open(RUNS / f'db/out/{DBFILE[rid]}.json'))['override_settings']
                 if tool == 'set_targeted_dev_spend']
    else:               # July runs have no DB: budgets parsed from the agent's commands
        calls = [c for c in P[rid]['lever_calls'] if c['tool'] == 'set_targeted_dev_spend']
    calls.sort(key=lambda c: c['day'])
    end = M[rid]['survival_days']; daily = [collections.Counter() for _ in range(505)]
    for i, c in enumerate(calls):
        b = min(calls[i + 1]['day'] if i + 1 < len(calls) else end, end)
        for day in range(c['day'], b):
            daily[day] = collections.Counter()
            for g, v in c['state'].items():
                if isinstance(v, (int, float)): daily[day][cat(g)] += v
    return daily
dev = {}
for m in ['GPT-5.6 Sol', 'GPT-6 Sol', 'Claude Fable 5', 'Claude Fable 5.1']:
    daily = dev_series(BEST[m]); cum = collections.Counter(); pts = []
    for day in range(505):
        if day % 7 == 0: pts.append(dict(day=day, **{k: cum[k] for k in ('S1', 'S2', 'S3', 'D', 'E')}))
        cum.update(daily[day])
    dev[m] = pts
out['targeted_dev_cum'] = dev

# ---- 6. weekly notes (the message each agent writes when ending a week), for quotes ----
def native_notes(rid):
    # the viewer's copy of GPT/Codex notes lost "$..." amounts to shell expansion; take them from the raw command instead
    notes = {}
    for line in open(VIEW / f'transcripts/{rid}.jsonl'):
        o = json.loads(line); cmd = (o.get('arguments') or {}).get('cmd', '')
        mm = re.search(r'next-week --request-id w(\d+) "(.*?)" [-\d. ]+\'$', cmd, re.S)
        if mm: notes[str(int(mm.group(1)))] = mm.group(2)
    return notes
out['notes'] = {m: (native_notes(rid) if m == 'GPT-6 Sol' else {k: v.get('rationale') or '' for k, v in view(rid)['days'].items()})
                for m, rid in BEST.items()}

json.dump(out, open(HERE / 'data.json', 'w'), indent=1, default=float)
for m, v in fc.items(): print(f'{m:18s} cash {v["best_cash"]:>14,.0f}  4wk err {v["err"]:.0%}')
for m, v in act.items(): print(m, {k: v[k] for k in ('tool_calls', 'weeks_config_changed', 'mutation_call_sites')})
for m, v in dev.items(): print(m, 'targeted dev by d100', {k: round(v[100 // 7 + 1][k] / 1e6, 2) for k in 'S1 S2 S3 D E'.split()}, 'total', {k: round(v[-1][k] / 1e6, 2) for k in 'S1 S2 S3 D E'.split()})
for m, v in revenue.items(): print(m, {k: round(x / 1e6, 1) for k, x in v.items()})
