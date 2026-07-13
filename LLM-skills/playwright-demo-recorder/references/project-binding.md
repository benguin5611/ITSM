# Project binding (template — fill in for your own app)

Everything specific to *your* project lives here so the skill core stays generic. This is a quarantine file: edit it once per project, never the core skill files. Do not commit real credentials — export them as environment variables, and never paste values into this file, a template, or a commit.

```bash
export DEMO_APP_URL=http://localhost:5173
# Only if your app has a login (otherwise set LOGIN = false in the recorder):
export DEMO_USER=<a real user in your local environment>
export DEMO_PASS=<their password>
```

## App and login

- Frontend: `<your dev-server command and port>`.
- Login: `<your auth provider — describe the selectors the recorder needs, e.g. #username, #password, and the submit control. If the app has no login, say so here and set LOGIN = false in the recorder>`.
- Post-login readiness signal: `<a locator that only appears once login has actually succeeded>`.
- `<Any route or view naming your demos will reference — settings paths, record paths, etc.>`

## Stack facts that bite recordings

Fill this section in as you discover them — it's the single highest-value section for the *next* person recording a demo against this app:

- `<Is "reachable" different from "has content"? Where does demo data come from here (seed script, fixtures, created through the UI, static), and what's the one assertion that proves it actually exists?>`
- `<Do any dev processes die independently of others — e.g. does a foreground dev server die with its shell session while a docker stack survives?>`
- `<Any known startup race — a service that needs to be warm before another, or a health-check that's flaky on cold start?>`
- `<Any known degradation mode that would poison a recording — CPU spikes, memory pressure — and how to recognise + recover from it?>`
- `<Which workspace/package does @playwright/test actually live in? Run the recorder from there so module resolution works.>`

## Voice

`<State your chosen voice and why — e.g. it matches your organisation's preferred English variant. See voiceover.md for the licence warning before sharing any voiced video.>`

## Prior art

`<Once you've recorded a first demo with this pipeline, note it here: which branch, which recorder script, any DEV coordinate hooks it added and where, and where the intermediate files (webm/timeline.json/audio) are preserved if someone wants to re-voice without re-recording.>`
