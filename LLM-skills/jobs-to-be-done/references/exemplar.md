# Exemplar: external file sharing

Four versions of the same JTBD write-up for a common feature — letting someone share a file or folder with a person **outside** their organisation, who isn't a user of the tool, via a time-limited link.

Read them in order. Version 0 is the raw material a colleague actually hands you — a solution wish-list, not jobs. Version 1 turns it into a structurally correct but unreadable draft. Version 2 is the overcorrection — an example bolted to every line. Version 3 is the target.

## Contents

- Version 0 — the raw material (what you're handed)
- Version 1 — bare
- Version 2 — bloated (excerpt)
- Version 3 — condensed (the target)
- The moves, annotated

---

## Version 0 — the raw material

*This is what lands in your lap — the discovery card. Notice it's written entirely in solution-space: it describes the mechanism (links, one-time codes, a Google-Drive-style UI) and a wish-list of controls. There's not a single job in it. Your first move is to translate, not transcribe.*

> Our external sharing is basic — you generate a public link that anyone can open, it never expires, and there's no way to see who's used it. We want a Google-Drive-style sharing experience: set how long the link lasts; choose view-only or edit; share to a specific email; the recipient verifies with a one-time code; the owner can see who has access and revoke it any time; and the invite email is branded.

Plus a couple of raw "I'd like to…" lines from the same discussion:

> - I'd like to share just one file, not the whole folder.
> - I'd like access to switch off on its own once the project's done.

**The rebuild test applied to the raw material:** "public link", "one-time code", "Google-Drive-style" — all mechanism. Strip them and ask what progress the person is making. That's Version 1.

---

## Version 1 — bare

*Structurally correct: every section present, the job-story grammar intact. Unreadable: zero grounding. A reader who hasn't seen the feature can't picture a single line of it. This is what a first draft typically looks like — a fine starting point, not a shippable artefact.*

### Jobs to be Done

**The struggle**

Three situations meet in this feature:

- Someone needs to get a file to (or collect one from) a person outside their organisation. Today they email attachments back and forth — versions sprawl, and there's no way to unshare.
- The outside party has been asked to open or return something and isn't (and shouldn't need to be) a registered user of the tool.
- Someone is accountable for making sure external sharing was appropriate and can be accounted for later.

**Core job to be done**

Get a document to (or from) an outside party — giving them access to exactly what they need for exactly as long as needed, without them creating an account and without exposing anything else.

**Job stories**

The owner sharing the file

- When I need to get a file to an outsider, I want to share just that file, so I can hand it over without exposing everything around it.
- When I set up a share, I want to control how long it stays open, so it doesn't linger after the reason for it is gone.
- When I re-share to someone who had access before, I want the old link to stop working, so a stale link can't be reused.
- When a project wraps up, I want access to switch off on its own, so no outsider is left with a way in.
- When access has expired but the work isn't done, I want to extend or re-issue it without starting over, so I can keep things moving.

The outside recipient

- When I'm sent something, I want to open it without creating an account, so I can get to it without another login to manage.
- When I come back later to finish, I want my access to still work or be easy to renew, so I can pick up where I left off.
- When I open a share, I want to see plainly what I've been given and for how long, so I can plan around it.

The administrator

- When there's a security review, I want to answer "who had access to this, and when?" in one place, so I can show sharing was controlled.
- When people share externally, I want them kept within the organisation's sharing rules, so no one over-shares by accident.

**Emotional and social jobs**

The owner

- Emotional: Feel confident that a share does not expose more than intended.
- Social: Be seen by the client as easy and professional to work with.

The outside recipient

- Emotional: Feel that the request is legitimate and their access is handled carefully.
- Social: Not be required to sign up or prove more than the task demands.

The administrator

- Emotional: Feel assured that the tool enforces the rules so they do not have to police people manually.
- Social: Be able to demonstrate to auditors that external access was controlled and logged.

**Forces of progress**

- Push: emailing attachments is messy — you can't unshare, can't tell who opened it, and versions sprawl.
- Pull: a scoped, expiring link you can revoke and that leaves a trail.
- Anxiety: will the link leak to the wrong person? will it stay live forever?
- Habit: email "just works", and recipients expect an attachment.

**Good, better, best**

- Good (enough): the owner can share a chosen file with an outsider via a link that expires and can be revoked, and the recipient can open it without an account.
- Better: scope and expiry hold, re-shares invalidate old links, there's a clear "who has access, until when" view, and the recipient can pick up where they left off.
- Best: access ends on its own when a project closes, expired shares stop leaking any preview, failed invites surface, and an admin can answer any access question instantly.

---

## Version 2 — bloated (excerpt)

*The overcorrection. An example bolted to every single line roughly doubles the length while adding, at best, one genuine insight per section. The examples become the document; the job stories drown. Excerpted below — the full version continued in this pattern for about twice the length of Version 3.*

### Jobs to be Done

**The struggle**

Three situations meet in this feature, each with a different person in it:

- Someone needs to get a file to a person outside their organisation and today emails it as an attachment. Example: a freelance designer sending a draft logo to a client and hoping they reply with feedback on the right version.
- The outside party asked to open or return it, who isn't (and shouldn't need to be) a registered user. Example: the client themselves, or their printer who needs the final artwork.
- Someone accountable for whether external sharing was appropriate. Example: the studio's operations lead, who has to answer during a security review who could see a client's files.

**Job stories — the owner sharing the file** *(first three shown)*

- When I need to get a file to an outsider, I want to share just that file, so I can hand it over without exposing everything around it (e.g. share the final logo, not the whole client folder).
- When I set up a share, I want to control how long it stays open, so it doesn't linger after the reason for it is gone (e.g. 7 days, not forever).
- When I re-share to someone who had access before, I want the old link to stop working, so a stale link can't be reused (e.g. the first link expired and I'm sending a fresh one to the same address).

*…and so on, for every remaining job story, every emotional and social job, every force, and every good/better/best tier. Note the pattern: half the parenthetical examples merely restate the story in different words ("7 days, not forever" adds nothing that "control how long it stays open" didn't already say). The other half are genuinely clarifying — the re-share one, for instance, rescues an otherwise abstract statement. The example budget exists to keep the second kind and cut the first.*

---

## Version 3 — condensed (the target)

*Roughly 40% shorter than Version 2. Every job story from Version 1 survives — ten in, ten out. One grounding example per section. This is the shape every write-up should ship in.*

### Jobs to be Done

**The struggle**

Someone needs to get a file to (or collect one from) a person outside their organisation, and today they chase it over email — versions sprawl, nothing can be unshared (e.g. a freelance designer sending draft artwork to a client). The outside party is not, and shouldn't need to be, a registered user. And someone — the administrator — has to account for that sharing later (e.g. an operations lead answering a security review).

**Core job to be done**

Get a document to (or from) an outside party — granting access to exactly what they need for exactly as long as needed, without them creating an account and without exposing anything else.

*Example thread: share one file with a client for 7 days, confirm they opened it, extend it once when feedback runs late — and access switches off on its own when the project closes.*

**Job stories**

The owner: When I need to get a file to an outsider, I want to share just that file, so I can hand it over without exposing everything around it; when I set it up, I want to control how long it stays open, so it can't linger past its reason; when I re-share to a prior recipient, I want the old link dead, so a stale link can't be reused; when a project wraps up, I want access to switch off on its own, so no outsider is left with a way in; and when access expires mid-task, I want to extend or re-issue it without starting over.

The recipient: When I'm sent something, I want to open it without creating an account; when I come back to finish, I want my access to still work or be easy to renew; and when I open a share, I want to see plainly what I've been given and for how long.

The administrator: When there's a security review, I want to answer "who had access, and when?" in one place; and whenever people share externally, I want them kept within the organisation's rules, so no one over-shares by accident.

**Emotional and social jobs**

The owner: Feel confident a share doesn't expose more than intended; be seen as easy and professional to work with.

The recipient: Feel the request is legitimate and their access is handled carefully; not be asked to sign up or prove more than the task demands.

The administrator: Feel assured the tool enforces the rules without manual policing; be able to demonstrate controlled, logged access to auditors.

**Forces of progress**

Push: email attachments can't be scoped, tracked, or unshared, and versions sprawl. Pull: a scoped, expiring link you can revoke and that leaves a trail. Anxiety: that the link leaks, or stays live forever. Habit: email "just works", and recipients expect an attachment — the feature has to beat that to win.

**Good, better, best**

- **Good (enough):** the owner can share a chosen file with an outsider via a link that expires and can be revoked, and the recipient can open it without an account. The core job gets done.
- **Better:** the trust jobs land — scope and expiry hold, re-shares kill old links, a clear "who has access, until when" view exists, and the recipient can pick up where they left off. The version people choose, not just tolerate.
- **Best:** access switches off on its own when a project closes; expired shares stop leaking any preview or file name; failed invitations surface instead of vanishing; an admin can answer any access question instantly.

*Known gaps at time of writing (what's shipped stops at "Good"):* link scope can be widened (one file → whole folder) with only a confirmation dialogue, no hard limit — so owners can't yet fully trust scope holds (Better); a failed invitation gives no feedback if the email bounces (Better); revoked or expired shares still expose the file name and a thumbnail until a cleanup job runs (Best); and external sharing has to be switched on per team by an administrator before anyone can use it, which blocks even reaching good-enough.

---

## The moves, annotated

What changed across the versions, and why each move is safe:

1. **Version 0 → 1 is a translation, not a copy.** The raw card was all mechanism (links, one-time codes, a Google-Drive-style UI). Version 1 asks "what progress?" of each line and rewrites it as a job — the single most important move, and the one people skip.
2. **The struggle leads with the situation, not the persona.** No "As a designer…". The sentences are about what's happening (needing to get a file to an outsider, chasing it over email) — Klement's point that the circumstance, not the job title, drives behaviour. Roles are named only because the three situations genuinely differ by who's in them.
3. **Job stories merged into one prose block per situation, keeping the grammar.** Every story still parses as When [situation] → I want to [motivation] → so I can [outcome]; only the bullet scaffolding and per-story examples went. The count held: ten job stories in Version 1 (five owner, three recipient, two administrator), ten in Version 3. This is the lossless check — run it every time.
4. **The core job carries the one worked example thread**, doing the work eight per-story examples were doing.
5. **Emotional and social compressed to one line per situation**, dropping the "Emotional:" / "Social:" labels because the sentences carry the distinction themselves.
6. **Forces of progress stayed tight — four lines.** Note the *habit* force ("email just works, recipients expect an attachment") is the one that quietly sinks features; naming it is the payoff of the section.
7. **Good/better/best is phrased as jobs served, not features.** "Scope and expiry hold" is progress; "add a server-side scope check" would be a feature. Keeping the tiers in job-language is what stops the section collapsing into a backlog. In retrospective mode the known gaps hang off *Better* and *Best* with the job still attached — never a bare bug report.

The principle behind every move: the school requires the skeleton and the job-story grammar; it does not require decoration. Examples are illustrative sugar. Budget them.
