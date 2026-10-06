"""Part 4a: one slide introducing the 'practice' toy game, framed as personal coaching, animated step by step.

Numbers come from data.json (see extract.py: the game's real engine, played noise-free). The models played the game
with abstract skills A-E; on the slide they get illustrative names (same thresholds and multipliers):
C (threshold 2, x1) Cooking, E (8, x2) Running, A (18, x4) Guitar, D (28, x7) Spanish, B (34, x20) Coding.
Writes out/sections.html and out/css.css; src/merge_parts.py splices them into the deck. Classes are prefixed ta-.

Steps (section classes ta-w1..ta-w4, ta-end, ta-rules drive CSS transitions/animations):
 0 five skills as gauges, each with a threshold line and its reward multiplier (x1 ... x20)
 1-4 weeks 1-4 of one example plan: 10 hour-tokens fly from the tray to the skills, levels rise; for every skill above
     its threshold a chip "(level - threshold) x multiplier" appears and its product flies into the reward pool
 5 arrows: low upfront cost, low reward (Cooking side) vs high upfront cost, high reward (Coding side)
 6 extra rules: forgetting, randomness, diminishing returns on one skill each week
Displayed payouts use the excess rounded to 0.1 (so chip arithmetic and the pool add up on screen); the engine's
unrounded values differ by < 0.1 and are in data.json.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / 'data.json'))
SPEC = D['spec']
NAMES = {'C': ('🍳', 'Cooking'), 'E': ('🏃', 'Running'), 'A': ('🎸', 'Guitar'), 'D': ('🗣️', 'Spanish'), 'B': ('💻', 'Coding')}
COL = ['#8c959f'] * 4 + ['#8554b2']                # coding purple, the rest neutral grey (as in part 4b)
GOLD, GOLD_SOFT = '#f0b429', '#fdf1d3'              # reward: excess above threshold, payout chips, pool
RUNS, WEEKS, UNITS = D['runs'], D['kw']['rounds'], D['kw']['units']
EX = RUNS['example']
NW = len(EX)
assert [s['id'] for s in SPEC] == list(NAMES)
assert all(sum(w['alloc'].values()) == UNITS for w in EX)

# ---- geometry (stage px) ----
CX = [232 + 240 * i for i in range(5)]
GW, GT, GB, MAXL = 110, 204, 464, 36                # gauge width/top/bottom, level shown at full height
PX = (GB - GT) / MAXL
NAME_Y = 480
TOK, TGAP, TOK_Y = 26, 34, 560                      # hour tokens under the skills
BOX_T, BOX_H = 616, 160                             # bottom row: tray (left) and reward pool (right)
TRAY_L, TRAY_W, POOL_L, POOL_W = 330, 520, 930, 340
TRAY_CX, TRAY_TOK_Y = TRAY_L + TRAY_W / 2, BOX_T + 110
POOL_CX, POOL_CY = POOL_L + POOL_W / 2, BOX_T + 100
T_TOK, T_FILL, T_CHIP, T_FLY, T_POOL = .35, 1.2, 2.1, 2.6, 3.5   # timeline within a week step (s)
S_END, S_RULES = NW + 1, NW + 2


def tint(c, a):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % tuple(round(255 - (255 - v) * a) for v in (r, g, b))


def f1(x): return f'{x:.1f}'


def fmt(x): return f'{x:,.0f}'


# displayed payouts: excess rounded to 0.1, times the multiplier; the pool is the running sum of what is shown
pays, pool = [], []
acc = 0.0
for w in EX:
    row = []
    for i, s in enumerate(SPEC):
        if w['pay'][s['id']] > 0:
            e = round(w['level'][s['id']] - s['bar'], 1)
            row.append((i, e, round(e * s['rate'], 1)))
            acc += e * s['rate']
    pays.append(row)
    pool.append(round(acc, 1))

css = [f'''
.ta-rate {{ position: absolute; top: {GT - 54}px; width: 200px; transform: translateX(-50%); text-align: center;
  font-size: 30px; font-weight: 700; white-space: nowrap; }}
.ta-g {{ position: absolute; top: {GT}px; width: {GW}px; height: {GB - GT}px; border-radius: 14px; overflow: hidden;
  background: var(--tb); border: 2px solid var(--tl); box-sizing: border-box; }}
.ta-fill {{ position: absolute; left: 0; right: 0; bottom: 0; height: 0; overflow: hidden; background: var(--c);
  transition: height .8s var(--ease) {T_FILL}s; }}
.ta-ex {{ position: absolute; left: 0; right: 0; height: 600px; background: {GOLD}; }}
.ta-bar {{ position: absolute; width: {GW + 24}px; border-top: 4px dashed var(--ln); }}
.ta-lab {{ position: absolute; font-size: 22px; transform: translateY(-50%); white-space: nowrap; }}
.ta-name {{ position: absolute; top: {NAME_Y}px; width: 220px; transform: translateX(-50%); text-align: center;
  font-size: 26px; font-weight: 600; white-space: nowrap; }}
.ta-name i {{ font-style: normal; font-size: 30px; margin-right: 6px; }}
.ta-sk {{ transition: opacity .5s ease; }}
.ta-end .ta-dim {{ opacity: .22; }}
.ta-tok {{ position: absolute; width: {TOK}px; height: {TOK}px; margin: -{TOK // 2}px 0 0 -{TOK // 2}px; border-radius: 50%;
  background: var(--ink); left: var(--x1); top: var(--y1); opacity: 0; transition: opacity .3s ease; }}
@keyframes ta-mv {{ from {{ left: var(--x1); top: var(--y1); }} to {{ left: var(--x2); top: var(--y2); }} }}
@keyframes ta-pay {{ 0% {{ left: var(--x1); top: var(--y1); opacity: 0; }} 15% {{ left: var(--x1); top: var(--y1); opacity: 1; }}
  85% {{ opacity: 1; }} 100% {{ left: var(--x2); top: var(--y2); opacity: 0; }} }}
.ta-box {{ position: absolute; top: {BOX_T}px; height: {BOX_H}px; border-radius: 20px; opacity: 0; transition: opacity .4s ease; }}
.ta-w1 .ta-box {{ opacity: 1; }}
.ta-end .ta-box {{ opacity: 0; }}
.ta-tray {{ left: {TRAY_L}px; width: {TRAY_W}px; background: #f3f5f7; }}
.ta-pool {{ left: {POOL_L}px; width: {POOL_W}px; background: {GOLD_SOFT}; }}
.ta-tray i {{ position: absolute; width: {TOK}px; height: {TOK}px; box-sizing: border-box; border-radius: 50%;
  border: 2px dashed #afb8c1; }}
.ta-box .t {{ position: absolute; left: 0; right: 0; top: 18px; text-align: center; font-size: 28px; font-weight: 600; }}
.ta-box .v {{ position: absolute; left: 0; right: 0; top: 64px; text-align: center; font-size: 54px; font-weight: 700;
  font-variant-numeric: tabular-nums; }}
.ta-sw {{ opacity: 0; transition: opacity .25s ease; }}
.ta-chip {{ position: absolute; transform: translateY(-50%); font-size: 22px; font-weight: 700; white-space: nowrap;
  padding: 3px 9px; border-radius: 999px; background: {GOLD_SOFT}; border: 2px solid {GOLD}; opacity: 0;
  transition: opacity .3s ease; }}
.ta-fly {{ position: absolute; transform: translate(-50%, -50%); font-size: 24px; font-weight: 700; white-space: nowrap;
  padding: 3px 10px; border-radius: 999px; background: {GOLD}; opacity: 0; }}
.ta-arw {{ position: absolute; left: 0; top: 0; overflow: visible; opacity: 0; transition: opacity .5s ease; }}
.ta-al {{ position: absolute; top: 640px; font-size: 30px; font-weight: 600; white-space: nowrap; opacity: 0;
  transform: translateY(10px); transition: opacity .5s ease, transform .5s var(--ease); }}
.ta-end .ta-arw {{ opacity: 1; transition-delay: .3s; }}
.ta-end .ta-al {{ opacity: 1; transform: none; transition-delay: .5s; }}
.ta-rules {{ position: absolute; left: 0; right: 0; top: 730px; display: flex; justify-content: center; align-items: center;
  gap: 18px; }}
.ta-rules .h {{ font-size: 28px; font-weight: 600; margin-right: 6px; }}
.ta-rules span.p {{ font-size: 28px; font-weight: 600; padding: 10px 26px; border-radius: 999px; background: var(--mark); }}
''']

body = []
# ---- gauges: reward multiplier, threshold line, name ----
for i, s in enumerate(SPEC):
    c, sid = COL[i], s['id']
    emo, name = NAMES[sid]
    dim = ' ta-dim' if 0 < i < 4 else ''
    st = f'--ln:{"#57606a" if i < 4 else c};--c:{c};--tb:{tint(c, .08)};--tl:{tint(c, .35)}'
    body.append(f'<div class="ta-sk{dim}" style="{st}">'
                f'<div class="ta-rate" style="left:{CX[i]}px">×{s["rate"]}</div>'
                f'<div class="ta-g" style="left:{CX[i] - GW // 2}px"><div class="ta-fill ta-f{i}">'
                f'<div class="ta-ex" style="bottom:{s["bar"] * PX - 2:.1f}px"></div></div></div>'
                f'<div class="ta-bar" style="left:{CX[i] - GW // 2 - 12}px;top:{GB - s["bar"] * PX - 2:.1f}px"></div>'
                f'<div class="ta-name" style="left:{CX[i]}px"><i>{emo}</i>{name}</div></div>')
LAB_X = CX[-1] + GW // 2 + 24
body.append(f'<div class="ta-lab" style="left:{LAB_X}px;top:{GB - SPEC[-1]["bar"] * PX:.1f}px">threshold</div>')
body.append(f'<div class="ta-lab" style="left:{LAB_X}px;top:{GT - 36}px">reward multiplier</div>')

# ---- bottom row: tray of 10 hours (week label, empty slots) and reward pool ----
tray = [(TRAY_CX + (k - (UNITS - 1) / 2) * 44, TRAY_TOK_Y) for k in range(UNITS)]
wk = ''.join(f'<span class="ta-sw ta-wl{w}">Week {w} of {WEEKS}</span>' for w in range(1, NW + 1))
pv = ''.join(f'<span class="ta-sw ta-pv{w}">{f1(v)}</span>' for w, v in enumerate([0.0] + pool))
rings = ''.join(f'<i style="left:{x - TRAY_L - TOK // 2:.0f}px;top:{y - BOX_T - TOK // 2:.0f}px"></i>' for x, y in tray)
body.append(f'<div class="ta-box ta-tray"><div class="t ta-stack">{wk}</div>{rings}</div>')
body.append(f'<div class="ta-box ta-pool"><div class="t">Reward pool</div><div class="v ta-stack">{pv}</div></div>')
css.append(f'.ta-stack {{ display: grid; }} .ta-stack > span {{ grid-area: 1 / 1; }} .ta-pool .ta-sw {{ background: {GOLD_SOFT}; }}')
# pool values stack (opaque background), so the value of week w simply covers week w-1 when its payouts land
css.append('.ta-pv0 { opacity: 1; }')
for w in range(1, NW + 1):
    css.append(f'.ta-w{w} .ta-wl{w} {{ opacity: 1; }} .ta-w{w} .ta-pv{w} {{ opacity: 1; transition-delay: {T_POOL}s; }}')
    nxt = f'.ta-w{w + 1}' if w < NW else '.ta-end'
    css.append(f'.ta-w{w} .ta-wl{w - 1}, {nxt} .ta-wl{w} {{ opacity: 0; transition-delay: 0s; }}')

# ---- per week: tokens tray -> skills, level heights, payout chips + flying products ----
for w, wd in enumerate(EX, 1):
    nxt = f'.ta-w{w + 1}' if w < NW else '.ta-end'
    alloc = [wd['alloc'][s['id']] for s in SPEC]
    dst = [(CX[i] + (k - (n - 1) / 2) * TGAP, TOK_Y) for i, n in enumerate(alloc) for k in range(n)]
    for j in range(UNITS):
        v = {'x1': tray[j][0], 'y1': tray[j][1], 'x2': dst[j][0], 'y2': dst[j][1]}
        body.append(f'<div class="ta-tok ta-k{w}" style="' + ';'.join(f'--{k}:{x:.0f}px' for k, x in v.items()) +
                    f';--d:{T_TOK + j * .05:.2f}s"></div>')
    css.append(f'.ta-w{w} .ta-k{w} {{ opacity: 1; animation: ta-mv .7s var(--ease) var(--d) both; }}'
               f' {nxt} .ta-k{w} {{ opacity: 0; }}')
    css.append(' '.join(f'.ta-w{w} .ta-f{i} {{ height: {wd["level"][s["id"]] * PX:.1f}px; }}' for i, s in enumerate(SPEC)))
    for i, e, prod in pays[w - 1]:
        s = SPEC[i]
        y = GB - (s['bar'] + e / 2) * PX
        x = CX[i] + GW // 2 + 10
        body.append(f'<div class="ta-chip ta-c{w}" style="left:{x}px;top:{y:.0f}px">{f1(e)} × {s["rate"]}</div>')
        body.append(f'<div class="ta-fly ta-p{w}" style="--x1:{x + 48}px;--y1:{y + 40:.0f}px;--x2:{POOL_CX:.0f}px;--y2:{POOL_CY:.0f}px">+{f1(prod)}</div>')
    css.append(f'.ta-w{w} .ta-c{w} {{ opacity: 1; transition-delay: {T_CHIP}s; }} {nxt} .ta-c{w} {{ opacity: 0; transition-delay: 0s; }}'
               f' .ta-w{w} .ta-p{w} {{ animation: ta-pay 1s ease-in-out {T_FLY}s both; }} {nxt} .ta-p{w} {{ display: none; }}')

# ---- step 5: arrows to both ends; step 6: extra rules ----
AY, L, R = 618, CX[0] - GW // 2, CX[-1] + GW // 2
body.append(f'<svg class="ta-arw" width="1600" height="900" viewBox="0 0 1600 900">'
            f'<path d="M{L + 6} {AY}H{R - 6}" stroke="#1f2328" stroke-width="4" fill="none"/>'
            f'<path d="M{L + 24} {AY - 13}L{L} {AY}L{L + 24} {AY + 13}" stroke="#1f2328" stroke-width="4" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="M{R - 24} {AY - 13}L{R} {AY}L{R - 24} {AY + 13}" stroke="#1f2328" stroke-width="4" fill="none" stroke-linejoin="round" stroke-linecap="round"/></svg>')
body.append(f'<div class="ta-al" style="left:{L}px">Low upfront cost, low reward</div>')
body.append(f'<div class="ta-al" style="right:{1600 - R}px">High upfront cost, high reward</div>')
body.append(f'<div class="ta-rules rise" data-in="{S_RULES}"><span class="h">Plus:</span><span class="p">Forgetting</span>'
            '<span class="p">Randomness</span><span class="p">Diminishing returns on one skill each week</span></div>')

E_TOT, H_TOT = RUNS['easy'][-1]['total'], RUNS['hard'][-1]['total']
F_HARD = next(k + 1 for k, x in enumerate(RUNS['hard']) if x['pay'][SPEC[-1]['id']] > 0)
MN, G = D['mean_score_noisy'], D['grow']
lv = lambda w, sid: f1(EX[w]['level'][sid])
notes = [
    "So let's try a toy test outside business. Think of it as personal coaching: you want to get good at five skills. "
    "Each skill has a threshold, the dashed line, and a reward multiplier on top. Cooking has a low threshold but a multiplier of 1; "
    "coding has a high threshold but a multiplier of 20. "
    "To be clear, the models played exactly this game with abstract skills labelled A to E, with the same thresholds and multipliers. "
    "The names are just illustrative.",
    f"Every week you get {UNITS} hours of practice to split across the skills, for {WEEKS} weeks. Here is one example plan. "
    f"Week 1: 4 hours of cooking, 3 of running, and 1 each on the rest. The levels go up. "
    f"Cooking is now at {lv(0, 'C')}, above its threshold of 2, so the part above the threshold, {f1(pays[0][0][1])}, "
    f"is multiplied by its reward multiplier, 1, and goes into the reward pool.",
    f"Week 2: a slightly different split. Cooking is further above its threshold, so it pays more: "
    f"{f1(pays[1][0][1])} times 1. The pool is at {f1(pool[1])}.",
    f"Week 3: running crosses its threshold of 8, so now two skills pay: {f1(pays[2][0][1])} times 1 for cooking, "
    f"and {f1(pays[2][1][1])} times 2 for running.",
    f"Week 4: the pool is at {f1(pool[3])}. Coding has had some hours every week, but it is at {lv(3, 'B')}, "
    f"still far below its threshold of 34, so it has paid nothing yet.",
    "That is the trade-off. On the left, cooking: low upfront cost, but low reward. On the right, coding: a high upfront cost, "
    f"but a high reward. For example, putting every hour into cooking pays from week 1, but only about {fmt(E_TOT)} points over "
    f"{WEEKS} weeks. Putting every hour into coding pays nothing until week {F_HARD}, and then about {fmt(H_TOT)} points in total. "
    f"(Game engine without noise; with its noise the averages are {fmt(MN['easy'])} and {fmt(MN['hard'])}. "
    f"Neither extreme is the best plan; 2 hours on every skill gets about {fmt(RUNS['spread'][-1]['total'])}.) "
    "It is the same question as in the business game: a small payoff now, or a bigger one later that costs more upfront.",
    "There are a few additional rules. Forgetting: every skill loses 3 percent of its level each week. "
    "Randomness: each week's gain varies by up to 20 percent. And diminishing returns: within a week, each extra hour on the "
    f"same skill helps less; 1 hour gives plus {f1(G['1'])}, but 4 hours only plus {f1(G['4'])}. "
    "The models get the rules in words, plus each skill's threshold and multiplier; they never see the formulas, "
    "so they have to learn them from their weekly results.",
]
body += [f'<div class="note" data-at="{i}">{n}</div>' for i, n in enumerate(notes)]

classes = {f'ta-w{w}': w for w in range(1, NW + 1)}
classes.update({'ta-end': S_END})
sec = (f'''  <section class="slide p2" data-name="Toy test: practice" data-classes='{json.dumps(classes)}' data-marks='{{"Toy test":0,"Weeks":1,"Now vs later":{S_END}}}'>
    <div class="c-kicker">A toy test outside business</div>
    <div class="c-h">Personal coaching: where should 10 practice hours a week go?</div>
''' + '\n'.join('    ' + b for b in body) + '\n  </section>\n')
(HERE / 'out').mkdir(exist_ok=True)
(HERE / 'out' / 'sections.html').write_text(sec)
(HERE / 'out' / 'css.css').write_text('\n'.join(css).strip('\n') + '\n')
print('pays', pays, 'pool', pool, '| easy', round(E_TOT), '| hard', round(H_TOT), 'from week', F_HARD)
