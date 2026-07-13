---
name: playwright-demo-recorder
description: "Record polished product-demo videos of a local web app programmatically: Playwright drives the UI headless with a synthetic cursor and positioned captions, macOS `say` generates an AI voiceover inline (each beat paced to its narration length), and ffmpeg muxes it all into one voiced mp4. Starts with a mandatory beat-planning phase deriving the demo story from the branch diff or feature description, user-approved before any code. Use when asked to record a demo, make a demo/walkthrough/feature-showcase video, a screen recording with captions or voiceover, or to show off a branch or prototype as a video. Hard prerequisites, each gated with abort-and-fix: macOS, the exact 'Karen (Premium)' voice downloaded, system ffmpeg, @playwright/test + Chromium in the target repo, a demo-ready local app. WARNING: Apple System Voices are licensed for personal non-commercial use only — any video shared in a business or public context needs a licensed TTS swap or the silent opt-out. Not for slide decks or live presentations."
---

# Playwright Demo Recorder

Turn a feature branch into a narrated demo video, end to end: plan the story from the actual diff, drive the app with Playwright while captions and a synthetic cursor overlay the UI, generate the voiceover inline so every beat is paced to its narration, and deliver **one mp4 with the voice baked in**.

The deliverable is always the voiced mp4. A silent video is the explicit opt-out, not the default.

Project-specific defaults (env vars, login selectors, stack quirks) are deliberately kept out of this file — see `references/project-binding.md` and fill in your own before your first run.

> ## ⚠️ Licence warning — read before any video leaves the machine
>
> Apple's macOS SLA (§2.F "Voices; Live Captions", verified 2026-07-10) licenses System Voices — including Karen (Premium) — for **personal, non-commercial use only**, and explicitly prohibits "recording, publishing or redistribution … in a profit, non-profit, public sharing or commercial context".
>
> **`say` narration is for local iteration and personal preview only. Before a video is shared in ANY business or public context — colleagues, customers, prospects, docs, socials — regenerate the narration with a commercially licensed TTS (one-function swap, see `references/voiceover.md`) or deliver the silent version.** State the voice source when handing over the final video.

## Prerequisites (each one is a hard Phase 0 gate)

On any miss: **stop and tell the user the exact fix. Never substitute, never improvise a fallback.**

1. **macOS** — the voiced pipeline uses `say`; on other platforms only the silent pipeline exists.
2. **Voice `Karen (Premium)` (en_AU), exact string** in `say -v '?'` output. It is a downloadable asset: System Settings → Accessibility → Read & Speak (older macOS: Spoken Content) → System voice → Manage Voices…. `say` **exits 0 for unknown voices and silently substitutes** — presence of `say` proves nothing; only the exact-match gate does. The compact "Karen" is not acceptable output.
3. **System ffmpeg + ffprobe** on PATH (`brew install ffmpeg`). Playwright's bundled ffmpeg records video only; without the system one, recording succeeds and the mux dies.
4. **`@playwright/test` + Chromium binaries in the target repo.** A successful import does not prove `chromium.launch()` works — probe a real launch; fix is `npx playwright install chromium`. Run the recorder from the workspace package that owns the dependency.
5. **App running, reachable, AND showing the content the demo needs** — assert a known record or element renders, not just HTTP 200. If the app is data-driven, get that data in place first however the app does it (seed script, fixtures, created through the UI); if it isn't, there's nothing to seed and the render assertion alone is the gate.
6. **Quiet, healthy machine** — no recording on a degraded/loaded stack; re-check app health after the take.

Tested-version baseline for drift diagnosis: `references/recorder-patterns.md`.

## Phase 0 — Preflight

Run every gate above (the template runs the voice/ffmpeg/credential gates itself; do the app/content/health checks before invoking it). Output dir: `~/Downloads/<demo-name>/`. If the app has a login, credentials come from `DEMO_USER`/`DEMO_PASS` env vars — never literals in scripts or commits; if it doesn't, set `LOGIN = false` in the template.

## Phase 1 — Beat plan (mandatory; user-approved before any code)

Follow `references/demo-planning.md`:

- Enumerate demoable features from the **actual work**: `git -C <repo> log --oneline origin/main..HEAD`, `git diff origin/main...HEAD --stat`, branch README, or the user's description — never from memory. Sanity-check the merge base (stale local `main` pollutes the list; re-anchor at the feature's first commit if needed). **Only the branch's story** — cut beats that showcase pre-existing features, and demo tooling itself is never a beat.
- Order beats in the narrative arc: frame the problem → config primes what follows → core flow → close the loop → payoff view → generality → summary → end card. One narration line + one action per beat (~4–12 s).
- Narration lines: ≤ ~12 words, both caption and voiceover; no em-dashes; never name specific sample-data parties (data varies per environment). **Invoke** a writing-polish/AI-tell-detection skill if you have one on the full set — AI tells are louder read aloud.
- Estimate runtime (≈3 s per line + action time) and present it with the beats.
- Flag undemoable interactions (canvas targets, hover-only, non-deterministic layouts) with the chosen workaround.
- **Get explicit approval.** Any later beat change is re-presented before recording.

## Phase 2 — Probe, then build

- Throwaway probe script against the live DOM first — confirm selectors and roles (`role="tab"` vs button is the classic silent miss).
- Copy `templates/demo-recorder.template.mjs` into the target workspace, fill CONFIG and the beats (captions verbatim from the approved plan), extend `SPEECH_MAP` for the demo's vocabulary.
- Canvas/hover targets: DEV-only coordinate hooks per the recipe in `references/recorder-patterns.md` (guard mandatory, separate commit, removed or justified before the feature PR).
- **Verify every interaction headless without video** — including in-app effects (does the dialog actually appear?) — before any recording run.

## Phase 3 — Record

Run the recorder. It records at a fixed viewport, injects the overlay, paces captions to their narration, ends with the end card, and writes `<demo>.webm`, `timeline.json`, and the audio clips. Note the exact webm path from the run output.

## Phase 4 — Gate, then the final voiced video

The template muxes in `finally`, so **a crashed run still produces a confident-sounding mp4**. Before accepting anything:

1. **Failed beats block delivery.** The run exits non-zero and lists `stepFailures` — any entry means the voiceover narrates actions that didn't happen. Fix and re-record.
2. **Freshness**: `<demo>.mp4` mtime must be newer than `<demo>.webm`; re-run the mux after every re-record.
3. **Runtime reconciliation**: actual vs the approved estimate; >20 % over → re-cut narration or beats, don't silently deliver.
4. **Watch and listen to the whole mp4, from t=0** (`ffprobe` proves streams exist, not that they're right — a clip-filename collision shipped a video narrating the end-card line over every caption, with a green run and a healthy AAC track): narration matches what's on screen from the very first beat; pronunciation (extend `SPEECH_MAP` and re-record if needed); pacing; **footage content — no real-looking personal data, no typed secrets, no URLs/emails beyond your demo data**. Record only against a local environment holding demo data, never real user data.
5. **The output dir holds exactly one mp4.** Delete superseded outputs (old names from earlier pipeline versions) in the same pass — stale leftovers get reviewed as "the video".

Silent opt-out and re-voice alternatives: `references/voiceover.md`.

## Phase 5 — Hand over

- **Hand the final mp4 to the user; the user sends it.** The agent never distributes a demo video. State the voice source (Apple `say` = personal preview only — licence warning above — vs licensed TTS).
- Offer to commit the recorder to the feature branch with run docs: the Prerequisites list, the preflight commands, env-var setup, and stack restart steps — so any teammate can re-record.
- Keep intermediates (`.webm`, `timeline.json`, `audio/`) until the video is accepted — they enable re-voicing without re-recording.

## References

- `references/demo-planning.md` — beat-plan method + worked example
- `references/recorder-patterns.md` — patterns, gotchas, tested versions, DEV-hook recipe
- `references/voiceover.md` — licence warning (full text), pacing model, pronunciation map, re-voice + silent paths
- `references/project-binding.md` — quarantine file for your project's specifics (env vars, login selectors, stack facts) — fill in for your own app; template only, no defaults are assumed
- `templates/demo-recorder.template.mjs` — the recorder (preflight gates + overlay + pacing + mux built in)
