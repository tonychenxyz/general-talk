"""Part 5b: SWEeper-Bench slides (paradigm, task domains, Focalboard walk-through).

Writes only out/sections.html and out/css.css; src/merge_parts.py splices them into the deck.
Inputs: data.json and img/ (made by extract.py from the sweeper-bench-plotting repo, i.e. the paper's figure sources).
All classes are prefixed sb-.
"""
import base64, html, json, math, pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)
D = json.load(open(HERE / 'data.json'))
esc = html.escape


def uri(name):
    return 'data:image/png;base64,' + base64.b64encode((HERE / 'img' / name).read_bytes()).decode()


S, CSS = [], []

# =====================================================================================
# 1. paradigm (paper Figure 1, paradigm.html): (a) deploy loop, (b) autonomous sweep
#    Geometry copied from the paper SVG (viewBox units); emoji images replaced by the deck's emoji font,
#    the arc legends replaced by direct labels, stage labels slightly enlarged for the slide.
# =====================================================================================
OUTER = ['M84.78,128.36 A104,104 0 0,1 {a}', 'M{b} A104,104 0 0,1 259.22,128.36',
         'M264.66,137.78 A104,104 0 0,1 264.66,232.22', 'M259.22,241.64 A104,104 0 0,1 177.44,288.86',
         'M166.56,288.86 A104,104 0 0,1 84.78,241.64', 'M79.34,232.22 A104,104 0 0,1 79.34,137.78']
DOTS = [(262.07, 133), (262.07, 237), (172, 289), (81.93, 237), (81.93, 133)]


def loop(top_a, top_b, first):
    """Outer cycle with the five stages; first = (emoji, line1, line2) for the top-right stage."""
    g = [f'<path d="{p.format(a=top_a, b=top_b)}" class="sb-ring" marker-end="url(#sb-outer)"/>' for p in OUTER]
    g += [f'<circle cx="{x}" cy="{y}" r="3" fill="#111"/>' for x, y in DOTS]
    stages = [('📦', 47, 96, ['Code Update']), (first[0], 298, 90, first[1:]), ('🔍', 295, 228, ['Diagnose']),
              ('💻', 49, 228, ['Implement']), ('💡', 172, 302, ['Design Fix'])]
    for emo, x, y, lines in stages:
        g.append(f'<text x="{x}" y="{y + 13.5}" text-anchor="middle" class="sb-emo">{emo}</text>')
        for i, t in enumerate(lines):
            g.append(f'<text x="{x}" y="{y + 29 + i * 13}" text-anchor="middle" class="sb-stage">{esc(t)}</text>')
    return ''.join(g)


def arrow_marker(mid, col, size):
    return (f'<marker id="{mid}" viewBox="0 0 8 8" refX="0" refY="4" markerWidth="{size}" markerHeight="{size}" orient="auto" '
            f'markerUnits="userSpaceOnUse"><path d="M0 0 8 4 0 8Z" fill="{col}"/></marker>')


SWE, SENIOR, SWEEP = '#BE776C', '#668499', '#8272B3'
K, X_MIN, X_MAX, Y_MIN, Y_MAX = 2.12, 12, 701, 64, 334           # scale and content extent in paper units
X0 = 800 - (X_MIN + X_MAX) / 2 * K
Y0 = 505 - (Y_MIN + Y_MAX) / 2 * K
SHIFT = (800 - (X0 + 172 * K)) / K                                # centres panel (a) while it is alone
pa = ['<g class="sb-pa">', loop('116,97.36', '228,97.36', ('😠', 'Frustrated', 'User')),
      '<rect x="118" y="64" width="108" height="43" rx="6" fill="#F2E4E1" stroke="#000" stroke-width=".95"/>',
      '<text x="144" y="80.5" text-anchor="middle" class="sb-emo">🌐</text><text x="183" y="81" text-anchor="middle" class="sb-box">Deploy</text>',
      '<text x="131" y="97.5" text-anchor="middle" class="sb-emo sm">🕒</text><text x="139" y="98" class="sb-small">Slow</text>',
      '<text x="183" y="97.5" text-anchor="middle" class="sb-emo sm">💰</text><text x="191" y="98" class="sb-small">Costly</text>',
      # Senior SWE-Bench: from Diagnose all the way round to Code Update
      '<g data-in="2"><path d="M241.28,145.00 A80,80 0 1,1 102.72,145.00" fill="none" stroke="#668499" stroke-width="4.5" marker-end="url(#sb-senior)"/>'
      '<circle cx="241.28" cy="145" r="3" fill="#668499"/>'
      '<text x="172" y="149" text-anchor="middle" class="sb-arc">Senior SWE-Bench</text></g>',
      # SWE-bench: from Design Fix to Code Update
      '<g data-in="1"><path d="M172.00,239.00 A54,54 0 0,1 125.23,158.00" fill="none" stroke="#BE776C" stroke-width="4.5" marker-end="url(#sb-swe)"/>'
      '<circle cx="172" cy="239" r="3" fill="#BE776C"/>'
      '<text x="180" y="201" text-anchor="middle" class="sb-arc">SWE-bench</text></g>',
      '</g>']
pb = ['<g class="sb-pb"><g transform="translate(376 0)">', loop('114,98.68', '230,98.68', ('🐞', 'Problem', 'Discovery')),
      '<rect x="116" y="64" width="112" height="43" rx="6" fill="#E9E5F3" stroke="#000" stroke-width=".95"/>',
      f'<image href="{uri("broom.png")}" x="120" y="72" width="27" height="27"/>',
      '<text x="187" y="82" text-anchor="middle" class="sb-box sm">Autonomous</text><text x="187" y="96" text-anchor="middle" class="sb-box sm">Sweep</text>',
      '<path d="M183.81,118.03 A68,68 0 1,1 162.54,117.66" fill="none" stroke="#8272B3" stroke-width="4.5" marker-end="url(#sb-sweep)"/>'
      '<circle cx="183.81" cy="118.03" r="3" fill="#8272B3"/>',
      '<text x="172" y="189" text-anchor="middle" class="sb-arc">SWEeper-Bench</text>',
      '</g><path d="M360 66V330" stroke="#a8abb2" stroke-width=".8" stroke-dasharray="1 4" stroke-linecap="round"/></g>']
svg = (f'<svg class="sb-svg" viewBox="0 0 1600 900"><defs>{arrow_marker("sb-outer", "#000", 4.5)}{arrow_marker("sb-swe", SWE, 9)}'
       f'{arrow_marker("sb-senior", SENIOR, 9)}{arrow_marker("sb-sweep", SWEEP, 9)}</defs>'
       f'<g transform="translate({X0:.1f} {Y0:.1f}) scale({K})">{"".join(pa)}{"".join(pb)}</g></svg>')
S.append(f'''  <section class="slide p2 sb-par" data-name="Waiting vs sweeping" data-classes='{{"sb-two":3}}' data-marks='{{"Autonomous sweep":3}}'>
    <div class="c-h">From waiting for bug reports to sweeping for bugs</div>
    {svg}
    <div class="sb-pbin" data-in="3"></div>
    <div class="note" data-at="0">Here's how software gets fixed today. We deploy, which is slow and costly. Then a user gets frustrated, someone diagnoses the problem, designs a fix, implements it, and ships a code update. Then we wait for the next report.</div>
    <div class="note" data-at="1">SWE-bench evaluates only the last part of this loop: it starts from a described issue and asks for the fix.</div>
    <div class="note" data-at="2">Senior SWE-Bench covers more, starting at diagnosis. But both start after a user has already reported the bug, and that report only comes after a slow and costly deployment.</div>
    <div class="note" data-at="3">In SWEeper-Bench, the agent closes the loop itself. It has to discover the problem on its own, by exploring the code and the running application, then diagnose it, fix it, and update the code before any user ever runs into it.</div>
  </section>''')
CSS.append(f'''
.sb-svg {{ position: absolute; inset: 0; width: 1600px; height: 900px; overflow: visible; }}
.sb-svg text {{ font-family: "Inter", sans-serif; fill: #111; }}
.sb-par .sb-ring {{ fill: none; stroke: #000; stroke-width: .95; }}
.sb-par .sb-emo {{ font-size: 15px; font-family: "Apple Color Emoji", "Inter", sans-serif; }}
.sb-par .sb-emo.sm {{ font-size: 11px; }}
.sb-par .sb-stage {{ font-size: 11px; font-weight: 600; }}
.sb-par .sb-box {{ font-size: 12.5px; font-weight: 700; }}
.sb-par .sb-box.sm {{ font-size: 11.5px; }}
.sb-par .sb-small {{ font-size: 9.5px; }}
.sb-par .sb-arc {{ font-size: 10.5px; font-weight: 700; }}
.sb-pbin {{ display: none; }}
.sb-pa {{ transform: translateX({SHIFT:.2f}px); transition: transform 1s var(--ease); }}
.sb-pb {{ opacity: 0; transition: opacity .7s ease; }}
.sb-two .sb-pa {{ transform: none; }}
.sb-two .sb-pb {{ opacity: 1; transition-delay: .55s; }}''')

# =====================================================================================
# 2. task domains (paper Figure 4, task-domains.html): donut + domain list, examples = two most-starred repos
# =====================================================================================
DOM = D['domains']
total = sum(d['tasks'] for d in DOM)
assert total == 200
R_OUT, R_IN, CX, CY = 78, 49, 0, 0                               # paper proportions
def pt(r, a):
    return f'{CX + r * math.sin(a):.3f} {CY - r * math.cos(a):.3f}'
paths, a0 = [], 0.0
for i, d in enumerate(DOM):
    a1 = a0 + d['tasks'] / total * 2 * math.pi
    big = 1 if a1 - a0 > math.pi else 0
    paths.append(f'<path d="M{pt(R_OUT, a0)}A{R_OUT} {R_OUT} 0 {big} 1 {pt(R_OUT, a1)}L{pt(R_IN, a1)}A{R_IN} {R_IN} 0 {big} 0 {pt(R_IN, a0)}Z" '
                 f'fill="{d["color"]}" stroke="#fff" stroke-width="1.6" stroke-linejoin="round" style="--i:{i}"/>')
    a0 = a1
donut = (f'<svg class="sb-donut" viewBox="-80 -80 160 160">{"".join(paths)}</svg>'
         f'<div class="sb-dc"><b>{total}</b><span>tasks</span></div>')
def kstars(n):
    return f'{round(n / 1000)}k'
rows = []
for i, d in enumerate(DOM):
    ex = ', '.join(f'{esc(e["product"])} ({kstars(e["github_stars"])}⭐)' for e in d['examples'])
    rows.append(f'<div class="sb-drow" style="--i:{i}"><i style="background:{d["color"]}"></i><b>{esc(d["label"])}</b>'
                f'<span class="n">{d["tasks"]}</span><span class="ex">{ex}</span></div>')
by = {d['label']: d['tasks'] for d in DOM}
med = D['median_stars']
S.append(f'''  <section class="slide p2 sb-dom" data-name="200 web apps">
    <div class="c-h">200 real bugs from 200 open-source web apps</div>
    <div class="sb-dwrap"><div class="sb-dleft">{donut}</div><div class="sb-dlist">{"".join(rows)}</div></div>
    <div class="note" data-at="0">So what's in the benchmark? 200 tasks, each built from a merged pull request that fixed a user-facing bug in an open-source web app. The parent commit is the buggy version, the merged fix is the reference repair, and each app contributes exactly one task, so that's 200 different apps. They span seven domains, from content and knowledge tools like Ghost and Outline to commerce like Bagisto. These are widely used projects: the median repository has about {med / 1000:.1f}k GitHub stars. We picked bugs that are hard to find but obvious once seen: reproducible through normal use, and any user would agree they need fixing.</div>
  </section>''')
CSS.append('''
.sb-dwrap { position: absolute; left: 0; right: 0; top: 150px; bottom: 50px; display: flex; align-items: center; justify-content: center; gap: 110px; }
.sb-dleft { position: relative; width: 500px; height: 500px; flex: none; }
.sb-donut { width: 500px; height: 500px; display: block; overflow: visible; }
.sb-donut path { opacity: 0; }
.sb-dom.active .sb-donut path { animation: sb-pop .5s var(--ease) calc(.1s + var(--i) * .1s) both; }
@keyframes sb-pop { from { opacity: 0; transform: scale(.94); } to { opacity: 1; transform: none; } }
.sb-dc { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.sb-dc b { font-size: 76px; font-weight: 700; letter-spacing: -.03em; line-height: 1; }
.sb-dc span { font-size: 30px; margin-top: 6px; }
.sb-dlist { width: 640px; display: flex; flex-direction: column; gap: 20px; }
.sb-drow { display: grid; grid-template-columns: 26px 1fr auto; column-gap: 12px; align-items: baseline; }
.sb-drow i { width: 20px; height: 20px; border-radius: 50%; align-self: center; }
.sb-drow b { font-size: 27px; font-weight: 700; letter-spacing: -.01em; }
.sb-drow .n { font-size: 27px; font-variant-numeric: tabular-nums; }
.sb-drow .ex { grid-column: 2 / 4; font-size: 22px; margin-top: 2px; }''')

# =====================================================================================
# 3. Focalboard walk-through (paper Figure 5, focalboard-056-procedure.html), full screen
#    Same panels, crops, zoom regions and cursor points as the paper's build_procedure.py (via data.json).
# =====================================================================================
CAPS = ['(1) Log in as miraDunn', '(2) Add board → Create empty board', '(3) Name the board', '(4) Open Share',
        '(5) Search for and select @kadeRue', '(6) Confirm kadeRue appears as a member', '(7) Close Share and log out',
        '(8) Log in as kadeRue and refresh', '<b>Fail</b>: board missing from recipient sidebar',
        '<b>Pass</b>: board listed in recipient sidebar']
P = D['panels']
assert [' '.join(p['caption']) for p in P] == [c.replace('<b>', '').replace('</b>', '') for c in CAPS], 'captions must match the paper'
CUR = uri('cursor.png')
PW_ = 255                                    # px per window (paper window = 134 x 153 units)
COLS, GAP_X, ROW_TOP, ROW_H = 5, 30, 108, 375
left0 = (1600 - COLS * PW_ - (COLS - 1) * GAP_X) / 2
panels = []
for i, p in enumerate(P):
    rx, ry, rw, rh = p['region']
    vx, vy, vw = 2, 14, 130; vh = vw * 1200 / 1920; sc = vw / 1920
    zx, zy, zw, zh = 3, 102, 128, 46
    g = [f'<svg class="sb-win" viewBox="0 0 134 153">',
         '<rect x=".35" y=".35" width="133.3" height="152.3" rx="5" fill="#fff" stroke="#cdd6e1" stroke-width=".7"/>'
         '<path d="M5.35 .35h123.3q5 0 5 5v6h-133.3v-6q0-5 5-5" fill="#eef2f6"/><path d="M.35 11.35h133.3" stroke="#dce3eb" stroke-width=".6"/>',
         ''.join(f'<circle cx="{dx}" cy="5.85" r="1.2" fill="#bec6d1"/>' for dx in (6, 11, 16)),
         f'<image x="{vx}" y="{vy}" width="{vw}" height="{vh:.3f}" href="{uri(p["frame"] + ".png")}" preserveAspectRatio="none"/>',
         f'<rect x="{vx + rx * sc:.3f}" y="{vy + ry * sc:.3f}" width="{rw * sc:.3f}" height="{rh * sc:.3f}" fill="none" stroke="#086bea" stroke-width=".6"/>',
         f'<path d="M{vx + (rx + rw / 2) * sc:.3f} {vy + (ry + rh) * sc:.3f}L{zx + zw / 2} {zy}" fill="none" stroke="#7d91a8" stroke-width=".55"/>',
         f'<rect x="{zx - .5}" y="{zy - .5}" width="{zw + 1}" height="{zh + 1}" rx="2" fill="#fff" stroke="#cdd6e1" stroke-width=".65"/>',
         f'<image x="{zx}" y="{zy}" width="{zw}" height="{zh}" href="{uri(p["frame"] + "-zoom.png")}" preserveAspectRatio="xMidYMid meet"/>']
    if p['point']:
        px, py = p['point']
        g.append(f'<image x="{vx + px * sc:.3f}" y="{vy + py * sc:.3f}" width="7" height="7.5" filter="url(#sb-glow)" href="{CUR}"/>')
        if rx <= px <= rx + rw and ry <= py <= ry + rh:
            z = min(zw / rw, zh / rh); ox = zx + (zw - rw * z) / 2; oy = zy + (zh - rh * z) / 2
            g.append(f'<image x="{ox + (px - rx) * z:.3f}" y="{oy + (py - ry) * z:.3f}" width="8" height="8.5" filter="url(#sb-glow)" href="{CUR}"/>')
    g.append('</svg>')
    kind = ' fail' if i == 8 else ' pass' if i == 9 else ''
    badge = '<span class="sb-badge">✕</span>' if i == 8 else '<span class="sb-badge">✓</span>' if i == 9 else ''
    x = left0 + (i % COLS) * (PW_ + GAP_X); y = ROW_TOP + (i // COLS) * ROW_H
    panels.append(f'<div class="sb-pan{kind} rise" data-in="{i}" style="left:{x:.0f}px;top:{y}px">'
                  f'<div class="sb-cap">{badge}<span>{CAPS[i]}</span></div>{"".join(g)}</div>')
glow = ('<svg width="0" height="0" style="position:absolute"><defs><filter id="sb-glow" x="-100%" y="-100%" width="300%" height="300%">'
        '<feDropShadow dx="0" dy="0" stdDeviation="1" flood-color="#2684ff" flood-opacity=".8"/></filter></defs></svg>')
NOTES = [
    "Here's one task. Focalboard is a project board tool. The verifier first logs in as one user, miraDunn.",
    "It adds a board and picks Create empty board.",
    "It names the board, Q3 Launch Desk.",
    "It opens the Share dialog.",
    "It searches for a second user, kadeRue, and selects him.",
    "And confirms kadeRue now appears as a member. Everything looks fine to the person sharing.",
    "It closes Share and logs out.",
    "Then it logs in as kadeRue and refreshes the page.",
    "With the bug, the shared board is missing from kadeRue's sidebar. He can still open it through a direct link, so nothing looks broken unless you check his sidebar. Adding a member saves the membership but never files the board under the member's default sidebar category.",
    "With the fix, the board shows up in his sidebar. The fix is a single function call. But the failure only appears after nine steps across two accounts, and the agent is only told: find and fix all issues in Focalboard's board sharing and membership.",
]
notes = '\n'.join(f'    <div class="note" data-at="{i}">{esc(n)}</div>' for i, n in enumerate(NOTES))
S.append(f'''  <section class="slide p2 sb-fb" data-name="Focalboard bug" data-marks='{{"Recipient logs in":7,"Fail vs pass":8}}'>
    <div class="c-h sb-fbh">A bug that takes nine steps and two accounts to see</div>
    {glow}
    {"".join(panels)}
{notes}
  </section>''')
CSS.append('''
.sb-fb .c-h.sb-fbh { top: 32px; }
.sb-pan { position: absolute; width: 255px; }
.sb-cap { height: 54px; display: flex; align-items: flex-end; gap: 8px; font-size: 20px; line-height: 1.3; margin-bottom: 8px; }
.sb-cap b { font-weight: 700; }
.sb-win { display: block; width: 255px; height: 291.2px; overflow: visible; }
.sb-pan.fail, .sb-pan.pass { padding: 6px 7px 7px; margin: -6px 0 0 -7px; width: 269px; border-radius: 12px; border: 1.5px solid; }
.sb-pan.fail { background: #fff0ef; border-color: #e8b8b8; }
.sb-pan.pass { background: #ebf8ef; border-color: #b9dfc5; }
.sb-badge { flex: none; width: 24px; height: 24px; border-radius: 50%; color: #fff; font-size: 15px; font-weight: 700; display: flex; align-items: center; justify-content: center; align-self: flex-start; margin-top: 2px; }
.fail .sb-badge { background: #b34646; }
.pass .sb-badge { background: #1f7a3f; }''')

(OUT / 'sections.html').write_text('\n'.join(S) + '\n')
(OUT / 'css.css').write_text('\n'.join(c.strip('\n') for c in CSS) + '\n')
print('wrote', OUT / 'sections.html', OUT / 'css.css', 'slides:', len(S))
