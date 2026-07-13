# Voiceover — pacing model, pronunciation, licensing

## ⚠️ Apple System Voices: personal, non-commercial use ONLY

**Verified against the primary source 2026-07-10** — Apple macOS Software License Agreement (Sequoia), §2.F "Voices; Live Captions" (https://www.apple.com/legal/sla/docs/macOSSequoia.pdf):

> "…you may: (i) use the system voices included in the Apple Software ("System Voices") (1) while running the Apple Software and (2) to create your own original content and projects for your **personal, non-commercial use** … **No other creation or use of the System Voices** … is permitted by this License, including but not limited to the use, reproduction, display, performance, **recording, publishing or redistribution** of any of the System Voices … **in a profit, non-profit, public sharing or commercial context**."

What this means for this skill:

- `say`-generated narration (including Karen (Premium)) is fine for **local iteration and personal preview**.
- **Any video that will be shared in a business context — to colleagues, customers, prospects, socials, docs sites — is not covered by the licence.** "Non-profit" and "public sharing" are explicitly excluded too, so there is no safe "it's only internal/free" reading.
- **Before a video leaves your machine, regenerate the narration with a commercially licensed TTS** (e.g. OpenAI TTS or ElevenLabs with a commercial plan — both licence generated audio for commercial use; verify the current terms of whichever you choose) — or deliver the silent version.
- The swap is one function: `speak()` is the only place audio is generated. Replace the `say` invocation with an API call that writes an audio file, keep returning the ffprobe duration, and the pacing/mux pipeline is unchanged.

The skill's Phase 4/5 delivery gate must state which voice source the final video used.

## Why the voice is generated inline (v2 pacing model)

The recorder generates each caption's narration **during** the take and holds the caption for exactly the narration's measured length (+~450 ms tail, clamped 1.4–8 s):

- **Pacing is right by construction** — no fixed hold that's too slow for short lines and clips long ones. (An early fixed-hold prototype's flat 5.2 s pauses were judged "way too slow" the moment voice existed.)
- **A/V sync is right by construction** — each clip's mux delay is stamped at the moment its caption appears.
- **Voice tier changes are absorbed automatically** — premium voices render different durations than compact ones; measuring each clip makes that irrelevant.

Trade-off: voice is coupled to the recording — **changing the voice or wording means re-recording**. For voice-only iteration there is a decoupled alternative (below).

Narration length is the pacing lever: keep lines ≤ ~12 words (see demo-planning.md).

## The exact voice, and why the gate is strict

- Voice: **`Karen (Premium)`** (en_AU), rate 190 wpm. The Premium tier is a **downloadable asset**: System Settings → Accessibility → Read & Speak (older macOS: Spoken Content) → System voice → Manage Voices… (Apple's guide: https://support.apple.com/guide/mac-help/mchlp2290/mac). The compact default "Karen" sounds robotic — not acceptable output.
- **`say` exits 0 even when the requested voice doesn't exist** (machine-verified: `say -v 'ZZZBogus' -o out.aiff` succeeds) and silently substitutes another voice. Presence of `say` proves nothing. The preflight gate must exact-match the voice string in `say -v '?'` output and **abort with the download path — never substitute**.

## Pronunciation map (`SPEECH_MAP`)

Captions show the real text; the map rewrites only what the voice **says**. It is one demo's vocabulary — extend it per demo, in review order (brand names first, regex-word-boundary acronyms after):

| Written | Spoken | Class |
|---|---|---|
| `Nginx` | Engine-X | brand name |
| `JSON` | Jay-sawn | format name |
| `API` | A P I | acronym spell-out |
| `walkthrough` | walk-throo | compound (see below) |
| `through` | throo | phonetic fix (voice-specific) |
| `config` | con-fig | stress fix (see below) |
| `%` | " percent" | symbol |
| `—`, `·` | ", ", ". " | pause punctuation |
| `…` | ". " | pause punctuation |

Two entry classes learned from user-reported mispronunciations:

- **Compounds need their own entry.** `\bthrough\b` cannot match inside "walkthrough" — the word-boundary regex that fixed the standalone word shipped "walk-thrao" in the end card. When you add a word fix, grep the narration lines for compounds containing it and map those first (longest match before shorter).
- **Stress fixes via hyphenated respelling.** Karen read "config" as "cunfig"; `con-fig` restores first-syllable stress. Hyphenate at the syllable you want emphasised.

Unmapped tokens get mispronounced *silently* — new demos must listen for their own vocabulary (product names, acronyms, URLs…) in the Phase 4 gate and extend the map.

**Sanctioned divergence point:** the end card takes separate display text and a `speakText` argument — on-screen "Demo complete" while the voice says "That's the end of the walkthrough. Thanks for watching." This is deliberate; don't "fix" it by unifying them.

## Decoupled re-voice (v1 alternative — no re-record)

The recorder still writes `timeline.json` (`[{t: <ms from video start>, text}]`). To change the voice/wording **without re-recording** — accepting that pacing was set by the *old* narration durations, so keep new lines similar in length:

1. Generate one clip per timeline entry (any TTS; apply the speech map first).
2. Mux at the recorded offsets onto the kept `.webm`:

```
ffmpeg -y -i demo.webm -i cap_0.aiff … \
  -filter_complex "[1:a]adelay=<t0>:all=1[a0];…;[a0][a1]…amix=inputs=N:normalize=0:dropout_transition=0[mix]" \
  -map 0:v:0 -map "[mix]" -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart demo.mp4
```

## Silent opt-out

With zero voice clips the mux can't run (`amix` needs ≥1 input) and the raw `.webm` won't open in QuickTime. The silent deliverable is one transcode:

```
ffmpeg -i <demo>.webm -c:v libx264 -pix_fmt yuv420p -movflags +faststart <demo>.mp4
```

## Verifying the audio landed

```
ffprobe -v error -show_entries stream=codec_type,codec_name -of default=nw=1 <demo>.mp4
```

must list both a `video` (h264) and an `audio` (aac) stream; also sanity-check `format=duration` against the expected runtime. Then actually listen to it (Phase 4 gate) — ffprobe can't hear a wrong voice or a mispronounced brand.
