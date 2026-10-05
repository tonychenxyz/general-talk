"""Part 5b · copy the SWEeper-Bench paper-figure inputs into this folder so build.py is reproducible.

Sources (sweeper-bench-plotting repo):
  analysis/task_domains/manifest.json + repo_stars.csv  -> data.json["domains"], data.json["median_stars"]  (paper Fig. 4)
  assets/focalboard-056/build_procedure.py panel table   -> data.json["panels"]                             (paper Fig. 5)
  assets/focalboard-056/<frame>.png                      -> img/<frame>.png (downscaled), <frame>-lg.png (1280x800) + img/<frame>-zoom.png (native crop)
  assets/autonomous-sweep.png, browser-agent-cursor.png -> img/                                              (paper Fig. 1)
"""
import csv, json, pathlib, statistics
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path('/scratch/gpfs/ZHUANGL/hc5019/sweeperbench_public/sweeper-bench-plotting')
IMG = HERE / 'img'
IMG.mkdir(exist_ok=True)

man = json.load(open(SRC / 'analysis/task_domains/manifest.json'))
stars = [int(r['stars']) for r in csv.DictReader(open(SRC / 'analysis/task_domains/repo_stars.csv')) if r['stars'].strip()]
assert sum(d['tasks'] for d in man['domains']) == 200

# panel table copied verbatim from assets/focalboard-056/build_procedure.py: (caption lines, frame, zoom region x,y,w,h, cursor point)
PANELS = [
    (['(1) Log in as', 'miraDunn'], '01-login', (730, 145, 465, 410), (960, 360)),
    (['(2) Add board →', 'Create empty board'], '03-empty', (1225, 625, 220, 90), (1335, 667)),
    (['(3) Name the board'], '04-name', (255, 65, 450, 95), (410, 96)),
    (['(4) Open Share'], '06-share', (655, 318, 610, 170), (1840, 96)),
    (['(5) Search for and', 'select @kadeRue'], '08-select', (680, 405, 555, 110), (835, 455)),
    (['(6) Confirm kadeRue', 'appears as a member'], '09-member', (682, 530, 550, 66), None),
    (['(7) Close Share', 'and log out'], '12-logout', (0, 50, 245, 265), (70, 218)),
    (['(8) Log in as', 'kadeRue and refresh'], '13-recipient-login', (730, 145, 465, 410), (960, 360)),
    (['Fail: board missing', 'from recipient', 'sidebar'], '15-fail', (0, 171, 240, 80), None),
    (['Pass: board listed', 'in recipient', 'sidebar'], '16-pass', (0, 171, 240, 110), None),
]
for _, name, (x, y, w, h), _ in PANELS:
    im = Image.open(SRC / 'assets/focalboard-056' / f'{name}.png').convert('RGB')
    assert im.size == (1920, 1200)
    im.crop((x, y, x + w, y + h)).save(IMG / f'{name}-zoom.png', optimize=True)
    im.resize((800, 500), Image.LANCZOS).save(IMG / f'{name}.png', optimize=True)
    im.resize((1280, 800), Image.LANCZOS).save(IMG / f'{name}-lg.png', optimize=True)   # full-screen step views

broom = Image.open(SRC / 'assets/autonomous-sweep.png')
broom.thumbnail((240, 240), Image.LANCZOS)
broom.save(IMG / 'broom.png', optimize=True)
Image.open(SRC / 'assets/browser-agent-cursor.png').save(IMG / 'cursor.png', optimize=True)

json.dump({'domains': man['domains'], 'stars_source': man['stars_source'],
           'median_stars': statistics.median(stars), 'repos_with_stars': len(stars),
           'panels': [{'caption': c, 'frame': n, 'region': r, 'point': p} for c, n, r, p in PANELS]},
          open(HERE / 'data.json', 'w'), indent=1, ensure_ascii=False)
print('wrote data.json and', len(list(IMG.iterdir())), 'images')
