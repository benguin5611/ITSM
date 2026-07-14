---
name: help-centre-article
description: Use when writing, editing, or auditing help centre articles. Covers classification (tutorial / how-to / reference / explanation), content shape per type, voice and Australian English conventions, label/content-tag suggestions, and the Zendesk Guide HTML constraints for publishing — supported elements, allowed inline styles, table layout, dark-mode-safe callouts, and known failure modes. Triggers on phrases like "write a help centre article", "knowledge base article", "Zendesk Guide article", "help center article", "audit this article", or pasting source content destined for a help centre.
argument-hint: "[file-path-or-source] [--audit]"
---

# Help Centre Article

A skill for writing help centre articles end to end — classifying the article so it has one job, drafting it with the voice and structure that job demands, then publishing it as Zendesk-compliant HTML.

The writing methodology comes from [Diátaxis](https://diataxis.fr), which splits documentation into four article types defined by what the reader is trying to do at the moment they open the page: **tutorial**, **how-to**, **reference**, **explanation**. Mixing types in a single article fails every reader. Classification at authoring time, before any HTML gets written, prevents the article that tries to do three jobs and does none of them.

The publishing target is Zendesk Guide. Zendesk's help centre editor silently strips unsupported HTML — articles render visually broken with no error message. Every HTML rule in this skill exists because the failure was hit in practice. The HTML rules are detailed in [Section 7 — Publishing rules](#7-publishing-rules--zendesk-html-constraints); refer to them while writing but don't let them dominate the work. The first job is to write a good article.

Australian English throughout — this skill assumes Australian conventions in prose, headings, and table content. Swap to your own locale if you adapt the skill, but pick one and stick to it.

---

## 1. Parse arguments and determine mode

- **File path** (e.g. `article.html`) → **Edit mode** — read and apply changes.
- **`--audit`** (with optional path) → **Audit mode** — validate against every rule, report violations.
- **Pasted source content** (PDF, doc, markdown, table) → **Build mode** — convert to a Zendesk-compliant HTML article.
- **No source** → ask for the content.

If a file path or upload is given, read it **first** before writing any HTML.

---

## 2. Classify the article

Classification comes before planning. The same source, written as a tutorial or as a reference, produces two very different articles — and the wrong choice fails the reader. Decide the type first so the rest of the planning has a frame.

Four questions, in order, against the source:

1. **Does the reader need to *do* something specific right now?** Yes → how-to or tutorial. No → reference or explanation.
2. **If yes — first encounter or done it before?** First encounter → tutorial. Done it before → how-to.
3. **If no — needs an exact value, field, code, default?** Yes → reference. No → explanation.
4. **Read your draft opening aloud.** Tutorial opens with the destination ("By the end you'll have..." or "In this tutorial, we'll..."); how-to opens straight at the first precondition or step — the Zendesk-rendered title carries the task statement, so the body shouldn't repeat it ("This article shows you how to..."); reference opens with a one-line scope statement ("This article lists every..."); explanation opens by framing the question ("There are three reasons we..."). If the opening sounds like the wrong type, the classification is wrong.

**When to split.** If the source genuinely mixes types (background + steps; tutorial + reference; two how-tos sharing setup), split into separate articles and cross-link. A small lookup directly consumed by a how-to's steps can stay inline; a whole reference section or a whole *why* section cannot.

**Surface rule.** Every Build delivery names the chosen type near the top so the user can sanity-check the classification before they paste.

See [references/diataxis.md](references/diataxis.md) for the full framework, the cross-quadrant linking patterns, the single-object Explanation article shape (a specialisation of the explanation quadrant), and the troubleshooting-article variant of How-to. The per-type writing structure is in [templates/tutorial.md](templates/tutorial.md), [templates/how-to.md](templates/how-to.md), [templates/reference.md](templates/reference.md), [templates/explanation.md](templates/explanation.md) (covers both General Explanation and the Explanation article specialisation), and [templates/troubleshooting.md](templates/troubleshooting.md) for symptom-driven diagnostic articles (a how-to variant; still tagged `how-to`). Each markdown template carries a *What earns a [type] article* test paragraph — treat that test as the classification rule before drafting. The type templates are markdown because they describe content shape; [templates/article-skeleton.html](templates/article-skeleton.html) stays HTML because it demonstrates Zendesk's allowed-styles palette and table-layout pattern.

---

## 3. Plan the article

Before writing any HTML:

- **Confirm the type** chosen in Section 2 still fits after reading the full source. If the source genuinely mixes types, decide the split now — article titles and link points — before writing HTML.
- **Confirm scope and content fidelity.** Read the **entire** source — every row, every footnote, every appendix. Count rows or items if the source is tabular. The most common failure in this skill is silently dropping content because the source was skimmed rather than read.
- **Identify all footnote markers** (¹ ² ³ † ‡ etc.) and their definitions. If the source has a footnote, the output must have both the marker in context and the definition.
- **Note the article title.** This will be set in Zendesk's metadata, not the body. Do not put it in the body as `<h1>`.
- **Decide the rendering approach.** Most help centre content is prose + tables + lists. Reach for interactive widgets only if the user explicitly wants one — and remember they cannot be interactive (no JS in Zendesk articles).
- **Identify the table widths.** If a table has 5+ columns of comparable importance, plan for `overflow-x: auto` and `min-width` on the table.
- **Plan the type tag and label topics.** The type is one of `tutorial`, `how-to`, `reference`, `explanation`. The label topics are a flat list of 4–8 reusable, lowercase-hyphenated tags that name the article's subject (e.g. `permissions`, `roles`, `onboarding`). See [Suggested labels and content tags](#suggested-labels-and-content-tags) below.
- **Ask clarifying questions** if scope is ambiguous, especially: "Is this the full content?" when the source is long.

---

## 4. Write the article

Use two templates together:

- The article-type template — [tutorial](templates/tutorial.md), [how-to](templates/how-to.md), [reference](templates/reference.md), [explanation](templates/explanation.md), or [troubleshooting](templates/troubleshooting.md) — for **content shape**: opening, headings, voice, what to include.
- [templates/article-skeleton.html](templates/article-skeleton.html) for **Zendesk HTML rendering**: inline-style palette, table layout, footnote pattern.

The markdown template tells you *what to write*; the HTML skeleton tells you *how to mark it up*.

Apply the rules from [Section 7](#7-publishing-rules--zendesk-html-constraints) as you write. Copy and update this progress tracker as you work:

```
Article progress:
- [ ] Article type chosen and emitted as the type / content tag in the delivery
- [ ] Read the entire source — every section, every row, every footnote
- [ ] Voice and structure match the chosen type's template (tutorial / how-to / reference / explanation / troubleshooting)
- [ ] Output is an HTML fragment — NO <!DOCTYPE>, <html>, <head>, <body>, <title>, <meta>
- [ ] No top-level <h1> in the body (Zendesk renders the article title from metadata)
- [ ] No <style> tags — all styling is inline
- [ ] No <script> tags — no JS, no event handlers (onclick, onchange, etc.)
- [ ] No <form>, <input>, <button>, <textarea>, <object>, <embed>, <applet> — unsafe HTML, stripped from articles by default
- [ ] All inline styles use only properties from the Zendesk allowed list (see references/allowed-inline-styles.md)
- [ ] No `margin*` inline styles on any element except <table> — Zendesk strips them silently. Use `padding*` instead (allowed globally)
- [ ] No `padding-bottom` on headings unless extra space genuinely needed — themes typically provide heading-to-content spacing already
- [ ] List indentation uses `padding-left` (not `margin-left`) on <ul>/<ol>
- [ ] No hardcoded light `background-color` on ANY element (not just callouts). `#fffaf0`/`#f8fafc`/`#fafafa`/`white` etc. on `<div>`/`<td>`/`<th>`/`<tr>`/`<p>` survive into dark mode and produce light-on-light invisible text. Use translucent `rgba()` instead — callouts use the patterns in references/callout-patterns.md; table headers, row-header cells, and subtle accents use `rgba(0, 0, 0, 0.04)`.
- [ ] Callouts and any other coloured-bg containers have no inline `color` on the wrapper or inner elements — let the theme paint
- [ ] Muted text (footnotes, captions) uses `color: #999` (a neutral mid-grey that reads in both modes)
- [ ] No CSS variables (var(--foo)) — explicit colour values only
- [ ] No CSS pseudo-classes (:hover, :focus, :active) — inline styles can't express them
- [ ] No @media queries — not expressible inline
- [ ] No animation, transition, transform, cursor, box-shadow — not in allowed list
- [ ] All <a href> protocols are in {ftp, http, https, mailto, sftp, sms, tel}
- [ ] All <img src> protocols are in {blob, data, http, https}
- [ ] Any <iframe> uses only allowed embed domains (YouTube, Vimeo, Loom, Wistia, JWPlayer, Vidyard, Brightcove, Microsoft Stream)
- [ ] Wide tables (5+ columns or >700px content width) wrapped in <div style="overflow-x: auto;">
- [ ] Wide tables have min-width set on <table> to prevent column collapse
- [ ] Multi-column tables have min-width set on each <th> to prevent header wrapping
- [ ] First column min-width tuned so content cells don't have excessive whitespace
- [ ] Multi-word column headers use <br> to wrap onto two lines cleanly (e.g. "View Only<br>Admin")
- [ ] Every footnote marker in source has both an in-context marker AND a definition in the output
- [ ] All counts (rows, list items, capabilities) from source match the output (verify by counting)
- [ ] Section heading hierarchy is consistent (h2 for sections, h3 for sub-sections; no h1)
- [ ] No empty <span> or <i> tags
- [ ] No empty <p> tags (Zendesk inserts &nbsp;, creating unwanted whitespace)
- [ ] No HTML comments containing implementation notes that should be removed before publish
- [ ] All prose, headings, and table content follow the style reference at `references/style-reference.md` — Australian English, sentence-case headings, no full stops in acronyms or on headings, common nouns and role titles lowercase. CSS property names/values, Zendesk product names ("help center"), and vendor names stay as-published.
- [ ] Type / content tag (one of `tutorial`, `how-to`, `reference`, `explanation`) and a flat list of 4–8 lowercase-hyphenated label topics listed alongside the article
```

---

## 5. Audit phase (audit mode only)

Run every check below against the article. For each violation found, report the location and the fix.

### A. Unsafe HTML checks (article will render incorrectly)

- Any `<script>`, `<style>`, `<form>`, `<input>`, `<button>`, `<textarea>`, `<object>`, `<embed>`, or `<applet>` tag? → Remove. These are unsafe HTML; in articles the content is stripped from the HTTP response.
- Any `on*` event handler attribute (`onclick`, `onchange`, `onload`, `onmouseover`, etc.)? → Remove. Zendesk strips them.
- Any inline `javascript:` URL in `href` or `src`? → Remove. Only `ftp`, `http`, `https`, `mailto`, `sftp`, `sms`, `tel` are allowed for `href`; only `blob`, `data`, `http`, `https` for `src`.

### B. Document-structure checks (will conflict with Zendesk's wrapper)

- Any `<!DOCTYPE>` declaration? → Remove. Articles are fragments.
- Any `<html>`, `<head>`, `<body>`, `<title>`, or `<meta>` tag? → Remove.
- Any `<link>` tag (e.g. external stylesheet)? → Remove. Theming belongs in the help centre theme, not the article.
- Any top-level `<h1>` rendering the article title in the body? → Remove. Zendesk shows the article title automatically from metadata; an in-body h1 produces a duplicate title.

### C. Inline style checks (will be stripped or rendered wrong)

- Any inline style using a CSS variable (`var(--foo)`)? → Replace with the resolved colour value. CSS variables defined in the article scope don't work.
- Any inline style using `cursor`, `transition`, `transform`, `animation`, `filter`, `backdrop-filter`, `pointer-events`, `box-shadow`, `position`, `z-index`, `opacity`, or other properties not in the Zendesk allowed list (see [references/allowed-inline-styles.md](references/allowed-inline-styles.md))? → Remove the property.
- Any `margin`, `margin-top`, `margin-bottom`, `margin-left`, or `margin-right` inline style on a non-`<table>` element (e.g. `<div>`, `<h1>`–`<h6>`, `<p>`, `<ul>`)? → Replace with `padding-*`. Margin is only allowed on `<table>` elements; on every other element it's silently stripped, so spacing collapses to whatever the theme provides.
- Any heading (`<h2>`, `<h3>`, etc.) with `padding-bottom` set inline? → Question whether it's needed. Themes typically provide a natural heading-to-content gap; adding `padding-bottom` stacks on top of it. Remove unless the theme gap is provably insufficient.
- Any inline `color` on a prose element (`<p>`, `<li>`, `<span>`, `<td>`, `<th>`, `<strong>`, `<h2>`–`<h4>`)? → If your theme paints `.article-body` text via `!important` rules (most modern themes do, especially in dark mode), the inline `color` either has no effect or breaks dark mode. Remove. Only set `color` inline on muted helpers like footnotes — and use `color: #999`, the one neutral that reads acceptably in both modes.
- Any inline `font-size`, `font-weight`, or `line-height` on `<h2>`/`<h3>`/`<h4>`/`<p>`/`<ul>`? → Remove. Themes typically set these with `!important`; inline values either lose silently or visibly fight the theme.
- Any **inline hardcoded light `background-color` on ANY element** (`<div>`, `<td>`, `<th>`, `<tr>`, `<p>`, `<span>`, `<figure>`, `<section>`, etc.)? Common culprits: `#fffaf0`, `#fef3c7`, `#fff3cd`, `#eff6ff`, `#ecfdf5`, `#fef2f2`, `#f8fafc`, `#fafafa`, `#f5f5f7`, `#ffffff`, `white`. → Replace with a translucent `rgba()` so the background tints the page surface in both light AND dark mode. This rule applies regardless of the element's role: a callout div, a row-header `<td>` in the first column of a table, a `<th>` cell, a banner `<section>`, anything. The failure shape is always the same — the light bg survives both modes unchanged, the theme paints text near-white in dark mode, light-on-light = invisible. Canonical substitutes:
  - **Callout backgrounds** (info / warning / tip) — use the patterns in [references/callout-patterns.md](references/callout-patterns.md).
  - **Table header / row-header / accent-cell backgrounds** — use `rgba(0, 0, 0, 0.04)` (a neutral translucent darken that reads as a subtle "card" in both modes).
  - **Subtle card / panel backgrounds** — same `rgba(0, 0, 0, 0.04)`. If a stronger separation is needed, go to `rgba(0, 0, 0, 0.08)`.

  Strip any inline `color` from the wrapper and inner elements at the same time — let the theme paint the text.
- Any inline `background`, `color`, `border`, or `padding` on `<code>`, `<pre>`, `<blockquote>`, or `<figcaption>`? → Most help centre themes already style these inside `.article-body`. Inline values are overridden or fight the theme. Remove unless you've verified your theme leaves these unstyled. See [references/theme-notes.md](references/theme-notes.md).
- Any inline style attempting `:hover`, `:focus`, `::before`, `::after`, or other pseudo-class/element via inline syntax? → Not expressible inline. Remove or move to theme CSS.
- Any `@media` query, `@keyframes`, or `@supports` block? → Cannot live inline. Remove.
- Any flexbox or grid alignment property (`gap`, `flex-direction`, `justify-content`, `align-items`, `grid-template-*`)? → Not in the allowed list. Use tables for grid-like layouts; basic block layout for everything else.

### D. Table / layout checks (will render visually broken)

- Any `<table>` with 5+ columns and no overflow wrapper? → Wrap in `<div style="overflow-x: auto;">` so the table can scroll horizontally on narrow viewports instead of collapsing columns.
- Any wide `<table>` without `min-width` set inline? → Add `min-width: NNNNpx` (typically 1000–1200px) to prevent column collapse. Tune so the first column doesn't get the lion's share of unallocated space.
- Any column header `<th>` with multi-word text (e.g. "View Only Admin", "Duty Manager") and no `min-width` set? → Add `min-width` per column. Without it, narrow columns squish their headers into 2-character-wide stacks.
- Any multi-word `<th>` content that would benefit from a `<br>` line break to keep alignment tidy? → Insert `<br>` between words.
- Any `<table>` where the first column has visibly excessive whitespace? → Reduce its `min-width` (e.g. from 240px to 200px) and consider lowering the table's `min-width` so less excess space is distributed to it.
- Any `<table>` with empty `<tr>` or empty `<td>` rows that don't add structure? → Remove.

### E. Content fidelity checks (most important)

- Does every section, row, and item from the source appear in the output? → Re-read the source. Count list items, table rows, capabilities, sections. The most common failure is omission. **Calibrate by type**: reference articles must be exhaustive (every row, every value — Diátaxis treats reference completeness as inviolable). Tutorials should be *usefully* complete (covers the path; doesn't have to cover every edge case from the source). Explanation should be *reasonably bounded* (covers the question; doesn't have to cover every adjacent topic). How-to guides cover the one task end to end and no more.
- Does every footnote marker in the source (¹ ² ³ etc.) appear in the output **both** as an in-context marker (on the row/sentence it qualifies) **and** as a defined explanation at the foot of the article? → Add whichever is missing.
- Are all link targets from the source preserved? → Cross-check.
- Are images referenced via `src` with one of {`blob`, `data`, `http`, `https`} protocol? → Fix protocol or remove image.

### F. Empty-element / cleanup checks

- Any empty `<p>` tags? → Zendesk replaces these with `<p>&nbsp;</p>` (visible blank line). Remove unless a deliberate spacer.
- Any empty `<span>`, `<i>`, `<em>`, `<strong>`, `<div>`? → Zendesk auto-removes these on save; cleaner not to author them.
- Any `data-list-item-id="e..."` attributes on `<li>` elements? → Harmless WYSIWYG artefacts — not consumed by theme CSS or JS. Strip during a tidy pass, or leave them if the article will be edited through the WYSIWYG later.
- Any `<zd-html-block>` wrapper elements? → Strip. These are WYSIWYG markers around pasted HTML blocks; they don't render anything and Zendesk re-adds them on save if needed.
- Any `<figure class="wysiwyg-table">` wrappers around `<table>` elements? → Harmless. Strip the wrapper for cleaner source, or leave it if the article will be WYSIWYG-edited later.
- Any `id="h_01..."` attributes on headings? → Zendesk auto-generates these as in-page anchors. Strip if you're writing fresh source; preserve if you're editing an existing article that already has them (table-of-contents widgets depend on them).

### G. Style reference checks

Audit against the style guide at [references/style-reference.md](references/style-reference.md). The most common help-centre-article violations to look for:

- Headings in Title Case → recase to sentence case ("Setting Up Workspaces" → "Setting up workspaces"). Applies to `<h2>`, `<h3>`, `<h4>`.
- Headings, captions, or table headers ending in a full stop → remove.
- Acronyms with internal full stops → strip the stops.
- Abbreviations with a trailing stop (`Dr.`, `Mr.`, `Mt.`) → remove unless genuinely ambiguous.
- `<li>` items ending in a full stop or semicolon when the item isn't a full sentence → remove the trailing punctuation.
- Role titles or common nouns capitalised mid-sentence (`the Administrator`, `the Customer`) → lowercase unless the title precedes a person's name.
- Double spaces after a full stop → collapse to single space.
- Spelling, currency, dates, numbers, quotation style → see the reference for the full rule set.

### H. Australian English checks

- Any American spelling in prose, headings, table cells, list items, or footnote text? → Replace with Australian equivalent. Common offenders:
  - `color` → `colour` (in prose only — CSS property names stay American)
  - `behavior` / `behavioral` → `behaviour` / `behavioural`
  - `organize` / `organization` / `organized` → `organise` / `organisation` / `organised`
  - `customize` / `customization` → `customise` / `customisation`
  - `optimize` / `optimization` → `optimise` / `optimisation`
  - `centralize` / `standardize` / `recognize` / `analyze` → `centralise` / `standardise` / `recognise` / `analyse`
  - `center` (in prose) → `centre` (but `text-align: center` in CSS stays American)
  - `gray` → `grey`
  - `defense` / `offense` → `defence` / `offence`
  - `license` (as noun) → `licence`; `license` (as verb) stays
  - `practice` (as verb) → `practise`; `practice` (as noun) stays
  - `fulfill` → `fulfil`; `enrollment` → `enrolment`; `installment` → `instalment`
  - `dialog` → `dialogue` (in prose); `dialog` stays only if it's a UI control name like "dialog box"
- Any American date format (`MM/DD/YYYY`, `May 8, 2026`)? → Use `DD/MM/YYYY` or `8 May 2026` (no comma after the day).
- Any "zip code" terminology? → Use "postcode".
- Any "cell phone"? → Use "mobile" or "mobile phone".

**Stays American (do not change):**

- CSS property names and values: `color`, `background-color`, `text-align: center`, `text-decoration`.
- Zendesk product/feature names exactly as Zendesk publishes them: "help center" (lowercase, American), "Knowledge admin", "content blocks".
- Vendor and product names quoted verbatim.
- Code examples, URLs, file names, IDs.

### I. Type tag and label topics

- Did the output include the type / content tag (exactly one of `tutorial`, `how-to`, `reference`, `explanation`)? → If not, add it.
- Did the output include a flat list of 4–8 lowercase-hyphenated label topics? → If not, add it. Topics only — no audience/feature/domain/format sub-categorisation, no "recommended minimum set".

### J. Classification check

- Does the article have a single dominant type (tutorial, how-to, reference, or explanation)? → If it tries to be more than one, propose a split with concrete article titles.
- Does its opening sentence, heading structure, and voice match that type? Tutorial opens by naming the outcome and the skill the reader will have; how-to opens straight at the first precondition or step; reference opens with a one-line scope statement; explanation opens by framing the question or sketching the context. → If the opening reads as the wrong type, recast or reclassify.
- Does the article contain content that belongs in a different type — e.g., a full reference table sitting inside an explanation, step-by-step instructions inside a reference, "why we built it this way" inside a how-to? → Recommend a split. Name the proposed articles, one per type, with the cross-links between them.
- **Explanation articles only:** is the article an Explanation article (an `explanation`-tagged article about a single named product object)? If so, does it follow the **closed four-section shape** — *What it is* (opening paragraph, no heading) / *Why X exists* / *Key properties* / *How X relates* — with **nothing after *How X relates***? → If a fifth section exists (a trailing link list, a closing summary, anything after the relationships section), remove it. Explanation articles have a deliberately closed shape; how-tos and reference articles link *to* the Explanation article, not the other way round.

---

## 6. Output

Every Build mode delivery includes both:

1. **The HTML fragment**, ready to paste into Zendesk's source code editor. Save to the appropriate output path and present the file. Do not wrap the file content in code fences; use code fences only when showing the HTML inline in chat for review.

2. **The type/content tag and a flat list of label topics.** Two lines, nothing else. Example presentation:

   > **Type / content tag:** `how-to`
   >
   > **Label topics:** `staff`, `roles`, `permissions`, `onboarding`, `administrator-guide`

   The type tag is exactly one of `tutorial`, `how-to`, `reference`, `explanation`. The label topics are a flat list of 4–8 lowercase-hyphenated tags — no audience / feature area / domain / format sub-categorisation, no "recommended minimum set", no further breakdown. The user pastes them straight into Zendesk.

For Edit mode: apply edits using `str_replace` or rewrite the file. Confirm with the user before destructive changes. Re-emit the suggested tags only if the edits change the article's topic or type.

For Audit mode: output a findings report grouped by severity (A through J). Provide concrete fixes, not generic advice. If section J finds a mixed-type article, propose the split — name the resulting articles and the cross-links between them.

---

## 7. Publishing rules — Zendesk HTML constraints

This section is the background guidance for getting an article to render correctly in Zendesk. It's secondary to writing the article well — but ignoring these rules produces articles that look fine in the editor and render visually broken on the live page, with no error message and no warning.

Before building anything for Zendesk, review the two source-of-truth articles:

- **Supported HTML**: https://support.zendesk.com/hc/en-us/articles/6644509092378-Supported-HTML-for-help-center-articles
- **Editing source code**: https://support.zendesk.com/hc/en-us/articles/4408824584602-Editing-the-source-code-of-help-center-articles

These articles change occasionally. If a user reports unexpected stripping or rendering, re-fetch them.

### Zendesk fundamentals

**Articles are content fragments, not full HTML documents.** Zendesk wraps your HTML inside its own template (header, footer, sidebar, theme CSS). Do **not** include `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`, `<title>`, or `<meta>` tags — Zendesk strips them or they break the wrapping template.

**Zendesk renders the article title separately.** The article title is set in the article's metadata (the title field in the Zendesk article editor) and rendered automatically above the article body. **Do not include a top-level `<h1>` in the body** — it produces a duplicate title. Start the body with `<h2>` for the first section heading, or with prose if the opening section needs no heading.

**The editor has two modes:**

1. **WYSIWYG editor** — what most authors use
2. **Source code editor** — accessed via the `<>` icon; required for custom HTML

**Two content types with different cleanup rules:**

- **Articles** — unsupported HTML is silently dropped from the HTTP response. The article saves and the editor doesn't complain, but the live page renders without the stripped content. There is no warning.
- **Content blocks** — unsupported HTML is wrapped in an editable HTML block (cleaner failure mode).

**The "Clean up styles" button** strips inline styles deemed non-essential. Only run it deliberately — it can flatten intentional formatting.

**Best practice per Zendesk**: use `class` attributes with CSS defined in the help centre theme. **Reality for ad-hoc articles**: inline styles are the only way to guarantee rendering without coordinating theme changes. This skill defaults to inline styles for self-contained article authoring. See the Inline styles vs CSS classes section in [references/html-and-layout-rules.md](references/html-and-layout-rules.md).

**Margin properties are only allowed on `<table>` elements.** This is the single biggest gotcha in Zendesk's allowed-styles list. `margin`, `margin-top`, `margin-bottom`, `margin-left`, `margin-right` are NOT in the global allowed list — they're only allowed on `<table>`. Use them on a `<div>`, `<h2>`, `<p>`, `<ul>`, or any other element and Zendesk silently strips them, leaving the element with whatever spacing the theme provides. Use `padding` instead — `padding` and all four `padding-*` properties are globally allowed. To create vertical space between any two non-table elements, use `padding-top` on the lower element or `padding-bottom` on the upper one. To indent a list, use `padding-left: 20px` on the `<ul>` or `<ol>`, not `margin-left`.

**Spacing tip — let the theme handle heading-to-content gaps.** Most help centre themes already provide spacing between a heading and the next element (paragraph, list, table). Adding `padding-bottom` to a heading stacks on top of that and produces visibly excessive space. Reach for `padding-bottom` on headings only when the theme's natural gap is genuinely too small. Use `padding-top` on a heading to create extra space above it (typically before a major section), and trust the theme for the gap below.

**Dark mode is widely supported.** If your help centre theme supports dark mode — most modern Zendesk themes do — the theme typically forces `.article-body` text colours via `!important` rules that swap between light and dark palettes. Two consequences for inline styles: (1) any inline `color` you set on a prose element (`<p>`, `<li>`, `<h2>`, `<td>`, etc.) loses to the theme override — it's either a no-op or it breaks dark mode if it survives Zendesk's cleanup; (2) any inline `background-color` survives both modes unchanged, so a hardcoded light callout background plus theme-painted near-white dark-mode text yields invisible content. See the Dark mode compatibility section in [references/html-and-layout-rules.md](references/html-and-layout-rules.md) and [references/callout-patterns.md](references/callout-patterns.md). General theme behaviour and the principles that drive these rules are in [references/theme-notes.md](references/theme-notes.md).

### Reference files — open when a check needs the full list

- **[references/html-and-layout-rules.md](references/html-and-layout-rules.md)** — supported/unsafe HTML elements, allowed inline styles summary, allowed `href`/`src` protocols, iframe embed domains, the wide-table layout pattern, spacing strategy, footnote pattern, image insertion workflow, dark mode compatibility, and inline styles vs CSS classes.
- **[references/allowed-inline-styles.md](references/allowed-inline-styles.md)** — the canonical Zendesk allowed-inline-styles list.
- **[references/known-failure-modes.md](references/known-failure-modes.md)** — every known failure, with cause and fix. Read it when diagnosing a broken article; skim it before delivering a complex one.
- **[references/callout-patterns.md](references/callout-patterns.md)** — dark-mode-safe callout HTML.
- **[references/theme-notes.md](references/theme-notes.md)** — theme behaviour: palette tokens, what the theme already styles, what it isn't.
- **[references/diataxis.md](references/diataxis.md)** — the full Diátaxis framework.

### Content fidelity — verify completeness

This is the failure mode most likely to ship. Before declaring done:

1. **Count items in the source** — rows, list items, sections, capabilities, headings.
2. **Count items in the output** — same categories.
3. **Match the totals.** If they don't match, find what's missing.
4. **Spot-check the last and middle items** — Claude tends to drop trailing content and content from the middle of long lists.

### Suggested labels and content tags

Every Build delivery emits exactly two things alongside the HTML:

1. **Type / content tag** — one of `tutorial`, `how-to`, `reference`, `explanation`. This is the classification expressed as a content tag. Pick exactly one — see [references/diataxis.md](references/diataxis.md) for the framework.
2. **Label topics** — a flat list of 4–8 lowercase-hyphenated tags that name the article's subject (e.g. `permissions`, `roles`, `onboarding`, `staff-management`).

No further categorisation. Do not split topics into audience / feature area / domain / format sub-buckets. Do not propose a "recommended minimum set". The user pastes the type tag and the topic list straight into Zendesk.

**Conventions for label topics:**

- Lowercase, hyphen-separated: `access-control`, not `Access Control` or `access_control`.
- Reusable: prefer tags that other articles in the same area might also use (`permissions`, `roles`, `staff`) over hyper-specific ones (`v2-staff-permissions-page`).
- 4–8 topics total. Fewer for a narrowly scoped article; more if it genuinely spans several subjects.
- Topics name the *subject* of the article. They do not name the article's shape (`troubleshooting`, `faq`) or its type — the type is the separate content tag.

## 8. Writing reference — Australian English and style

The full style reference is in [references/style-reference.md](references/style-reference.md). Read it before drafting or auditing a new article. The Australian English summary that follows is the quick-lookup version; the reference covers punctuation, names, numbers, dates, voice, and the longer style decisions.

The full Australian English rule set lives in `references/style-reference.md`; the audit checklist's section H carries the common offenders. Zendesk-specific exceptions below.

### Zendesk-specific style exceptions

- Zendesk product names stay as Zendesk publishes them, including capitalisation: `help center` (lowercase, American spelling), `Knowledge admin`, `Guide`, `content blocks`.
- CSS property names and values inside inline `style` attributes stay American (`color`, `background-color`).
- Vendor product names and verbatim vendor-doc quotes stay as published.

---
