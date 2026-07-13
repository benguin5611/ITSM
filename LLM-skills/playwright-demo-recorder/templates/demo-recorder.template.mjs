/* eslint-disable */
/**
 * <DEMO> — programmatic demo recording with captions and a baked-in voiceover.
 *
 * Playwright drives the app headless and records video; captions render as an
 * injected overlay; narration is generated per caption with macOS `say`; each
 * caption holds for exactly its narration length; the audio is muxed onto the
 * video at the end of the same run. One deliverable: <OUT>/<DEMO>.mp4.
 *
 * Run:  node demo-recorder.mjs   (prefix DEMO_USER=... DEMO_PASS=... when LOGIN is true)
 * Docs: playwright-demo-recorder skill — references/recorder-patterns.md
 */
import { chromium } from '@playwright/test'
import { rename, mkdir, writeFile, rm, readdir } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { createRequire } from 'node:module'
import { homedir } from 'node:os'
import { join } from 'node:path'

// ---------------------------- CONFIG ----------------------------
const DEMO = 'my-demo' // kebab-case; names the output dir and the mp4
const APP = process.env.DEMO_APP_URL ?? 'http://localhost:5173'
const LOGIN = true // false if the app has no login — skips the credential gate and the login block
const USER = process.env.DEMO_USER ?? ''
const PASS = process.env.DEMO_PASS ?? ''
const VOICE = 'Karen (Premium)' // EXACT string from `say -v '?'` — see SKILL.md prerequisites
const RATE = '190' // words per minute
const SIZE = { width: 1512, height: 945 }
const BEAT = 700 // ms pause between actions
const STEPS = 45 // cursor-move steps; higher = slower cursor travel
const TAIL = 450 // ms of quiet after each narration before the next action
const OUT = join(homedir(), 'Downloads', DEMO)
const AUDIO = join(OUT, 'audio')

// How narration READS (captions keep the original text). Extend per demo:
// brand names, format names, acronym spell-outs, phonetic/stress fixes.
// Compounds need their own entry — \bthrough\b can't match inside "walkthrough".
// See voiceover.md.
const SPEECH_MAP = [
  [/\bAPI\b/g, 'A P I'],
  [/walkthrough/gi, 'walk-throo'],
  [/\bthrough\b/gi, 'throo'],
  [/\bconfig\b/gi, 'con-fig'],
  [/·/g, '. '],
  [/—/g, ', '],
  [/…/g, '. '],
  [/%/g, ' percent'],
]

// ------------------- Preflight gates (abort with the fix; NEVER substitute) -------------------
const die = (msg) => {
  console.error('\nPREFLIGHT FAILED: ' + msg)
  process.exit(1)
}
{
  const voices = spawnSync('say', ['-v', '?'], { encoding: 'utf8' })
  if (voices.status !== 0) die('`say` unavailable — the voiced pipeline requires macOS.')
  if (!voices.stdout.includes(VOICE))
    die(
      `voice "${VOICE}" is not installed. It must appear EXACTLY in \`say -v '?'\` — ` +
        '`say` exits 0 and silently substitutes another voice otherwise. Fix: System Settings → ' +
        'Accessibility → Read & Speak (older macOS: Spoken Content) → System voice → Manage Voices… ' +
        'and download it. Do NOT fall back to another voice.',
    )
  for (const bin of ['ffmpeg', 'ffprobe'])
    if (spawnSync(bin, ['-version']).status !== 0)
      die(
        `${bin} is not on PATH. Playwright bundles a private ffmpeg for recording only — ` +
          'the mux needs the system one. Fix: brew install ffmpeg',
      )
  if (LOGIN && (!USER || !PASS))
    die('set DEMO_USER and DEMO_PASS env vars (no credential literals in this file), or set LOGIN = false if the app has no login.')
  const pw = createRequire(import.meta.url)('@playwright/test/package.json').version
  console.log(`preflight OK — voice "${VOICE}", @playwright/test ${pw}`)
}

await mkdir(OUT, { recursive: true })
await rm(AUDIO, { recursive: true, force: true })
await mkdir(AUDIO, { recursive: true })
// Clear stray recordings from previous crashed runs so Phase 4 can't mux stale footage.
for (const f of await readdir(OUT)) if (/^page.*\.webm$/.test(f)) await rm(join(OUT, f))

// ------------------- Speech -------------------
const speechText = (t) => {
  let s = t
  for (const [re, sub] of SPEECH_MAP) s = s.replace(re, sub)
  return s.replace(/\s+/g, ' ').trim()
}
const ttsDurationMs = (file) => {
  const r = spawnSync(
    'ffprobe',
    ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', file],
    { encoding: 'utf8' },
  )
  const d = parseFloat((r.stdout || '').trim())
  return Number.isFinite(d) ? Math.round(d * 1000) : 1500
}
const timeline = []
const clips = []
const stepFailures = []
let t0 = 0
let capN = 0
// Generate speech for a caption; returns its duration in ms. delay is filled in when shown.
const speak = (text) => {
  const spoken = speechText(text)
  if (!spoken) return 0
  const file = join(AUDIO, `cap_${capN++}.aiff`)
  const r = spawnSync('say', ['-v', VOICE, '-r', RATE, '-o', file, spoken])
  if (r.status !== 0) {
    console.log(`  ⚠ say failed for: ${spoken}`)
    return 0
  }
  const dur = ttsDurationMs(file)
  clips.push({ file, delay: -1, dur, text: spoken })
  return dur
}

// ------------------- Overlay: synthetic cursor + positionable caption bar -------------------
const overlay = () => {
  const ensure = () => {
    if (!document.body) return
    if (!document.getElementById('__demo_cursor')) {
      const c = document.createElement('div')
      c.id = '__demo_cursor'
      c.style.cssText =
        'position:fixed;width:22px;height:22px;border-radius:50%;border:2px solid #fff;' +
        'background:rgba(56,189,248,0.45);box-shadow:0 0 0 2px rgba(0,0,0,.25);' +
        'left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:2147483647;' +
        'transition:width .1s,height .1s;'
      document.body.appendChild(c)
    }
    if (!document.getElementById('__demo_caption')) {
      const cap = document.createElement('div')
      cap.id = '__demo_caption'
      cap.style.cssText =
        'position:fixed;left:50%;top:24px;transform:translateX(-50%);max-width:820px;' +
        'padding:14px 24px;background:rgba(15,23,42,.94);color:#fff;font-size:20px;line-height:1.4;' +
        'font-family:-apple-system,Segoe UI,Roboto,sans-serif;border-radius:12px;text-align:center;' +
        'box-shadow:0 8px 30px rgba(0,0,0,.45);z-index:2147483647;opacity:0;transition:opacity .3s ease;' +
        'border:1px solid rgba(255,255,255,.14);'
      document.body.appendChild(cap)
    }
  }
  document.addEventListener('DOMContentLoaded', ensure)
  document.addEventListener('mousemove', (e) => {
    ensure()
    const c = document.getElementById('__demo_cursor')
    if (c) {
      c.style.left = e.clientX + 'px'
      c.style.top = e.clientY + 'px'
    }
  })
  document.addEventListener('mousedown', () => {
    const c = document.getElementById('__demo_cursor')
    if (c) {
      c.style.width = '34px'
      c.style.height = '34px'
      setTimeout(() => {
        c.style.width = '22px'
        c.style.height = '22px'
      }, 200)
    }
  })
  const POS = {
    top: { left: '50%', right: 'auto', top: '24px', bottom: 'auto', transform: 'translateX(-50%)' },
    bottom: { left: '50%', right: 'auto', top: 'auto', bottom: '30px', transform: 'translateX(-50%)' },
    'top-left': { left: '32px', right: 'auto', top: '24px', bottom: 'auto', transform: 'none' },
    'top-right': { left: 'auto', right: '32px', top: '24px', bottom: 'auto', transform: 'none' },
    left: { left: '32px', right: 'auto', top: '50%', bottom: 'auto', transform: 'translateY(-50%)' },
    center: { left: '50%', right: 'auto', top: '44%', bottom: 'auto', transform: 'translate(-50%,-50%)' },
  }
  // @ts-ignore
  window.__demoCaptionPos = (region) => {
    const cap = document.getElementById('__demo_caption')
    if (!cap) return
    const s = POS[region] || POS.top
    cap.style.left = s.left
    cap.style.right = s.right
    cap.style.top = s.top
    cap.style.bottom = s.bottom
    cap.style.transform = s.transform
  }
  // @ts-ignore
  window.__demoHideCaption = () => {
    const cap = document.getElementById('__demo_caption')
    if (cap) cap.style.opacity = '0'
  }
  // @ts-ignore
  window.__demoCaption = (t) => {
    ensure()
    const cap = document.getElementById('__demo_caption')
    if (!cap) return
    cap.textContent = t
    cap.style.opacity = '1'
  }
}

const browser = await chromium.launch({ headless: true, slowMo: 60 })
const context = await browser.newContext({ viewport: SIZE, recordVideo: { dir: OUT, size: SIZE } })
await context.addInitScript(overlay)
const page = await context.newPage()
t0 = Date.now()

// Caption: generate TTS while the previous caption is still up, fade to the new
// one, then hold for exactly the narration length plus TAIL (clamped 1.4–8 s).
const caption = async (text, opts = {}) => {
  const at = opts.at || 'top'
  const before = clips.length
  const durMs = speak(text)
  const clip = clips.length > before ? clips[clips.length - 1] : null
  await page.evaluate(() => window.__demoHideCaption?.())
  await page.waitForTimeout(320)
  await page.evaluate((r) => window.__demoCaptionPos?.(r), at)
  await page.evaluate((x) => window.__demoCaption?.(x), text)
  const startMs = Date.now() - t0
  if (clip) clip.delay = startMs
  timeline.push({ t: startMs, text })
  await page.waitForTimeout(Math.min(8000, Math.max(1400, durMs + (opts.tail ?? TAIL))))
}

// Full-screen end card so it's unmistakable the demo has finished. The display
// text and the spoken line diverge deliberately — see voiceover.md.
const endCard = async (title, sub, speakText) => {
  const before = clips.length
  const durMs = speak(speakText)
  const clip = clips.length > before ? clips[clips.length - 1] : null
  await page.evaluate(() => window.__demoHideCaption?.())
  await page.evaluate(
    ([t, s]) => {
      let el = document.getElementById('__demo_endcard')
      if (!el) {
        el = document.createElement('div')
        el.id = '__demo_endcard'
        document.body.appendChild(el)
      }
      el.style.cssText =
        'position:fixed;inset:0;background:rgba(9,13,24,0.98);z-index:2147483647;display:flex;' +
        'flex-direction:column;align-items:center;justify-content:center;gap:18px;color:#fff;' +
        'font-family:-apple-system,Segoe UI,Roboto,sans-serif;opacity:0;transition:opacity .5s ease;'
      // textContent, not innerHTML — angle brackets or ampersands in the copy must render, not parse
      el.replaceChildren()
      const h = document.createElement('div')
      h.style.cssText = 'font-size:46px;font-weight:700;letter-spacing:-.5px'
      h.textContent = t
      const sub = document.createElement('div')
      sub.style.cssText = 'font-size:22px;opacity:.75'
      sub.textContent = s
      el.append(h, sub)
      requestAnimationFrame(() => {
        el.style.opacity = '1'
      })
    },
    [title, sub],
  )
  const startMs = Date.now() - t0
  if (clip) clip.delay = startMs
  await page.waitForTimeout(Math.max(3800, durMs + 700))
}

const moveTo = async (locator) => {
  try {
    await locator.scrollIntoViewIfNeeded({ timeout: 4000 })
    const box = await locator.boundingBox()
    if (!box) return null
    const x = box.x + box.width / 2
    const y = box.y + box.height / 2
    await page.mouse.move(x, y, { steps: STEPS })
    return { x, y }
  } catch {
    return null
  }
}
const clickLoc = async (locator) => {
  const p = await moveTo(locator)
  await page.waitForTimeout(280)
  if (p) await page.mouse.click(p.x, p.y)
  else await locator.click({ timeout: 5000 }).catch(() => {})
  await page.waitForTimeout(BEAT)
}
// Failed steps are RECORDED, not swallowed: Phase 4 diffs stepFailures against
// the approved beat plan and blocks delivery if any beat failed.
const step = async (name, fn) => {
  try {
    await fn()
  } catch (e) {
    const msg = e.message?.split('\n')[0]
    stepFailures.push({ name, msg })
    console.log(`  ⚠ step "${name}" FAILED:`, msg)
  }
}

try {
  // ---- Login (skipped when LOGIN is false; adjust selectors to your app's
  // login form — these are placeholders, see references/project-binding.md) ----
  if (LOGIN) {
    console.log('login…')
    await page.goto(APP, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('#username', { timeout: 30000 })
    await page.fill('#username', USER)
    await page.fill('#password', PASS)
    await page.click('button[type="submit"]')
    await page.getByRole('link', { name: '<post-login readiness signal — see project-binding.md>' }).first().waitFor({ timeout: 30000 })
    await page.waitForTimeout(1200)
  } else {
    await page.goto(APP, { waitUntil: 'domcontentloaded' })
  }

  // ---- REQUIRED first beat: content probe. Assert one known record/element the
  // demo depends on renders — "app up but empty" records confident narration
  // over blank screens.
  // await page.goto(`${APP}/<content-path>`, { waitUntil: 'domcontentloaded' })
  // await page.getByText('<known-content>').first().waitFor({ timeout: 10000 })

  // ---- BEATS — one step() per approved beat-plan beat, captions verbatim ----
  await caption('<Title beat — name the demo>', { at: 'center' })

  // await step('<beat name>', async () => {
  //   await caption('<narration line, ≤ ~12 words>', { at: 'top' })
  //   await clickLoc(page.getByRole('link', { name: '<target>' }).first())
  // })

  await caption('<Summary beat — the one-line takeaway>', { at: 'center' })
  await endCard('Demo complete', '<Feature> — <Product>', "That's the end of the walkthrough. Thanks for watching.")
} finally {
  const videoPath = await page.video()?.path()
  await context.close()
  await browser.close()

  if (videoPath) await rename(videoPath, join(OUT, `${DEMO}.webm`)).catch(() => {})
  const src = join(OUT, `${DEMO}.webm`)
  try {
    await writeFile(join(OUT, 'timeline.json'), JSON.stringify(timeline, null, 2))
  } catch {}

  const voiced = clips.filter((c) => c.delay >= 0)
  const outMp4 = join(OUT, `${DEMO}.mp4`)
  // Invariant: every clip is a distinct file. A filename collision (observed in the
  // wild: an unincremented counter) makes every caption speak the LAST line — the
  // run stays green and ffprobe still shows a healthy audio track.
  if (voiced.length && new Set(voiced.map((c) => c.file)).size !== voiced.length) {
    console.error(`✗ AUDIO CLIP COLLISION: ${voiced.length} clips share filenames — not muxing.`)
    process.exit(1)
  }
  if (voiced.length) {
    console.log(`Muxing ${voiced.length} voice clips…`)
    const inputs = ['-i', src]
    voiced.forEach((c) => inputs.push('-i', c.file))
    const filter =
      voiced.map((c, i) => `[${i + 1}:a]adelay=${c.delay}:all=1[a${i}]`).join(';') +
      ';' +
      voiced.map((_, i) => `[a${i}]`).join('') +
      `amix=inputs=${voiced.length}:normalize=0:dropout_transition=0[mix]`
    const r = spawnSync(
      'ffmpeg',
      ['-y', ...inputs, '-filter_complex', filter, '-map', '0:v:0', '-map', '[mix]',
       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', outMp4],
      { encoding: 'utf8' },
    )
    if (r.status !== 0) console.log('ffmpeg error:', (r.stderr || '').split('\n').slice(-3).join('\n'))
    else console.log('VIDEO (with voice):', outMp4)
    // Pacing report: dead air is invisible in a green run — surface silent gaps.
    for (let i = 0; i < voiced.length - 1; i++) {
      const gapMs = voiced[i + 1].delay - (voiced[i].delay + voiced[i].dur)
      if (gapMs > 10000)
        console.log(`  ⚠ ${Math.round(gapMs / 1000)}s of silence after "${voiced[i].text}" — restructure the beat (navigate/settle DURING narration, not between captions)`)
    }
  } else {
    console.log('no voice clips; silent webm at', src, '— see voiceover.md for the silent transcode')
  }

  if (stepFailures.length) {
    console.error(`\n✗ ${stepFailures.length} BEAT(S) FAILED — do NOT deliver this video:`)
    for (const f of stepFailures) console.error(`  - ${f.name}: ${f.msg}`)
    console.error('The voiceover narrates actions that may not have happened. Fix and re-record.')
    process.exit(1)
  }
}
