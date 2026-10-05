"""Part 4b · practice-game allocations (who invests in the big, delayed payoff) + CEO-Bench conclusion.

Reads data.json (see extract.py) and writes out/sections.html + out/css.css; src/merge_parts.py splices them
into the deck. All classes are prefixed tb-.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / 'data.json'))
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)
slides, css = [], []

COL = {'Fable 5': '#111827', 'Fable 5.1': '#702da5', 'GPT-5.6 Sol': '#0072b2', 'GPT-6 Sol': '#176f45'}
FAMILIES = [('Claude Fable', ['Fable 5', 'Fable 5.1']), ('GPT Sol', ['GPT-5.6 Sol', 'GPT-6 Sol'])]
B = '#8554b2'                                         # skill B (shown as 💻 Coding) colour of the practice heatmap
OTHER = {'D': '#c3c8ce', 'A': '#d3d7dc', 'E': '#e1e4e8', 'C': '#eceef1'}   # muted, stacked above B
ORDER = ['B', 'D', 'A', 'E', 'C']                     # bottom -> top
M = D['models']
for m in M:
    for wk in M[m]['weeks']: assert abs(sum(wk.values()) - 10) < 1e-9
wk1_b = {m: M[m]['weeks'][0]['B'] for m in M}
share_b = {m: sum(w['B'] for w in M[m]['weeks']) / (10 * len(M[m]['weeks'])) for m in M}
mean_wk = {m: {k: sum(w[k] for w in M[m]['weeks']) / len(M[m]['weeks']) for k in ORDER} for m in M}
score = {m: M[m]['score_mean'] for m in M}


def tag_in(step, out=None):
    return f' data-in="{step}"' + (f' data-out="{out}"' if out is not None else '')


# =====================================================================================
# 1. allocation: week 1 -> all 20 weeks -> mean over all weeks
# =====================================================================================
X0, CW, GAP, H = 330, 40, 6, 104          # week columns: left edge, width, gap, height (= 10 hours)
MX, MW = 1290, 64                         # mean column
FAM_Y = [222, 528]                        # family header baselines
ROW_DY = [26, 154]                        # row tops relative to family header
colx = lambda w: X0 + w * (CW + GAP)
ROWY = {}
for (fam, ms), fy in zip(FAMILIES, FAM_Y):
    for m, dy in zip(ms, ROW_DY): ROWY[m] = fy + dy


def column(alloc, x, y, w):
    parts, yy = [], y + H
    for k in ORDER:
        h = alloc[k] / 10 * H
        if h <= 0: continue
        yy -= h
        parts.append(f'<rect x="{x}" y="{yy:.2f}" width="{w}" height="{h:.2f}" fill="{B if k == "B" else OTHER[k]}"/>')
    return ''.join(parts)


s = ['<svg class="tb-svg" viewBox="0 0 1600 900">']
# week axis labels (above the first row)
ay = FAM_Y[0] - 32
for w in (1, 5, 10, 15, 20):
    s.append(f'<text x="{colx(w - 1) + CW / 2:.0f}" y="{ay}" text-anchor="middle" class="tb-tick{" tb-wk" if w > 1 else ""}" style="--d:{(w - 1) * .05:.2f}s">'
             f'{"week 1" if w == 1 else w}</text>')
s.append(f'<text x="{MX + MW / 2}" y="{ay}" text-anchor="middle" class="tb-tick tb-mean" style="font-weight:600">all weeks</text>')
for m, y in ROWY.items():
    wks = M[m]['weeks']
    s.append(f'<g class="tb-w1">{column(wks[0], colx(0), y, CW)}</g>')
    for i in range(1, len(wks)):
        s.append(f'<g class="tb-wk" style="--d:{i * .05:.2f}s">{column(wks[i], colx(i), y, CW)}</g>')
    s.append(f'<g class="tb-mean">{column(mean_wk[m], MX, y, MW)}</g>')
    # step 0: hours on B in week 1
    s.append(f'<g{tag_in(0, 1)}><text x="{colx(0) + CW + 20}" y="{y + H - 8}" class="tb-num">{wk1_b[m]:.1f} h<tspan class="tb-onb" dx="10">on coding</tspan></text></g>')
    # step 2: share of all hours on B
    s.append(f'<text x="{MX + MW + 20}" y="{y + H - 8}" class="tb-num tb-mean">{share_b[m]:.0%}</text>')
s.append('</svg>')
h = []
for (fam, ms), fy in zip(FAMILIES, FAM_Y):
    h.append(f'<div class="tb-fam" style="top:{fy - 22}px">{fam}</div>')
    for m in ms:
        h.append(f'<div class="tb-name" style="top:{ROWY[m] + H / 2 - 18:.0f}px"><span class="tb-dot" style="background:{COL[m]}"></span>{m}</div>')
    old, new = ms
    d = round(share_b[new] * 100) - round(share_b[old] * 100)
    h.append(f'<div class="tb-delta tb-mean" style="top:{ROWY[new] - 22:.0f}px">+{d} pts</div>')
legend = (f'<div class="tb-legend"><span><i style="background:{B}"></i><b>Coding</b>: big, delayed payoff</span>'
          f'<span><i style="background:{OTHER["A"]}"></i>cooking, running, guitar, Spanish</span></div>')
f5, f51, g56, g6 = (share_b[m] for m in ('Fable 5', 'Fable 5.1', 'GPT-5.6 Sol', 'GPT-6 Sol'))
slides.append(f'''  <section class="slide p2" data-name="Practice: allocation" data-classes='{{"tb-all":1,"tb-avg":2}}' data-marks='{{"All 20 weeks":1,"Mean":2}}'>
    <div class="c-h" style="top:40px">Newer models invest more in the big, delayed payoff</div>
    {legend}
    {''.join(s)}
    {''.join(h)}
    <div class="note" data-at="0">Here's how each model splits its 10 hours in week 1 (each column is one week's 10 hours, averaged over 5 trials per model). Purple is coding, the big, delayed payoff; grey is cooking, running, guitar and Spanish. (The models actually saw abstract skills A to E with these thresholds and reward rates; the names are just for illustration, coding is skill B.) Within each family, the newer model puts more on coding from the start: Fable 5 puts {wk1_b["Fable 5"]:.1f} hours on it, Fable 5.1 {wk1_b["Fable 5.1"]:.1f}; GPT-5.6 Sol {wk1_b["GPT-5.6 Sol"]:.1f}, GPT-6 Sol {wk1_b["GPT-6 Sol"]:.1f}.</div>
    <div class="note" data-at="1">Now all 20 weeks. Every model ends up putting the largest part of its time on coding, but Fable 5.1 stays above Fable 5 every week, and GPT-6 Sol is ahead of GPT-5.6 Sol in every week from week 10 on.</div>
    <div class="note" data-at="2">Averaged over all weeks: Fable goes from {f5:.0%} to {f51:.0%} of hours on coding, a clear gap. For GPT Sol the gap is small, {g56:.0%} to {g6:.0%}. This is 5 trials per model, and final scores are close: GPT-6 Sol {score["GPT-6 Sol"]:,.0f}, Fable 5.1 {score["Fable 5.1"]:,.0f}, Fable 5 {score["Fable 5"]:,.0f}, GPT-5.6 Sol {score["GPT-5.6 Sol"]:,.0f}. So it's a tendency, consistent with what we saw in CEO-Bench, not a big score difference.</div>
  </section>''')
css.append(f'''
.tb-svg {{ position: absolute; inset: 0; width: 1600px; height: 900px; overflow: visible; }}
.tb-svg text {{ font-family: "Inter", sans-serif; fill: #1f2328; }}
.tb-tick {{ font-size: 18px; }}
.tb-num {{ font-size: 36px; font-weight: 700; letter-spacing: -.02em; }}
.tb-onb {{ font-size: 22px; font-weight: 500; }}
.tb-fam {{ position: absolute; left: 100px; font-size: 18px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #1f2328; }}
.tb-name {{ position: absolute; left: 100px; display: flex; align-items: center; gap: 12px; font-size: 26px; font-weight: 600; white-space: nowrap; line-height: 36px; }}
.tb-dot {{ width: 16px; height: 16px; border-radius: 50%; }}
.tb-legend {{ position: absolute; left: 100px; right: 100px; top: 102px; display: flex; justify-content: center; gap: 34px; font-size: 20px; white-space: nowrap; }}
.tb-legend b {{ font-weight: 600; }}
.tb-legend i {{ display: inline-block; width: 18px; height: 18px; border-radius: 4px; margin-right: 10px; vertical-align: -3px; }}
.tb-lg2 {{ color: #6b737c; }}
.tb-delta {{ position: absolute; left: 1460px; font-size: 22px; font-weight: 700; color: var(--text); background: var(--c-green-soft); padding: 4px 12px; border-radius: 999px; white-space: nowrap; }}
.tb-wk {{ opacity: 0; transform: translateX(-10px); transition: opacity .35s ease var(--d), transform .35s var(--ease) var(--d); }}
.tb-all .tb-wk {{ opacity: 1; transform: none; }}
.tb-w1, .tb-all .tb-wk {{ transition: opacity .5s ease, transform .35s var(--ease) var(--d); }}
.tb-avg .tb-w1, .tb-avg .tb-wk {{ opacity: .3; transition-delay: 0s; }}
.tb-mean {{ opacity: 0; transition: opacity .6s ease; }}
.tb-avg .tb-mean {{ opacity: 1; }}''')

# =====================================================================================
# 2. conclusion of the CEO-Bench part
# =====================================================================================
slides.append('''  <section class="slide p2" data-name="CEO-Bench takeaway">
    <div class="tb-concl">
      <div class="tb-lead">As models get better, <b>CEO-Bench</b> elicits<br><b>interesting differences in behavior</b> that are…</div>
      <div class="tb-two">
        <div class="tb-col rise" data-in="1"><b>Not captured</b><span>by other benchmarks</span></div>
        <div class="tb-col rise new" data-in="2"><b>Crucial in real life</b><span>when we put models to work</span></div>
      </div>
      <div class="tb-pill rise" data-in="3">especially for <b>complex, long-horizon decisions</b></div>
    </div>
    <div class="note" data-at="0">So, to wrap up CEO-Bench: as models get better, CEO-Bench elicits interesting differences in how they behave…</div>
    <div class="note" data-at="1">…differences that other benchmarks don't capture…</div>
    <div class="note" data-at="2">…and that are crucial when we use these models in real life…</div>
    <div class="note" data-at="3">…especially for complex, long-horizon decision-making.</div>
  </section>''')
css.append('''
.tb-concl { position: absolute; left: 120px; right: 120px; top: 130px; display: flex; flex-direction: column; align-items: center; text-align: center; }
.tb-lead { font-size: 44px; font-weight: 500; letter-spacing: -.02em; line-height: 1.3; max-width: 1240px; }
.tb-lead b { font-weight: 700; }
.tb-two { display: flex; gap: 60px; margin-top: 60px; }
.tb-col { width: 520px; border: 3px solid #c9ced4; border-radius: 22px; padding: 28px 30px; display: flex; flex-direction: column; gap: 10px; align-items: center; }
.tb-col .e { font-size: 64px; line-height: 1; }
.tb-col b { font-size: 36px; font-weight: 600; }
.tb-col span { font-size: 28px; line-height: 1.3; }
.tb-col.new { border-color: var(--c-green); background: var(--c-green-soft); }
.tb-pill { margin-top: 60px; font-size: 34px; padding: 14px 34px; border-radius: 999px; background: #f3f5f7; }
.tb-pill b { font-weight: 700; }''')

(OUT / 'sections.html').write_text('\n'.join(slides) + '\n')
(OUT / 'css.css').write_text('\n'.join(css).lstrip('\n') + '\n')
print('wrote', OUT, 'slides:', len(slides))
