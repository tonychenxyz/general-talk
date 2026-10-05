import os
import base64, json, math, re, random

B = os.path.dirname(os.path.abspath(__file__)) + '/'
# clone of tonychenxyz/ceo-bench-webpage (branch codex/latest-agent-trajectories)
WEB = os.environ.get('CEO_WEBPAGE', '/home/claude/tonychenxyz/ceo-bench-webpage') + '/assets/'
FIG = WEB + 'figures/'
OUT = B + 'part2.html'  # build output, not committed; merge.py copies it into index.html

b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
AGENT_ICON = 'data:image/png;base64,' + b64(FIG + 'assets/llm-agent-icon.png')


def scope_css(css, prefix):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        sels = []
        for s in sel.split(','):
            s = s.strip()
            if not s:
                continue
            if s in (':root', 'html', 'body'):
                sels.append(prefix)
            else:
                sels.append(prefix + ' ' + s)
        out.append(', '.join(dict.fromkeys(sels)) + ' {' + body.strip() + '}')
    return '\n'.join(out)


def style_and_body(path):
    s = open(path).read()
    css = re.search(r'<style>(.*?)</style>', s, re.S).group(1)
    body = re.search(r'<body[^>]*>(.*?)(<script|</body>)', s, re.S).group(1)
    return css, body

# ---------------- agent complexity figure ----------------
ac_css, ac_body = style_and_body(FIG + 'agent-complexity.html')
ac_css = scope_css(ac_css, '.c-acwrap')
ac_body = ac_body.replace('src="assets/llm-agent-icon.png"', f'src="{AGENT_ICON}"')
# symbol ids must be unique-ish in the whole deck
ac_body = ac_body.replace('id="icon-', 'id="c-icon-').replace('href="#icon-', 'href="#c-icon-')

# ---------------- teaser ----------------
tz_css, tz_body = style_and_body(FIG + 'teaser.html')
tz_css = scope_css(tz_css, '.c-tz')
arrows = json.load(open(B + 'teaser-arrows.json'))
tz_body = tz_body.replace('<svg id="leftArrowSvg" preserveAspectRatio="none"></svg>', arrows['svg'])
tz_body = tz_body.replace('src="assets/llm-agent-icon.png"', f'src="{AGENT_ICON}"')
tz_body = tz_body.replace('<div class="down-arrow rotate-right">', f'<div class="down-arrow rotate-right" style="top:{arrows["top"]}">')
def tag(body, needle, n, nth=1):
    i = -1
    for _ in range(nth):
        i = body.index(needle, i + 1)
    new = needle[:-1] + f' data-in="{n}">'
    return body[:i] + new + body[i + len(needle):]
tz_body = tag(tz_body, '<div class="tile agent">', 1)
mid = tz_body.index('<div class="middle">')
k = tz_body.index('<div class="down-arrow">', mid)
tz_body = tz_body[:k] + '<div class="down-arrow" data-in="2">' + tz_body[k + len('<div class="down-arrow">'):]
tz_body = tag(tz_body, '<div class="terminal">', 2)
tz_body = tag(tz_body, '<div class="tile neg">', 3)
tz_body = tag(tz_body, '<div class="tile db">', 4)
tz_body = tag(tz_body, '<div class="tile soc">', 5)
tz_body = tag(tz_body, '<div class="right-arrow-col">', 6)
tz_body = tag(tz_body, '<div class="tile world">', 6)
r = tz_body.index('<div class="right">')
k = tz_body.index('<div class="down-arrow">', r)
tz_body = tz_body[:k] + '<div class="down-arrow" data-in="7">' + tz_body[k + len('<div class="down-arrow">'):]
tz_body = tag(tz_body, '<div class="tile out">', 7)
tz_body = re.sub(r'<!--.*?-->', '', tz_body, flags=re.S)

# ---------------- growth heatmap ----------------
groups3 = [('🎓', 'Price-sensitive'), ('💼', 'Quality-focused'), ('💻', 'Power users')]
chans = [('📱', 'Social'), ('🔎', 'Search'), ('👔', 'LinkedIn'), ('✍️', 'Content'), ('🤝', 'Referral')]
leads = [[124.6, 124.6, 49.8, 320.4, 302.6],     # S1 price-sensitive individuals
         [149.5, 64.1, 160.2, 231.4, 135.3],     # S2 quality-focused individuals
         [106.8, 81.9, 35.6, 99.7, 170.9]]       # S3 power users
budget = [['2K', '1K', '0.5K', '1K', '1K'], ['1K', '2K', '1K', '0.5K', '1K'], ['0.5K', '2K', '1K', '1K', '0.5K']]
h = ['<div class="c-heat"><div></div>']
for e, n in chans:
    h.append(f'<div class="ch"><b>{e}</b>{n}</div>')
for gi, (e, n) in enumerate(groups3):
    h.append(f'<div class="rh"><b>{e}</b>{n}</div>')
    for ci in range(5):
        v = leads[gi][ci]
        a = 0.08 + 0.82 * (v / 320.4)
        col = '#fff' if a > .5 else 'var(--ink)'
        d = f'{(gi * 5 + ci) * 0.05:.2f}s'
        h.append(f'<div class="c-cell"><div class="bud">${budget[gi][ci]}<i>/day</i></div><div class="ht" style="--h:{a:.2f};--hc:{col};--d:{d}">{v:.0f}</div></div>')
h.append('</div>')
HEAT = ''.join(h)

# ---------------- quality chart ----------------
# Required quality vs price, exactly as SaaSBenchSimulation._compute_required_quality:
# asymmetric sigmoid from q_min (price 0) to q_max (price c_max); above c_max the customer never subscribes.
def sig(x): return 1 / (1 + math.exp(-max(-500, min(500, x))))
def q_req(c, cmax, qmin, qmax, sl=1.2, sr=2.8):
    n = c / cmax; r = qmax - qmin
    if n < .5: return qmin + r / 2 * sig(sl * (n - .25) * 10)
    return qmin + r / 2 + r / 2 * sig(sr * (n - .75) * 10)
# mean group parameters from config.py (q_min_mean, q_min_mean + q_range_mean, c_max_mean);
# steepness_left ~ Exp(1)+0.2 and steepness_right ~ Exp(2)+0.8, so their means are 1.2 and 2.8
QG = [('var(--c-green)', 'Price-sensitive', .10, .55, 50),
      ('var(--c-blue)', 'Quality-focused', .30, .85, 140),
      ('var(--c-amber)', 'Power users', .25, .80, 180)]
def qx(c): return 80 + c / 200 * 440
def qy(q): return 330 - q * 300
svg = ['<div class="c-qchart"><svg width="820" height="380" viewBox="0 0 820 380">']
svg.append('<line x1="80" y1="330" x2="520" y2="330" stroke="#1f2328" stroke-width="2"/><line x1="80" y1="330" x2="80" y2="20" stroke="#1f2328" stroke-width="2"/>')
svg.append('<text x="520" y="384" text-anchor="end" font-size="19" fill="#1f2328">price →</text>')
svg.append('<text x="0" y="0" font-size="19" fill="#1f2328" transform="translate(56 330) rotate(-90)">quality needed →</text>')
for c in (0, 50, 100, 150, 200):
    svg.append(f'<text x="{qx(c):.0f}" y="352" text-anchor="middle" font-size="14" fill="#1f2328">${c}</text>')
for i, (col, name, qmin, qmax, cmax) in enumerate(QG):
    pts = [(cc, q_req(cc, cmax, qmin, qmax)) for cc in [cmax * k / 60 for k in range(61)]]
    d = 'M' + ' L'.join(f'{qx(cc):.1f} {qy(q):.1f}' for cc, q in pts) + f' L{qx(cmax):.1f} {qy(1):.1f}'
    svg.append(f'<path class="c-draw q" pathLength="1" d="{d}" fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round" style="--d:{.2 + i * .35:.2f}s"/>')
    svg.append(f'<line x1="540" x2="580" y1="{110 + i * 44}" y2="{110 + i * 44}" stroke="{col}" stroke-width="5"/>')
    svg.append(f'<text x="592" y="{117 + i * 44}" font-size="19" font-weight="600" fill="{col}">{name}</text>')
# your product quality: drawn at step 5, rises after R&D at step 6
y0, y1 = qy(.38), qy(.66)
svg.append(f'<g class="c-ql" data-in="5" style="--dy:{y1 - y0:.0f}px"><line x1="80" x2="520" y1="{y0:.0f}" y2="{y0:.0f}" stroke="#1f2328" stroke-width="3" stroke-dasharray="10 7"/>'
           f'<text x="515" y="{y0 + 26:.0f}" text-anchor="end" font-size="18" font-weight="600" fill="#1f2328">product quality</text></g>')
svg.append('</svg></div>')
QCHART = ''.join(svg)

# ---------------- competitor chart ----------------
def cx(d): return 80 + d / 500 * 540
def cy(q): return 400 - (q - .3) / .7 * 360
ev = [(40, .44), (95, .47), (150, .50), (200, .54), (245, .59), (290, .65), (330, .70), (370, .74), (410, .79), (445, .83), (480, .87)]
exp_pts = [(0, .42)]
q_ = .42
for d_, v in ev:
    exp_pts += [(d_, q_), (d_, v)]; q_ = v
exp_pts.append((500, q_))
events = ev
dexp = 'M' + ' L'.join(f'{cx(d):.0f} {cy(v):.0f}' for d, v in exp_pts)
# agent quality: R&D bumps with lag, one stretch where it falls behind
ag = [(0, .50), (70, .51), (100, .57), (180, .59), (230, .61), (280, .60), (345, .62), (365, .76), (420, .80), (440, .87), (500, .90)]
dag = 'M' + ' L'.join(f'{cx(d):.0f} {cy(v):.0f}' for d, v in ag)
svg = ['<div class="c-qchart" style="height:430px"><svg width="820" height="430" viewBox="0 0 820 430">']
svg.append('<line x1="80" y1="400" x2="620" y2="400" stroke="#1f2328" stroke-width="2"/><line x1="80" y1="400" x2="80" y2="20" stroke="#1f2328" stroke-width="2"/>')
svg.append('<text x="620" y="428" text-anchor="end" font-size="19" fill="#1f2328">day →</text>')
svg.append('<text x="0" y="0" font-size="19" fill="#1f2328" transform="translate(56 400) rotate(-90)">quality →</text>')
svg.append(f'<path class="c-draw cc" pathLength="1" d="{dag}" fill="none" stroke="var(--c-blue)" stroke-width="5" stroke-linejoin="round" style="--d:.2s"/>')
svg.append(f'<path class="c-draw cc" pathLength="1" d="{dexp}" fill="none" stroke="var(--c-red)" stroke-width="4" stroke-linejoin="round" style="--d:.7s"/>')
svg.append(f'<text x="{cx(500) + 8:.0f}" y="{cy(ag[-1][1]) + 6:.0f}" font-size="19" font-weight="600" fill="var(--c-blue)">product quality</text>')
svg.append(f'<rect x="{cx(290):.0f}" y="{cy(.72):.0f}" width="{cx(365)-cx(290):.0f}" height="{cy(.58)-cy(.72):.0f}" rx="8" fill="var(--c-red)" opacity=".12"/><text x="{cx(327):.0f}" y="{cy(.58) + 26:.0f}" text-anchor="middle" font-size="19" fill="var(--c-red)">customers leave</text>')
svg.append(f'<text x="{cx(500) + 8:.0f}" y="{cy(exp_pts[-1][1]) + 26:.0f}" font-size="19" font-weight="600" fill="var(--c-red)">customer expectation</text>')
svg.append('</svg></div>')
COMP = ''.join(svg)

EYEOFF = '<svg class="c-eyeoff" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.7 5.1A10.4 10.4 0 0 1 12 5c6.5 0 10 7 10 7a17.7 17.7 0 0 1-2.2 3.2"/><path d="M6.6 6.6A17.4 17.4 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.4-1.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/><path d="M2 2l20 20"/></svg>'
# ---------------- (a) customer groups ----------------
G = [('g1', '🧑‍🎨', 'Freelancers', (.12, .06), (.45, .15)),
     ('g2', '💻', 'Engineers', (.55, .12), (.70, .12)),
     ('g3', '📊', 'Finance', (.82, .10), (.75, .12)),
     ('g4', '🏥', 'Healthcare', (.50, .10), (.88, .08))]
rnd = random.Random(11)
h = ['<div class="c-groups">']
for gi, (cls, e, n, pm, qm) in enumerate(G):
    h.append(f'<div class="c-g {cls}" data-in="{gi + 1}"><div class="gh"><b>{e}</b>{n}</div><div class="rows">')
    for r in range(6):
        p = min(.98, max(.05, rnd.gauss(*pm)))
        qv = min(.98, max(.05, rnd.gauss(*qm)))
        din = 5 if r == 0 else 6
        h.append(f'<div class="c-cust" data-in="{din}"><span>👤</span><span>💵</span><span class="bar"><i style="width:{p * 100:.0f}%"></i></span><span>⭐</span><span class="bar"><i style="width:{qv * 100:.0f}%"></i></span></div>')
    h.append(f'<div class="c-veil" data-in="7">{EYEOFF}</div></div></div>')
h.append('</div>')
GROUPS = ''.join(h)

SQL = ('<span class="k">SELECT</span> channel_id, group_id,\n'
       '  <span class="k">SUM</span>(leads_generated) leads,\n'
       '  <span class="k">SUM</span>(spend) spend,\n'
       '  <span class="k">ROUND</span>(1000.0*<span class="k">SUM</span>(leads_generated)\n'
       '        /<span class="k">SUM</span>(spend), 1) lp1k\n'
       '<span class="k">FROM</span> ad_channel_leads <span class="k">WHERE</span> day&gt;<span class="s">14</span>\n'
       '<span class="k">GROUP BY</span> 1,2 <span class="k">ORDER BY</span> 2,5 <span class="k">DESC</span>')

# ---------------- (b) price vs quality ----------------
W0, W1, H0, H1 = 70, 740, 20, 540
def curve_y(x): return 460 - 400 * ((x - W0) / (W1 - W0)) ** 1.8
cpath = 'M' + ' L'.join(f'{x} {curve_y(x):.1f}' for x in range(W0, W1 + 1, 10))
svg = ['<div class="c-pq"><svg width="760" height="620" viewBox="0 0 760 620">']
svg.append(f'<path class="c-reg" data-in="1" d="{cpath} L{W1} {H0} L{W0} {H0} Z" fill="#eef2e8"/>')
svg.append(f'<path class="c-reg" data-in="1" d="{cpath} L{W1} {H1} L{W0} {H1} Z" fill="#f4e9df"/>')
svg.append(f'<path class="c-draw" pathLength="1" d="{cpath}" fill="none" stroke="#0a2540" stroke-width="5" stroke-linejoin="round" style="--d:0s"/>')
svg.append(f'<line x1="{W0}" y1="{H1}" x2="{W1}" y2="{H1}" stroke="#0a2540" stroke-width="3"/><line x1="{W0}" y1="{H1}" x2="{W0}" y2="{H0}" stroke="#0a2540" stroke-width="3"/>')
svg.append('<g class="c-reg" data-in="1" transform="translate(190 150)"><circle r="22" fill="#7a8c6f"/><path d="M-9 0 L-2.5 7 L9 -6.5" stroke="#fff" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><text x="36" y="11" font-size="32" font-weight="500" fill="#1f2328">subscribe</text></g>')
svg.append('<g class="c-reg" data-in="1" transform="translate(470 460)"><circle r="22" fill="#a87158"/><path d="M-8 -8 L8 8 M8 -8 L-8 8" stroke="#fff" stroke-width="4.5" stroke-linecap="round"/><text x="36" y="11" font-size="32" font-weight="500" fill="#1f2328">reject</text></g>')
svg.append(f'<text x="{W1}" y="{H1 + 40}" text-anchor="end" font-size="24" fill="#1f2328">price →</text>')
svg.append(f'<text x="0" y="0" font-size="24" fill="#1f2328" transform="translate({W0 - 22} {H1}) rotate(-90)">quality →</text>')
svg.append('</svg></div>')
PQ = ''.join(svg)

# ---------------- (c) network ----------------
N = {'eng': (400, 330, 'var(--c-blue)', '💻', 'Engineers'),
     'fre': (920, 330, 'var(--c-green)', '🧑‍🎨', 'Freelancers'),
     'hea': (400, 700, 'var(--c-pink)', '🏥', 'Healthcare'),
     'fin': (920, 700, 'var(--c-amber)', '📊', 'Finance')}
edges = [('eng', 'fre', 6), ('fre', 'eng', 2), ('eng', 'hea', 3), ('hea', 'fin', 6), ('fin', 'eng', 2.5), ('fre', 'fin', 3),
         ('eng', 'fin', 5), ('fin', 'fre', 2), ('hea', 'eng', 2), ('fre', 'hea', 2.5), ('hea', 'fre', 1.6), ('fin', 'hea', 1.6)]
svg = ['<svg class="c-net" viewBox="0 0 1600 900">']
for i, (a, b, w) in enumerate(edges):
    x1, y1 = N[a][:2]; x2, y2 = N[b][:2]
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    bend = 60
    mx, my = (x1 + x2) / 2 + nx * bend, (y1 + y2) / 2 + ny * bend
    # shorten ends toward control point
    def towards(px, py, qx_, qy_, d):
        vx, vy = qx_ - px, qy_ - py; l = math.hypot(vx, vy); return px + vx / l * d, py + vy / l * d
    sx, sy = towards(x1, y1, mx, my, 92); ex, ey = towards(x2, y2, mx, my, 100)
    d = f'{i * .18:.2f}s'
    svg.append(f'<path class="arr" pathLength="1" d="M{sx:.0f} {sy:.0f} Q{mx:.0f} {my:.0f} {ex:.0f} {ey:.0f}" stroke-width="{w}" style="--d:{d}"/>')
    # arrow head at end, pointing along tangent (control -> end)
    tx, ty = ex - mx, ey - my; tl = math.hypot(tx, ty); tx, ty = tx / tl, ty / tl
    s = 10 + w * 1.6
    p1 = (ex - tx * s + ty * s * .6, ey - ty * s - tx * s * .6)
    p2 = (ex - tx * s - ty * s * .6, ey - ty * s + tx * s * .6)
    svg.append(f'<path class="ah" d="M{p1[0]:.0f} {p1[1]:.0f} L{ex + tx * 4:.0f} {ey + ty * 4:.0f} L{p2[0]:.0f} {p2[1]:.0f} Z" fill="#0a2540" style="--d:{d}"/>')
svg.append('</svg>')
for k_, (x, y, c, e, n) in N.items():
    svg.append(f'<div class="c-gnode" style="left:{x}px;top:{y}px;--gc:{c}">{e}</div>')
    svg.append(f'<div class="c-glab" style="left:{x}px;top:{y - 136 if y < 500 else y + 86}px;--gc:{c}">{n}</div>')
NET = ''.join(svg)

# ---------------- code figure (actual HTML) ----------------
cf_css, cf_body = style_and_body(FIG + 'gpt5.5_code_example.html')
cf_css = re.sub(r'@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', cf_css)
cf_css = scope_css(cf_css, '.c-codefig')
CODEFIG = cf_body

# ---------------- leaderboard ----------------
runs = {r['pretty']: r for r in json.load(open(WEB + 'runs.json'))}
base = [(int(l.split(',')[0]), float(l.split(',')[1])) for l in open(WEB + 'rule_based_baseline_day_vs_cash.csv').read().split()[1:]]
COL = {"Claude Opus 4.7": "#cc79a7", "Claude Sonnet 5": "#009e73", "Claude Haiku 4.5": "#0c6fa6", "GLM 5.2": "#7c2d6f", "Kimi K2.6": "#b15c00", "Claude Sonnet 4.6": "#00875a", "Claude Fable 5.1": "#702da5", "GPT-6 Sol": "#176f45", "Claude Opus 5.5": "#c44500", "GPT-6 Astra": "#0959b0",
       "Claude Fable 5": "#111827", "GPT-5.6 Sol": "#0072b2", "Claude Opus 4.8": "#d55e00", "Qwen 3.7 Max": "#8a63d2",
       "Grok 4.6": "#a16207", "Kimi K3": "#3f8f8f", "Gemini 3.5 Flash": "#2f6df6", "GPT-5.5": "#e69f00"}
PH = ['A', 'D', 'E', 'F']
added = {
    'A': ['GPT-5.5', 'Claude Opus 4.7', 'Claude Sonnet 4.6', 'Claude Haiku 4.5', 'Kimi K2.6', 'GLM 5.1', 'DeepSeek V4 Pro',
          'Gemini 3 Flash', 'Grok 4.20', 'Claude Opus 4.8', 'Claude Fable 5'],
    'D': ['GLM 5.2', 'Qwen 3.7 Max', 'Claude Sonnet 5', 'Gemini 3.5 Flash', 'GPT-5.6 Sol', 'Kimi K3', 'Grok 4.6'],
    'E': ['GPT-6 Sol', 'Claude Opus 5.5', 'GPT-6 Astra'],
    'F': ['Claude Fable 5.1'],
}
step_of = {'A': 1, 'D': 2, 'E': 3, 'F': 6}
date_lbl = {'A': 'June 2026 🗓️', 'D': 'August', 'E': 'Today 🤫', 'F': 'Today'}
X0, X1, YT, YB = 120, 1080, 140, 780
def X(d): return X0 + d / 500 * (X1 - X0)
def Y(c, top=9): return YB - (math.log10(max(c, 1e3)) - 3) / (top - 3) * (YB - YT)
models_in = {}
acc = []
for p in PH:
    acc = acc + added[p]
    models_in[p] = list(acc)
ranked = {p: sorted(models_in[p], key=lambda m: -runs[m]['final_cash']) for p in PH}
hl = {p: ranked[p][:3] for p in PH}
cls_of = lambda m: 'm-' + re.sub(r'[^a-z0-9]+', '-', m.lower()).strip('-')

lb = ['<svg class="c-plot" viewBox="0 0 1600 900"><g class="c-scale">']
for e in range(3, 11):
    y = Y(10 ** e)
    din = ' data-in="6"' if e == 10 else ''
    lb.append(f'<line{din} x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="#eef0f2" stroke-width="1" vector-effect="non-scaling-stroke"/>')
# upper bound (only after rescale)
yub = Y(2.2e9)
# lb.append(f'<line class="c-ub" data-in="6" x1="{X0}" y1="{yub:.1f}" x2="{X1}" y2="{yub:.1f}" stroke="#c9ced4" stroke-width="2" stroke-dasharray="2 6" vector-effect="non-scaling-stroke"/>')
def path_for(pts):
    pts = [(d, c) for d, c in pts if d <= 500]
    thin = [pts[0]] + [pt for i, pt in enumerate(pts[1:-1]) if i % 2 == 0] + [pts[-1]]
    return 'M' + ' L'.join(f'{X(d):.1f} {Y(c):.1f}' for d, c in thin)
lb.append(f'<path class="c-ln base" d="{path_for(base)}"/>')
for p in PH:
    for m in added[p]:
        r = runs[m]
        lb.append(f'<path class="c-ln {cls_of(m)}" data-in="{step_of[p]}" pathLength="1" d="{path_for(r["points"])}"/>')
        if r['final_cash'] <= 0:
            d_, _ = r['points'][-1]
            x, y = X(d_), Y(1)
            lb.append(f'<path class="c-x" data-in="{step_of[p]}" d="M{x - 7:.0f} {y - 7:.0f} L{x + 7:.0f} {y + 7:.0f} M{x + 7:.0f} {y - 7:.0f} L{x - 7:.0f} {y + 7:.0f}"/>')
lb.append('</g>')
lb.append(f'<line x1="{X0}" y1="{YB}" x2="{X1}" y2="{YB}" stroke="#1f2328" stroke-width="1.5"/>')
lb.append('</svg>')
# y labels
labels = {3: '$1K', 4: '$10K', 5: '$100K', 6: '$1M', 7: '$10M', 8: '$100M', 9: '$1B', 10: '$10B'}
for e, t in labels.items():
    y1 = Y(10 ** e); y2 = Y(10 ** e, top=10)
    extra = ' only2' if e == 10 else ''
    lb.append(f'<div class="c-ylab{extra}" style="--y1:{y1:.1f}px;--y2:{y2:.1f}px">{t}</div>')
for d in (0, 100, 200, 300, 400, 500):
    lb.append(f'<div class="c-xlab" style="left:{X(d):.0f}px">{d}</div>')
lb.append(f'<div class="c-axt" style="left:{X(500)-30:.0f}px;top:818px">day</div>')
lb.append(f'<div class="c-axt" style="left:{X0}px;top:100px">💵 cash on hand (log scale), best run per model</div>')
bf = base[-1][1]
lb.append(f'<div class="c-blab" style="--x:{X1}px;--y1:{Y(bf):.1f}px;--y2:{Y(bf, 10):.1f}px">🤖 Rule-based baseline</div>')
# date chips
lb.append('<div class="c-date">')
prev = None
for i, p in enumerate(PH):
    nxt = PH[i + 1] if i + 1 < len(PH) else None
    out = f' data-out="{step_of[nxt]}"' if nxt else ''
    lb.append(f'<span data-in="{step_of[p]}"{out}>{date_lbl[p]}</span>')
lb.append('</div>')
# rankings
def money(c):
    if c >= 1e9: return f'${c / 1e9:.2f}B'
    if c >= 1e6: return f'${c / 1e6:.1f}M'
    if c >= 1e3: return f'${c / 1e3:.0f}K'
    return 'bankrupt'
lb.append('<div class="c-rank">')
for i, p in enumerate(PH):
    nxt = PH[i + 1] if i + 1 < len(PH) else None
    out = f' data-out="{step_of[nxt]}"' if nxt else ''
    rows = [(m, runs[m]['final_cash']) for m in ranked[p][:5]] + [('🤖 Rule-based', bf)]
    rows.sort(key=lambda t: -t[1])
    h_ = [f'<div class="rk" data-in="{step_of[p]}"{out}><h4>🏆 Best-run cash</h4>']
    rk = 0
    for m, c in rows:
        if m.startswith('🤖'):
            h_.append(f'<div class="c-row base"><span class="r"></span><span class="d"></span><span>{m}</span><span class="v">{money(c)}</span></div>')
        else:
            rk += 1
            top = ' top' if rk == 1 else ''
            h_.append(f'<div class="c-row{top}"><span class="r">{rk}</span><span class="d" style="background:{COL.get(m, "#9aa1a8")}"></span><b style="font-weight:{700 if rk == 1 else 500}">{m}</b><span class="v">{money(c)}</span></div>')
    h_.append('</div>')
    lb.append(''.join(h_))
lb.append('</div>')
# callouts
lb.append(f'<div class="c-callout" data-in="1" data-out="2" style="left:{X(170):.0f}px;top:{Y(5e7) - 20:.0f}px">Nobody beats the baseline 😬</div>')
lb.append(f'<div class="c-callout" data-in="2" data-out="3" style="left:{X(150):.0f}px;top:{Y(1.6e8) - 20:.0f}px;color:#3f8f8f">Kimi K3 is #1 🤯</div>')
lb.append(f'<div class="c-callout" data-in="2" data-out="3" style="left:{X(150):.0f}px;top:{Y(1.6e8) + 26:.0f}px;font-size:22px;font-weight:400">We are measuring something other benchmarks aren\'t</div>')
lb.append('<div class="c-omt" data-in="5" data-out="6">One more thing… 🍎</div>')
# multipliers: bracket between two models' final cash at day 500
def mult(a, b, step, top, out=None):
    ca, cb = runs[a]['final_cash'], runs[b]['final_cash']
    k = cb / ca; o = f' data-out="{out}"' if out else ''
    ya, yb = Y(ca, top), Y(cb, top); x = X1 + 20
    lb.append(f'<svg class="c-mult" data-in="{step}"{o} viewBox="0 0 1600 900"><path pathLength="1" d="M{x - 10} {ya:.1f} H{x} V{yb:.1f} H{x - 10}"/></svg>')
    lb.append(f'<div class="c-mlab" data-in="{step}"{o} style="left:{x + 14}px;top:{(ya + yb) / 2:.1f}px"><b>{k:.0f}×</b><span>{b.replace("Claude ", "")}<br>vs {a.replace("Claude ", "")}</span></div>')
mult('GPT-5.6 Sol', 'GPT-6 Sol', 4, 9, out=5)
mult('Claude Fable 5', 'Claude Fable 5.1', 7, 10)
LB = ''.join(lb)

# per-phase highlight css
css = []
for p in PH:
    css.append(f'.p{p} .c-ln:not(.base) {{ stroke: #d3d8de; stroke-width: 2.2; }}')
    for m in hl[p]:
        css.append(f'.p{p} .c-ln.{cls_of(m)} {{ stroke: {COL.get(m, "#555")}; stroke-width: 4; }}')
css.append(f'.mS:not(.pF) .c-ln.{cls_of("GPT-5.6 Sol")} {{ stroke: {COL["GPT-5.6 Sol"]}; stroke-width: 4; }}')
css.append(f'.mF .c-ln.{cls_of("Claude Fable 5")} {{ stroke: {COL["Claude Fable 5"]}; stroke-width: 4; }}')
css.append('.zc .c-draw.cc { stroke-dashoffset: 0; }')
css.append('.c-ev { opacity: 0; transition: opacity .3s ease var(--d); } .zc .c-ev { opacity: 1; }')
HL = '\n'.join(css)
# specificity: '.pX .c-ln:not(.base)' (0,3,0) vs '.pX .c-ln.m-x' (0,3,0): later rule wins, phases are in order.

t = open(B + 'template.html').read()
DBI = '<svg class="c-dbi" viewBox="0 0 12 12" fill="none"><ellipse cx="6" cy="2.5" rx="4" ry="1.3" stroke="currentColor" stroke-width="1.1"></ellipse><path d="M2 2.5v7c0 .72 1.79 1.3 4 1.3s4-.58 4-1.3v-7" stroke="currentColor" stroke-width="1.1" fill="none"></path><path d="M2 6c0 .72 1.79 1.3 4 1.3s4-.58 4-1.3" stroke="currentColor" stroke-width="1.1" fill="none"></path></svg>'
DBL = '<svg class="c-dbl" viewBox="0 0 24 24" fill="none"><path d="M2 7l10 5 10-5-10-5-10 5z" fill="#ff3621"></path><path d="M2 12l10 5 10-5" stroke="#ff3621" stroke-width="1.7"></path><path d="M2 17l10 5 10-5" stroke="#ff3621" stroke-width="1.7"></path></svg>'
rep = {'EYEOFF': EYEOFF, 'DBI': DBI, 'DBL': DBL, 'INTER': b64(B + 'inter.woff2'), 'JBM': b64(B + 'jetbrains-mono.woff2'), 'TEASER_CSS': tz_css + '\n' + ac_css + '\n' + cf_css, 'CODEFIG': CODEFIG,
       'TEASER_HTML': tz_body, 'AC_HTML': ac_body, 'HEAT_HTML': HEAT, 'QCHART': QCHART, 'COMP_CHART': COMP,
       'GROUPS_HTML': GROUPS, 'SQL': SQL, 'PQ_SVG': PQ, 'NET_HTML': NET, 'LB_HTML': LB, 'HL_CSS': HL,
       'VBTITLE': b64(B + 'vbtitle.png'), 'FBIPNG': b64(B + 'fbi.png'), 'CEOLOGO': b64(B + 'ceobench-icon.png')}
for k_, v in rep.items():
    assert '{{' + k_ + '}}' in t, k_
    t = t.replace('{{' + k_ + '}}', v)
assert '{{' not in t
open(OUT, 'w').write(t)
print('wrote', OUT, len(t))
print({p: ranked[p][:4] for p in PH})
