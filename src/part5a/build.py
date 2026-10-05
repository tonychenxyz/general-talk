"""Part 5a · opening of the SWEeper-Bench half: "Discovery" title, the iPhone glitch video, the RSVP story, and the
SWEeper-Bench title. Writes out/sections.html + out/css.css (merged into the deck by src/merge_parts.py).

Assets (icon, Claude mark, video poster) come from extract.py. All classes are prefixed sa-.
The story follows the explainer video's script (sweeperbench_public/video/audio/dialogue.json), in the deck's style.
"""
import base64, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)


def uri(name, mime):
    return f'data:{mime};base64,' + base64.b64encode((HERE / name).read_bytes()).decode()


ICON = uri('icon_sweeper.png', 'image/png')
POSTER = uri('poster.jpg', 'image/jpeg')
CLAUDE = (HERE / 'claude-color.svg').read_text().strip()
CLAUDE = re.sub(r'<title>.*?</title>', '', CLAUDE)
CLAUDE = CLAUDE.replace('height="1em" style="flex:none;line-height:1"', 'class="sa-cl"').replace(' width="1em"', '')
CPATH = re.search(r'<path d="([^"]+)"', CLAUDE).group(1)


def notes(*lines):
    return '\n'.join(f'    <div class="note" data-at="{i}">{t}</div>' for i, t in lines)


S = []

# ---------- 1. Discovery title ----------
S.append(f'''  <section class="slide p2" data-name="Discovery title">
    <div class="title">
      <div class="sa-kick">Open-ended task #2</div>
      <h1>Discovery</h1>
      <div class="temo">🔍</div>
      <div class="by sa-sub rise" data-in="1">Specifically, hunting for <b>bugs</b> in <b>interactive software</b></div>
    </div>
{notes((0, "That brings me to the second category of open-ended task: discovery."),
       (1, "Specifically, hunting for bugs in interactive software."))}
  </section>''')

# ---------- 2. iPhone glitch video ----------
S.append(f'''  <section class="slide p2" data-name="iPhone glitch">
    <video class="sa-vid" src="media/iphone-glitch.mp4" poster="{POSTER}" playsinline preload="auto" controls></video>
    <script>(() => {{
      const s = document.currentScript.closest("section"), v = s.querySelector("video");
      let on = false;
      v.addEventListener("click", e => e.stopPropagation());   // clicks on the player must not advance the slide
      new MutationObserver(() => {{
        const a = s.classList.contains("active");
        if (a === on) return;
        on = a;
        if (a) {{ v.currentTime = 0; v.play().catch(() => {{}}); }} else v.pause();
      }}).observe(s, {{ attributes: true, attributeFilter: ["class"] }});
    }})();</script>
{notes((0, "Here's what I mean. Someone plays with a widget on their iPhone home screen, and after just the right sequence of touches, it breaks: the widget turns into an empty box. Bugs like this only show up after a particular sequence of interactions, and today it's usually the users who find them. (Video via @techdroider on X.)"))}
  </section>''')

# ---------- 3. RSVP story ----------
# guests: (avatar, name, detail, what goes wrong for them)
GUESTS = [('👵', 'Grandma', 'old iPad, huge text', 'Can’t find Send'),
          ('🧑', 'Cousin', 'in Tokyo', 'Shows Friday'),
          ('🧑‍🤝‍🧑', 'Two friends', 'send at once', 'One reply lost'),
          ('🧔', 'On a train', 'taps twice', 'Counted twice')]
# small drawn status icons (no emoji in labels)
IC_BAD = ('<svg class="sa-ic" viewBox="0 0 20 20"><circle cx="10" cy="10" r="10" fill="#cd3500"/>'
          '<path d="M6.6 6.6l6.8 6.8M13.4 6.6l-6.8 6.8" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg>')
IC_OK = ('<svg class="sa-ic" viewBox="0 0 20 20"><circle cx="10" cy="10" r="10" fill="#00875a"/>'
         '<path d="M5.6 10.4l3 3 5.8-6.6" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
cards = []
for i, (av, name, det, bug) in enumerate(GUESTS):
    x, y = 1040 + (i % 2) * 240, 230 + (i // 2) * 250
    d = f'--d:{i * .25:.2f}s'
    cards.append(f'''      <div class="sa-card" data-in="2" style="left:{x}px;top:{y}px;{d}">
        <div class="sa-av">{av}<span class="sa-mood" data-in="4" data-out="7" style="{d}">😤</span><span class="sa-mood" data-in="10" style="{d}">😊</span></div>
        <div class="sa-nm">{name}</div><div class="sa-det">{det}</div>
        <div class="sa-pill sa-bad" data-in="3" data-out="7" style="{d}">{IC_BAD}{bug}</div>
        <div class="sa-pill sa-good" data-in="10" style="{d}">{IC_OK}Works</div>
      </div>''')

HEADS = [(0, 1, 'Today, writing software is a quick ask'),
         (1, 2, 'Minutes later, it’s done'),
         (2, 3, 'Off it goes, to every guest'),
         (3, 4, 'Each of them finds something different'),
         (4, 5, 'It all comes back to you'),
         (5, 6, 'You tell Claude…'),
         (6, 7, '…Claude fixes it, and everyone waits'),
         (7, 9, 'What if Claude didn’t have to wait?'),
         (9, 10, 'It uses the app itself, again and again'),
         (10, 99, 'Until whatever reaches people just works')]
heads = '\n'.join(f'    <div class="c-h sa-h" data-in="{a}"' + (f' data-out="{b}"' if b < 99 else '') + f'>{t}</div>' for a, b, t in HEADS)

LOOP = 'M835 160 H900 A90 90 0 0 1 990 250 V690 A90 90 0 0 1 900 780 H770 A90 90 0 0 1 680 690 V250 A90 90 0 0 1 770 160 Z'   # clockwise loop around the app
S.append(f'''  <section class="slide p2 sa-story" data-name="RSVP story" data-classes='{{"sa-p1":1,"sa-p2":2,"sa-dim":7,"sa-ok":10}}'
    data-marks='{{"Send to guests":2,"Everyone waits":6,"What if…":7,"Loop":9}}'>
{heads}
    <div class="sa-stage">
    <svg class="sa-svg" viewBox="0 0 1600 900">
      <defs><marker id="sa-ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#0a2540"/></marker>
      <marker id="sa-ahr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#cd3500"/></marker></defs>
      <line data-in="1" data-out="5" x1="292" y1="470" x2="372" y2="470" stroke="#0a2540" stroke-width="4" marker-end="url(#sa-ah)"/>
      <line data-in="7" x1="292" y1="470" x2="372" y2="470" stroke="#0a2540" stroke-width="4" marker-end="url(#sa-ah)"/>
      <line data-in="1" x1="548" y1="470" x2="696" y2="470" stroke="#0a2540" stroke-width="4" marker-end="url(#sa-ah)"/>
      <line data-in="2" x1="970" y1="470" x2="1026" y2="470" stroke="#0a2540" stroke-width="4" marker-end="url(#sa-ah)"/>
      <line data-in="5" data-out="7" x1="292" y1="470" x2="372" y2="470" stroke="#cd3500" stroke-width="4" stroke-dasharray="10 9" marker-end="url(#sa-ahr)"/>
      <path data-in="4" data-out="7" d="M1270 728 Q 780 920 200 590" fill="none" stroke="#cd3500" stroke-width="4" stroke-dasharray="10 9" marker-end="url(#sa-ahr)"/>
      <g data-in="9" class="sa-loop">
        <path d="{LOOP}" fill="none" stroke="#286ee0" stroke-width="3" stroke-dasharray="2 10" stroke-linecap="round"/>
        <g><circle r="24" fill="#fff" stroke="#D97757" stroke-width="2.5"/><path transform="translate(-15 -15) scale(1.25)" d="{CPATH}" fill="#D97757"/>
          <animateMotion dur="4s" repeatCount="indefinite" path="{LOOP}"/></g>
      </g>
    </svg>
    <div class="sa-you"><div class="sa-e">👩</div><div class="sa-lb">You</div></div>
    <div class="sa-claude">{CLAUDE}<div class="sa-lb">Claude</div></div>
    <div class="sa-bub rise" data-out="1">Hey Claude, can you make us an RSVP site for the wedding?</div>
    <div class="sa-bub rise" data-in="5" data-out="7">Um, Claude? Grandma can’t find the send button…</div>
    <div class="sa-bub rise" data-in="8" data-out="9">Find and fix issues in the RSVP page.</div>
    <div class="sa-wait rise" data-in="6" data-out="7">Everyone waits</div>
    <div class="sa-phone rise" data-in="1">
      <div class="sa-notch"></div>
      <div class="sa-ttl">RSVP</div>
      <div class="sa-who">Lia &amp; Tom</div>
      <div class="sa-date">Saturday, June 14</div>
      <div class="sa-field">Your name</div>
      <div class="sa-yn"><span class="on">Yes</span><span>No</span></div>
      <div class="sa-send">Send RSVP</div>
      <div class="sa-cur" data-in="9">👆</div>
    </div>
    <div class="sa-step" data-in="9" style="left:835px;top:160px">Click</div>
    <div class="sa-step" data-in="9" style="left:964px;top:754px;--d:.3s">Break</div>
    <div class="sa-step" data-in="9" style="left:706px;top:754px;--d:.6s">Fix</div>
    <div class="sa-guests">
{chr(10).join(cards)}
    </div>
    </div>
{notes((0, "These days, when we need a bit of software, we just ask for it: “Hey Claude, can you make us an RSVP site for the wedding?”"),
       (1, "A few minutes later, it's done."),
       (2, "And off it goes, to everyone on the guest list. Then people actually use it. Grandma, on an old iPad, text turned way up. A cousin in Tokyo. Two friends, hitting send at the same moment. Someone on a train, tapping twice."),
       (3, "Each of them finds something different."),
       (4, "And it all comes back to you."),
       (5, "“Um, Claude? Grandma can't find the send button… and my cousin thinks it's on Friday?”"),
       (6, "Claude fixes it, and everyone waits."),
       (7, "But what if Claude didn't have to wait?"),
       (8, "You'd just say: “Find and fix issues in the RSVP page.”"),
       (9, "And it goes and uses the thing itself. Clicking, breaking, fixing… again and again,"),
       (10, "until whatever reaches people just works."))}
  </section>''')

# ---------- 4. SWEeper-Bench title ----------
S.append(f'''  <section class="slide p2 sa-tslide" data-name="SWEeper-Bench title" data-classes='{{"sa-swe":1}}'>
    <div class="title">
      <img class="sa-icon" src="{ICON}" alt="">
      <h1><span class="sa-hl">SWE</span>eper-Bench</h1>
      <div class="by sa-sub rise" data-in="1"><b>S</b>oft<b>w</b>are <b>e</b>ngineering… with a broom</div>
    </div>
{notes((0, "That's the idea behind SWEeper-Bench. The full title of the paper: can agents discover bugs in interactive software?"), (1, "S, W, E: software engineering… with a broom."))}
  </section>''')

CSS = r'''
.sa-kick { font-size: 30px; font-weight: 500; color: var(--text); margin-bottom: 18px; }
.title .sa-sub { font-size: 34px; margin-top: 40px; }
.title .sa-sub b { font-weight: 600; }
/* video */
.sa-vid { position: absolute; left: 100px; top: 56px; width: 1400px; height: 788px; border-radius: 24px;
  background: #111; object-fit: cover; box-shadow: 0 24px 60px -24px rgba(31, 35, 40, .35); }
/* story */
.sa-story [data-in], .sa-story [data-out] { transition-delay: var(--d, 0s); }
.sa-stage { position: absolute; left: 0; top: 20px; width: 1600px; height: 900px; transform: translate(420px, 50px);
  transition: transform .9s var(--ease); }
.sa-p1 .sa-stage { transform: translateX(270px); }
.sa-p2 .sa-stage { transform: none; }
.sa-svg { position: absolute; inset: 0; width: 1600px; height: 900px; overflow: visible; }
.sa-you, .sa-claude { position: absolute; width: 160px; text-align: center; }
.sa-you { left: 100px; top: 400px; }
.sa-claude { left: 390px; top: 405px; }
.sa-you .sa-e { font-size: 110px; line-height: 1; }
.sa-cl { width: 104px; height: 104px; display: block; margin: 0 auto 12px; }
.sa-lb { font-size: 24px; font-weight: 600; margin-top: 10px; }
.sa-bub { position: absolute; left: 100px; bottom: 540px; width: 560px; padding: 18px 26px; font-size: 28px; line-height: 1.35;
  background: #f3f5f7; border-radius: 22px; }
.sa-bub::after { content: ""; position: absolute; left: 66px; bottom: -14px; border: 14px solid transparent;
  border-bottom: 0; border-top-color: #f3f5f7; }
.sa-wait { position: absolute; left: 640px; top: 760px; padding: 10px 22px; border-radius: 999px; font-size: 26px; font-weight: 600;
  background: var(--c-red-soft); color: var(--text); }
.sa-phone { position: absolute; left: 710px; top: 230px; width: 250px; height: 480px; border: 4px solid var(--ink); border-radius: 40px;
  background: #fff; padding: 66px 24px 0; text-align: center; box-shadow: 0 20px 44px -24px rgba(10, 37, 64, .45); }
.sa-notch { position: absolute; left: 50%; top: 14px; width: 74px; height: 20px; margin-left: -37px; border-radius: 10px; background: var(--ink); }
.sa-ttl { font-size: 40px; font-weight: 700; letter-spacing: .04em; color: var(--ink); }
.sa-who { font-size: 20px; color: var(--text); margin-top: 6px; }
.sa-date { font-size: 18px; font-weight: 600; color: var(--ink); margin-top: 4px; }
.sa-field { margin-top: 32px; border: 2px solid var(--faint); border-radius: 10px; padding: 9px 12px; font-size: 18px; color: var(--text); text-align: left; }
.sa-yn { display: flex; gap: 10px; margin-top: 18px; }
.sa-yn span { flex: 1; border: 2px solid var(--faint); border-radius: 999px; padding: 6px 0; font-size: 18px; }
.sa-yn .on { border-color: var(--accent); color: var(--accent); background: var(--c-blue-soft); font-weight: 600; }
.sa-send { margin-top: 44px; background: var(--accent); color: #fff; border-radius: 12px; padding: 13px 0; font-size: 20px; font-weight: 600; }
.sa-cur { position: absolute; left: 0; top: 0; font-size: 40px; line-height: 1; }
.sa-story.active .sa-cur:not(.frag-hidden) { animation: sa-tap 3.2s var(--ease) infinite; }
@keyframes sa-tap {
  0%, 100% { transform: translate(70px, 190px); }
  25% { transform: translate(150px, 250px) scale(.85); }
  50% { transform: translate(110px, 330px) scale(.85); }
  75% { transform: translate(60px, 250px) scale(.85); }
}
.sa-step { position: absolute; transform: translate(-50%, -50%); padding: 8px 22px; border-radius: 999px; background: #fff;
  border: 2px solid var(--accent); color: var(--text); font-size: 24px; font-weight: 600; white-space: nowrap; }
.sa-guests { transition: opacity .6s ease, filter .6s ease; }
.sa-dim:not(.sa-ok) .sa-guests { opacity: .3; filter: grayscale(1); }
.sa-card { position: absolute; width: 220px; height: 230px; border: 2px solid var(--faint); border-radius: 18px; background: #fff;
  text-align: center; padding-top: 16px; }
.sa-card.frag-hidden { transform: translateY(14px); }
.sa-av { position: relative; display: inline-block; font-size: 64px; line-height: 1; }
.sa-mood { position: absolute; left: -38px; bottom: -6px; font-size: 34px; }
.sa-mood.frag-hidden { transform: scale(.3); }
.sa-nm { font-size: 22px; font-weight: 600; margin-top: 12px; }
.sa-det { font-size: 18px; color: var(--text); margin-top: 2px; }
.sa-pill { position: absolute; left: 14px; right: 14px; bottom: 14px; border-radius: 999px; padding: 7px 0; font-size: 19px; font-weight: 600;
  color: var(--text); display: flex; align-items: center; justify-content: center; gap: 8px; }
.sa-ic { width: 20px; height: 20px; flex: none; }
.sa-pill.frag-hidden { transform: scale(.4); }
.sa-bad { background: var(--c-red-soft); }
.sa-good { background: var(--c-green-soft); }
/* SWEeper-Bench title */
.sa-icon { width: 170px; height: auto; margin-bottom: 26px; }
.sa-hl { background: linear-gradient(var(--mark), var(--mark)) no-repeat 0 82% / 0 36%; transition: background-size .8s var(--ease); }
.sa-swe .sa-hl { background-size: 100% 36%; }
.sa-tslide .sa-sub b { font-weight: 700; }
'''

(OUT / 'sections.html').write_text('\n'.join(S) + '\n')
(OUT / 'css.css').write_text(CSS.strip() + '\n')
print('wrote', OUT / 'sections.html', OUT / 'css.css', 'slides:', len(S))
