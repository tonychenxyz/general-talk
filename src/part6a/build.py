"""Part 6a · SWEeper-Bench task construction: the paper's Figure 3 (fig_pipeline) built up component by component,
then a zoom into the verifier with paper Table 1 (tab:robustness) beside it.

Inputs (committed, produced by extract.py): fig.html, data.json, logos/.
Outputs: out/sections.html, out/css.css (spliced into the deck by ../merge_parts.py). All classes/ids prefixed ra-.
"""
import base64, html, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'out'
D = json.load(open(HERE / 'data.json'))
FIG_W, FIG_H = D['fig_size']

# ---------------- figure: prefix classes + ids, scope CSS ----------------
fig = (HERE / 'fig.html').read_text()
fcss = re.search(r'<style>(.*?)</style>', fig, re.S).group(1)
fbody = fig[fig.index('</style>') + len('</style>'):].strip()

fcss = re.sub(r'/\*.*?\*/', '', fcss, flags=re.S)
fcss = re.sub(r'@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', fcss)   # print / narrow-window rules


def scope_css(css, prefix):
    out = []
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        sels = []
        for s in sel.split(','):
            s = s.strip()
            if not s or re.search(r'lightbox|close|button|source|frame-link', s):
                continue
            s = re.sub(r'\.(?=[A-Za-z_])([\w-]+)', r'.ra-\1', s)
            s = re.sub(r'#(?=[A-Za-z_])([\w-]+)', r'#ra-\1', s)
            sels.append(prefix if s in (':root', 'html', 'body') else prefix + ' ' + s)
        if sels:
            out.append(', '.join(dict.fromkeys(sels)) + '{' + body.strip() + '}')
    return '\n'.join(out)


fcss = scope_css(fcss, '.ra-fig')
fbody = re.sub(r'class="([^"]+)"', lambda m: 'class="' + ' '.join('ra-' + c for c in m.group(1).split()) + '"', fbody)
fbody = re.sub(r'\bid="([\w-]+)"', r'id="ra-\1"', fbody)
fbody = re.sub(r'href="#([\w-]+)"', r'href="#ra-\1"', fbody)
fbody = fbody.replace('url(#arrowhead)', 'url(#ra-arrowhead)')
fbody = re.sub(r'<(/?)section\b', r'<\1div', fbody)          # avoid any section-level deck rules
fbody = fbody.replace('<main>', '<div class="ra-main">').replace('</main>', '</div>')
fcss = fcss.replace('.ra-fig main', '.ra-fig .ra-main')


def tag(body, needle, n, nth=1, rise=True):
    """Add data-in=n (and the deck's rise class) to the nth occurrence of opening tag `needle`."""
    i = -1
    for _ in range(nth):
        i = body.index(needle, i + 1)
    new = needle[:-1] + f' data-in="{n}">'
    if rise and 'class="' in new:
        new = new.replace('class="', 'class="rise ', 1)
    return body[:i] + new + body[i + len(needle):]


# reading order: codebase, prompt, agent, hidden bug, sandbox, PR, workflow, verifier, outcome
B = fbody
B = tag(B, '<div class="ra-divider">', 1, rise=False)
B = tag(B, '<h2>', 1, nth=2)                                   # "Prompt" heading (1st <h2> is "Codebase")
B = tag(B, '<p class="ra-prompt">', 1)
B = tag(B, '<div class="ra-down">', 2, rise=False)      # input -> agent
B = tag(B, '<h2 class="ra-agent">', 2)
B = tag(B, '<div class="ra-hidden-bug">', 3)
B = B.replace('<path id="ra-agent-sandbox"', '<path data-in="4" id="ra-agent-sandbox"')
B = tag(B, '<div class="ra-sandbox">', 4)
B = tag(B, '<div class="ra-down">', 5, rise=False)      # sandbox -> PR (earlier ones are already tagged)
B = tag(B, '<div class="ra-pr">', 5)
B = tag(B, '<div class="ra-workflow ra-separate">', 6)
B = tag(B, '<div class="ra-down">', 7, rise=False)      # workflow -> verifier
B = B.replace('<path id="ra-pr-verifier"', '<path data-in="7" id="ra-pr-verifier"')
B = tag(B, '<div class="ra-verifier">', 7)
B = tag(B, '<div class="ra-down ra-status-down">', 8, rise=False)
B = tag(B, '<div class="ra-status">', 8)
assert B.count('data-in=') == 16, B.count('data-in=')

# ---------------- geometry ----------------
S1, X1 = 2.0, (1600 - 2.0 * FIG_W) / 2                   # whole figure: 1440 x 552
Y1 = round((150 + 840) / 2 - S1 * FIG_H / 2)              # centered between title and bottom
VX = 484                                                  # left edge of the verifier column in figure px (grid 212+16+240+16)
S2 = 2.4                                                  # zoomed: verifier column ~566 x 662
VW = FIG_W - VX                                           # verifier column width in figure px
DY = 172 - Y1
DXC = (1600 - S2 * VW) / 2 - X1 - S2 * VX                 # step 9: zoomed column centered
DX = 100 - X1 - S2 * VX                                   # step 10: column moves left, table on the right


# ---------------- Table 1, simplified ----------------
def logo(name):
    svg = (HERE / 'logos' / f'{name}.svg').read_text()
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


LOGO = {'openai': logo('openai'), 'claude': logo('claude-color')}
COLS = [('buggy_target', 0), ('buggy_pres', 100), ('fix_target', 100), ('fix_pres', 100)]


def num(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.') if v not in (0, 100) else f'{v:.0f}'


rows = []
for r in D['robustness']:
    cells = ''.join(f'<div class="ra-v">{num(r[k][0])}%</div>' for k, _ in COLS)
    rows.append(f'<div class="ra-row"><div class="ra-cfg"><img src="{LOGO[r["icon"]]}" alt="">'
                f'<div><b>{html.escape(r["model"])}</b><span>{html.escape(r["harness"])}</span></div></div>{cells}</div>')
max_sd = max(r[k][1] for r in D['robustness'] for k in ('buggy_target', 'buggy_pres', 'fix_target', 'fix_pres'))
table = f'''<div class="ra-tab" data-in="10">
      <div class="ra-grp"><div></div><div class="ra-span2">Buggy app</div><div class="ra-span2">Reference fix</div></div>
      <div class="ra-hd"><div></div><div>Target test</div><div>Preservation test</div><div>Target test</div><div>Preservation test</div></div>
      <div class="ra-row ra-ideal"><div class="ra-cfg">Ideal</div><div>0%</div><div>100%</div><div>100%</div><div>100%</div></div>
      {"".join(rows)}
    </div>'''

luna_codex, luna_bu, sonnet = D['robustness']
notes = [
    "Here is how one task runs, using a real task from SearXNG, an open-source search engine. "
    "The agent gets the codebase at the buggy version: the parent commit of a merged pull request that fixed a user-facing bug.",
    "And it gets a one-sentence, open-ended prompt that only names a product area: find and fix issues in SearXNG's search "
    "suggestion interface. It doesn't say what is broken, where the code lives, or how to reproduce it. "
    "It's like asking a colleague to sweep a feature before release.",
    "A language model agent gets the codebase and the prompt.",
    "The bug itself is hidden from the agent. Here, query suggestions that contain an ampersand get HTML-escaped in the dropdown. "
    "The agent never sees the issue, the pull request, the reference patch, the repository history, or our tests.",
    "The agent works in an isolated sandbox: the source code, a running instance of the app that reflects its edits, a terminal, "
    "and a Chromium browser with Playwright. Outbound network access is blocked. "
    "It decides for itself what to read, what to test, and when to stop. Here it scripted the browser and checked that special characters show up as plain text.",
    "When it stops, we take only its code changes. Here, a one-line diff that removes the escape call.",
    "To check the fix, each task has behavior tests, written as step-by-step user instructions with explicit pass and fail criteria. "
    "Here: type AT-ampersand in the search bar and wait at least a second.",
    "An agentic verifier applies the patch to a fresh copy of the app and follows those steps in the browser. "
    "It never sees the source code. It judges only what a user would observe.",
    "And it reports the outcome: pass if AT&T shows up with no escaped ampersand, fail if the text is escaped or there are no suggestions. "
    "Each task has two such tests: a target test that reproduces the bug, and a preservation test that checks nearby features still work. "
    "A task passes only if both pass.",
    "But can we trust an agent as the judge? Let's zoom in on the verifier.",
    "We ran both tests on the buggy version and on the reference fix, with three verifier configurations, three times each, on all 200 tasks. "
    "An accurate verifier never passes the target test on the buggy app, and always passes it on the reference fix. "
    f"All three are within one point of that: {num(luna_codex['buggy_target'][0])} percent on the buggy app, "
    f"{num(luna_codex['fix_target'][0])} percent on the fix. The preservation test passes on both versions, 99 to 100 percent. "
    f"And across runs, the standard deviation is at most {max_sd:g} points. "
    f"So we use the cheapest one, GPT-5.6 Luna with Codex, at about {round(float(luna_codex['cost'].lstrip('$')) * 100)} cents a task, "
    f"versus {luna_bu['cost']} with Browser Use and {sonnet['cost']} for Claude Sonnet 5.",
]
note_html = '\n'.join(f'    <div class="note" data-at="{i}">{html.escape(t)}</div>' for i, t in enumerate(notes))

sec = f'''  <section class="slide p2 ra-s" data-name="How a task runs" data-classes='{{"ra-zoom": 9, "ra-side": 10}}' data-marks='{{"Verifier": 9}}'>
    <div class="c-h" data-out="9">How a task runs</div>
    <div class="c-h" data-in="9" data-out="10">Can we trust the verifier?</div>
    <div class="c-h" data-in="10">The verifier is accurate and consistent</div>
    <div class="ra-fig">
{B}
    </div>
    {table}
{note_html}
  </section>
'''

css = fcss + f'''
.ra-s .ra-fig {{ position: absolute; left: {X1:g}px; top: {Y1}px; width: {FIG_W:g}px; transform-origin: 0 0;
  transform: scale({S1}); transition: transform 1.2s var(--ease); }}
.ra-fig .ra-main {{ width: {FIG_W:g}px; margin: 0; padding: 0; }}
.ra-fig .ra-left-column, .ra-fig .ra-build-column, .ra-fig .ra-connectors {{ transition: opacity .6s ease; }}
.ra-zoom .ra-fig {{ transform: translate({DXC:.1f}px, {DY}px) scale({S2}); }}
.ra-side .ra-fig {{ transform: translate({DX:.1f}px, {DY}px) scale({S2}); }}
.ra-zoom .ra-fig .ra-left-column, .ra-zoom .ra-fig .ra-build-column, .ra-zoom .ra-fig .ra-connectors {{ opacity: 0; }}
.ra-fig .rise.frag-hidden {{ transform: translateY(6px); }}

.ra-tab {{ position: absolute; left: 725px; top: 503px; transform: translateY(-50%); width: 775px; font-size: 22px; color: var(--text); }}
.ra-tab.frag-hidden {{ transform: translateY(-50%); }}
.ra-tab .ra-grp, .ra-tab .ra-hd, .ra-tab .ra-row {{ display: grid; grid-template-columns: 250px 131px 131px 131px 131px; align-items: center; }}
.ra-tab .ra-grp > div, .ra-tab .ra-hd > div, .ra-tab .ra-row > div:not(.ra-cfg) {{ text-align: center; }}
.ra-tab .ra-grp {{ font-size: 24px; font-weight: 600; }}
.ra-tab .ra-grp > div:not(:empty) {{ margin: 0 10px; padding-bottom: 8px; border-bottom: 2px solid var(--text); }}
.ra-tab .ra-span2 {{ grid-column: span 2; }}
.ra-tab .ra-hd {{ font-size: 20px; padding: 10px 0 14px; line-height: 1.25; }}
.ra-tab .ra-row {{ height: 112px; border-top: 1px solid var(--faint); }}
.ra-tab .ra-ideal {{ height: 84px; font-size: 28px; font-weight: 600; color: var(--text); border-top: 0; }}
.ra-tab .ra-ideal .ra-cfg {{ color: var(--text); font-size: 22px; }}
.ra-tab .ra-cfg {{ display: flex; align-items: center; gap: 16px; }}
.ra-tab .ra-cfg img {{ width: 40px; height: 40px; flex: none; }}
.ra-tab .ra-cfg b {{ display: block; font-size: 24px; font-weight: 600; }}
.ra-tab .ra-cfg span {{ display: block; font-size: 20px; margin-top: 2px; }}
.ra-tab .ra-v {{ justify-self: center; font-size: 28px; font-weight: 600; font-variant-numeric: tabular-nums;
  background: var(--c-green-soft); color: var(--text); border-radius: 12px; padding: 6px 12px; min-width: 112px; text-align: center; }}
'''

OUT.mkdir(exist_ok=True)
(OUT / 'sections.html').write_text(sec)
(OUT / 'css.css').write_text(css)
print('wrote', OUT / 'sections.html', len(sec) // 1000, 'kB;', 'css', len(css) // 1000, 'kB')
