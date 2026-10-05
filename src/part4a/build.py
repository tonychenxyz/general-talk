"""Part 4a: one slide introducing the 'practice' toy game, framed as personal coaching, animated step by step.

Numbers come from data.json (see extract.py: the game's real engine, played noise-free). The models played the game
with abstract skills A-E; on the slide they get illustrative names (same thresholds and rates):
C (bar 2, x1) Cooking, E (8, x2) Running, A (18, x4) Guitar, D (28, x7) Spanish, B (34, x20) Coding.
Writes out/sections.html and out/css.css; src/merge_parts.py splices them into the deck. Classes are prefixed ta-.

Steps (section classes ta-p1..ta-p3 drive CSS transitions):
 0 five skills as gauges, each with a threshold line and its reward per point (x1 ... x20)
 1 a tray of 10 hour-tokens per week
 2 one example week (4/3/2/1/0 h): tokens drop under the skills, levels rise with diminishing returns
 3 all hours on cooking vs all on coding over 20 weeks (weekly points, first paying week, total) + takeaway
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / 'data.json'))
SPEC = D['spec']
NAMES = {'C': ('🍳', 'Cooking'), 'E': ('🏃', 'Running'), 'A': ('🎸', 'Guitar'), 'D': ('🗣️', 'Spanish'), 'B': ('💻', 'Coding')}
COL = ['#8c959f'] * 4 + ['#8554b2']                # coding purple, the rest neutral grey (as in part 4b)
RUNS, WEEKS, UNITS = D['runs'], D['kw']['rounds'], D['kw']['units']
WEEK = RUNS['week'][0]
assert [s['id'] for s in SPEC] == list(NAMES)

# ---- geometry (stage px) ----
CX = [232 + 240 * i for i in range(5)]
GW, GT, GB, MAXL = 110, 215, 495, 40                # gauge width/top/bottom, level shown at full height
PX = (GB - GT) / MAXL
TOK, TGAP = 30, 38
NAME_Y, TOK_Y = 512, 590                            # skill name row, token row in step 2
TRAY_Y = 618                                        # tray top (step 1)


def tint(c, a):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % tuple(round(255 - (255 - v) * a) for v in (r, g, b))


def fmt(x): return f'{x:,.0f}'


css = [f'''
.ta-rate {{ position: absolute; top: {GT - 56}px; width: 200px; transform: translateX(-50%); text-align: center;
  font-size: 30px; font-weight: 700; white-space: nowrap; }}
.ta-g {{ position: absolute; top: {GT}px; width: {GW}px; height: {GB - GT}px; border-radius: 14px; overflow: hidden;
  background: var(--tb); border: 2px solid var(--tl); box-sizing: border-box; }}
.ta-fill {{ position: absolute; left: 0; right: 0; bottom: 0; height: 0; background: var(--c);
  transition: height .5s var(--ease); }}
.ta-bar {{ position: absolute; width: {GW + 24}px; border-top: 4px dashed var(--ln); }}
.ta-thr {{ position: absolute; font-size: 22px; transform: translateY(-50%); white-space: nowrap; }}
.ta-rw {{ top: {GT - 38}px; }}
.ta-name {{ position: absolute; top: {NAME_Y}px; width: 220px; transform: translateX(-50%); text-align: center;
  font-size: 26px; font-weight: 600; white-space: nowrap; }}
.ta-name i {{ font-style: normal; font-size: 30px; margin-right: 6px; }}
.ta-sk {{ transition: opacity .5s ease; }}
.ta-p3 .ta-dim {{ opacity: .22; }}
.ta-gain {{ position: absolute; font-size: 24px; font-weight: 700; transform: translateY(-50%); white-space: nowrap;
  opacity: 0; transition: opacity .3s ease; }}
.ta-p2 .ta-gain {{ opacity: 1; transition: opacity .5s ease 1.9s; }}
.ta-p3 .ta-gain {{ opacity: 0; transition: opacity .3s ease; }}
.ta-tray {{ position: absolute; left: 540px; width: 520px; top: {TRAY_Y}px; height: 150px; border-radius: 20px;
  background: #f3f5f7; transition: opacity .5s ease; }}
.ta-tray .t {{ position: absolute; left: 0; right: 0; top: 22px; text-align: center; font-size: 28px; font-weight: 600; }}
.ta-p2 .ta-tray {{ opacity: 0; transition: opacity .6s ease .9s; }}
.ta-tok {{ position: absolute; width: {TOK}px; height: {TOK}px; margin: -{TOK // 2}px 0 0 -{TOK // 2}px; border-radius: 50%;
  background: var(--ink); left: var(--x1); top: var(--y1); opacity: 0;
  transition: left .8s var(--ease) var(--d), top .8s var(--ease) var(--d), opacity .4s ease; }}
.ta-p1 .ta-tok {{ opacity: 1; }}
.ta-p2 .ta-tok {{ left: var(--x2); top: var(--y2); }}
.ta-p3 .ta-tok {{ opacity: 0; transition: opacity .3s ease; }}
.ta-cap {{ position: absolute; left: 0; right: 0; top: 680px; text-align: center; font-size: 30px; font-weight: 600;
  opacity: 0; transition: opacity .3s ease; }}
.ta-p2 .ta-cap {{ opacity: 1; transition: opacity .6s ease 2.4s; }}
.ta-p3 .ta-cap {{ opacity: 0; transition: opacity .3s ease; }}
.ta-card {{ position: absolute; top: 588px; width: 560px; height: 172px; border-radius: 20px; background: var(--tb);
  box-sizing: border-box; padding: 16px 30px; opacity: 0; transform: translateY(14px);
  transition: opacity .5s ease, transform .5s var(--ease); }}
.ta-p3 .ta-card {{ opacity: 1; transform: none; transition-delay: .3s; }}
.ta-card .h {{ font-size: 26px; font-weight: 600; white-space: nowrap; }}
.ta-card .h i {{ font-style: normal; font-size: 30px; margin-right: 6px; }}
.ta-card svg {{ display: block; margin: 8px 0 6px; overflow: visible; }}
.ta-card .s {{ font-size: 24px; white-space: nowrap; display: flex; justify-content: space-between; }}
.ta-card .s b {{ font-weight: 700; }}
.ta-wb {{ transform: scaleY(0); transform-box: fill-box; transform-origin: bottom; }}
.ta-p3 .ta-wb {{ transform: scaleY(1); transition: transform .25s ease-out var(--d); }}
.ta-take {{ position: absolute; left: 0; right: 0; top: 782px; text-align: center; }}
.ta-take span {{ display: inline-block; font-size: 32px; font-weight: 600; padding: 12px 34px; border-radius: 999px; background: var(--mark); }}
''']

body = []
# ---- gauges: reward per point, threshold line, name ----
for i, s in enumerate(SPEC):
    c, sid = COL[i], s['id']
    emo, name = NAMES[sid]
    dim = ' ta-dim' if 0 < i < 4 else ''
    st = f'--ln:{"#57606a" if i < 4 else c};--c:{c};--tb:{tint(c, .08)};--tl:{tint(c, .35)}'
    gain = (f'<div class="ta-gain ta-gn{i}" style="left:{CX[i] + GW // 2 + 18}px">+{WEEK["grown"][sid]:.1f}</div>'
            if WEEK['grown'][sid] > 0 else '')
    body.append(f'<div class="ta-sk{dim}" style="{st}">'
                f'<div class="ta-rate" style="left:{CX[i]}px">×{s["rate"]}</div>'
                f'<div class="ta-g" style="left:{CX[i] - GW // 2}px"><div class="ta-fill ta-f{i}"></div></div>'
                f'<div class="ta-bar" style="left:{CX[i] - GW // 2 - 12}px;top:{GB - s["bar"] * PX - 2:.1f}px"></div>'
                + gain +
                f'<div class="ta-name" style="left:{CX[i]}px"><i>{emo}</i>{name}</div></div>')
    g = WEEK['grown'][sid]
    css.append(f'.ta-p2 .ta-f{i} {{ height: {g * PX:.1f}px; transition: height 1s var(--ease) 1.1s; }}'
               f' .ta-gn{i} {{ top: {GB - g * PX:.1f}px; }}')
thr_y = GB - SPEC[-1]['bar'] * PX
body.append(f'<div class="ta-thr" style="left:{CX[-1] + GW // 2 + 24}px;top:{thr_y:.1f}px">threshold</div>')
body.append(f'<div class="ta-thr ta-rw" style="left:{CX[-1] + GW // 2 + 24}px">reward per level</div>')

# ---- hour tokens: tray (step 1) -> under the skills (step 2) ----
alloc = [4, 3, 2, 1, 0]                              # must match extract.py's 'week' strategy
assert all((a > 0) == (WEEK['grown'][s['id']] > 0) for a, s in zip(alloc, SPEC))
assert all(abs(WEEK['grown'][s['id']] - D['grow'][str(a)]) < 1e-6 for a, s in zip(alloc, SPEC))
pos1 = [(800 + (k - 4.5) * 46, TRAY_Y + 95) for k in range(UNITS)]
pos2 = [(CX[i] + (k - (n - 1) / 2) * TGAP, TOK_Y) for i, n in enumerate(alloc) for k in range(n)]
body.append(f'<div class="ta-tray" data-in="1"><div class="t">{UNITS} practice hours a week</div></div>')
for j in range(UNITS):
    v = {'x1': pos1[j][0], 'y1': pos1[j][1], 'x2': pos2[j][0], 'y2': pos2[j][1]}
    body.append('<div class="ta-tok" style="' + ';'.join(f'--{k}:{x:.0f}px' for k, x in v.items()) + f';--d:{j * .05:.2f}s"></div>')
body.append('<div class="ta-cap">Each extra hour on the same skill helps less</div>')

# ---- step 3: all hours on cooking vs all on coding, weekly points over 20 weeks ----
SW, SH = 500, 64
pmax = max(max(w['pay'][SPEC[0]['id']] for w in RUNS['easy']), max(w['pay'][SPEC[-1]['id']] for w in RUNS['hard']))
bw = SW / WEEKS


def card(kind, gi, x):
    sid, c = SPEC[gi]['id'], COL[gi]
    emo, name = NAMES[sid]
    w = RUNS[kind]
    first = next(k + 1 for k, x_ in enumerate(w) if x_['pay'][sid] > 0)
    bars = ''.join(f'<rect class="ta-wb" x="{k * bw + 3:.1f}" y="{SH - max(2, x_["pay"][sid] / pmax * SH):.1f}" width="{bw - 6:.1f}"'
                   f' height="{max(2, x_["pay"][sid] / pmax * SH):.1f}" fill="{c if x_["pay"][sid] > 0 else "#d3d7dc"}" style="--d:{.6 + k * .08:.2f}s"/>'
                   for k, x_ in enumerate(w))
    return (f'<div class="ta-card" style="left:{x}px;--c:{c};--tb:{tint(c, .09)}">'
            f'<div class="h"><i>{emo}</i>All hours on {name}</div>'
            f'<svg width="{SW}" height="{SH}" viewBox="0 0 {SW} {SH}">{bars}</svg>'
            f'<div class="s"><span>first points: <b>week {first}</b></span><span>total: <b>{fmt(w[-1]["total"])}</b> points</span></div></div>'), first


c_easy, f_easy = card('easy', 0, 190)
c_hard, f_hard = card('hard', 4, 850)
body += [c_easy, c_hard]
body.append('<div class="ta-take" data-in="3"><span>Small payoff now, or big payoff later?</span></div>')

E_TOT, H_TOT = RUNS['easy'][-1]['total'], RUNS['hard'][-1]['total']
MN = D['mean_score_noisy']
g = {s['id']: f"{WEEK['grown'][s['id']]:.1f}" for s in SPEC}
notes = [
    "So let's try a toy test outside business. Think of it as personal coaching: you want to get good at five skills. "
    "Each skill has a threshold, the dashed line, and a reward rate. Cooking is easy: the threshold is low but it only pays 1 point per level above it. "
    "Coding is hard: the threshold is high, but every level above it pays 20 points, every week. "
    "To be clear, the models played exactly this game with abstract skills labelled A to E, with the same thresholds and rates. "
    "The names are just illustrative.",
    f"Every week you have {UNITS} hours of practice to split across the skills, for {WEEKS} weeks.",
    f"Here is one example week: 4 hours of cooking, 3 of running, 2 of guitar, 1 of Spanish. Practice raises a skill's level, "
    f"but extra hours on the same skill within a week help less and less, because of fatigue: 4 hours of cooking give plus {g['C']}, "
    f"while a single hour of Spanish already gives plus {g['D']}. Fatigue resets every week, learning carries over, and you also forget a little between weeks. "
    "Every week, each skill above its threshold earns rate times how far above the threshold it is; after this week only cooking pays.",
    f"Now the trade-off. Put every hour into cooking and you earn points from week {f_easy}, but only a little: about {fmt(E_TOT)} points over {WEEKS} weeks. "
    f"Put every hour into coding and you earn nothing at all for {f_hard - 1} weeks, it only clears its threshold in week {f_hard}, "
    f"but then it pays a lot: about {fmt(H_TOT)} points. "
    f"(These are the game's own engine, without noise; with its random noise the averages are {fmt(MN['easy'])} and {fmt(MN['hard'])}. "
    f"Neither extreme is the best plan; for example 2 hours on every skill gets about {fmt(RUNS['spread'][-1]['total'])}.) "
    "So it is the same question as in the business game: a small payoff now, or a bigger one later that costs more upfront. "
    "The models get the rules in words, as I just described them, plus each skill's threshold and reward rate; they never see the practice or forgetting formulas, so they have to learn those from their weekly results.",
]
body += [f'<div class="note" data-at="{i}">{n}</div>' for i, n in enumerate(notes)]

sec = (f'''  <section class="slide p2" data-name="Toy test: practice" data-classes='{{"ta-p1":1,"ta-p2":2,"ta-p3":3}}' data-marks='{{"Toy test":0,"Now vs later":3}}'>
    <div class="c-kicker">A toy test, outside business</div>
    <div class="c-h">Personal coaching: where should 10 practice hours a week go?</div>
''' + '\n'.join('    ' + b for b in body) + '\n  </section>\n')
(HERE / 'out').mkdir(exist_ok=True)
(HERE / 'out' / 'sections.html').write_text(sec)
(HERE / 'out' / 'css.css').write_text('\n'.join(css).strip('\n') + '\n')
print('easy', round(E_TOT), 'from week', f_easy, '| hard', round(H_TOT), 'from week', f_hard, '| noisy means', MN)
