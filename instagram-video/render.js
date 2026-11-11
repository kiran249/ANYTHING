// Renders scene.html frame-by-frame with headless Chromium, then encodes an Instagram Reel MP4.
// Usage: node render.js            (needs: playwright, ffmpeg, python3 + numpy)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const FPS = 30, DUR = 15;
const dir = __dirname;
const frames = path.join(dir, 'build', 'frames');
const only = process.argv[2]; // optional: comma-separated seconds for preview stills

(async () => {
  fs.mkdirSync(frames, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(dir, 'scene.html') + '?render');
  await page.evaluate(async () => {
    await document.fonts.load('900 80px Inter');
    await document.fonts.load('80px "Noto Color Emoji"', '😀');
    window.__render(0);
  });
  const times = only ? only.split(',').map(Number) : [...Array(FPS * DUR).keys()].map(i => i / FPS);
  for (let i = 0; i < times.length; i++) {
    const url = await page.evaluate(t => { window.__render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, times[i]);
    const name = only ? `still_${times[i]}.jpg` : `f${String(i).padStart(4, '0')}.jpg`;
    fs.writeFileSync(path.join(only ? path.join(dir, 'build') : frames, name), Buffer.from(url.split(',')[1], 'base64'));
  }
  await browser.close();
  if (only) return;

  execFileSync('python3', ['-I', path.join(dir, 'audio.py'), path.join(dir, 'build', 'audio.wav')], { stdio: 'inherit' });
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(FPS), '-i', path.join(frames, 'f%04d.jpg'),
    '-i', path.join(dir, 'build', 'audio.wav'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-movflags', '+faststart', '-shortest',
    path.join(dir, 'shopping-payback-reel.mp4')], { stdio: 'inherit' });
  console.log('done -> shopping-payback-reel.mp4');
})();
