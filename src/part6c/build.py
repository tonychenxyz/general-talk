"""Part 6c · SWEeper-Bench analysis: Focalboard trajectories (paper Fig. 6) and time budget (paper Fig. 9).

Reads data.json (see extract.py) and writes out/sections.html + out/css.css; src/merge_parts.py splices them
into the deck. All classes are prefixed rc-.
"""
import base64, html, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / 'data.json'))
esc = html.escape
slides, css = [], []


def tag_in(step, out=None):
    return f' data-in="{step}"' + (f' data-out="{out}"' if out is not None else '')


# =====================================================================================
# 1. Seeing a bug is not the same as recognizing it (Focalboard, four agents)
# =====================================================================================
ROWS = D['trajectories']
LOGO = {k: 'data:image/svg+xml;base64,' + base64.b64encode(v.encode()).decode() for k, v in D['logos'].items()}
# The paper's evidence-type icons and their legend line are dropped on the slide (code font already marks code).
ARROW = '<svg viewBox="0 0 16 16"><path d="M1 8H14M10 4l4 4-4 4"/></svg>'
OK = ('<svg class="rc-mk" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#2e9e5b"/>'
      '<path d="M9 16.5l4.5 4.5L23 11.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')
NO = ('<svg class="rc-mk" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#d05454"/>'
      '<path d="M11 11l10 10M21 11L11 21" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>')
CW, AW, X0 = 256, 30, 100            # card width, arrow gap, left edge  (5*256 + 4*30 = 1400)


def wbr(t):   # display-only breaks inside long identifiers (as in the paper figure)
    return esc(t).replace('AddMemberToBoard', 'AddMember<wbr>ToBoard').replace('goto(', 'goto(<wbr>')


def head(r, cls, attrs='', rest_in=None):
    """Row header: logo in a ring + the paper's sentence (verbatim), outcome word in bold.
    rest_in: step from which the rest of the sentence (which gives away the outcome) appears."""
    rest = esc(r['headline'][len(r['name']):])
    rest = re.sub(r'\b(unfixed|fixed)\b', r'<b>\1</b>', rest)
    rest = f'<span{tag_in(rest_in)}>{rest}</span>' if rest_in is not None else rest
    return (f'<div class="{cls}"{attrs}><span class="rc-logo" style="border-color:{r["ring"]}">'
            f'<img src="{LOGO[r["logo"]]}" alt=""></span><b>{esc(r["name"])}</b>{rest}</div>')


def tone(r, i):
    return ' seen' if i == 1 else (' pass' if r['fixed'] else ' fail') if i == 4 else ''


CH = 500                            # big-card height (same for every row; fits the tallest card's content)
BT = 150 + (690 - (46 + 30 + (CH or 500))) // 2   # header top: header + gap + cards centered in y 150..840


def big_row(r, start, end):
    """One model's five cards, large; card i appears at start+i."""
    h = [f'<div class="rc-big"{tag_in(start, end)}>', head(r, 'rc-bh', rest_in=start + 4), '<div class="rc-row">']
    for i, c in enumerate(r['cards']):
        st = start + i
        q = wbr(c['quote'])
        q = f'<code>{q}</code>' if c['code'] else f'“{q}”'
        if i:
            h.append(f'<span class="rc-arr"{tag_in(st)}>{ARROW}</span>')
        h.append(f'<div class="rc-card{tone(r, i)}"{tag_in(st)}>'
                 f'<div class="rc-sum">{wbr(c["summary"])}</div>'
                 f'<div class="rc-q{" code" if c["code"] else ""}">{q}</div></div>')
    h.append('</div></div>')
    return ''.join(h)


# steps: Fable cards 0-4, GLM 5-9, Opus 10-14, Astra 15-19, all four 20, shaded column 21
FS = 20
h = [big_row(r, 5 * k, 5 * k + 5) for k, r in enumerate(ROWS)]
h.append(f'<div class="rc-all"{tag_in(FS)}>')
for k, r in enumerate(ROWS):
    top = 152 + k * 166
    h.append(head(r, 'rc-sh', f' style="top:{top}px"'))
    for i, c in enumerate(r['cards']):
        x = X0 + i * (CW + AW)
        if i:
            h.append(f'<span class="rc-arr sm" style="left:{x - AW}px;top:{top + 42}px">{ARROW}</span>')
        mark = (OK if r['fixed'] else NO) if i == 4 else ''
        h.append(f'<div class="rc-sc{tone(r, i)}" style="left:{x}px;top:{top + 42}px">{wbr(c["summary"])}{mark}</div>')
h.append(f'<div class="rc-bandlab"{tag_in(FS + 1)} style="left:{X0 + CW + AW}px;width:{CW}px">all four see it</div>')
h.append('</div>')

notes = [
    # Fable 5.1, card by card
    'Here is one Focalboard task, the shared board that never shows up in the recipient’s sidebar. Let’s follow four agents. First, Claude Fable 5.1. It joins an open board as a second user, Carol.',
    'Carol’s sidebar is empty. This shaded card is the moment every agent we look at reaches: the bug is right there on the page.',
    'Fable digs in. It learns that the sidebar only lists boards that are filed in a category.',
    'And it sees that joining a board never files it into one.',
    'So it decides to fix it: the new member needs the board in their sidebar, so it adds it to their default category. Fixed.',
    # GLM 5.3
    'Second, GLM 5.3. It opens the board as the invited user.',
    'The board opens, but the sidebar is empty. Same observation.',
    'GLM flags it as a bug right away: “Sidebar no boards likely bug!”',
    'It traces it to AddMemberToBoard, which should add the board to the new user’s default category.',
    'And it decides to fix it. Also fixed.',
    # Opus 5
    'Now Claude Opus 5. It also joins the open board as Carol.',
    'And the sidebar is still empty after joining. Same observation again.',
    'But it trusts the unit tests, which use strict mocks and never check the sidebar.',
    'So it concludes the empty sidebar is intended: “this is the intended behaviour of this version rather than a regression.”',
    'And it decides not to fix it: “changing it would be a product decision, not a bug fix.” Existing tests can reinforce the wrong expectation. Unfixed.',
    # Astra
    'Finally, GPT-6 Astra. It opens the board as the invited member.',
    'It sees the empty sidebar, and moves on without comment.',
    'It focuses on the Share dialog’s member list instead.',
    'There it finds a role-permissions bug.',
    'And it decides to fix those other bugs instead. So it leaves this one unfixed.',
    # all four
    'Side by side: two agents fixed it, two left it unfixed.',
    'And all four reached the empty sidebar: they all saw the buggy behavior, but some chose to ignore it.',
]
marks = {'GLM 5.3': 5, 'Claude Opus 5': 10, 'GPT-6 Astra': 15, 'All four': FS}
slides.append(f'''  <section class="slide p2" data-name="Seeing vs recognizing" data-classes='{{"rc-seen": {FS + 1}}}' data-marks='{json.dumps(marks)}'>
    <div class="c-kicker">Focalboard: a shared board never shows up in the recipient’s sidebar</div>
    <div class="c-h">All agents see the buggy behavior, some choose to ignore it</div>
    {''.join(h)}
''' + '\n'.join(f'    <div class="note" data-at="{i}">{esc(n)}</div>' for i, n in enumerate(notes)) + '\n  </section>')
css.append(f'''
.rc-big {{ position: absolute; left: 0; top: 0; width: 1600px; height: 900px; }}
.rc-bh {{ position: absolute; left: {X0}px; top: {BT}px; height: 46px; display: flex; align-items: center; font-size: 30px; white-space: pre; letter-spacing: -.01em; }}
.rc-bh b, .rc-sh b {{ font-weight: 600; }}
.rc-logo {{ flex: none; display: flex; align-items: center; justify-content: center; width: 46px; height: 46px; border: 2px solid; border-radius: 50%; margin-right: 14px; background: #fff; }}
.rc-logo img {{ width: 26px; height: 26px; }}
.rc-row {{ position: absolute; left: {X0}px; top: {BT + 76}px; width: 1400px; display: flex; align-items: stretch; }}
.rc-card {{ flex: none; width: {CW}px; height: {f'{CH}px' if CH else 'auto'}; box-sizing: border-box; background: #f2f3f5; border: 2px solid #f2f3f5; border-radius: 16px; padding: 22px 18px; display: flex; flex-direction: column; transition: opacity .45s ease; }}
.rc-card.seen, .rc-sc.seen {{ background: #eef2f6; border-color: #bec6d1; }}
.rc-card.pass, .rc-sc.pass {{ background: #ebf8ef; border-color: #b9dfc5; }}
.rc-card.fail, .rc-sc.fail {{ background: #fff0ef; border-color: #e8b8b8; }}
.rc-sum {{ font-size: 30px; line-height: 1.24; letter-spacing: -.01em; min-height: 172px; }}
.rc-q {{ background: #fff; border: 1.5px solid #d8dfe7; border-radius: 10px; padding: 12px 14px; font-size: 24px; line-height: 1.32; overflow-wrap: anywhere; }}
.rc-q.code code {{ font-family: "JetBrains Mono", monospace; font-size: 21px; line-height: 1.4; letter-spacing: -.02em; white-space: pre-wrap; }}
.rc-arr {{ flex: none; width: {AW}px; display: flex; align-items: center; justify-content: center; }}
.rc-all .rc-arr {{ position: absolute; }}
.rc-arr svg {{ width: 28px; height: 28px; fill: none; stroke: #1f2328; stroke-width: 1.3; stroke-linejoin: round; stroke-linecap: round; }}
.rc-arr.sm svg {{ width: 22px; height: 22px; }}
.rc-arr.sm {{ height: 100px; align-items: center; }}
.rc-all {{ position: absolute; left: 0; top: 0; width: 1600px; height: 900px; }}
.rc-sh {{ position: absolute; left: {X0}px; display: flex; align-items: center; font-size: 24px; white-space: pre; }}
.rc-sh .rc-logo {{ width: 34px; height: 34px; margin-right: 10px; }}
.rc-sh .rc-logo img {{ width: 19px; height: 19px; }}
.rc-sc {{ position: absolute; width: {CW}px; height: 100px; background: #f2f3f5; border: 2px solid #f2f3f5; border-radius: 12px; padding: 10px 13px; font-size: 22px; line-height: 1.2; transition: border-color .4s, box-shadow .4s; }}
.rc-seen .rc-sc.seen {{ border-color: #5d6b7e; box-shadow: 0 0 0 3px #5d6b7e; }}
.rc-mk {{ position: absolute; right: 10px; bottom: 10px; width: 30px; height: 30px; }}
.rc-bandlab {{ position: absolute; top: 800px; text-align: center; font-size: 22px; font-weight: 600; }}''')

# =====================================================================================
# 2. More time helps only up to a point (time budget)
# =====================================================================================
TB = D['time_budget']
PX0, PX1, PY0, PY1 = 230, 1130, 180, 730           # plot box; x 17..83 min, y 30..65 %
fx = lambda m: PX0 + (m - 17) / 66 * (PX1 - PX0)
fy = lambda p: PY1 - (p - 30) / 35 * (PY1 - PY0)


def marker(kind, x, y, col):
    if kind == 'o':
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{col}"/>'
    if kind == 's':
        return f'<rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18" fill="{col}"/>'
    return f'<path d="M{x:.1f} {y - 12:.1f} L{x + 11.5:.1f} {y + 8:.1f} L{x - 11.5:.1f} {y + 8:.1f}Z" fill="{col}"/>'


s = ['<svg class="rc-svg" viewBox="0 0 1600 900">']
s.append(f'<g{tag_in(1)}><rect x="{fx(40):.1f}" y="{PY0}" width="{fx(80) - fx(40):.1f}" height="{PY1 - PY0}" fill="#f3f5f7"/>'
         f'<text x="{(fx(40) + fx(80)) / 2:.1f}" y="{PY0 + 40}" text-anchor="middle" class="rc-band-t">no gain beyond 40 minutes</text></g>')
for p in (30, 40, 50, 60):
    s.append(f'<line x1="{PX0}" x2="{PX1}" y1="{fy(p):.1f}" y2="{fy(p):.1f}" stroke="#e5e7eb" stroke-width="1.5"/>'
             f'<text x="{PX0 - 16}" y="{fy(p) + 7:.1f}" text-anchor="end" class="rc-tick">{p}</text>')
for m in TB['minutes']:
    s.append(f'<line x1="{fx(m):.1f}" x2="{fx(m):.1f}" y1="{PY1}" y2="{PY1 + 8}" stroke="#1f2328" stroke-width="1.5"/>'
             f'<text x="{fx(m):.1f}" y="{PY1 + 38}" text-anchor="middle" class="rc-tick">{m}</text>')
s.append(f'<path d="M{PX0} {PY0} V{PY1} H{PX1}" fill="none" stroke="#1f2328" stroke-width="1.5"/>')
s.append(f'<text x="{(PX0 + PX1) / 2}" y="{PY1 + 86}" text-anchor="middle" class="rc-axt">Time budget (minutes)</text>')
s.append(f'<text transform="translate({PX0 - 74} {(PY0 + PY1) / 2}) rotate(-90)" text-anchor="middle" class="rc-axt">Pass rate (%)</text>')
for half, step in (((0, 1), 0), ((1, 2, 3), 1)):
    g = [f'<g{tag_in(step)}>']
    for ser in reversed(TB['series']):                  # Luna (black) on top, as in the paper
        pts = [(fx(TB['minutes'][i]), fy(ser['rates'][i])) for i in half]
        if step:
            pts = [(fx(40), fy(ser['rates'][1]))] + pts
        g.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{ser["color"]}" stroke-width="4" stroke-linejoin="round"/>')
        g += [marker(ser['marker'], x, y, ser['color']) for x, y in (pts[1:] if step else pts)]
    s.append(''.join(g) + '</g>')
# legend (paper style: line + marker, label in text ink)
for k, ser in enumerate(TB['series']):
    y = (PY0 + PY1) / 2 - 64 + k * 64
    s.append(f'<line x1="1190" x2="1250" y1="{y}" y2="{y}" stroke="{ser["color"]}" stroke-width="4"/>'
             + marker(ser['marker'], 1220, y, ser['color'])
             + f'<text x="1270" y="{y + 10}" class="rc-leg">{esc(ser["model"])}</text>')
s.append('</svg>')
ser = {x['model']: x['rates'] for x in TB['series']}
peaks = ', '.join(f'{v[1]:g}%' for v in ser.values())
slides.append(f'''  <section class="slide p2" data-name="Time budget" data-marks='{{"Beyond 40 min":1}}'>
    <div class="c-kicker">Does working longer help?</div>
    <div class="c-h">More time helps only up to a point</div>
    {''.join(s)}
    <div class="note" data-at="0">Does more time help the same agent? We gave GPT-5.6 Luna, GPT-5.6 Terra, and GLM 5.3 budgets of 20, 40, 60, and 80 minutes on the same {TB['tasks']} tasks, and told each to keep working until its deadline. A task counts as passed only if both behavior tests pass. Going from 20 to 40 minutes helps all three.</div>
    <div class="note" data-at="1">But not beyond that. Pass rates peak at 40 minutes, at {peaks}. With {TB['tasks']} tasks these differences aren't statistically significant, but there's no sign that more time alone closes the gap.</div>
  </section>''')
css.append('''
.rc-svg { position: absolute; inset: 0; width: 1600px; height: 900px; overflow: visible; }
.rc-svg text { font-family: "Inter", sans-serif; fill: #1f2328; }
.rc-tick { font-size: 24px; }
.rc-axt { font-size: 26px; }
.rc-leg { font-size: 28px; }
.rc-band-t { font-size: 26px; font-weight: 600; }''')

# =====================================================================================
# 3. SWEeper-Bench conclusion
# =====================================================================================
slides.append('''  <section class="slide p2" data-name="SWEeper-Bench takeaway">
    <div class="rc-concl"><p>Even on tasks we think are well solved, <b>open-endedness</b> presents significant challenges.</p></div>
    <div class="note" data-at="0">So the takeaway from SWEeper-Bench: even on tasks we think are well solved, like fixing bugs in a codebase, open-endedness presents significant challenges. When nobody tells the agent what the bug is, it has to find and recognize the problem itself, and that is where today’s agents fall short.</div>
  </section>''')
css.append('''
.rc-concl { position: absolute; left: 200px; right: 200px; top: 0; bottom: 0; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 60px; font-weight: 500; line-height: 1.3; letter-spacing: -.02em; color: #1f2328; text-wrap: balance; }
.rc-concl b { font-weight: 700; }''')

out = HERE / 'out'
out.mkdir(exist_ok=True)
(out / 'sections.html').write_text('\n'.join(slides) + '\n')
(out / 'css.css').write_text('\n'.join(css).strip() + '\n')
print('wrote', out, 'slides:', len(slides))
