"""Part 6b · SWEeper-Bench results (paper Sections 3-4), built from data.json (see extract.py).

Writes out/sections.html and out/css.css; src/merge_parts.py splices them into the deck.
Slide 1 rebuilds Figure 2 (pass rate vs cost, provider-logo markers + ranked list) and slide 2 rebuilds
Figure 7a (cumulative stages), both in the paper's style, scaled up. All classes are prefixed rb-.
"""
import base64, html, json, math, pathlib

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / 'data.json'))
esc = html.escape
slides, css = [], []


def tag_in(step, out=None):
    return f' data-in="{step}"' + (f' data-out="{out}"' if out is not None else '')


def logo_uri(logo):
    svg = D['logos'][logo].replace('currentColor', '#000')
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


# =====================================================================================
# 1. Figure 2: pass rate vs mean cost per task
# =====================================================================================
B = D['leaderboard']
LC = D['logo_colors']
L, R, T, BOT = 180, 980, 200, 730
XLO, XHI, YLO, YHI = .09, 42, 26, 61
xp = lambda v: L + math.log(v / XLO) / math.log(XHI / XLO) * (R - L)
yp = lambda v: BOT - (v - YLO) / (YHI - YLO) * (BOT - T)
OFFS = {'gpt-5.6-sol': -16, 'muse-spark-1.3': 16}      # same display nudge as the paper figure (7 px there)
RAD = 20                                                # marker radius (10 in the paper)
IMG = 1.36 * RAD                                        # logo size inside the marker
below = [r for r in B if r['pass_pct'] < 50]
best = B[0]
assert best['rank'] == 1 and best['name'] == 'Grok 4.6' and len(B) == 15

s = ['<svg class="rb-svg" viewBox="0 0 1600 900">']
for t in (30, 40, 50, 60):
    s.append(f'<line x1="{L}" x2="{R}" y1="{yp(t):.1f}" y2="{yp(t):.1f}" stroke="#e5e8ed"/>'
             f'<text x="{L - 16}" y="{yp(t) + 7:.1f}" text-anchor="end" class="rb-tick">{t}%</text>')
for t in (.1, .2, .5, 1, 2, 5, 10, 20, 40):
    s.append(f'<line x1="{xp(t):.1f}" x2="{xp(t):.1f}" y1="{T}" y2="{BOT}" stroke="#eff1f4"/>'
             f'<text x="{xp(t):.1f}" y="{BOT + 34}" text-anchor="middle" class="rb-tick">${t:g}</text>')
s.append(f'<path d="M{L} {T}V{BOT}H{R}" stroke="#1f2328" stroke-width="1.6" fill="none"/>')
s.append(f'<text x="{(L + R) / 2}" y="{BOT + 80}" text-anchor="middle" class="rb-axt">Mean cost per task (USD, log scale)</text>'
         f'<text x="{L - 76}" y="{T - 30}" class="rb-axt">Pass rate</text>')
# highlight ring for the best agent (step 2)
bx, by = xp(best['cost']) + OFFS.get(best['model'], 0), yp(best['pass_pct'])
s.append(f'<g{tag_in(2)}><circle cx="{bx:.1f}" cy="{by:.1f}" r="{RAD + 12}" fill="var(--mark)" opacity=".85"/></g>')
# markers (all at step 1); draw low ranks last so the leaders sit on top
for r in sorted(B, key=lambda r: -r['rank']):
    x, y = xp(r['cost']) + OFFS.get(r['model'], 0), yp(r['pass_pct'])
    col, k = LC[r['logo']], RAD / 10
    s.append(f'<g class="rb-pt"{tag_in(1)}><title>{r["rank"]}. {esc(r["name"])}: {r["pass_pct"]:.1f}%, ${r["cost"]:.2f}/task</title>'
             f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{RAD}" fill="#fff" stroke="{col}" stroke-width="2.4"/>'
             f'<image x="{x - IMG / 2:.1f}" y="{y - IMG / 2:.1f}" width="{IMG:.1f}" height="{IMG:.1f}" href="{logo_uri(r["logo"])}"/>'
             f'<path d="M{x + RAD:.1f} {y:.1f}A{RAD / math.sqrt(2):.2f} {RAD / math.sqrt(2):.2f} 0 0 1 {x:.1f} {y + RAD:.1f}Z" fill="{col}"/>'
             f'<text x="{x + 7.2 * k:.1f}" y="{y + 9.4 * k:.1f}" text-anchor="middle" class="rb-rk">{r["rank"]}</text></g>')
s.append('</svg>')
# ranked list (model + %)
ROW0, ROWH = T + 2, (BOT - T) / 14.6
rows = []
for r in B:
    y = ROW0 + (r['rank'] - 1) * ROWH
    cls = ' rb-best' if r is best else (' rb-low' if r['pass_pct'] < 50 else '')
    rows.append(f'<div class="rb-row{cls}"{tag_in(1)} style="top:{y - 19:.0f}px"><span class="rb-n">{r["rank"]}</span>'
                f'<img src="{logo_uri(r["logo"])}" alt=""><b>{esc(r["name"])}</b><span class="rb-p">{r["pass_pct"]:.1f}%</span></div>')
mid = [r for r in B if r['pass_pct'] == 56.5]
slides.append(f'''  <section class="slide p2" data-name="SWEeper-Bench results" data-classes='{{"rb-top": 2}}' data-marks='{{"Best agent": 2}}'>
    <div class="c-kicker">15 agents, 200 tasks</div>
    <div class="c-h">SWEeper-Bench is far from solved</div>
    {''.join(s)}
    <div class="rb-list">{''.join(rows)}</div>
    <div class="note" data-at="0">Here are the results. Each agent pairs a frontier model with its native harness, or Codex if it has none. On the x axis, mean cost per task, log scale; on the y axis, pass rate. A task passes only if both the target behavior test and the preservation test pass. Cost is the prediction cost only.</div>
    <div class="note" data-at="1">Each logo is one agent, numbered by rank. Cost varies a lot: agents with similar pass rates differ in cost by more than 30 times, and {mid[1]['name']} matches {mid[0]['name']} at more than twice the cost.</div>
    <div class="note" data-at="2">The best agent, {best['name']} with Cursor, passes only {best['pass_pct']:.1f}% of tasks. {B[1]['name']} follows at {B[1]['pass_pct']:.1f}%, then three agents at 56.5%. And {len(below)} of {len(B)} agents pass fewer than half of the tasks. Nearly all failures come from the target behavior test; preservation pass rates stay between 97.5 and 100%. Agents rarely break working features, but they often miss the bug they were asked to find.</div>
  </section>''')
css.append('''
.rb-svg { position: absolute; inset: 0; width: 1600px; height: 900px; overflow: visible; }
.rb-svg text { font-family: "Inter", sans-serif; fill: #1f2328; }
.rb-tick { font-size: 20px; }
.rb-axt { font-size: 22px; }
.rb-svg text.rb-call { font-size: 26px; font-weight: 700; }
.rb-svg text.rb-rk { font-size: 16px; font-weight: 700; fill: #fff; }
.rb-list { position: absolute; left: 1060px; top: 0; width: 440px; }
.rb-row { position: absolute; left: 0; width: 440px; height: 38px; display: flex; align-items: center; gap: 12px; font-size: 22px; padding: 0 10px; border-radius: 8px; white-space: nowrap; transition: background .4s, opacity .6s ease, transform .6s var(--ease); }
.rb-row b { font-weight: 700; }
.rb-row img { width: 24px; height: 24px; }
.rb-n { width: 24px; text-align: right; }
.rb-p { margin-left: auto; font-variant-numeric: tabular-nums; }
.rb-top .rb-row.rb-best { background: var(--mark); }
.rb-half .rb-row.rb-low { background: var(--c-red-soft); }''')

# =====================================================================================
# 2. Figure 7a: where do agents stumble? (cumulative stages, + a 100% start)
# =====================================================================================
ST = D['stages']
LAB = ['Start', 'Identified|target feature', 'Identified|buggy behavior', 'Diagnosed|root cause',
       'Fixed the|buggy behavior', 'Maintained|existing behaviors']
avg = [100.0] + ST['average']
lines = {m: [100.0] + v['rates'] for m, v in ST['models'].items()}
drops = [avg[i] - avg[i + 1] for i in range(len(avg) - 1)]
top2 = sorted(range(len(drops)), key=lambda i: -drops[i])[:2]
assert sorted(top2) == [0, 1], drops                   # the two biggest drops are the first two stages
assert [round(avg[i], 1) for i in (1, 2, 5)] == [75.4, 50.0, 40.8], avg   # numbers quoted in the paper
NS = len(LAB)
SX0, SDX, SY0, SY1 = 260, 224, 222, 732                # x of Start, stage spacing, y of 100%, y of 0%
sx = lambda i: SX0 + i * SDX
sy = lambda v: SY1 - v / 100 * (SY1 - SY0)
HOT = NS                                               # step that highlights the two drops
s = ['<svg class="rb-svg" viewBox="0 0 1600 900">']
# drop bands (behind everything)
for i in top2:
    s.append(f'<rect class="rb-band"{tag_in(HOT)} x="{sx(i) + 8}" y="{SY0 - 16}" width="{SDX - 16}" height="{SY1 - SY0 + 16}" rx="12" fill="var(--c-red-soft)"/>')
for t in range(0, 101, 20):
    s.append(f'<line x1="{SX0 - 40}" x2="{sx(NS - 1) + 40}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" stroke="#e5e8ed"/>'
             f'<text x="{SX0 - 56}" y="{sy(t) + 7:.1f}" text-anchor="end" class="rb-tick">{t}%</text>')
s.append(f'<path d="M{SX0 - 40} {SY0 - 16}V{SY1}H{sx(NS - 1) + 40}" stroke="#1f2328" stroke-width="1.6" fill="none"/>')
s.append(f'<text x="0" y="0" transform="translate({SX0 - 138} {(SY0 + SY1) / 2}) rotate(-90)" text-anchor="middle" class="rb-axt">% of cases reaching stage</text>')
for i, lab in enumerate(LAB):
    a, *b = lab.split('|')
    s.append(f'<text x="{sx(i)}" y="{SY1 + 42}" text-anchor="middle" class="rb-stage"{tag_in(i)}>'
             f'<tspan x="{sx(i)}">{a}</tspan>' + ''.join(f'<tspan x="{sx(i)}" dy="28">{t}</tspan>' for t in b) + '</text>')
# three layers, each split into one group per stage (so a stage appears with its step):
# gray per-agent lines < black average line < value labels (labels never get crossed by later lines)
gray, black, labels = [], [], []
for i in range(NS):
    g = [f'<g class="rb-step"{tag_in(i)}>']
    if i:
        for m, v in lines.items():
            g.append(f'<path class="rb-seg" pathLength="1" d="M{sx(i - 1)} {sy(v[i - 1]):.1f}L{sx(i)} {sy(v[i]):.1f}" stroke="#c4c4c4" stroke-width="2.5"/>')
        for m, v in lines.items():
            g.append(f'<circle class="rb-dot" cx="{sx(i)}" cy="{sy(v[i]):.1f}" r="5.5" fill="#c4c4c4"/>')
    gray.append(''.join(g) + '</g>')
    g = [f'<g class="rb-step"{tag_in(i)}>']
    if i:
        hot = ' rb-hotseg' if i - 1 in top2 else ''
        g.append(f'<path class="rb-seg rb-avg{hot}" pathLength="1" d="M{sx(i - 1)} {sy(avg[i - 1]):.1f}L{sx(i)} {sy(avg[i]):.1f}" stroke-width="5"/>')
    g.append(f'<circle class="rb-dot rb-avgdot" cx="{sx(i)}" cy="{sy(avg[i]):.1f}" r="9"/>')
    black.append(''.join(g) + '</g>')
    g = [f'<g class="rb-step"{tag_in(i)}>']
    lx, ly, anc = (sx(i) + 16, sy(avg[i]) - 16, 'start') if i else (sx(i), sy(avg[i]) - 22, 'middle')
    g.append(f'<text class="rb-dot rb-avgv" x="{lx}" y="{ly:.1f}" text-anchor="{anc}">{avg[i]:.1f}%</text>'.replace('100.0%', '100%'))
    if i == NS - 1:
        g.append(f'<text class="rb-dot rb-avgname" x="{sx(i) + 16}" y="{sy(avg[i]) + 36:.1f}">Average</text>'
                 f'<text class="rb-dot rb-grayname" x="{sx(i) + 16}" y="{sy(max(v[i] for v in lines.values())) - 14:.1f}">Each agent</text>')
    labels.append(''.join(g) + '</g>')
s += gray + black + labels
# drop callouts (bottom of each band, where no line passes)
for i in top2:
    s.append(f'<text class="rb-drop"{tag_in(HOT)} x="{sx(i) + SDX / 2}" y="{SY1 - 36}" text-anchor="middle">−{drops[i]:.1f}</text>')
s.append('</svg>')
n = len(lines)
fmin = min(v['rates'][0] for v in ST['models'].values()); fmax = max(v['rates'][0] for v in ST['models'].values())
notes = [
    f"So where do agents stumble? We split each trajectory into five cumulative stages; each stage requires all the previous ones. GPT-5.6 Luna reads each trajectory and judges the first three stages; the last two come from the behavior tests. Each gray line is one agent, the black line is the average over {n} agents. Everyone starts at 100%.",
    f"First: did the agent even find the feature that contains the bug? On average only {avg[1]:.1f}% of the time, from {fmin:.1f} to {fmax:.1f}% across agents. For example, in the AbanteCart task Grok 4.6 fixes phone numbers, addresses and notifications on the profile page, but never tries the ID photo upload where the bug lives.",
    f"Second: did it identify the buggy behavior? This drops to {avg[2]:.1f}%. Agents reach the feature but never run the interaction that exposes the bug, or they trigger it and don't recognize it as a bug. On Focalboard, all four agents we inspected reach the empty sidebar, and Claude Opus 5 even concludes it is intended, because the existing unit tests expect it.",
    f"Third: did it diagnose the root cause? {avg[3]:.1f}%. A much smaller drop.",
    f"Fixing: once the cause is found, agents usually fix it. {avg[4]:.1f}% pass the target behavior test.",
    f"And {avg[5]:.1f}% also keep the existing behaviors working. Very few regressions.",
    f"So the two biggest drops are the first two stages: about {drops[0]:.0f} points lost before even finding the feature, and another {drops[1]:.0f} before identifying the buggy behavior. Half of all cases are gone before the agent has found the bug. Agents mostly fail at finding the bug, not at fixing it.",
]
note_html = '\n'.join(f'    <div class="note" data-at="{k}">{esc(t, quote=False)}</div>' for k, t in enumerate(notes))
slides.append(f'''  <section class="slide p2" data-name="Where agents stumble" data-classes='{{"rb-hot": {HOT}}}' data-marks='{{"Two biggest drops": {HOT}}}'>
    <div class="c-h">Where do agents stumble?</div>
    {''.join(s)}
{note_html}
  </section>''')
css.append('''
.rb-stage { font-size: 22px; }
.rb-svg .rb-seg { fill: none; stroke-dasharray: 1; stroke-dashoffset: 0; transition: stroke-dashoffset .8s var(--ease), stroke .4s; }
.rb-svg .rb-avg { stroke: #000; }
.rb-step.frag-hidden { transform: none; }
.rb-step.frag-hidden .rb-seg { stroke-dashoffset: 1; }
.rb-step .rb-dot { transition: opacity .3s ease .6s, fill .4s; }
.rb-step.frag-hidden .rb-dot { opacity: 0; transition: none; }
.rb-svg .rb-avgdot { fill: #000; }
.rb-svg .rb-avgv { font-size: 24px; font-weight: 700; paint-order: stroke; stroke: #fff; stroke-width: 7px; stroke-linejoin: round; }
.rb-svg .rb-avgname { font-size: 24px; font-weight: 700; }
.rb-svg .rb-grayname { font-size: 22px; fill: #8a8f95; }
.rb-svg .rb-drop { font-size: 40px; font-weight: 700; }
.rb-hot .rb-svg .rb-hotseg { stroke: var(--c-red); }''')

out = HERE / 'out'
out.mkdir(exist_ok=True)
(out / 'sections.html').write_text('\n'.join(slides) + '\n')
(out / 'css.css').write_text('\n'.join(c.strip('\n') for c in css) + '\n')
print('wrote', out, 'drops', [round(d, 1) for d in drops])
