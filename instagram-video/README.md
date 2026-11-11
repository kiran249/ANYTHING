# Shopping Payback Reel

15s vertical Instagram Reel (1080x1920, 30fps, H.264 + AAC): `shopping-payback-reel.mp4`.

Story beats: she finds the bag → his sigh → card tap → makeup → shoes (running total) →
walking out with the bags → "later that night… she paid him back" → **Comment "PAID"** CTA.

All visuals and audio are original (canvas animation + synthesized music/SFX).

## Edit & re-render
1. Change captions, prices, store names or the CTA word in the `CONFIG` block at the top of `scene.html`
   (open the file in a browser to preview the animation live).
2. `node render.js` → re-renders frames, regenerates the audio (`audio.py`) and rewrites the MP4.
   Needs Playwright (Chromium), ffmpeg, python3 + numpy, and the Inter + Noto Color Emoji fonts.
