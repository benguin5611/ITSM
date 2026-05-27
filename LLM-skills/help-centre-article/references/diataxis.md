# Diátaxis for help centre articles

[Diátaxis](https://diataxis.fr) is a framework that splits technical documentation into four article types, defined by what the reader is trying to do at the moment they open the page. Use it because mixing types in a single article fails every reader: someone learning gets bogged down in edge-case detail, someone looking up a value has to skim through tutorial scaffolding, and someone trying to follow steps loses the thread in a paragraph of background. Classification at authoring time, before any HTML gets written, prevents the article that tries to do three jobs and does none of them.

The four quadrants sit on two axes — action vs cognition, and acquisition vs application — and an article should sit in exactly one.

## The four quadrants

| Quadrant | Reader orientation | Reader question | Example article titles |
|---|---|---|---|
| **Tutorial** | Learning | "Help me learn to use this product" | Getting started — your first project. Running your first end-to-end workflow. |
| **How-to guide** | Doing a specific task | "How do I do this exact thing?" | How to add a team member. How to export a report. How to reassign an open ticket. |
| **Reference** | Looking up information | "What are the exact details?" | Permission roles. Fields in the project setup form. API status codes. |
| **Explanation** | Building understanding | "Why does this work this way?" | Understanding how billing periods work. How users, teams, and projects fit together. Why we separate roles from permissions. |

Diátaxis sometimes calls explanation articles *discussion*, *background*, *conceptual guides*, or *topics*. If source material is labelled with one of those words, it almost certainly belongs in the explanation quadrant.

Two implications worth being explicit about:

- A tutorial is **not** a how-to with extra hand-holding. The Diátaxis framework calls the tutorial-vs-how-to confusion "the root of many difficulties" in technical writing. A tutorial teaches a skill the reader doesn't yet have, and earns the reader's confidence through perfect reliability — every step works, every time. A how-to assumes the reader already knows the shape of what they're doing and just needs the recipe for one specific task.
- Reference is **not** explanation with bullet points. Reference describes *what is* (fields, values, codes, defaults) and only describes. Explanation describes *why* (the model behind the product, the reasoning, the tradeoffs) and is allowed to take a position, weigh alternatives, and express opinion.

## Classification heuristic

Four questions, in order, against the source content the user has handed you.

1. **Does the reader need to *do* something specific right now?** If yes, it's a how-to or a tutorial. If no, it's reference or explanation.
2. **If yes — has the reader done it before, or is this their first encounter with the product surface?** First encounter → tutorial. Done-it-before → how-to.
3. **If no — does the reader need the exact value, field name, code, default, or rule?** Yes → reference. No → explanation.
4. **Sanity check.** Read your draft opening aloud. Tutorial opens with the destination and the journey ("In this tutorial, we'll..." or "By the end, you'll have..."); how-to opens straight at the task, usually with the first imperative or precondition (the Zendesk-rendered title carries the "how do I X?" framing — the body doesn't need to repeat it); reference opens with a one-line scope statement ("This article lists every..."); explanation opens by framing the question or sketching the context ("There are three reasons we..." or "X works this way because..."). If the opening reads as the wrong quadrant, the classification is probably wrong.

These opening shapes and the section names used in `templates/` (Phase 1, What you've learned, Next steps, Before you start, Result, See also) are conventions inspired by Diátaxis. The framework prescribes the *spirit* — tutorials show the destination, deliver early results, and acknowledge the learner's accomplishment; how-tos use conditional imperatives and assume competence — but not the specific labels.

## When to split

A single source can mix quadrants. When that happens, split into separate articles and cross-link them rather than publishing one article that tries to do all of it.

- **Background plus steps → split.** "Understanding billing periods" plus "How to change your billing date" are two articles. The how-to links the explanation under *Before you start*; the explanation links the how-to under *See also*.
- **Tutorial plus reference → split.** "Your first project" should not embed the full field reference. Link to the reference article from inside the tutorial when the reader is about to fill the form.
- **Two how-tos that share a setup → usually two articles.** Duplicate the short setup or extract it into a third "Before you start" reference. Don't fuse them.
- **Reference plus a few lines of explanation → judgement call.** A one-paragraph scope statement at the top of a reference article is fine. A whole *Why we built it this way* section is not.
- **A small lookup inside a how-to is fine if the steps directly consume it.** "Set the role to one of: admin, member, viewer." That's pragmatism — strict Diátaxis would push the values into a separate reference article, but pulling the reader out for three values is worse. The converse — folding steps into a reference article — is not a judgement call; reference *describes and only describes*, and procedural steps belong in a how-to.

The test is: would a reader who landed only on this article get what they came for? If the article contains a section the target reader would skip on every visit, that section probably belongs in a different article.

## Tags, not navigation sections

The quadrant is recorded as a content tag, not as a Zendesk category or section. Help centre users typically land on articles via Google search or in-app help links; when they do browse, their mental model is feature-shaped — "Projects", "Billing", "Team management" — not document-shaped. Carving out a top-level "Reference" or "Tutorials" navigation section would put a how-to about billing and its supporting reference article in different parts of the site, forcing readers through two navigations for one task.

So categories and sections stay feature-oriented. The quadrant lives on the article as metadata and drives *how the article is written* — opening pattern, heading structure, voice, what to include, whether to split — even though the reader rarely sees the label.

## Quadrant tag

Every article carries exactly one type / content tag, drawn from this list:

| Tag | Meaning |
|---|---|
| `tutorial` | Diátaxis: learning-oriented. End-to-end first-time walkthrough that teaches a skill. |
| `how-to` | Diátaxis: task-oriented. Recipe for a specific task the reader already understands the shape of. |
| `reference` | Diátaxis: information-oriented. Lookup table, field list, codes, defaults. Neutral, factual. |
| `explanation` | Diátaxis: understanding-oriented. Concepts, model, reasoning, tradeoffs. Discursive prose. |

Pick exactly one. The type tag is separate from the article's label topics, which name the subject of the article (e.g. `billing`, `team-management`, `projects`).

## Cross-quadrant linking patterns

Quadrants stay distinct inside an article, but they should link to each other generously. Three patterns cover almost every case.

- **Before you start** — appears near the top of a how-to or tutorial. Links sideways to the reference or explanation articles the reader needs to make sense of what they're about to do. For a how-to on changing a billing date, *Before you start* points at the reference for billing fields and at the explanation for how billing periods work.
- **See also** — appears at the foot of tutorials, how-tos, references, and general Explanation articles (but **not** Concept articles, which have a closed four-section shape). Links sideways to the same-topic articles in other quadrants. A reference on permission roles links to the how-to for adding a team member and to the explanation of the product's role model.
- **Next steps** — appears only at the foot of a tutorial. Points forwards to the next thing the reader should learn or the how-to articles they'll need now that they have the skill. A getting-started tutorial closes with "Next steps" links to the how-to articles for running subsequent tasks and for handling common follow-on cases.

Reference articles rarely need *Next steps* — readers don't visit a reference to be taken somewhere else. Explanation articles rarely need *Before you start* — there's nothing to start. How-tos almost always benefit from both *Before you start* and *See also*. Tutorials almost always benefit from both *Before you start* and *Next steps*.

## Concept articles — a specialisation of Explanation

Within Explanation, help centres often have a recurring shape called a **Concept article** — a short, Explanation-mode page about a single named thing in the product (e.g. Projects, Workspaces, Tags, Roles). Concept articles are the spine of the help centre: how-tos link back to the relevant Concept(s) so readers can ground themselves before acting on the thing.

A term earns a Concept article when both are true:

1. It is a **product** thing — a named object, surface, or feature the product exposes, not industry vocabulary.
2. It is best served by Explanation treatment — one Glossary line isn't enough; it benefits from background, "why it exists", and how it relates to other things.

That test cleanly separates Concept articles from Glossary entries.

- Product surfaces with semantics worth explaining (e.g. *Projects*, *Workspaces*, *Roles*, *Tags*, *Notifications*) → **Concept article** (plus a one-line Glossary entry pointing at it, so the Glossary stays the single search surface for "what does X mean in this product").
- Industry or domain terms the product is **about** but does not own → **Glossary entry only**, cross-linked to the Concept article(s) that implement them in the product.

A product help centre explains what the product does, not the industry the product operates in. Industry vocabulary lives in the Glossary as cross-references; it never gets a Concept article of its own. The line "is this a product thing in *this* product?" is the test that holds the boundary.

The per-article structure for a Concept article lives in [templates/explanation.md](../templates/explanation.md) alongside the General Explanation shape — same file, with a decision rule at the top so the author picks the right one. Concept pages are reference-adjacent and need a working model delivered in under five minutes; they are tighter and more scaffolded than the General Explanation shape. Concept articles have a **closed four-section shape** — *What it is* / *Why it exists* / *Key properties* / *How it relates* — and nothing follows *How it relates*. No trailing link list, no closing sub-section. How-tos and reference articles that act on the Concept link *to* this article, not the other way round, so a Concept page never maintains outbound link lists.

## Troubleshooting articles — a how-to variant

Within How-to guides, help centres often have a recurring shape called a **troubleshooting article** — a symptom-driven, diagnostic-checks article that helps a reader find the cause of a problem they've hit (sign-in failing, MFA rejected, notification missing). Troubleshooting articles are how-to variants in Diátaxis terms — they assume the reader knows roughly what they were trying to do, just not why it broke.

A symptom earns its own troubleshooting article when both are true:

1. It has **multiple plausible causes** the reader can self-diagnose by working a short checklist.
2. *And* one of: the reader arrives at the symptom without having been mid-task (e.g. "I can't sign in"), the symptom is common across many tasks (e.g. "MFA code rejected"), or the diagnostic tree has 4+ realistic branches.

Single-cause symptoms — or symptoms tied to one specific task — belong in the **Troubleshooting** section of the relevant how-to, not in a standalone troubleshooting article.

The per-article structure is in [templates/troubleshooting.md](../templates/troubleshooting.md). Troubleshooting articles use the `how-to` content tag — there is no separate troubleshooting quadrant. The diagnostic shape is a sub-structure of how-to, not a fifth Diátaxis classification.
