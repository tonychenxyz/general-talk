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


def arc(d, cls, marker, delay=0):
    """An arc that draws itself when its step appears; its arrowhead (a stroke-less copy) fades in at the end."""
    st = f' style="--d:{delay}s"' if delay else ''
    return (f'<path d="{d}" pathLength="1" class="{cls} sb-draw"{st}/>'
            f'<path d="{d}" class="sb-head"{st} marker-end="url(#{marker})"/>')


def label(emo, x, y, lines):
    g = [f'<text x="{x}" y="{y + 13.5}" text-anchor="middle" class="sb-emo">{emo}</text>']
    g += [f'<text x="{x}" y="{y + 29 + i * 13}" text-anchor="middle" class="sb-stage">{esc(t)}</text>' for i, t in enumerate(lines)]
    return ''.join(g)


def loop(top_a, top_b, first, step0):
    """Outer cycle, one stage per step from step0: first stage (top right), Diagnose, Design Fix, Implement, Code Update.
    The arc into each stage draws, then its dot and label fade in; Code Update also closes the loop back to the box."""
    stages = [(first[0], 298, 90, first[1:]), ('🔍', 295, 228, ['Diagnose']), ('💡', 172, 302, ['Design Fix']),
              ('💻', 49, 228, ['Implement']), ('📦', 47, 96, ['Code Update'])]
    g = []
    for k, (emo, x, y, lines) in enumerate(stages):
        dx, dy = DOTS[k]
        body = arc(OUTER[k + 1].format(a=top_a, b=top_b), 'sb-ring', 'sb-outer')
        body += f'<g class="sb-lab"><circle cx="{dx}" cy="{dy}" r="3" fill="#111"/>{label(emo, x, y, lines)}</g>'
        if k == 4:
            body += arc(OUTER[0].format(a=top_a, b=top_b), 'sb-ring', 'sb-outer', delay=0.9)
        g.append(f'<g class="sb-st" data-in="{step0 + k}">{body}</g>')
    return ''.join(g)


def bench(d, col, marker, dot, labels, step):
    lab = ''.join(f'<text x="{x}" y="{y}" text-anchor="middle" class="{c}">{esc(t)}</text>' for x, y, c, t in labels)
    return (f'<g class="sb-st" data-in="{step}"><circle cx="{dot[0]}" cy="{dot[1]}" r="3" fill="{col}"/>'
            f'<g style="stroke:{col};stroke-width:4.5;fill:none">{arc(d, "sb-bench", marker)}</g><g class="sb-lab">{lab}</g></g>')


def arrow_marker(mid, col, size):
    return (f'<marker id="{mid}" viewBox="0 0 8 8" refX="0" refY="4" markerWidth="{size}" markerHeight="{size}" orient="auto" '
            f'markerUnits="userSpaceOnUse"><path d="M0 0 8 4 0 8Z" fill="{col}"/></marker>')


SWE, SENIOR, SWEEP = '#BE776C', '#668499', '#8272B3'
K, X_MIN, X_MAX, Y_MIN, Y_MAX = 2.12, 12, 701, 64, 334           # scale and content extent in paper units
X0 = 800 - (X_MIN + X_MAX) / 2 * K
Y0 = 505 - (Y_MIN + Y_MAX) / 2 * K
SHIFT = (800 - (X0 + 172 * K)) / K                                # centres panel (a) while it is alone
# steps: 0 Deploy, 1-5 stages of (a), 6 SWE-bench, 7 Senior SWE-Bench, 8 Autonomous Sweep, 9-13 stages of (b), 14 SWEeper-Bench
B0 = 8
pa = ['<g class="sb-pa">',
      '<g class="sb-st" data-in="0"><rect x="118" y="64" width="108" height="43" rx="6" fill="#F2E4E1" stroke="#000" stroke-width=".95"/>',
      '<text x="144" y="80.5" text-anchor="middle" class="sb-emo">🌐</text><text x="183" y="81" text-anchor="middle" class="sb-box">Deploy</text>',
      '<text x="131" y="97.5" text-anchor="middle" class="sb-emo sm">🕒</text><text x="139" y="98" class="sb-small">Slow</text>',
      '<text x="183" y="97.5" text-anchor="middle" class="sb-emo sm">💰</text><text x="191" y="98" class="sb-small">Costly</text></g>',
      loop('116,97.36', '228,97.36', ('😠', 'Frustrated', 'User'), 1),
      # SWE-bench: from Design Fix to Code Update
      bench('M172.00,239.00 A54,54 0 0,1 125.23,158.00', SWE, 'sb-swe', (172, 239),
            [(180, 201, 'sb-arc', 'SWE-bench'), (180, 212, 'sb-cite', '(Jimenez et al., 2024)')], 6),
      # Senior SWE-Bench: from Diagnose all the way round to Code Update
      bench('M241.28,145.00 A80,80 0 1,1 102.72,145.00', SENIOR, 'sb-senior', (241.28, 145),
            [(172, 149, 'sb-arc', 'Senior SWE-Bench'), (172, 160, 'sb-cite', '(Ehrenberg et al., 2026)')], 7),
      '</g>']
pb = ['<g class="sb-pb"><g transform="translate(376 0)">',
      f'<g class="sb-st sb-late" data-in="{B0}"><rect x="116" y="64" width="112" height="43" rx="6" fill="#E9E5F3" stroke="#000" stroke-width=".95"/>',
      f'<image href="{uri("broom.png")}" x="120" y="72" width="27" height="27"/>',
      '<text x="187" y="82" text-anchor="middle" class="sb-box sm">Autonomous</text><text x="187" y="96" text-anchor="middle" class="sb-box sm">Sweep</text></g>',
      loop('114,98.68', '230,98.68', ('🐞', 'Problem', 'Discovery'), B0 + 1),
      bench('M183.81,118.03 A68,68 0 1,1 162.54,117.66', SWEEP, 'sb-sweep', (183.81, 118.03),
            [(172, 189, 'sb-arc', 'SWEeper-Bench')], B0 + 6),
      f'</g><path class="sb-st sb-late" data-in="{B0}" d="M360 66V330" stroke="#a8abb2" stroke-width=".8" stroke-dasharray="1 4" stroke-linecap="round"/></g>']
svg = (f'<svg class="sb-svg" viewBox="0 0 1600 900"><defs>{arrow_marker("sb-outer", "#000", 4.5)}{arrow_marker("sb-swe", SWE, 9)}'
       f'{arrow_marker("sb-senior", SENIOR, 9)}{arrow_marker("sb-sweep", SWEEP, 9)}</defs>'
       f'<g transform="translate({X0:.1f} {Y0:.1f}) scale({K})">{"".join(pa)}{"".join(pb)}</g></svg>')
PAR_NOTES = [
    (0, "Here's how software gets fixed today. We deploy, which is slow and costly."),
    (1, "Then a user runs into a bug and gets frustrated."),
    (2, "Someone diagnoses the problem,"),
    (3, "designs a fix,"),
    (4, "implements it,"),
    (5, "and ships a code update. Then we deploy again and wait for the next report."),
    (6, "SWE-bench evaluates only the last part of this loop: it starts from a described issue and asks for the fix."),
    (7, "Senior SWE-Bench covers more, starting at diagnosis. But both start after a user has already reported the bug, and that report only comes after a slow and costly deployment."),
    (B0, "In SWEeper-Bench, the agent closes the loop itself. Instead of deploying and waiting, it sweeps the app autonomously."),
    (B0 + 1, "It has to discover the problem on its own, by exploring the code and the running application,"),
    (B0 + 2, "then diagnose it,"),
    (B0 + 3, "design a fix,"),
    (B0 + 4, "implement it,"),
    (B0 + 5, "and update the code, all before any user ever runs into the bug."),
    (B0 + 6, "SWEeper-Bench evaluates this whole loop."),
]
par_notes = '\n'.join(f'    <div class="note" data-at="{i}">{esc(n)}</div>' for i, n in PAR_NOTES)
S.append(f'''  <section class="slide p2 sb-par" data-name="Waiting vs sweeping" data-classes='{{"sb-two":{B0}}}' data-marks='{{"Autonomous sweep":{B0}}}'>
    <div class="c-h">From waiting for bug reports to sweeping for bugs</div>
    {svg}
{par_notes}
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
.sb-par .sb-cite {{ font-size: 7.5px; font-weight: 400; }}
.sb-par .sb-head {{ fill: none; stroke: none; }}
/* a step group stays visible; its arc draws, then the arrowhead and the stage label fade in */
.sb-par .sb-st.frag-hidden {{ opacity: 0 !important; transition: none; }}
.sb-par .sb-st:not(.frag-hidden) {{ transition: opacity .3s ease; }}
.sb-par .sb-draw {{ stroke-dasharray: 1; stroke-dashoffset: 0; transition: stroke-dashoffset .7s var(--ease) var(--d, 0s); }}
.sb-par .sb-st.frag-hidden .sb-draw {{ stroke-dashoffset: 1; transition: none; }}
.sb-par .sb-head {{ transition: opacity .2s ease calc(var(--d, 0s) + .6s); }}
.sb-par .sb-lab {{ transition: opacity .4s ease .55s; }}
.sb-par .sb-st.frag-hidden .sb-head, .sb-par .sb-st.frag-hidden .sb-lab {{ opacity: 0; transition: none; }}
.sb-par .sb-late:not(.frag-hidden) {{ transition: opacity .6s ease .55s; }}
.sb-pa {{ transform: translateX({SHIFT:.2f}px); transition: transform 1s var(--ease); }}
.sb-two .sb-pa {{ transform: none; }}''')

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
# 3. Focalboard walk-through (paper Figure 5, focalboard-056-procedure.html)
#    Same frames, zoom regions and cursor points as the paper's build_procedure.py (via data.json).
#    Steps 0-7: one action per step, full screen (big screenshot + zoom inset). Step 8: Fail and Pass side by side.
# =====================================================================================
CAPS = ['(1) Log in as miraDunn', '(2) Add board → Create empty board', '(3) Name the board', '(4) Open Share',
        '(5) Search for and select @kadeRue', '(6) Confirm kadeRue appears as a member', '(7) Close Share and log out',
        '(8) Log in as kadeRue and refresh', '<b>Fail</b>: board missing from recipient sidebar',
        '<b>Pass</b>: board listed in recipient sidebar']
P = D['panels']
assert [' '.join(p['caption']) for p in P] == [c.replace('<b>', '').replace('</b>', '') for c in CAPS], 'captions must match the paper'
# slide captions = paper captions without the "(n) " prefix (the number goes in a badge), with line breaks for the side column
STEP_CAPS = ['Log in as miraDunn', 'Add board →<br>Create empty board', 'Name the board', 'Open Share',
             'Search for and select<br>@kadeRue', 'Confirm kadeRue<br>appears as a member', 'Close Share and log out',
             'Log in as kadeRue<br>and refresh']
assert [c.replace('<br>', ' ') for c in STEP_CAPS] == [c.split(') ', 1)[1] for c in CAPS[:8]]
CUR = uri('cursor.png')
BAR = 26                                     # browser-chrome bar height (px)


def window(p, x, y, w, zoom_box, conn, cur=26, zcur=30):
    """SVG (slide coordinates) of one browser window with the screenshot, the zoom region, its inset and the cursor.
    zoom_box = (zx, zy, zw, zh); conn = 'right' (line to the inset's left edge) or 'below' (line to its top edge)."""
    rx, ry, rw, rh = p['region']
    h = w * 1200 / 1920; sc = w / 1920; ix, iy = x, y + BAR
    zx, zy, zw, zh = zoom_box
    bx, by, bw, bh = ix + rx * sc, iy + ry * sc, rw * sc, rh * sc
    g = [f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h + BAR - 1.5}" rx="10" fill="#fff"/>',
         f'<path d="M{x + 10.75} {y + .75}h{w - 21.5}q10 0 10 10v{BAR - 10.75}h{-(w - 1.5)}v{-(BAR - 10.75)}q0-10 10-10" fill="#eef2f6"/>',
         ''.join(f'<circle cx="{x + dx}" cy="{y + BAR / 2}" r="4" fill="#bec6d1"/>' for dx in (16, 30, 44)),
         f'<image x="{ix}" y="{iy}" width="{w}" height="{h:.2f}" href="{uri(p["frame"] + "-lg.png")}" preserveAspectRatio="none"/>',
         f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h + BAR - 1.5}" rx="10" fill="none" stroke="#cdd6e1" stroke-width="1.5"/>',
         f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="none" stroke="#086bea" stroke-width="2.5"/>']
    if conn == 'right':
        g.append(f'<path d="M{bx + bw:.2f} {by + bh / 2:.2f}L{zx} {zy + zh / 2:.2f}" stroke="#7d91a8" stroke-width="1.6"/>')
    else:
        g.append(f'<path d="M{bx + bw / 2:.2f} {by + bh:.2f}L{zx + zw / 2:.2f} {zy}" stroke="#7d91a8" stroke-width="1.6"/>')
    g.append(f'<rect x="{zx - 1}" y="{zy - 1}" width="{zw + 2}" height="{zh + 2}" rx="4" fill="#fff" stroke="#086bea" stroke-width="2"/>'
             f'<image x="{zx}" y="{zy}" width="{zw}" height="{zh}" href="{uri(p["frame"] + "-zoom.png")}" preserveAspectRatio="xMidYMid meet"/>')
    if p['point']:
        px, py = p['point']
        g.append(f'<image x="{ix + px * sc:.2f}" y="{iy + py * sc:.2f}" width="{cur}" height="{cur * 48 / 46:.1f}" filter="url(#sb-glow)" href="{CUR}"/>')
        if rx <= px <= rx + rw and ry <= py <= ry + rh:
            z = zw / rw
            g.append(f'<image x="{zx + (px - rx) * z:.2f}" y="{zy + (py - ry) * z:.2f}" width="{zcur}" height="{zcur * 48 / 46:.1f}" filter="url(#sb-glow)" href="{CUR}"/>')
    return ''.join(g)


# --- steps (1)-(8): window on the left, caption + zoom inset in the right column, the pair centred on the slide
WX, WW, COLX, COLW = 100, 880, 1036, 464
WH = WW * 1200 / 1920 + BAR
WY = round(498 - WH / 2)
LINE, CAPGAP = 40, 26
views = []
for i, p in enumerate(P[:8]):
    rx, ry, rw, rh = p['region']
    nl = STEP_CAPS[i].count('<br>') + 1
    z = min(COLW / rw, (WH - 2 * LINE - CAPGAP) / rh, 2.2)
    zw, zh = rw * z, rh * z
    top = WY + (WH - (nl * LINE + CAPGAP + zh)) / 2
    zy = top + nl * LINE + CAPGAP
    svg = f'<svg class="sb-svg">{window(p, WX, WY, WW, (COLX, round(zy, 1), round(zw, 1), round(zh, 1)), "right")}</svg>'
    views.append(f'<div class="sb-view" data-in="{i}" data-out="{i + 1}">{svg}'
                 f'<div class="sb-scap" style="left:{COLX}px;top:{top:.0f}px;width:{COLW}px"><span class="sb-num">{i + 1}</span>'
                 f'<span>{STEP_CAPS[i]}</span></div></div>')

# --- step 9: Fail and Pass side by side, each a window with its sidebar zoom underneath
FW, FGAP, PAD = 600, 100, 20
FX0 = (1600 - 2 * FW - FGAP) / 2
FTOP, FBOT, FCAP_Y, FWIN_Y = 150, 842, 166, 222
FH = FW * 1200 / 1920 + BAR
FZY = FWIN_Y + FH + 22
zs = (FBOT - 18 - FZY) / max(p['region'][3] for p in P[8:])     # one zoom scale for both, sized to fit the taller crop
finals = []
for j, p in enumerate(P[8:]):
    x = FX0 + j * (FW + FGAP)
    rx, ry, rw, rh = p['region']
    kind, mark = ('fail', '✕') if j == 0 else ('pass', '✓')
    zw = rw * zs
    zbox = (round(x + (FW - zw) / 2, 1), round(FZY, 1), round(zw, 1), round(rh * zs, 1))
    svg = f'<svg class="sb-svg">{window(p, x, FWIN_Y, FW, zbox, "below")}</svg>'
    finals.append(f'<div class="sb-fin {kind}" style="left:{x - PAD:.0f}px;top:{FTOP}px;width:{FW + 2 * PAD}px;height:{FBOT - FTOP}px"></div>{svg}'
                  f'<div class="sb-fcap" style="left:{x:.0f}px;top:{FCAP_Y}px;width:{FW}px"><span class="sb-badge {kind}">{mark}</span><span>{CAPS[8 + j]}</span></div>')
views.append(f'<div class="sb-view" data-in="8">{"".join(finals)}</div>')
glow = ('<svg width="0" height="0" style="position:absolute"><defs><filter id="sb-glow" x="-100%" y="-100%" width="300%" height="300%">'
        '<feDropShadow dx="0" dy="0" stdDeviation="2" flood-color="#2684ff" flood-opacity=".8"/></filter></defs></svg>')
NOTES = [
    "Here's one task. Focalboard is a project board tool. The verifier first logs in as one user, miraDunn.",
    "It adds a board and picks Create empty board.",
    "It names the board, Q3 Launch Desk.",
    "It opens the Share dialog.",
    "It searches for a second user, kadeRue, and selects him.",
    "And confirms kadeRue now appears as a member. Everything looks fine to the person sharing.",
    "It closes Share and logs out.",
    "Then it logs in as kadeRue and refreshes the page.",
    "With the bug, the shared board is missing from kadeRue's sidebar. He can still open it through a direct link, so nothing looks broken unless you check his sidebar. Adding a member saves the membership but never files the board under the member's default sidebar category. "
    "With the fix, the board shows up in his sidebar. The fix is a single function call. But the failure only appears after nine steps across two accounts, and the agent is only told: find and fix all issues in Focalboard's board sharing and membership.",
]
notes = '\n'.join(f'    <div class="note" data-at="{i}">{esc(n)}</div>' for i, n in enumerate(NOTES))
S.append(f'''  <section class="slide p2 sb-fb" data-name="Focalboard bug" data-marks='{{"Recipient logs in":7,"Fail vs pass":8}}'>
    <div class="c-h">A bug that takes nine steps and two accounts to see</div>
    {glow}
    {"".join(views)}
{notes}
  </section>''')
CSS.append('''
.sb-view { position: absolute; inset: 0; }
.sb-view .sb-svg { pointer-events: none; }
.sb-scap { position: absolute; display: flex; align-items: flex-start; gap: 16px; font-size: 32px; line-height: 40px; font-weight: 600; letter-spacing: -.01em; }
.sb-num { flex: none; width: 40px; height: 40px; border-radius: 50%; background: #1f2328; color: #fff; font-size: 22px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.sb-fin { position: absolute; border-radius: 16px; border: 1.5px solid; }
.sb-fin.fail { background: #fff0ef; border-color: #e8b8b8; }
.sb-fin.pass { background: #ebf8ef; border-color: #b9dfc5; }
.sb-fcap { position: absolute; display: flex; align-items: center; gap: 14px; font-size: 28px; line-height: 40px; white-space: nowrap; }
.sb-fcap b { font-weight: 700; }
.sb-badge { flex: none; width: 36px; height: 36px; border-radius: 50%; color: #fff; font-size: 21px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.sb-badge.fail { background: #b34646; }
.sb-badge.pass { background: #1f7a3f; }''')

(OUT / 'sections.html').write_text('\n'.join(S) + '\n')
(OUT / 'css.css').write_text('\n'.join(c.strip('\n') for c in CSS) + '\n')
print('wrote', OUT / 'sections.html', OUT / 'css.css', 'slides:', len(S))
