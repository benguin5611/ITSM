# Recorder patterns and gotchas

Everything here was learned building a real recording pipeline across two architecture iterations and roughly ten recording runs. The template (`templates/demo-recorder.template.mjs`) already implements the patterns; this file explains them and lists the traps.

## Tested versions (authoring baseline)

| Component | Version | Notes |
|---|---|---|
| macOS | 26.5.1 | `say`, voice assets |
| `@playwright/test` | 1.60.0 | target-workspace devDependency; preflight prints the resolved version |
| ffmpeg / ffprobe | 8.1.1 (Homebrew) | system install — Playwright's bundled ffmpeg records only |

A future failure on different versions should diagnose against this baseline first.

## Selector and interaction traps

- **Toggle/segmented controls are often `role="tab"`** — `getByRole('button', …)` silently misses them and the beat no-ops. Probe roles against the live DOM before building (Phase 2 probe script); prefer `getByRole('tab', …)` for view switches.
- **The `step()` helper records failures, it doesn't hide them.** Every beat runs inside `step(name, fn)`; a throw lands in `stepFailures`, is printed, and makes the script exit non-zero after the mux. A failed beat means the voiceover narrates something that never happened — Phase 4 blocks delivery on any entry.
- **Canvas graphs (ECharts etc.): never guess pixels.** Nodes/edges are non-deterministic force-layout pixels. Expose real settled coordinates from the component via a DEV-only hook and click those:

  ```js
  // In the component (Vue example) — DEV-only, no-op in production:
  if (import.meta.env.DEV) {
    window.__demoGraphNodePoint = () => /* settled node's client x/y */
    window.__demoGraphEdgePoint = () => /* an edge midpoint's client x/y */
  }
  ```

  **Recipe (all three parts mandatory):** (1) `import.meta.env.DEV` guard; (2) committed separately with a demo-tooling label, not folded into feature commits; (3) before the feature PR is raised, the hook is removed or explicitly justified in the PR description.
- **Hover-only labels don't exist on video.** A passive viewer can't hover. Make labels always-visible for the demo (usually better UX anyway), or narrate what hovering would show.
- **Force layouts need settle time** — ~3.5–5 s after render before narrating over a graph, or the viewer watches nodes still flying.

## Motion and camera

- **Synthetic cursor**: an overlay div tracking `mousemove` with a click-pulse on `mousedown` — the real cursor isn't captured in headless recording. Move with `page.mouse.move(x, y, { steps: ~45 })` and `slowMo: 60` so travel is followable.
- **Camera moves must be pronounced.** A single small `mouse.wheel` reads as nothing. Zoom = 4–5 chained wheel steps (e.g. `wheel(0, -600)` × 4 with ~450 ms pauses), aimed at a specific cluster, then explicitly zoom back out.
- **Narrate-then-act rhythm**: the caption fades out (~320 ms), repositions while hidden, fades in, and holds for its narration; the action happens after. Reading and motion never compete.
- **No dead air between captions.** Navigation, sample loading, and layout settling sandwiched between two captions read as the video hanging — a user reported "super slow" at what was a 27-second silent gap (goto + load + graph settle between two narration lines). Structure section transitions as: navigate/load silently *first*, narrate over the loaded content, then act. The template prints a warning for any inter-narration silence over 10 s — treat every warning as a beat to restructure, and probe those timestamps in the watch gate.
- **Caption positioning**: place each caption near what it describes (`top`/`bottom`/`top-left`/`top-right`/`left`/`center`), clear of in-app legends/toolbars. Check the target view before choosing.

## Run hygiene

- **Login state is fresh each run** (new browser context) — if the app has a login, script it; read credentials from `DEMO_USER`/`DEMO_PASS` env vars, never literals in the script.
- **Content probe is the first beat**: assert one known record or element the demo depends on renders. "App up but empty" gives HTTP 200 and blank screens — with swallowed errors the voiceover confidently narrates nothing.
- **Record on a quiet, healthy stack** — check app health before AND after the take (mid-take degradation produces a green run narrating on-screen failures); don't record while the machine is loaded.
- **Stray `page@*.webm` files** from crashed runs are cleared at startup so the mux can never pair new audio with stale footage. The deliverable is `<demo>.mp4`; the freshness check is `<demo>.mp4` mtime > `<demo>.webm` mtime — both named explicitly.
- **Verify in-app effects headless before trusting a take** (e.g. "does the confirm dialog actually appear?") — a quick no-video probe run beats discovering it in the recording.
- **Audio clips must have unique filenames — and the template asserts it before muxing.** Observed failure: an unincremented clip counter made every `speak()` overwrite `cap_0.aiff`, so the delivered video narrated the end-card line over all captions. The run was green, ffprobe showed a healthy AAC track, and only *listening* caught it — from the first seconds. This is why the watch-and-listen gate starts at t=0, not a mid-video skim.
- **Exactly one mp4 in the output dir.** When the pipeline's output name changes (e.g. `-voiced.mp4` → plain `.mp4`), delete the superseded file in the same pass — an observed stale leftover got reviewed as "the video" and reported as a regression.
- **`.webm` won't open in QuickTime** — never hand over the webm; it's an intermediate.

## The mux (reference)

One input per clip, each delayed to its caption's timestamp, mixed, mapped over the original video:

```
ffmpeg -y -i demo.webm -i cap_0.aiff … \
  -filter_complex "[1:a]adelay=<ms>:all=1[a0];…;[a0][a1]…amix=inputs=N:normalize=0:dropout_transition=0[mix]" \
  -map 0:v:0 -map "[mix]" -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart demo.mp4
```

`yuv420p` + `+faststart` are load-bearing (QuickTime compatibility, streamable start) — don't drop them when improvising.
