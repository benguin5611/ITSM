# Explanation template

**Diátaxis quadrant:** Explanation (understanding-oriented). Diátaxis sometimes calls this *discussion*, *background*, *conceptual guides*, or *topics* — if source material is labelled with one of those words, it almost certainly belongs here.

Explanation has **two distinct shapes** in a typical help centre, and both live in this template:

- **General Explanation** — discursive prose about a model, reasoning, or tradeoffs that span multiple things ("Understanding how billing periods work", "Why we separate roles from permissions", "How users, teams, and projects fit together").
- **Explanation article** — a tighter, scaffolded specialisation about **one named product object** (Workspaces, Projects, Roles, Tags, Notifications, etc.).

Pick the shape using the decision rule below, then follow the section for that shape. Both carry the same Diátaxis tag (`explanation`) — the shape difference is structural, not classificatory.

---

## Decision: General Explanation or Explanation article?

**Use Explanation article** when the article is about a **single named product object** — a primitive the product exposes by name. If the article title would be "Workspaces" or "Tags" (the name of one thing) and a reader arrives wanting "what is X in this product?", it's an Explanation article. Use the tighter four-section scaffold (What it is / Why it exists / Key properties / How it relates).

**Use General Explanation** when the article is about a **model, process, or cross-cutting reasoning** — a *system* or *philosophy* rather than one named object. If the article title would be "Understanding X", "Why we Y", or "How A and B fit together", it's General Explanation. Use the discursive prose shape with section headings that name questions.

**Test by article title.** A title that names one thing ("Workspaces", "Notifications") → Explanation article. A title that frames a question or process ("Understanding billing periods", "Why we separate roles from permissions") → General Explanation.

**Test by subject coverage.** Explains *what one named product object is* → Explanation article. Explains *the reasoning that connects several objects or the model behind them* → General Explanation. An article called *Notifications* is an Explanation article (the thing); an article called *Understanding how notifications are scheduled* is General Explanation (the reasoning).

**Edge cases.** An article that starts as an Explanation article ("Notifications") but spends most of its body on the *why* behind scheduling is mis-shaped — extract the why into a sibling General Explanation article ("Understanding how notifications are scheduled") and leave the Explanation article with the tight scaffold. The converse — a General Explanation that ends up describing one object — should usually be re-titled and re-shaped as an Explanation article.

If the article would naturally lead the reader into action steps, split either way: keep the *why* or *what is* here, and link to the [how-to](how-to.md) that carries the steps.

---

## General Explanation

**When to use:** the reader wants to understand the model, the reasoning, or the tradeoffs behind a part of the product. Explanation articles answer "why does this work this way?" — they connect the product to the reader's mental model and to the design choices that aren't visible in the UI. They are not how-to guides, and they don't replace reference articles.

**Voice and tone:** discursive, considered, prose-led. Paragraphs do the work, not bullet lists or tables. Write as if explaining the model to a colleague over coffee: honest about the tradeoffs, willing to name what was left out, comfortable with nuance. Diátaxis explicitly admits opinion, perspective, and the weighing of alternatives — explanation is the one quadrant that's allowed to take a position.

**Structural elements:**

- **Opening:** frame the question the article answers, or sketch the context that makes the rest of the article relevant. No "this article explains..." preamble. Pose the actual question.
- **Section headings name concepts, not tasks or fields.** "How notifications are scheduled", "Why notifications are best-effort, not guaranteed", "Where the user can override the default" — not "Steps" or "Fields".
- **The body is prose.** Lists and tables appear only when they're genuinely the clearest way to express a comparison; they should not be the dominant form.
- **See also:** sideways links to the how-to guides the reader may now want to try and to the reference articles they'll consult next.

**What to avoid:**

- Steps. If the article tells the reader how to do something, it's a how-to guide, not an explanation.
- Field lists or value tables. Those belong in the reference article. Link to it.
- Hedging marketing voice. Explanation is allowed to take a position. "We chose X because the alternative is worse" is a stronger sentence than "Our approach to X is designed to be flexible".
- Pretending there are no tradeoffs. The whole reason an explanation article exists is that something non-obvious is going on — name it.

### Worked example — *Understanding how notifications are scheduled*

> Every change in the product can produce a notification — a comment on a task, an assignment, a status change, a mention. The product doesn't fire those notifications the instant the underlying event happens. There's a short delay, sometimes a batch step, and sometimes a deliberate suppression. This article explains how that scheduling works, why it's deliberately not real-time, and where the user's preferences sit on top of the system's defaults.
>
> #### How notifications are scheduled
>
> A notification scheduler runs continuously and groups events along three axes. The first is *recency* — events that happen within a few minutes of each other for the same recipient and the same source are bundled into a single notification rather than producing one per event. The second is *channel* — email and in-product notifications run on different cadences, with email batched more aggressively (typically every 15 minutes) and in-product near-real-time. The third is *recipient preference* — a recipient can opt every channel down to a daily digest, or up to immediate per-event, and the scheduler honours those overrides.
>
> The grouping is content-aware. Three task assignments to the same person within a few minutes produce one notification listing all three, not three separate notifications. The bundle's subject is generated from the bundle's contents, not a fixed template — so a recipient sees "3 new tasks assigned to you" rather than three near-identical "Task assigned" emails.
>
> #### Why notifications are best-effort, not guaranteed
>
> The scheduler is built for throughput, not for delivery guarantees. If the email provider is briefly slow, the scheduler queues and retries. If the recipient's mailbox bounces the message, the system records the failure and moves on — it does not promote the notification to another channel, and it does not block the underlying product change.
>
> This is a deliberate choice. The alternative — guaranteed delivery — invites two failure modes. The first is that the product becomes coupled to its notification system: changes can't be committed until their notifications have been confirmed, which is the worst kind of latency to introduce. The second is that "guaranteed" delivery against an unreliable downstream (third-party email, push services) is mostly a fiction; reaching for the guarantee creates the appearance of reliability without the substance. Best-effort delivery with visible failure logs is more honest than promised delivery with hidden gaps.
>
> #### Where the recipient overrides the system
>
> Every scheduled notification can be customised by the recipient in their notification preferences. The preferences are layered: a global default, then per-source overrides (e.g. notifications about Project X get treated differently from notifications about Project Y), then per-channel overrides (email less often than in-product). The system applies the most specific layer that matches when scheduling a notification.
>
> This is the part new users sometimes find surprising. Preferences are not a single switch. "Mute notifications" at the top level still leaves any per-source override that promotes a specific project's notifications back up to immediate. The intent is to let the recipient mute the noise without losing the signal — but the cost is that the preferences UI has more depth than a single toggle.
>
> #### See also
>
> - [Notification channels reference](#) — the full list of channels and the cadence each one runs on.
> - [How to change your notification preferences](#)
> - [How to mute a noisy project](#) — the most common follow-on once the model clicks.

---

## Explanation articles (specialisation of Explanation)

**When to use:** the reader has encountered a product-specific term — in the UI, in another help article, or in the Glossary — and needs to understand what it is, why it exists, and how it fits with the rest of the product. Explanation articles are the spine of the help centre: how-tos link back to the relevant Explanation article(s) so readers can ground themselves before acting on the thing.

**What earns an Explanation article.** See [references/diataxis.md](../references/diataxis.md#explanation-articles--a-specialisation-of-explanation) for the principle. In short: a term earns an Explanation article when it is (a) a **product** thing in *this* product — not industry vocabulary — *and* (b) best served by Explanation treatment, where one Glossary line isn't enough. Industry or domain terms the product is *about* live in the Glossary only and cross-link to the Explanation articles that implement them.

**Voice and tone:** explanatory prose, tighter and more scaffolded than General Explanation. Explanation articles are reference-adjacent — readers arrive looking up "what is X in this product" and should leave with a working model in under five minutes. Diátaxis allows Explanation to take a position; Explanation articles inherit that licence but use it sparingly.

**Structural elements:**

1. **What it is** — one-paragraph definition. No preamble. Name the thing, state what it is, identify what part of the product it lives in.
2. **Why it exists** — what problem it solves, or what operational reality made it necessary. This is the section that justifies an Explanation article over a Glossary entry: if there's nothing interesting to say here, the term probably belongs in the Glossary instead.
3. **Key properties / sub-types** — the structure of the concept: its fields, its sub-types, the constraints that govern it, the way it relates to itself. Bullet lists or a small table are appropriate here. Structure, not steps.
4. **How it relates** — links to neighbouring Explanation articles. Prose when the relationship has nuance worth a sentence; a list when it's straightforward.

**That's the whole article.** An Explanation article has exactly those four sections — nothing follows *How it relates*. No trailing link list, no closing sub-section, no further headings. Once you've named the neighbouring Explanation articles in *How it relates*, the article has done its job. How-tos and reference articles that act on the Explanation article link *to* this article, not the other way round, so an Explanation article never needs to maintain outbound link lists. Keep it tight and reference-shaped.

**What to avoid:**

- **Steps.** If the article tells the reader how to do something, it's a how-to. Explanation articles can mention the relevant how-tos by name ("the Tags Explanation article is acted on by *How to tag an item*") but never carry the steps.
- **Exhaustive field-by-field listings.** A few key properties belong in section 3; a complete field reference belongs in a Reference article — link to it.
- **Industry-definition prose.** An Explanation article about a product feature explains the *feature*. It does not explain what the underlying industry term means generally — that belongs in the Glossary entry, which cross-links here.
- **Tasks-disguised-as-prose.** "When you create a Workspace, the system also creates..." reads as a steps article in a tuxedo. Recast as static description: "A Workspace contains exactly one...". If the dynamic behaviour matters, it's a How-to or a Reference.

### Worked example — *Projects*

> A Project is a container for related work in the product. Projects live inside a Workspace — a Project cannot exist on its own, and every Project belongs to exactly one Workspace.
>
> #### Why Projects exist
>
> Work is structured. People collaborate around discrete pieces of work that have an owner, a timeline, and a set of contributors — and the product needs a primitive that captures that shape. Projects give a Workspace a way to group tasks, files, and activity by what they're for, so that a member working on Project A doesn't see the noise from Project B unless they want to.
>
> The workspace-only constraint is deliberate. A Project's meaning depends on which Workspace it belongs to: the same shape of work can be a customer-facing engagement in one Workspace and an internal initiative in another, and the Workspace is what disambiguates them. Pulling Projects out of Workspaces would force every Project to carry that context itself, which either duplicates Workspace metadata onto every Project or strips Projects of the context they need to be meaningful.
>
> #### Key properties
>
> - **Parent Workspace** — exactly one. A Project cannot be moved between Workspaces.
> - **Owner** — exactly one member, who can be reassigned. Other members have roles within the Project.
> - **Visibility** — public to the Workspace, restricted to invited members, or private to the owner.
> - **Tasks, Files, Activity** — the three primary surfaces a Project exposes. All three are scoped to the Project.
>
> #### How Projects relate
>
> Projects live inside [Workspaces](#) and are the primary way work is organised within one. The data a Project captures is acted on by [Tasks](#), [Files](#), and [Tags](#). A Project may trigger an [Automation](#) when a task changes state, or raise a [Notification](#) when activity happens. The tasks that *act on* Projects — creating one, inviting members, archiving — live in the relevant How-to articles.
