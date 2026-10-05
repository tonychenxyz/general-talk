"""Part 5a assets: copy the paper icon + Claude mark, and grab a poster frame from the iPhone glitch video.

Run once; build.py only reads the committed files written here.
"""
import pathlib, shutil, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SB = ROOT.parent / 'sweeperbench_public'
shutil.copy(SB / 'overleaf/figures/icon_sweeper.png', HERE / 'icon_sweeper.png')
shutil.copy(SB / 'sweeper-bench-plotting/assets/provider-logos/claude-color.svg', HERE / 'claude-color.svg')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '3', '-i', str(ROOT / 'media/iphone-glitch.mp4'),
                '-frames:v', '1', '-vf', 'scale=960:-2', '-q:v', '5', str(HERE / 'poster.jpg')], check=True)
print('ok')
