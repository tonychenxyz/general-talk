"""Part 7 · Open questions for open-ended problems (closing slides). Writes out/sections.html and out/css.css."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / 'out'
S = []

import math, random

W, H = 1600, 900
FADE = ('<defs><radialGradient id="{id}g" cx="50%" cy="48%" r="62%"><stop offset="0" stop-color="#000"/>'
        '<stop offset=".42" stop-color="#000"/><stop offset=".78" stop-color="#fff"/></radialGradient>'
        '<mask id="{id}m"><rect width="1600" height="900" fill="url(#{id}g)"/></mask></defs>')


def svg(id_, body):
    """Decoration layer behind the text, faded out around the centre so the words stay clean."""
    return (f'<svg class="oq-deco" viewBox="0 0 {W} {H}" aria-hidden="true">{FADE.format(id=id_)}'
            f'<g mask="url(#{id_}m)">{body}</g></svg>')


def constellation(seed=3):
    """Open, unbounded network: points everywhere, links to near neighbours, a few running off the edges."""
    r = random.Random(seed); pts = [(r.uniform(-60, W + 60), r.uniform(-60, H + 60)) for _ in range(150)]
    out = []
    for i, (x, y) in enumerate(pts):
        near = sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:3]
        for j in near:
            if j > i: out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{pts[j][0]:.0f}" y2="{pts[j][1]:.0f}" stroke="#c9d0d8" stroke-width="1.2"/>')
    for k, (x, y) in enumerate(pts):
        out.append(f'<circle class="oq-tw" cx="{x:.0f}" cy="{y:.0f}" r="{r.choice((2.5, 3, 4, 5)):.1f}" fill="#aab3bd" style="--d:{(k % 13) * .37:.2f}s"/>')
    return ''.join(out)


def experts(seed=5):
    """Many experts from diverse areas (muted colours) feeding one learner in the middle."""
    r = random.Random(seed); cols = ['#7c9cbf', '#c39b6a', '#8fae8b', '#b58db0', '#c98a7d', '#8aa8a6', '#a3a07a']
    cx, cy = W / 2, H / 2; out = []
    for k in range(70):
        a = r.uniform(0, 2 * math.pi); d = r.uniform(520, 860)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a) * .62
        c = cols[k % len(cols)]
        out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{cx + (x - cx) * .55:.0f}" y2="{cy + (y - cy) * .55:.0f}" stroke="{c}" stroke-width="1.6" stroke-opacity=".55"/>')
        out.append(f'<circle class="oq-tw" cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(6, 11):.1f}" fill="{c}" fill-opacity=".75" style="--d:{(k % 11) * .41:.2f}s"/>')
    return ''.join(out)


def signals(seed=8):
    """A dump of raw information (grey dots) with a few subtle signals, linked, and a lens drifting over it."""
    r = random.Random(seed); out = []
    for gy in range(0, H + 1, 26):
        for gx in range(0, W + 1, 26):
            x, y = gx + r.uniform(-6, 6), gy + r.uniform(-6, 6)
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.2" fill="#c4cbd3"/>')
    sig = [(150, 760), (330, 140), (1240, 110), (1470, 690), (980, 820), (90, 330)]
    out.append('<path d="M' + ' L'.join(f'{x} {y}' for x, y in sig) + '" fill="none" stroke="#1f2328" stroke-width="1.6" stroke-dasharray="5 7" opacity=".55"/>')
    for k, (x, y) in enumerate(sig):
        out.append(f'<circle class="oq-tw" cx="{x}" cy="{y}" r="7" fill="#1f2328" style="--d:{k * .5:.1f}s"/>')
    out.append('<g class="oq-lens"><circle cx="0" cy="0" r="70" fill="none" stroke="#1f2328" stroke-width="5" opacity=".6"/>'
               '<line x1="50" y1="50" x2="105" y2="105" stroke="#1f2328" stroke-width="10" stroke-linecap="round" opacity=".6"/></g>')
    return ''.join(out)


def society(seed=13):
    """A crowd of people, some connected: orchestrating a society of humans."""
    r = random.Random(seed); out = []; heads = []
    for row, (y0, n, sc) in enumerate([(770, 26, .85), (836, 22, 1.0), (906, 18, 1.15)]):
        for k in range(n):
            x = (k + .5) * W / n + r.uniform(-14, 14); y = y0 + r.uniform(-8, 8)
            heads.append((x, y - 34 * sc))
            out.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({sc})"><circle cx="0" cy="-34" r="12" fill="#b9c1ca"/>'
                       f'<path d="M-20 12 Q-20 -14 0 -16 Q20 -14 20 12 Z" fill="#b9c1ca"/></g>')
    for k in range(16):
        a, b = r.sample(heads, 2)
        mx, my = (a[0] + b[0]) / 2, min(a[1], b[1]) - r.uniform(30, 70)
        out.insert(0, f'<path class="oq-arc" pathLength="1" d="M{a[0]:.0f} {a[1]:.0f} Q{mx:.0f} {my:.0f} {b[0]:.0f} {b[1]:.0f}" fill="none" stroke="#7d8996" stroke-width="1.8" style="--d:{k * .18:.2f}s"/>')
    return ''.join(out)


S.append('''  <section class="slide p2 oq-on" data-name="Open questions">
    ''' + svg('oq0', constellation()) + '''
    <div class="title">
      <h1>Open Questions for Open-Ended Problems</h1>
    </div>
    <div class="note" data-at="0">To close, some open questions for open-ended problems.</div>
  </section>''')

# question 1: the headline grows from "people" into "really, really smart people in diverse areas"
S.append('''  <section class="slide p2" data-name="Q1: learning from people" data-classes='{"oq-grow":1}'>
    ''' + svg('oq1', experts()) + '''
    <div class="oq">
      <div class="oq-k">Question #1</div>
      <div class="oq-q">Does learning from <span class="oq-ins"><span>really, really smart&nbsp;</span></span>people<span class="oq-ins"><span> in diverse areas</span></span> help?</div>
      <ul class="oq-sub">
        <li class="rise" data-in="2">How to create smart-people data scalably?</li>
        <li class="rise" data-in="3">How to measure the gap in thinking between LLMs and these really, really smart people?</li>
      </ul>
    </div>
    <div class="note" data-at="0">First: does learning from people help?</div>
    <div class="note" data-at="1">More precisely: does learning from really, really smart people, in diverse areas, help?</div>
    <div class="note" data-at="2">If so, how do we create data from such people at scale?</div>
    <div class="note" data-at="3">And how do we measure the gap in thinking between LLMs and these people?</div>
  </section>''')

S.append('''  <section class="slide p2 oq-on" data-name="Q2: the open world">
    ''' + svg('oq2', signals()) + '''
    <div class="oq">
      <div class="oq-k">Question #2</div>
      <div class="oq-q">How can agents better understand the vast open world?</div>
      <ul class="oq-sub">
        <li class="rise" data-in="1">How to enable agents to grasp more pieces of reality?</li>
        <li class="rise" data-in="2">Given a huge dump of raw information, how to find subtle signals scattered all over it?</li>
      </ul>
    </div>
    <div class="note" data-at="0">Second: how do agents get a better understanding of the vast open world?</div>
    <div class="note" data-at="1">How do we let agents grasp more pieces of reality?</div>
    <div class="note" data-at="2">And given a huge dump of raw information, how do they find the subtle signals scattered all over it?</div>
  </section>''')

S.append('''  <section class="slide p2 oq-on" data-name="Q3: dealing with humans">
    ''' + svg('oq3', society()) + '''
    <div class="oq">
      <div class="oq-k">Question #3</div>
      <div class="oq-q">How should agents deal with humans?</div>
      <ul class="oq-sub">
        <li class="rise" data-in="1">Anything involving humans is open-ended!</li>
        <li class="rise" data-in="2">Can agents orchestrate a society of humans?</li>
      </ul>
    </div>
    <div class="note" data-at="0">Third: how do agents deal with humans?</div>
    <div class="note" data-at="1">Anything that involves humans is open-ended.</div>
    <div class="note" data-at="2">Can an agent orchestrate a whole society of humans?</div>
  </section>''')

CSS = '''
.oq-deco { position: absolute; inset: 0; width: 1600px; height: 900px; pointer-events: none; }
.oq-tw { animation: oq-tw 4.5s ease-in-out var(--d, 0s) infinite alternate; }
@keyframes oq-tw { from { opacity: .45; } to { opacity: 1; } }
.oq-lens { animation: oq-lens 18s ease-in-out infinite alternate; }
@keyframes oq-lens { 0% { transform: translate(260px, 700px); } 33% { transform: translate(1260px, 160px); } 66% { transform: translate(1380px, 720px); } 100% { transform: translate(220px, 230px); } }
.oq-arc { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.6s var(--ease) var(--d, 0s); }
.oq-on.active .oq-arc { stroke-dashoffset: 0; }
.oq, .title { z-index: 1; }
.oq { position: absolute; left: 160px; right: 160px; top: 0; bottom: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.oq-k { font-size: 28px; font-weight: 500; margin-bottom: 26px; }
.oq-q { font-size: 54px; font-weight: 600; letter-spacing: -.02em; line-height: 1.2; max-width: 1200px; }
.oq-ins { display: inline-grid; grid-template-columns: 0fr; transition: grid-template-columns 1s var(--ease); vertical-align: bottom; }
.oq-ins > span { overflow: hidden; white-space: nowrap; }
.oq-grow .oq-ins { grid-template-columns: 1fr; }
.oq-grow .oq-ins > span { white-space: normal; }
.oq-sub { list-style: none; margin-top: 64px; display: flex; flex-direction: column; gap: 26px; max-width: 1150px; }
.oq-sub li { font-size: 32px; line-height: 1.35; }
'''
OUT.mkdir(exist_ok=True)
(OUT / 'sections.html').write_text('\n'.join(S) + '\n')
(OUT / 'css.css').write_text(CSS.strip() + '\n')
print('wrote', OUT)
