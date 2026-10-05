"""Extract what build.py needs for part 6a (SWEeper-Bench task construction) into committed files.

  fig.html   - the paper's Figure 3 ("Task execution and verification", fig_pipeline) from
               sweeper-bench-plotting/index.html: its CSS + body markup, after headless Chrome ran the page's
               own layout script, so the two elbow connectors carry their computed `d` paths. Fonts are dropped
               (the deck already inlines Inter), the click-to-enlarge originals are dropped, the agent logo is
               downscaled.  Layout size of the figure is stored in data.json.
  data.json  - paper Table 1 (tab:robustness), parsed from the tex, plus the figure size.
  logos/     - provider logos (openai, claude) copied from sweeper-bench-plotting/assets/provider-logos.

Run once: python3 src/part6a/extract.py   (needs the Playwright Chromium in ~/.cache/ms-playwright)
"""
import base64, glob, io, json, pathlib, re, shutil, subprocess, tempfile
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SB = pathlib.Path('/scratch/gpfs/ZHUANGL/hc5019/sweeperbench_public')
PLOT = SB / 'sweeper-bench-plotting'
TEX = SB / 'overleaf' / 'iclr2027_conference.tex'
CHROME = glob.glob(str(pathlib.Path.home() / '.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))[0]

# ---------- figure: run its layout script in Chrome, then dump the DOM ----------
src = (PLOT / 'index.html').read_text()
probe = ('<script>window.addEventListener("load",()=>{fit();const f=document.querySelector(".flow").getBoundingClientRect();'
         'document.body.dataset.size=f.width+"x"+f.height;});</script></body>')
with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / 'fig.html'
    p.write_text(src.replace('</body>', probe))
    dom = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1600,900',
                          '--virtual-time-budget=4000', '--dump-dom', p.as_uri()],
                         capture_output=True, text=True, timeout=120).stdout
w, h = map(float, re.search(r'data-size="([\d.]+)x([\d.]+)"', dom).group(1, 2))

css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)            # first <style>: layout (second = fonts)
defs = re.search(r'<svg style="position:absolute;width:0;height:0".*?</svg>', dom, re.S).group(0)
main = re.search(r'<main>(.*?)</main>', dom, re.S).group(1)
main = re.sub(r'<a class="frame-link"[^>]*>(.*?)</a>', r'\1', main, flags=re.S)   # drop click-to-enlarge originals
for d in ('agent-sandbox', 'pr-verifier'):
    assert re.search(rf'<path id="{d}"[^>]* d="M [^"]+"', main), d


def shrink(m):   # the agent logo is a 893px PNG shown at ~20px; 128px is plenty even zoomed in
    im = Image.open(io.BytesIO(base64.b64decode(m.group(1))))
    im.thumbnail((128, 128), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'class="agent-logo" src="data:image/png;base64,' + base64.b64encode(b.getvalue()).decode() + '"'


main = re.sub(r'class="agent-logo" src="data:image/png;base64,([^"]+)"', shrink, main)
(HERE / 'fig.html').write_text(f'<style>{css}</style>\n{defs}\n<main>{main}</main>\n')

# ---------- Table 1 (tab:robustness) ----------
tex = TEX.read_text()
tab = re.search(r'\\begin\{tabular\}\{lccccc\}(.*?)\\end\{tabular\}.*?\\label\{tab:robustness\}', tex, re.S).group(1)
rows = []
for icon, name, rest in re.findall(r'\\sweepermodelname\{(\w+)\}\{([^}]*)\}(.*?)\\\\', tab):
    cells = [c.strip() for c in rest.strip().lstrip('&').split('&')]
    pm = [tuple(float(x) for x in re.findall(r'[\d.]+', c)) for c in cells[:4]]
    model, harness = [s.strip() for s in name.split(',')]
    rows.append({'icon': icon, 'model': model, 'harness': harness,
                 'buggy_target': pm[0], 'buggy_pres': pm[1], 'fix_target': pm[2], 'fix_pres': pm[3],
                 'cost': cells[4].replace('\\$', '$')})
assert len(rows) == 3, rows
json.dump({'fig_size': [w, h], 'robustness': rows}, open(HERE / 'data.json', 'w'), indent=1)

(HERE / 'logos').mkdir(exist_ok=True)
for f in ('openai.svg', 'claude-color.svg'):
    shutil.copy(PLOT / 'assets' / 'provider-logos' / f, HERE / 'logos' / f)
print('figure', w, 'x', h, '| fig.html', len((HERE / 'fig.html').read_text()) // 1000, 'kB')
for r in rows: print(r)
