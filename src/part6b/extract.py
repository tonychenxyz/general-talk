"""Extract SWEeper-Bench numbers for part 6b into data.json (run once; build.py only reads data.json).

Sources (sweeper-bench-plotting repo, the data behind the paper's figures):
  analysis/cost_pass/data/model_summary.csv        -> Figure 2 (pass rate vs mean cost, 15 agents)
  analysis/identification/data/stage-rates.csv     -> Figure 7a (cumulative stages, 14 agents)
  assets/provider-logos/*.svg                      -> marker logos
"""
import csv, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
PLOT = pathlib.Path('/scratch/gpfs/ZHUANGL/hc5019/sweeperbench_public/sweeper-bench-plotting')

# display name + logo, as in analysis/cost_pass/build_figure.py (LABELS / LOGO_COLORS)
LABELS = {
    'gpt-6-astra': ('GPT-6 Astra', 'openai'), 'gpt-5.6-sol': ('GPT-5.6 Sol', 'openai'),
    'gpt-5.6-terra': ('GPT-5.6 Terra', 'openai'), 'gpt-5.6-luna': ('GPT-5.6 Luna', 'openai'),
    'claude-fable-5-1': ('Claude Fable 5.1', 'claude-color'), 'claude-opus-5': ('Claude Opus 5', 'claude-color'),
    'glm-5.3': ('GLM 5.3', 'zai'), 'glm-5.3-flash': ('GLM 5.3 Flash', 'zai'),
    'qwen3.8-flash': ('Qwen 3.8 Flash', 'qwen-color'), 'qwen3.8-max': ('Qwen 3.8 Max', 'qwen-color'),
    'kimi-k3': ('Kimi K3', 'moonshot'), 'deepseek-v4.1-flash': ('DeepSeek V4.1 Flash', 'deepseek-color'),
    'deepseek-v4-pro': ('DeepSeek V4 Pro', 'deepseek-color'), 'grok-4.6': ('Grok 4.6', 'grok'),
    'muse-spark-1.3': ('Muse Spark 1.3', 'meta-color'),
}
LOGO_COLORS = {'claude-color': '#D97757', 'grok': '#000000', 'openai': '#000000', 'zai': '#000000',
               'moonshot': '#000000', 'qwen-color': '#6336E7', 'deepseek-color': '#4D6BFE', 'meta-color': '#0867DF'}

board = []
for r in csv.DictReader(open(PLOT / 'analysis/cost_pass/data/model_summary.csv')):
    name, logo = LABELS[r['model']]
    board.append(dict(model=r['model'], name=name, effort=r['reasoning_level'].removesuffix('-fast'),
                      rank=int(r['rank']), pass_pct=float(r['both_pass_pct']), cost=float(r['mean_cost_usd']),
                      cost_basis=r['cost_basis'], logo=logo))

STAGES = ['feature', 'behavior', 'cause', 'core_pass', 'preservation_pass']
stages = {}
for r in csv.DictReader(open(PLOT / 'analysis/identification/data/stage-rates.csv')):
    stages[r['model']] = dict(n=int(r['completed_tasks']), rates=[float(r[s + '_rate']) for s in STAGES])
avg = [sum(v['rates'][i] for v in stages.values()) / len(stages) for i in range(len(STAGES))]
ref = json.load(open(PLOT / 'analysis/identification/figures/identification_half_page.json'))['average_rates']
assert all(abs(a - b) < 1e-9 for a, b in zip(avg, ref)), (avg, ref)

logos = {l: (PLOT / 'assets/provider-logos' / f'{l}.svg').read_text().strip() for l in LOGO_COLORS}
json.dump(dict(leaderboard=board, logo_colors=LOGO_COLORS, logos=logos,
               stages=dict(names=STAGES, models=stages, average=avg)),
          open(HERE / 'data.json', 'w'), indent=1)
print('avg', [round(a, 1) for a in avg])
