"""Part 3 · "What improved?" slides, built from data.json (see extract.py) and spliced into ../../index.html.

Everything lives between `part3:begin` / `part3:end` markers (one CSS block, one run of <section>s placed
right after the Leaderboard slide), so rerunning only replaces this part and leaves other editors' slides alone.
All classes are prefixed w- to avoid clashing with parts 1 and 2.
"""
import html, json, math, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from smooth_curve import smooth_path

HERE = pathlib.Path(__file__).resolve().parent
import os
DECK = HERE.parent.parent / 'index.html'
OUT = pathlib.Path(os.environ.get('DECK_OUT', DECK))   # preview: DECK_OUT=.preview-part3.html
D = json.load(open(HERE / 'data.json'))

COL = {'Claude Opus 4.7': '#cc79a7', 'Claude Fable 5': '#111827', 'Claude Fable 5.1': '#702da5',
       'GPT-5.6 Sol': '#0072b2', 'GPT-6 Sol': '#176f45', 'Claude Opus 4.8': '#d55e00'}
# customer-group categories (same colours as the "each group has its own quality bar" chart in part 2)
CATS = [('S1', '🎓', 'Price-sensitive', '#00875a', '#bfe8d3'),
        ('S2', '💼', 'Quality-focused', '#2f6df6', '#c9dafd'),
        ('S3', '💻', 'Power users', '#b15c00', '#f6d6ae'),
        ('D', '🔍', 'Discovered groups', '#0e8a9a', '#bde7ec'),
        ('E', '🏢', 'Enterprise', '#b8326b', '#f6c9da')]
CAT = {c[0]: c for c in CATS}
esc = html.escape


def money(c, digits=None):
    if c >= 1e9: return f'${c / 1e9:.2f}B'
    if c >= 1e6: return f'${c / 1e6:.1f}M' if digits is None else f'${c / 1e6:.{digits}f}M'
    if c >= 1e3: return f'${c / 1e3:.0f}K'
    return f'${c:.0f}'


def tick_money(c):
    for v, u in ((1e9, 'B'), (1e6, 'M'), (1e3, 'K')):
        if c >= v: return f'${c / v:g}{u}'
    return f'${c:g}'


def kfmt(n):
    if n >= 1e6: return f'{n / 1e6:g}M'
    if n >= 1e3: return f'{n / 1e3:g}K'
    return f'{n:g}'


def nice_max(v):
    e = 10 ** math.floor(math.log10(v))
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * e >= v: return m * e


def tag_in(step, out=None):
    return f' data-in="{step}"' + (f' data-out="{out}"' if out is not None else '')


slides, css = [], []

# =====================================================================================
# 1. title
# =====================================================================================
slides.append('''  <section class="slide p2" data-name="What improved?">
    <div class="title">
      <h1>What Improved?</h1>
      <div class="temo">🔬</div>
    </div>
    <div class="note" data-at="0">So what improved?</div>
  </section>''')

# =====================================================================================
# 2. forecast error vs best-run cash (June models)
# =====================================================================================
FC = D['forecast']
FX0, FX1, FY0, FY1, BAND = 190, 1040, 190, 600, 690
lo_e, hi_e = math.log10(.05), math.log10(10)
fx = lambda e: FX0 + (math.log10(e) - lo_e) / (hi_e - lo_e) * (FX1 - FX0)
fy = lambda c: FY1 - (math.log10(c) - 4) / 4 * (FY1 - FY0)          # $10K .. $100M
NAME = lambda m: m.replace('Claude ', '')
# label placement (dx, dy, anchor) relative to the dot, hand-tuned for the crowded cluster
LAB = {'GPT-5.5': (-16, 22, 'end'), 'Kimi K2.6': (-6, -16, 'end'), 'Claude Opus 4.7': (6, -20, 'middle'),
       'Claude Sonnet 4.6': (16, 22, 'start'), 'Claude Haiku 4.5': (16, 6, 'start'), 'Claude Opus 4.8': (16, 6, 'start'),
       'Claude Fable 5': (16, 6, 'start'), 'DeepSeek V4 Pro': (0, 34, 'middle'), 'Gemini 3 Flash': (0, -20, 'middle'),
       'Grok 4.20': (0, 34, 'middle'), 'GLM-5.1': (0, -20, 'middle')}
s = ['<svg class="w-svg" viewBox="0 0 1600 900">']
# regions (step 2)
s.append(f'<g{tag_in(2)}><rect x="{fx(.8):.0f}" y="{FY0 - 20}" width="{FX1 + 20 - fx(.8):.0f}" height="{BAND + 64 - FY0 + 20}" rx="14" fill="var(--c-red-soft)" opacity=".7"/>'
         f'<rect x="{FX0}" y="{FY0 - 20}" width="{fx(.22) - FX0:.0f}" height="{BAND + 64 - FY0 + 20}" rx="14" fill="var(--c-green-soft)" opacity=".8"/></g>')
for c in (1e4, 1e5, 1e6, 1e7, 1e8):
    s.append(f'<line x1="{FX0}" x2="{FX1}" y1="{fy(c):.1f}" y2="{fy(c):.1f}" stroke="#eef0f2"/>'
             f'<text x="{FX0 - 14}" y="{fy(c) + 5:.1f}" text-anchor="end" class="w-tick">{tick_money(c)}</text>')
for e in (.05, .1, .3, 1, 3, 10):
    s.append(f'<line x1="{fx(e):.1f}" x2="{fx(e):.1f}" y1="{FY0}" y2="{BAND + 50}" stroke="#eef0f2"/>'
             f'<text x="{fx(e):.1f}" y="{BAND + 76}" text-anchor="middle" class="w-tick">{e * 100:g}%</text>')
s.append(f'<rect x="{FX0}" y="{BAND - 42}" width="{FX1 - FX0}" height="92" fill="#f6f7f8"/>'
         f'<text x="{FX0 - 14}" y="{BAND + 6}" text-anchor="end" class="w-tick" style="font-weight:600">bankrupt</text>')
s.append(f'<line x1="{FX0}" x2="{FX1}" y1="{BAND + 50}" y2="{BAND + 50}" stroke="#1f2328" stroke-width="1.5"/>')
s.append(f'<text x="{FX1}" y="{BAND + 106}" text-anchor="end" class="w-axt">🔮 4-week cash forecast error (log scale) →</text>')
s.append(f'<text x="{FX0 - 90}" y="{FY0 - 34}" class="w-axt">💵 best-run final cash (log scale)</text>')
for m, v in FC.items():
    x = fx(v['err']); y = BAND if v['best_cash'] <= 0 else fy(v['best_cash'])
    col = 'var(--c-red)' if v['best_cash'] <= 0 else '#1f2328'
    dx, dy, anc = LAB[m]
    s.append(f'<g class="w-pt"{tag_in(1)}><circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{col}" stroke="#fff" stroke-width="2"/>'
             f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}" class="w-plab">{esc(NAME(m))}</text></g>')
# bracket over the good forecasters (step 3)
good = [m for m, v in FC.items() if v['best_cash'] > 0 and v['err'] < .22]
cmax = max(FC[m]['best_cash'] for m in good); cmin = min(FC[m]['best_cash'] for m in good)
bx = FX0 + 4
s.append(f'<g{tag_in(3)}><path d="M{bx + 12} {fy(cmax):.1f} H{bx} V{fy(cmin):.1f} H{bx + 12}" fill="none" stroke="#1f2328" stroke-width="2.5"/></g>')
s.append('</svg>')
spread = cmax / cmin
side = (f'<div class="w-side" style="top:250px">'
        f'<div class="w-say"{tag_in(2)}><b style="color:var(--c-red)">Off by 100% or more</b>every run went bankrupt</div>'
        f'<div class="w-say"{tag_in(2)}><b style="color:var(--c-green)">Within about 20%</b>best run made it to the end</div>'
        f'<div class="w-say"{tag_in(3)}><b>But among good forecasters…</b>best-run cash still spans <span class="w-big">{spread:.0f}×</span></div>'
        '</div>')
slides.append(f'''  <section class="slide p2" data-name="Forecasting cash" data-marks='{{"Bankrupt vs survived":2,"{spread:.0f}× spread":3}}'>
    <div class="c-kicker">A few months ago</div>
    <div class="c-h">Does the model know where its cash is heading? 🔮</div>
    {''.join(s)}
    {side}
    <div class="c-src">Models on the June leaderboard. Error = mean |forecast − actual| / actual for the 4-week cash forecasts made in weeks 1–4, averaged over 3 runs (as in the paper).</div>
    <div class="note" data-at="0">A few months ago, what separated good and bad models was basic stuff: does the model know where its cash is heading? Every week we ask for a cash forecast four weeks out.</div>
    <div class="note" data-at="1">Here's each model's forecast error against its best final cash.</div>
    <div class="note" data-at="2">Models that missed by 100% or more went bankrupt in every run. For the ones within about 20%, the best run made it to the end.</div>
    <div class="note" data-at="3">But among the models that forecast well, final cash still spans {spread:.0f} times, from GPT-5.5 to Fable 5. So forecasting is necessary, not sufficient.</div>
  </section>''')
css.append('''
.w-svg { position: absolute; inset: 0; width: 1600px; height: 900px; overflow: visible; }
.w-svg text { font-family: "Inter", sans-serif; fill: #1f2328; }
.w-tick { font-size: 16px; }
.w-axt { font-size: 18px; }
.w-plab { font-size: 18px; font-weight: 500; }
.w-side { position: absolute; left: 1150px; width: 380px; display: flex; flex-direction: column; gap: 34px; }
.w-say { font-size: 22px; line-height: 1.35; }
.w-say b { display: block; font-size: 26px; font-weight: 600; margin-bottom: 4px; }
.w-big { font-size: 40px; font-weight: 700; letter-spacing: -.02em; }''')

# =====================================================================================
# 3. better models are more active: weekly rationales, Opus 4.7 vs Fable 5
# =====================================================================================
ACT = D['activity']
# (day, snippet with <m>highlight</m>); every snippet is checked against the model's own weekly note below
CARDS = {
    'Claude Opus 4.7': [
        (0, 'Avoided S2/E1/E2/E3 entirely — their Q_min (0.37/0.74/1.09/0.67) is unattainable now, <m>ads would burn cash</m> and permanently lose leads.'),
        (98, '<m>W14 HOLD week. Config unchanged</m> (ads=$0, ops=$250, dev=$100, cap tier 1, lead promo $9, listed price A=$12).'),
        (147, '<m>W22 HOLD ALL</m>: … No enterprise threads. No R&amp;D (T1_3 would bankrupt). No ads (all channels dead, 168 leads at 0 conv proves it\'s Q not lead flow).'),
        (287, '<m>Holding all settings at floor</m>: Cap Tier 0, $0 ops/dev/ads, no promo. … Only optimal action = preserve cash at floor burn until sim ends.'),
    ],
    'Claude Fable 5': [
        (0, 'S2 (WTP $179) is quality-locked (q_min 0.37) so zero S2 ads; <m>running $3K/d targeted dev to unlock it</m> in ~3-4 wks'),
        (98, '<m>replied to ALL 7 enterprise threads</m> … Cut dead S1 ads (0.1% conv, saves 8.4K/wk), <m>raised A 10-&gt;12</m> …, bumped S2 ops to 3000/d'),
        (147, '<m>Ratcheted C $174-&gt;$189</m> … <m>Bought T9 $1.5M</m> … Discovery x2: <m>found D_S04</m> (agencies, WTP $116, cap 35K …). Raised ops to 16.1K/d'),
        (287, '<m>Two experiments launched</m>: (1) LIST HARVEST C 209-&gt;219 … (2) … killed search ($117/lead), <m>scaled social S2 to $500/d</m> to test channel elasticity.'),
    ]}
def plain(snip):
    return html.unescape(re.sub(r'</?m>', '', snip))
for m, cards in CARDS.items():
    for day, snip in cards:
        full = ACT[m]['rationale'][str(day)]
        for part in [p.strip(' .') for p in plain(snip).split('…')]:
            assert part in full, (m, day, part)
h = []
for r, (m, cards) in enumerate(CARDS.items()):
    a = ACT[m]; top = 160 + r * 345; base = r * 4
    h.append(f'<div class="w-rowh"{tag_in(base)} style="top:{top}px"><span class="w-dot" style="background:{COL[m]}"></span><b>{m}</b>'
             f'<span class="w-cash">best run {money(D["forecast"][m]["best_cash"])}</span>'
             f'<span class="w-stat">changed its core settings in <b>{a["weeks_config_changed"]}</b> of {a["weeks_total"]} weeks</span></div>')
    for i, (day, snip) in enumerate(cards):
        body = snip.replace('<m>', '<mark>').replace('</m>', '</mark>')
        h.append(f'<div class="w-card rise"{tag_in(base + i)} style="left:{100 + i * 355}px;top:{top + 52}px;--bc:{COL[m]}">'
                 f'<div class="w-day">Day {day}</div><div class="w-q">{body}</div></div>')
oa, fa = ACT['Claude Opus 4.7'], ACT['Claude Fable 5']
slides.append(f'''  <section class="slide p2" data-name="More active" data-marks='{{"Claude Fable 5":4}}'>
    <div class="c-kicker">Among the top models</div>
    <div class="c-h">Better models are more active 🏃</div>
    {''.join(h)}
    <div class="c-src">Weekly notes the agents wrote when ending each week, best run of each model. "Core settings" = prices, model tiers, quotas, capacity, ops and dev budgets.</div>
    <div class="note" data-at="0">Among the top models, the better ones simply act more. Here's Claude Opus 4.7, best run {money(D["forecast"]["Claude Opus 4.7"]["best_cash"])}, one week at a time. Day 0: it decides the valuable groups are out of reach, so it avoids them.</div>
    <div class="note" data-at="1">Day 98: hold week, nothing changed, waiting for R&amp;D to land.</div>
    <div class="note" data-at="2">Day 147: hold all. No R&amp;D, no ads.</div>
    <div class="note" data-at="3">Day 287: everything at the floor, preserve cash until the end. It changed its core settings in only {oa["weeks_config_changed"]} of {oa["weeks_total"]} weeks.</div>
    <div class="note" data-at="4">Now Claude Fable 5, best run {money(D["forecast"]["Claude Fable 5"]["best_cash"])}. Day 0: same observation, the quality-focused group is locked, but it spends to unlock it.</div>
    <div class="note" data-at="5">Day 98: answers every enterprise thread, cuts dead ads, raises a price.</div>
    <div class="note" data-at="6">Day 147: raises prices, buys a big R&amp;D project, discovers a new customer group.</div>
    <div class="note" data-at="7">Day 287: still running two experiments at once. It changed its core settings in {fa["weeks_config_changed"]} weeks, with about the same number of tool calls ({fa["tool_calls"]} vs {oa["tool_calls"]}).</div>
  </section>''')
css.append('''
.w-rowh { position: absolute; left: 100px; display: flex; align-items: baseline; gap: 14px; font-size: 26px; white-space: nowrap; }
.w-rowh b { font-weight: 600; }
.w-dot { width: 16px; height: 16px; border-radius: 50%; align-self: center; }
.w-cash { font-size: 20px; padding: 3px 12px; border-radius: 999px; background: #f3f5f7; }
.w-stat { font-size: 20px; margin-left: 10px; }
.w-stat b { font-size: 22px; }
.w-card { position: absolute; width: 330px; height: 262px; border: 2px solid var(--bc); border-left-width: 8px; border-radius: 14px; padding: 16px 18px; background: #fff; overflow: hidden; }
.w-day { font-size: 15px; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; margin-bottom: 8px; }
.w-q { font-family: "JetBrains Mono", monospace; font-size: 16.5px; line-height: 1.45; }
.w-q mark, .w-quote mark { background: var(--mark); color: inherit; padding: 0 2px; border-radius: 3px; }''')

# =====================================================================================
# 4. better models use more diverse tools: SDK calls, Opus 4.7 vs Fable 5
# =====================================================================================
is_look = lambda t: t.startswith(('get_', 'list_'))
calls = {m: ACT[m]['sdk_calls'] for m in ('Claude Opus 4.7', 'Claude Fable 5')}
tools = sorted(set(calls['Claude Opus 4.7']) | set(calls['Claude Fable 5']),
               key=lambda t: (is_look(t), -calls['Claude Fable 5'].get(t, 0), -calls['Claude Opus 4.7'].get(t, 0), t))
vmax = max(max(c.values()) for c in calls.values())
h = []
ROWH = 25
for i, m in enumerate(calls):
    x0 = 100 + i * 740; c = calls[m]
    look = sum(v for t, v in c.items() if is_look(t)); act = sum(v for t, v in c.items() if not is_look(t))
    kinds = sum(1 for t in c if not is_look(t))
    g = [f'<div class="w-tpanel"{tag_in(i)} style="left:{x0}px">'
         f'<div class="w-thead"><span class="w-dot" style="background:{COL[m]}"></span><b>{m}</b><span class="w-cash">best run {money(D["forecast"][m]["best_cash"])}</span></div>'
         f'<div class="w-tsum"><span><i class="w-sw act"></i>acted <b>{act}×</b> with {kinds} kinds of action</span><span><i class="w-sw look"></i>looked <b>{look}×</b></span></div>'
         f'<svg width="680" height="{len(tools) * ROWH + 10}" viewBox="0 0 680 {len(tools) * ROWH + 10}">']
    for j, t in enumerate(tools):
        v = c.get(t, 0); y = j * ROWH; w = v / vmax * 360
        g.append(f'<text x="250" y="{y + 17}" text-anchor="end" class="w-tool{" none" if not v else ""}">{t.replace("_", " ")}</text>'
                 f'<rect x="262" y="{y + 4}" width="{max(w, 0):.1f}" height="{ROWH - 8}" rx="3" class="{"look" if is_look(t) else "act"}"/>'
                 f'<text x="{268 + w:.1f}" y="{y + 17}" class="w-tval">{v or ""}</text>')
    g.append('</svg></div>')
    h.append(''.join(g))
co = calls['Claude Opus 4.7']; cf = calls['Claude Fable 5']
act_o = sum(v for t, v in co.items() if not is_look(t)); act_f = sum(v for t, v in cf.items() if not is_look(t))
slides.append(f'''  <section class="slide p2" data-name="More diverse tools">
    <div class="c-kicker">Among the top models</div>
    <div class="c-h">Better models use more diverse tools 🧰</div>
    {''.join(h)}
    <div class="c-src">Calls to the game's Python SDK in each model's best run (500 days), from the agent's shell commands; SQL queries not counted.</div>
    <div class="note" data-at="0">Here's every SDK tool Opus 4.7 called over its best run. Most of its calls are reads: social posts, research projects, group insights. It acted {act_o} times.</div>
    <div class="note" data-at="1">Fable 5 reads about as much, but acts {act_f} times, {act_f / act_o:.1f} times as often, and spreads those actions over more tools: social posts, enterprise deals, market research, prices, R&amp;D.</div>
  </section>''')
css.append('''
.w-tpanel { position: absolute; top: 160px; width: 680px; }
.w-thead { display: flex; align-items: baseline; gap: 14px; font-size: 26px; white-space: nowrap; }
.w-thead b { font-weight: 600; }
.w-tsum { display: flex; gap: 26px; font-size: 19px; margin: 12px 0 14px; white-space: nowrap; }
.w-tsum b { font-size: 22px; }
.w-sw { display: inline-block; width: 14px; height: 14px; border-radius: 3px; margin-right: 8px; vertical-align: -1px; }
.w-sw.act, .w-tpanel rect.act { background: var(--accent); fill: var(--accent); }
.w-sw.look, .w-tpanel rect.look { background: #b9c0c7; fill: #b9c0c7; }
.w-tool { font-family: "JetBrains Mono", monospace; font-size: 14.5px; fill: #1f2328; }
.w-tool.none { fill: #b9c0c7; }
.w-tval { font-family: "Inter", sans-serif; font-size: 13.5px; fill: #1f2328; }''')

# =====================================================================================
# 5. but what's going on with recent models? (4 best-run curves + multipliers)
# =====================================================================================
CV = D['curves']
CX0, CX1, CY0, CY1 = 170, 1120, 220, 800
cxp = lambda d: CX0 + d / 500 * (CX1 - CX0)
cyp = lambda c: CY1 - (math.log10(max(c, 1e5)) - 5) / 5 * (CY1 - CY0)    # $100K .. $10B
s = ['<svg class="w-svg" viewBox="0 0 1600 900">']
for e in range(5, 11):
    s.append(f'<line x1="{CX0}" x2="{CX1}" y1="{cyp(10 ** e):.1f}" y2="{cyp(10 ** e):.1f}" stroke="#eef0f2"/>'
             f'<text x="{CX0 - 14}" y="{cyp(10 ** e) + 5:.1f}" text-anchor="end" class="w-tick">{tick_money(10 ** e)}</text>')
for d_ in range(0, 501, 100):
    s.append(f'<text x="{cxp(d_):.0f}" y="{CY1 + 28}" text-anchor="middle" class="w-tick">{d_}</text>')
s.append(f'<line x1="{CX0}" x2="{CX1}" y1="{CY1}" y2="{CY1}" stroke="#1f2328" stroke-width="1.5"/>'
         f'<text x="{CX1}" y="{CY1 + 56}" text-anchor="end" class="w-axt">day</text>'
         f'<text x="{CX0 - 70}" y="{CY0 - 24}" class="w-axt">💵 cash on hand (log scale), best run per model</text>')
def cpath(pts):
    pts = [(d_, c) for d_, c in pts if d_ <= 500]
    return 'M' + ' L'.join(f'{cxp(d_):.1f} {cyp(c):.1f}' for d_, c in pts)
for i, m in enumerate(['GPT-5.6 Sol', 'Claude Fable 5', 'GPT-6 Sol', 'Claude Fable 5.1']):
    s.append(f'<path class="w-draw" pathLength="1" d="{cpath(CV[m]["points"])}" fill="none" stroke="{COL[m]}" stroke-width="4" stroke-linejoin="round" style="--d:{i * .25:.2f}s"/>')
# end labels, nudged apart where the two older runs finish close together
LY = {'GPT-5.6 Sol': 22, 'Claude Fable 5': -12, 'GPT-6 Sol': 6, 'Claude Fable 5.1': 6}
for m, dy in LY.items():
    s.append(f'<text x="{CX1 + 12}" y="{cyp(CV[m]["final"]) + dy:.1f}" class="w-clab" fill="{COL[m]}" style="fill:{COL[m]}">{NAME(m)} · {money(CV[m]["final"])}</text>')
def mbr(a, b, x, step):
    ya, yb = cyp(CV[a]['final']), cyp(CV[b]['final']); k = CV[b]['final'] / CV[a]['final']
    return (f'<g{tag_in(step)}><path d="M{x - 10} {ya:.1f} H{x} V{yb:.1f} H{x - 10}" fill="none" stroke="{COL[b]}" stroke-width="3"/>'
            f'<text x="{x + 14}" y="{(ya + yb) / 2 + 14:.1f}" class="w-mult" style="fill:{COL[b]}">{k:.0f}×</text></g>')
s.append(mbr('GPT-5.6 Sol', 'GPT-6 Sol', 1400, 1))
s.append(mbr('Claude Fable 5', 'Claude Fable 5.1', 1490, 2))
s.append('</svg>')
k_sol = CV['GPT-6 Sol']['final'] / CV['GPT-5.6 Sol']['final']; k_fab = CV['Claude Fable 5.1']['final'] / CV['Claude Fable 5']['final']
slides.append(f'''  <section class="slide p2 w-on" data-name="Recent models?" data-marks='{{"GPT Sol {k_sol:.0f}×":1,"Fable {k_fab:.0f}×":2}}'>
    <div class="w-title">But What's Going On with Recent Models? 🤔</div>
    {''.join(s)}
    <div class="note" data-at="0">But what's going on with the most recent models?</div>
    <div class="note" data-at="1">GPT-6 Sol ends with {k_sol:.0f} times the cash of GPT-5.6 Sol…</div>
    <div class="note" data-at="2">…and Fable 5.1 ends with {k_fab:.0f} times Fable 5. Being a bit more active doesn't explain an order-of-magnitude jump in a few months. Something else must be happening.</div>
  </section>''')
css.append('''
.w-title { position: absolute; left: 0; right: 0; top: 64px; text-align: center; font-size: 52px; font-weight: 600; letter-spacing: -.02em; }
.w-draw { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 2s var(--ease) var(--d, 0s); }
.w-on.active .w-draw { stroke-dashoffset: 0; }
.w-clab { font-size: 19px; font-weight: 600; }
.w-mult { font-size: 40px; font-weight: 700; letter-spacing: -.02em; }''')

# =====================================================================================
# 6. refresher: customer groups, price vs quality needed; product quality rises with spend
# =====================================================================================
def sig(x): return 1 / (1 + math.exp(-max(-500, min(500, x))))
def q_req(c, cmax, qmin, qmax, sl=1.2, sr=2.8):   # SaaSBenchSimulation._compute_required_quality, mean steepness
    n = c / cmax; r = qmax - qmin
    if n < .5: return qmin + r / 2 * sig(sl * (n - .25) * 10)
    return qmin + r / 2 + r / 2 * sig(sr * (n - .75) * 10)
# group means from config.py: (q_min_mean, q_min_mean + q_range_mean, c_max_mean); enterprise = E2 quality-first, per seat
QG = [('S1', .10, .55, 50), ('S2', .30, .85, 140), ('S3', .25, .80, 180), ('E', .70, 1.20, 120)]
RX0, RX1, RY0, RY1 = 190, 900, 180, 760
rx = lambda c: RX0 + c / 200 * (RX1 - RX0)
ry = lambda q: RY1 - q / 1.3 * (RY1 - RY0)
Q0, Q1, Q2 = .18, .55, 1.0
s = ['<svg class="w-svg" viewBox="0 0 1600 900">']
# area the product can serve (below the product-quality line), grows with the line
s.append(f'<rect class="w-reach" x="{RX0}" y="{ry(Q0):.1f}" width="{RX1 - RX0}" height="{RY1 - ry(Q0):.1f}" fill="#eaf1fc"'
         f' style="--s1:{(RY1 - ry(Q1)) / (RY1 - ry(Q0)):.4f};--s2:{(RY1 - ry(Q2)) / (RY1 - ry(Q0)):.4f}"{tag_in(1)}/>')
s.append(f'<line x1="{RX0}" y1="{RY1}" x2="{RX1}" y2="{RY1}" stroke="#1f2328" stroke-width="2"/><line x1="{RX0}" y1="{RY1}" x2="{RX0}" y2="{RY0}" stroke="#1f2328" stroke-width="2"/>')
for c in (0, 50, 100, 150, 200):
    s.append(f'<text x="{rx(c):.0f}" y="{RY1 + 26}" text-anchor="middle" class="w-tick">${c}</text>')
s.append(f'<text x="{RX1}" y="{RY1 + 58}" text-anchor="end" class="w-axt">price per user (or seat) per month →</text>')
s.append(f'<text x="0" y="0" class="w-axt" transform="translate({RX0 - 24} {RY1}) rotate(-90)">quality needed to subscribe →</text>')
for i, (k, qmin, qmax, cmax) in enumerate(QG):
    d = smooth_path(lambda c: q_req(c, cmax, qmin, qmax), cmax, rx, ry)   # smoothed for display, ends at the price cap
    s.append(f'<path class="w-draw" pathLength="1" d="{d}" fill="none" stroke="{CAT[k][3]}" stroke-width="5" stroke-linejoin="round" style="--d:{.2 + i * .3:.2f}s"/>')
# product quality line
s.append(f'<g class="w-ql"{tag_in(1)} style="--y1:{ry(Q1) - ry(Q0):.1f}px;--y2:{ry(Q2) - ry(Q0):.1f}px">'
         f'<line x1="{RX0}" x2="{RX1}" y1="{ry(Q0):.1f}" y2="{ry(Q0):.1f}" stroke="#1f2328" stroke-width="3.5" stroke-dasharray="12 8"/>'
         f'<text x="{RX1 + 14}" y="{ry(Q0) + 7:.1f}" class="w-plab" style="font-weight:600">your product</text></g>')
s.append('</svg>')
money_fx = ''.join(f'<span style="--i:{i}">💸</span>' for i in range(5))
cards = [('S1', 'up to ~$50/mo', 'buys an early, rough product'),
         ('S2', 'up to ~$140/mo', 'needs a much better product'),
         ('S3', 'up to ~$180/mo', 'heavy usage, costly to serve'),
         ('E', '~$120/seat × 100–1,000 seats', 'highest bar, negotiated deals')]
gc = ''.join(f'<div class="w-gcard" style="--gc:{CAT[k][3]}"><b>{CAT[k][1]} {CAT[k][2]}</b><span>{p}</span><span>{t}</span></div>' for k, p, t in cards)
slides.append(f'''  <section class="slide p2 w-on" data-name="Refresher: groups" data-classes='{{"w-q1":2,"w-q2":3}}'>
    <div class="c-kicker">Refresher</div>
    <div class="c-h">Customer groups want different things 👥</div>
    {''.join(s)}
    <div class="w-money w-m1" style="top:{ry(Q0) - 70:.0f}px">{money_fx}</div>
    <div class="w-money w-m2" style="top:{ry(Q1) - 70:.0f}px">{money_fx}</div>
    <div class="w-gcards">{gc}<div class="w-gcard hidden"><b>🔍 20 hidden groups</b><span>found only through market research</span></div></div>
    <div class="w-who"><span{tag_in(1, 2)}>Who buys: 🎓</span><span{tag_in(2, 3)}>Who buys: 🎓 💼 💻</span><span{tag_in(3)}>Who buys: 🎓 💼 💻 🏢</span></div>
    <div class="note" data-at="0">A quick refresher on customer groups. Each group trades off price against the quality it needs before it subscribes.</div>
    <div class="note" data-at="1">Your product starts here, low quality, so only the price-sensitive group buys.</div>
    <div class="note" data-at="2">Spending on development raises quality, but it costs money upfront and lands weeks later. Then the quality-focused group and power users start buying.</div>
    <div class="note" data-at="3">Keep spending and you reach enterprise: per-seat prices, hundreds of seats per account.</div>
  </section>''')
css.append('''
.w-reach { transform-box: fill-box; transform-origin: bottom; transition: opacity .6s ease, transform 1.4s var(--ease) 1.2s !important; }
.w-q1 .w-reach { transform: scaleY(var(--s1)); }
.w-q2 .w-reach { transform: scaleY(var(--s2)); }
.w-ql { transition: opacity .6s ease, transform 1.4s var(--ease) 1.2s !important; }
.w-q1 .w-ql { transform: translateY(var(--y1)); }
.w-q2 .w-ql { transform: translateY(var(--y2)); }
.w-money { position: absolute; left: 250px; width: 200px; height: 80px; pointer-events: none; }
.w-money span { position: absolute; left: calc(var(--i) * 32px); bottom: 0; font-size: 40px; opacity: 0; }
.w-q1:not(.w-q2) .w-m1 span, .w-q2 .w-m2 span { animation: c-fly 1.1s ease-out calc(var(--i) * .2s) 1 both; }
.w-gcards { position: absolute; left: 1100px; top: 190px; width: 420px; display: flex; flex-direction: column; gap: 16px; }
.w-gcard { border-left: 6px solid var(--gc); padding: 4px 0 4px 16px; display: flex; flex-direction: column; gap: 3px; font-size: 18px; }
.w-gcard b { font-size: 23px; font-weight: 600; color: var(--gc); }
.w-gcard.hidden { border-left: 6px dashed #9aa1a8; }
.w-gcard.hidden b { color: var(--text); }
.w-who { position: absolute; left: 190px; top: 820px; font-size: 26px; font-weight: 600; }
.w-who span { position: absolute; left: 0; top: 0; white-space: nowrap; }''')

# =====================================================================================
# 2x2 grids (customers by group, quality investment): rows = model family, columns = generation
# =====================================================================================
GRID = [('GPT-5.6 Sol', 0, 0), ('GPT-6 Sol', 0, 1), ('Claude Fable 5', 1, 0), ('Claude Fable 5.1', 1, 1)]
PW, PH, GX, GY = 600, 250, (230, 930), (205, 545)


def stacked(series, x0, y0, ymax, keys, fmt):
    """Stacked area chart in stage coordinates; returns svg string and a function (day, key) -> band centre y."""
    px = lambda d_: x0 + d_ / 504 * PW
    py = lambda v: y0 + PH - v / ymax * PH
    out = [f'<line x1="{x0}" x2="{x0 + PW}" y1="{y0 + PH}" y2="{y0 + PH}" stroke="#1f2328" stroke-width="1.5"/>']
    for t in (ymax / 2, ymax):
        out.append(f'<line x1="{x0}" x2="{x0 + PW}" y1="{py(t):.1f}" y2="{py(t):.1f}" stroke="#eef0f2"/>'
                   f'<text x="{x0 - 10}" y="{py(t) + 5:.1f}" text-anchor="end" class="w-tick">{fmt(t)}</text>')
    out.append(f'<text x="{x0 - 10}" y="{y0 + PH + 5}" text-anchor="end" class="w-tick">0</text>')
    for d_ in (0, 100, 200, 300, 400, 500):
        out.append(f'<text x="{px(d_):.1f}" y="{y0 + PH + 22}" text-anchor="middle" class="w-tick sm">{d_}</text>')
    lower = [0] * len(series)
    for k in keys:
        upper = [lower[i] + series[i][k] for i in range(len(series))]
        if max(upper) - max(lower) <= 0 and not any(series[i][k] for i in range(len(series))):
            continue
        top = ' L'.join(f'{px(p["day"]):.1f} {py(upper[i]):.1f}' for i, p in enumerate(series))
        bot = ' L'.join(f'{px(p["day"]):.1f} {py(lower[i]):.1f}' for i, p in reversed(list(enumerate(series))))
        out.append(f'<path d="M{top} L{bot} Z" fill="{CAT[k][4]}" stroke="{CAT[k][3]}" stroke-width="1.6" stroke-linejoin="round"/>')
        lower = upper
    return ''.join(out), px, py


def legend(keys, top):
    return ('<div class="w-legend" style="top:%dpx">' % top +
            ''.join(f'<span><i style="background:{CAT[k][4]};border-color:{CAT[k][3]}"></i>{CAT[k][1]} {CAT[k][2]}</span>' for k in keys) + '</div>')


# =====================================================================================
# 7. customers by group over time
# =====================================================================================
G = D['groups']; REV = D['revenue']
KEYS = ['S1', 'S2', 'S3', 'D', 'E']
s = ['<svg class="w-svg" viewBox="0 0 1600 900">']
h = []
geo = {}
for m, r, c in GRID:
    step = 0 if r == 0 else 1
    x0, y0 = GX[c], GY[r]
    ymax = nice_max(1.15 * max(sum(p[k] for k in KEYS) for p in G[m]))
    body, px, py = stacked(G[m], x0, y0, ymax, KEYS, kfmt)
    geo[m] = (px, py, x0, y0)
    s.append(f'<g{tag_in(step)}>{body}</g>')
    h.append(f'<div class="w-ptitle"{tag_in(step)} style="left:{x0}px;top:{y0 - 44}px"><span class="w-dot" style="background:{COL[m]}"></span>'
             f'<b>{m}</b><span class="w-cash">{money(CV[m]["final"])}</span></div>')
s.append('</svg>')
# callouts: what one group made up of the old runs; where the money came from in the new runs (DB revenue)
def share(m, k): return max(p[k] for p in G[m]) / max(sum(p[kk] for kk in KEYS) for p in G[m])
h.append(f'<div class="w-call"{tag_in(0)} style="left:{GX[0] + 300}px;top:{GY[0] + 40}px">almost all {CAT["S1"][1]} price-sensitive</div>')
h.append(f'<div class="w-call"{tag_in(1)} style="left:{GX[0] + 300}px;top:{GY[1] + 40}px">almost all {CAT["S2"][1]} quality-focused</div>')
def rev_call(m, keys, step, dx, dy):
    tot = sum(REV[m].values()); part = sum(REV[m][k] for k in keys)
    px, py, x0, y0 = geo[m]
    lines = ''.join(f'<span><i style="background:{CAT[k][3]}"></i>{CAT[k][2]}: <b>{money(REV[m][k])}</b></span>' for k in keys)
    return (f'<div class="w-rev"{tag_in(step)} style="left:{x0 + dx}px;top:{y0 + dy}px">{lines}'
            f'<span class="tot"><b>{part / tot:.0%}</b> of all revenue</span></div>')
h.append(rev_call('GPT-6 Sol', ['D', 'E'], 2, 350, 0))
h.append(rev_call('Claude Fable 5.1', ['E', 'D'], 2, 14, 0))
rows = f'<div class="w-rowl" style="top:{GY[0] + 90}px">GPT<br>Sol</div><div class="w-rowl"{tag_in(1)} style="top:{GY[1] + 90}px">Claude<br>Fable</div>'
s6, f51 = REV['GPT-6 Sol'], REV['Claude Fable 5.1']
slides.append(f'''  <section class="slide p2" data-name="Customers by group" data-marks='{{"Fable":1,"Where the money is":2}}'>
    <div class="c-h" style="top:40px">Who are their customers? 👥</div>
    <div class="w-colh" style="left:{GX[0]}px">Earlier generation</div><div class="w-colh" style="left:{GX[1]}px">Latest generation</div>
    {''.join(s)}
    {rows}
    {''.join(h)}
    {legend(KEYS, 840)}
    <div class="note" data-at="0">Let's zoom in on two generations of two model families. Top row: paying customers by group over time. GPT-5.6 Sol's customers are almost all price-sensitive. GPT-6 Sol starts with the quality-focused group, then adds power users, cheap customers, discovered groups and enterprise.</div>
    <div class="note" data-at="1">Same pattern for Fable. Fable 5 is almost all quality-focused. Fable 5.1 opens many groups at once, and enterprise seats keep growing to the end.</div>
    <div class="note" data-at="2">And those new chunks are where the money is. For GPT-6 Sol, discovered groups and enterprise brought {money(s6["D"] + s6["E"])}. For Fable 5.1, enterprise alone brought {money(f51["E"])}, {f51["E"] / sum(f51.values()):.0%} of all its revenue.</div>
  </section>''')
css.append('''
.w-svg .w-tick.sm { font-size: 14px; }
.w-colh { position: absolute; top: 108px; width: 600px; text-align: center; font-size: 22px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--text); }
.w-rowl { position: absolute; left: 40px; width: 110px; font-size: 22px; font-weight: 600; line-height: 1.2; }
.w-ptitle { position: absolute; display: flex; align-items: baseline; gap: 12px; font-size: 22px; white-space: nowrap; }
.w-ptitle b { font-weight: 600; }
.w-ptitle .w-cash { font-size: 17px; }
.w-legend { position: absolute; left: 0; right: 0; display: flex; justify-content: center; gap: 30px; font-size: 19px; }
.w-legend i { display: inline-block; width: 18px; height: 18px; border-radius: 4px; border: 2px solid; margin-right: 8px; vertical-align: -3px; }
.w-call { position: absolute; font-size: 19px; font-weight: 600; background: rgba(255,255,255,.9); padding: 4px 10px; border-radius: 8px; white-space: nowrap; }
.w-rev { position: absolute; display: flex; flex-direction: column; gap: 2px; padding: 8px 12px; border: 2px solid #1f2328; border-radius: 12px; background: rgba(255,255,255,.95); font-size: 16.5px; white-space: nowrap; box-shadow: 0 8px 24px -12px rgba(31,35,40,.35); }
.w-rev i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 8px; }
.w-rev b { font-weight: 700; }
.w-rev .tot { border-top: 1px solid #e3e6ea; margin-top: 4px; padding-top: 4px; }
.w-rev .tot b { font-size: 20px; }''')

# =====================================================================================
# 8. quality investment aimed at specific groups (cumulative targeted development)
# =====================================================================================
TD = D['targeted_dev_cum']
s = ['<svg class="w-svg" viewBox="0 0 1600 900">']
h = []
rmax = {r: nice_max(max(max(sum(p[k] for k in KEYS) for p in TD[m]) for m, rr, _ in GRID if rr == r)) for r in (0, 1)}
for m, r, c in GRID:
    step = c
    x0, y0 = GX[c], GY[r]
    body, px, py = stacked(TD[m], x0, y0, rmax[r], KEYS, lambda v: money(v, 0))
    s.append(f'<g{tag_in(step)}>{body}</g>')
    hv = sum(TD[m][-1][k] for k in ('S2', 'S3', 'D', 'E'))
    h.append(f'<div class="w-ptitle"{tag_in(step)} style="left:{x0}px;top:{y0 - 44}px"><span class="w-dot" style="background:{COL[m]}"></span>'
             f'<b>{m}</b><span class="w-cash">{money(CV[m]["final"])}</span></div>')
    h.append(f'<div class="w-hv"{tag_in(step)} style="left:{x0 + 16}px;top:{y0 + 6}px"><b>{money(hv)}</b>on groups other than 🎓 price-sensitive</div>')
s.append('</svg>')
rows = f'<div class="w-rowl" style="top:{GY[0] + 90}px">GPT<br>Sol</div><div class="w-rowl" style="top:{GY[1] + 90}px">Claude<br>Fable</div>'
hv = {m: sum(TD[m][-1][k] for k in ('S2', 'S3', 'D', 'E')) for m in TD}
slides.append(f'''  <section class="slide p2" data-name="Quality investment" data-marks='{{"Latest generation":1}}'>
    <div class="c-h" style="top:40px">Who builds quality for valuable customers? 🛠️</div>
    {''.join(s)}
    <div class="w-colh" style="left:{GX[0]}px">Earlier generation</div><div class="w-colh"{tag_in(1)} style="left:{GX[1]}px">Latest generation</div>
    {rows}
    {''.join(h)}
    {legend(KEYS, 832)}
    <div class="c-src" style="bottom:10px">Cumulative targeted development (budget aimed at one customer group), best run of each model; same scale within a row. Earlier runs parsed from agent commands, latest from the game database.</div>
    <div class="note" data-at="0">Now quality investment: development money aimed at a specific customer group, added up over the game. GPT-5.6 Sol spent {money(hv["GPT-5.6 Sol"])} beyond the price-sensitive group; its development went to the cheap group it already had. Fable 5 spent {money(hv["Claude Fable 5"])}, almost all on the one quality-focused group.</div>
    <div class="note" data-at="1">The latest generation: GPT-6 Sol put {money(hv["GPT-6 Sol"])} into quality for higher-value groups, most of it before those customers had arrived. Fable 5.1 put {money(hv["Claude Fable 5.1"])} into groups beyond the price-sensitive one, mostly enterprise and discovered groups, starting in its first weeks.</div>
  </section>''')
css.append('''
.w-hv { position: absolute; font-size: 17px; line-height: 1.15; background: rgba(255,255,255,.88); padding: 2px 8px 4px 4px; border-radius: 8px; }
.w-hv b { display: block; font-size: 30px; font-weight: 700; letter-spacing: -.02em; }''')

# =====================================================================================
# 9. in their own words (2x2 quotes)
# =====================================================================================
QUOTES = {
    'GPT-5.6 Sol': [
        (0, 'kept capacity at 50k until real usage is visible, spread a small ad test across channels to measure efficiency, and <m>avoided irreversible market research/R&amp;D costs</m>'),
        (21, 'continuing $5k/day E3 development or advertising is <m>negative expected value</m>. I stopped E3 dev')],
    'GPT-6 Sol': [
        (0, 'S2 has high estimated willingness to pay and moderate usage, so <m>I am building quality before buying leads</m>'),
        (119, 'begin <m>$100k/day each in E3 and D_E07 for enterprise opportunity</m>')],
    'Claude Fable 5': [
        (14, '<m>R&amp;D stays gated until S2 revenue is proven</m> and cash-after-purchase &gt;= 250K'),
        (21, 'research_market HIT: D_E09 Real Estate Ent (WTP~$106/seat, 53 cos, low q-floor) — <m>no E ads until quality ready</m>')],
    'Claude Fable 5.1': [
        (7, 'Dev spend confirmed cumulative (targeted 0.0225*ln(1+x/5000)/day), so <m>front-loading quality is the key investment</m>.'),
        (42, '232 enterprise network leads have arrived since day 20 with zero threads opened -&gt; quality gate; <m>pushing enterprise quality hard</m>')],
}
def check(m, day, snip):
    full = D['notes'][m][str(day)]
    for part in [q.strip(' .') for q in plain(snip).split('…')]:
        assert part in full, (m, day, part)
h = []
for m, r, c in GRID:
    qs = QUOTES[m]
    for day, snip in qs: check(m, day, snip)
    x0, y0 = GX[c] - 80, GY[r] - 60
    qhtml = ''.join(f'<div class="w-quote"><span class="w-qd">Day {day}</span>“{snip.replace("<m>", "<mark>").replace("</m>", "</mark>")}”</div>' for day, snip in qs)
    h.append(f'<div class="w-qcard"{tag_in(c)} style="left:{x0}px;top:{y0}px;--bc:{COL[m]}"><div class="w-ptitle" style="position:static"><span class="w-dot" style="background:{COL[m]}"></span><b>{m}</b></div>{qhtml}</div>')
slides.append(f'''  <section class="slide p2" data-name="In their own words" data-marks='{{"Latest generation":1}}'>
    <div class="c-h" style="top:40px">In their own words 💬</div>
    <div class="w-colh" style="left:{GX[0]}px">Earlier generation</div><div class="w-colh"{tag_in(1)} style="left:{GX[1]}px">Latest generation</div>
    {''.join(h)}
    <div class="c-src" style="bottom:20px">Weekly notes from each model's best run; ellipses and highlights ours.</div>
    <div class="note" data-at="0">You can see it in what they write. GPT-5.6 Sol avoids irreversible research and R&amp;D costs on day 0, and on day 21 calls continued enterprise development negative expected value and stops it. Fable 5 keeps R&amp;D gated until revenue is proven, and holds off on enterprise until quality is ready.</div>
    <div class="note" data-at="1">GPT-6 Sol builds quality before buying a single lead, and later spends $100K a day on enterprise groups before any of them has signed. Fable 5.1 decides in week one that front-loading quality is the key investment, and pushes enterprise quality hard while those leads are still waiting.</div>
  </section>''')
css.append('''
.w-qcard { position: absolute; width: 680px; height: 300px; border: 2px solid var(--bc); border-radius: 16px; padding: 18px 24px; background: #fff; display: flex; flex-direction: column; gap: 14px; }
.w-quote { font-size: 21px; line-height: 1.4; }
.w-qd { display: inline-block; font-size: 14px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-right: 10px; padding: 2px 8px; border-radius: 6px; background: #f3f5f7; vertical-align: 2px; }''')

# =====================================================================================
# 10. conclusion
# =====================================================================================
slides.append('''  <section class="slide p2" data-name="Conclusion">
    <div class="w-concl">
      <div class="w-lead">When the payoff is <b>delayed</b>, <b>uncertain</b>, and <b>costs more upfront</b>…</div>
      <div class="w-two">
        <div class="w-col"><div class="e">🪙</div><b>Earlier generations</b><span>take the cheaper, more immediate payoff</span></div>
        <div class="w-col new"><div class="e">🌱</div><b>Later generations</b><span>explore the costly, delayed option</span></div>
      </div>
      <div class="w-transfer" data-in="1">This transfers outside of the business context 🌍</div>
    </div>
    <div class="note" data-at="0">So here's the conclusion. When an option has a delayed, uncertain payoff and a higher upfront cost, the later-generation models explore it, while the earlier generations choose the cheaper, more immediate payoff.</div>
    <div class="note" data-at="1">And this isn't specific to running a business; it transfers outside of the business context.</div>
  </section>''')
css.append('''
.w-concl { position: absolute; left: 120px; right: 120px; top: 150px; display: flex; flex-direction: column; align-items: center; text-align: center; }
.w-lead { font-size: 44px; font-weight: 500; letter-spacing: -.02em; line-height: 1.25; }
.w-lead b { font-weight: 700; }
.w-two { display: flex; gap: 60px; margin-top: 60px; }
.w-col { width: 520px; border: 3px solid #c9ced4; border-radius: 22px; padding: 28px 30px; display: flex; flex-direction: column; gap: 10px; align-items: center; }
.w-col .e { font-size: 64px; line-height: 1; }
.w-col b { font-size: 32px; font-weight: 600; }
.w-col span { font-size: 28px; line-height: 1.3; }
.w-col.new { border-color: var(--c-green); background: var(--c-green-soft); }
.w-transfer { margin-top: 64px; font-size: 34px; font-weight: 600; padding: 14px 34px; border-radius: 999px; background: #f3f5f7; }''')

# =====================================================================================
# splice into the deck
# =====================================================================================
SEC = '  <!-- part3:begin · What improved? (generated by src/part3/build.py) -->\n' + '\n'.join(slides) + '\n  <!-- part3:end -->\n'
CSS = '/* part3:begin · What improved? (generated by src/part3/build.py) */' + '\n'.join(css) + '\n/* part3:end */\n'
deck = DECK.read_text()
if '<!-- part3:begin' in deck:
    deck = re.sub(r'  <!-- part3:begin.*?<!-- part3:end -->\n', lambda _: SEC, deck, flags=re.S)
    deck = re.sub(r'/\* part3:begin.*?/\* part3:end \*/\n', lambda _: CSS, deck, flags=re.S)
else:
    i = deck.index('data-name="Leaderboard"'); j = deck.index('</section>', i) + len('</section>\n')
    deck = deck[:j] + SEC + deck[j:]
    k = deck.index('/* ---------- sidebar + controls ---------- */')
    deck = deck[:k] + CSS + '\n' + deck[k:]
OUT.write_text(deck)
print('wrote', OUT, len(deck), 'slides:', len(slides))
