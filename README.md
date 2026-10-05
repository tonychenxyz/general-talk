# General talk: measuring AI on open-ended problems

A 45-minute talk by Tony Chen. The whole deck is one self-contained HTML file, `index.html`, with fonts and images inlined.

## Open the deck

- Open `index.html` in any browser (double-click it, or serve the folder with `python3 -m http.server`).
- Online copy: https://claude.ai/artifact/3uGLBtuSuBizZk1NWQMSHv

## Controls

| Key | Action |
| --- | --- |
| → ↓ Space Enter PageDown | Next slide |
| ← ↑ PageUp Backspace | Previous slide |
| Home / End | First / last slide |
| M (or S) or ☰ | Slide sidebar with previews (Esc closes) |
| F or ⛶ | Fullscreen |
| N | Speaker notes |

## Layout

- `media/` — videos played by the deck (e.g. `iphone-glitch.mp4`), referenced by relative path, not inlined. Keep this folder next to `index.html` when copying the deck.

- `index.html` — the deck. Edit this file directly.
- `src/part2/` — the CEO-Bench section's generator. `build.py` fills `template.html` with charts, the teaser and the leaderboard from `tonychenxyz/ceo-bench-webpage` (branch `codex/latest-agent-trajectories`), and `merge.py` copies the CEO-Bench CSS block and sections (CEO-Bench title through Leaderboard) into the deck in place. Paths at the top of both scripts are the original working paths; adjust them before rerunning.
- `src/part3/` — the "What improved?" section (after the Leaderboard). `extract.py` collects the numbers from the local CEO-Bench analysis outputs on della into `data.json` (committed); `build.py` turns `data.json` into the slides and replaces only the `part3:begin`…`part3:end` blocks in `index.html`, so rerunning it doesn't touch other slides.
- `src/part4a`…`src/part6c/` — later sections (toy experiment and CEO-Bench takeaway; SWEeper-Bench intro and results). Each `build.py` writes only `out/sections.html` and `out/css.css`; `src/merge_parts.py` splices all of them into `index.html` after part 3 (rerun it after rebuilding any part). `src/smooth_curve.py` draws the smoothed price-vs-quality curves.
- `src/fonts/` — Inter and JetBrains Mono (woff2) that the deck inlines.
- `src/images/` — original images used on the opening slides (already inlined in the deck).

## Working on the deck (for everyone editing it, people and Claude threads)

Several editors work on `index.html` at once, so:

1. `git pull` right before you start editing.
2. Keep each change small and focused on your own slides, and commit it on its own with a clear message.
3. Push to `main` straight away. If the push is rejected, pull (rebase), re-check your slides, and push again.
4. Never regenerate the whole deck from an old copy; that wipes other people's edits.
