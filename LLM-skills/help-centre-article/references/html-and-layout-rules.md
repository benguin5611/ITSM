# Zendesk HTML and Layout Rules

Detailed lookup material for building Zendesk-compliant article HTML. The workflow and audit checklists live in `SKILL.md`; this file holds the full rules they enforce.

### Supported HTML elements

The full canonical list lives at the Zendesk supported-HTML article. Common safe elements:

**Structural**: `div`, `section`, `article`, `aside`, `header`, `footer`, `nav`, `figure`, `figcaption`, `details`, `summary`

**Text**: `h1` through `h6`, `p`, `blockquote`, `pre`, `hr`, `br`

**Inline**: `a`, `span`, `strong`, `em`, `b`, `i`, `u`, `s`, `code`, `kbd`, `mark`, `small`, `sub`, `sup`, `cite`, `q`, `time`, `del`, `ins`, `var`, `samp`, `dfn`, `abbr`, `bdi`, `bdo`, `ruby`, `rt`, `rp`, `data`

**Lists**: `ul`, `ol`, `li`, `dl`, `dt`, `dd`

**Tables**: `table`, `thead`, `tbody`, `tfoot`, `tr`, `th`, `td`, `caption`, `colgroup`, `col`

**Media**: `img`, `audio`, `video`, `source`, `track`, `iframe` (restricted domains only)

**Common attributes**: `aria-*`, `class`, `data-*`, `dir`, `id`, `lang`, `tabindex`, `title`

### Unsafe HTML (stripped from articles by default)

```
applet, button, embed, form, input, object, script, style, textarea
```

There is a Knowledge admin setting ("Display Unsafe Content") to allow these, but it carries security warnings and should not be assumed enabled. Default to never using these.

### Allowed inline styles

Zendesk publishes an explicit allowed list for inline styles. Anything not on the list is stripped. The full list is in [references/allowed-inline-styles.md](allowed-inline-styles.md). Highlights:

**Layout**: `display`, `width`, `height`, `min-width`, `min-height`, `max-width`, `max-height`, `padding*`, `box-sizing` (NOT `margin*` — table-only)

**Typography**: `font*`, `color`, `text-align`, `text-decoration*`, `text-indent`, `text-transform`, `letter-spacing`, `line-height`, `word-spacing`, `white-space`, `vertical-align`

**Borders & background**: `border*`, `border-radius`, `background*`, `outline`

**Tables**: `border-collapse`, `border-spacing`, `margin*` (only on `<table>` elements)

**Notably absent (do NOT use inline)**: `cursor`, `transition`, `transform`, `animation`, `filter`, `box-shadow`, `pointer-events`, `position`, `top/left/right/bottom`, `z-index`, `opacity`, `flex*`, `grid*`, `gap`, `margin*` (on non-table elements)

For grid-like layouts, use `<table>`. For everything else, basic block layout with `padding` provides reliable spacing.

### Allowed `href` protocols

```
ftp, http, https, mailto, sftp, sms, tel
```

### Allowed `src` protocols

For `img`, `audio`, `video`, `source`, `track`:

```
blob, data, http, https
```

### Allowed `<iframe>` embed domains

```
https://content.jwplatform.com/
https://fast.wistia.com/
https://play.vidyard.com/
https://player.vimeo.com/
https://players.brightcove.net/
https://web.microsoftstream.com/
https://www.loom.com/
https://www.microsoft.com/
https://www.youtube-nocookie.com/
https://www.youtube.com/
```

If an embed source isn't on this list, the iframe is stripped.

The list mirrors Zendesk's published allowed list exactly (checked July 2026). That includes `web.microsoftstream.com`, which Microsoft now redirects to `stream.office.com`; the redirect target isn't on Zendesk's list, so don't swap it in.

### Wide tables — the layout pattern

Most Zendesk themes render the article container at roughly **770–810px effective width** on desktop. The threshold of 700px content width gives a small safety margin for narrower viewports and browser zoom.

For any table with 5+ columns or content width ≥ 700px:

```html
<div style="overflow-x: auto; padding-bottom: 48px;">
<table style="width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #999; min-width: 1000px;">
  <thead style="background-color: rgba(0, 0, 0, 0.04); border-bottom: 2px solid #999;">
    <tr>
      <th style="padding: 12px; text-align: left; font-weight: 600; color: #999; border-right: 1px solid #999; min-width: 200px; text-transform: uppercase; letter-spacing: 0.5px; font-size: 11px;">First col</th>
      <th style="padding: 12px; text-align: center; font-weight: 600; color: #999; border-right: 1px solid #999; min-width: 55px; text-transform: uppercase; letter-spacing: 0.5px; font-size: 11px;">Short</th>
      <th style="padding: 12px; text-align: center; font-weight: 600; color: #999; border-right: 1px solid #999; min-width: 65px; text-transform: uppercase; letter-spacing: 0.5px; font-size: 11px;">Two<br>Words</th>
      <!-- ... -->
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #999;">
      <td style="padding: 12px; border-right: 1px solid #999; font-weight: 500;">Row label</td>
      <td style="padding: 12px; text-align: center;">value</td>
    </tr>
  </tbody>
</table>
</div>
```

Critical pieces:

- **`<div style="overflow-x: auto;">`** wrapper — table scrolls instead of collapsing on narrow viewports.
- **`padding-bottom` on the wrapper div** (not `margin-bottom` — would be stripped on a div). Provides space before the next element.
- **`min-width` on `<table>`** (1000–1200px typical) — prevents column collapse when content is short. Tune so the first column doesn't end up with disproportionate whitespace.
- **`min-width` on each `<th>`** — prevents narrow columns from squishing headers into 2-char stacks.
- **`<br>` in multi-word headers** — keeps alignment clean instead of letting headers wrap unpredictably.
- **Smaller `font-size` on multi-word headers** (e.g. 11–12px vs 13px body) — visual fit without truncation. Pair with uppercase + letter-spacing on `<th>` for a tidy header row.
- **First column `min-width` should be just enough for the longest cell content.** If the column has noticeably excessive whitespace, reduce its `min-width` and consider reducing the table's `min-width` correspondingly.
- **Border colour `#999`** is a mode-portable neutral. Don't reach for `#e2e8f0`/`#edf2f7` — they vanish against a dark page background.
- **Header background `rgba(0, 0, 0, 0.04)`** tints whatever surface is underneath, so it darkens in light mode and barely shifts in dark mode — never breaks.
- **`color: #999` on `<th>` text** is the only safe inline colour. **No inline `color` on `<td>` body cells** — let the theme paint the cell text in mode-appropriate colour.
- **Most help centre themes apply NO default styling to `<table>` inside `.article-body`** — every property in the example above must be inline.

### Spacing strategy

Because `margin` is stripped on every element except `<table>`:

| Goal | Wrong | Right |
|---|---|---|
| Space above a section heading | `<h2 style="margin-top: 64px;">` | `<h2 style="padding-top: 64px;">` |
| Space below a paragraph or list | `<p style="margin-bottom: 16px;">` | `<p style="padding-bottom: 16px;">` (or trust theme) |
| Indent a list | `<ul style="margin-left: 20px;">` | `<ul style="padding-left: 20px;">` |
| Space between table and next heading | `<div style="margin-bottom: 32px;">` wrapper | `<div style="padding-bottom: 32px;">` wrapper, OR `padding-top` on the next heading |
| Space between two `<table>` elements | Either `margin` works on tables, or `padding` on a wrapper | Both are fine |

**Don't double-space headings.** Most themes provide natural spacing between a heading and the immediately-following element. Adding `padding-bottom` to a heading stacks on top of that and creates visibly excessive space. Reach for `padding-bottom` on a heading only when the theme's natural gap is genuinely insufficient (rare).

### Footnote pattern

Inline marker (use `<sup>` for visual lift):

```html
<td>Some capability<sup style="font-size: 10px;">¹</sup></td>
```

Or on a value cell where the marker qualifies the icon:

```html
<td>✏️<sup style="font-size: 10px;">²</sup></td>
```

Definitions at the foot of the article:

```html
<h2>Footnotes</h2>
<p style="font-size: 12px; color: #999;"><strong>¹</strong> Definition of footnote 1.</p>
<p style="font-size: 12px; color: #999;"><strong>²</strong> Definition of footnote 2.</p>
```

`color: #999` is a neutral mid-grey that reads acceptably against both light and dark page surfaces. Don't use `#718096`, `#2c3e50`, or `#1a202c` for footnotes — they all break dark mode.

If the source has marker ¹ but no marker ², that doesn't mean ² is unused — search the full source. In tabular sources, footnote markers often appear inside cells alongside other content (e.g. `✏️ list only¹`, `✏️ run from form²`).

### Image insertion workflow

When an article needs inline images, the cleanest path is to **let Zendesk's WYSIWYG handle the upload and URL wiring**, then fix the cosmetics in source mode. Don't pre-build `<img>` placeholders with fake URLs expecting to transplant real URLs in later — that two-stage flow has more moving parts than it's worth.

**Recommended flow:**

1. Paste the prose-only HTML (no image tags) into the source editor.
2. Switch to WYSIWYG. Position the cursor at each insertion point and use **Insert Image** — Zendesk uploads the file and inserts a `<figure><img ...></figure>` with the correct URL.
3. Switch back to source mode and fix two things per image:
   - **Alt text** — Zendesk's auto-insert uses the filename or empty alt; replace with a meaningful description.
   - **Sizing styles** — re-add `style="max-width: 100%; display: block;"` on the `<img>` if the layout needs it (this is the only styling worth fighting for; everything else Zendesk inserts is acceptable).

This takes ~10 seconds per image in source mode and avoids the brittleness of URL transplanting.

### Dark mode compatibility

If your help centre theme supports dark mode — triggered either by an explicit user toggle (often persisted to `localStorage`) or by `@media (prefers-color-scheme: dark)` — articles must render correctly in both modes.

**The single rule that matters:** never set inline `color` on prose elements. Themes typically paint `.article-body` body text, headings, links, code, and blockquote with `!important` overrides that swap palette between light and dark mode. Inline `color` either loses to those overrides (and is invisible drift in the source) or — worse — survives and produces an unreadable combination in the other mode.

What "prose elements" means here: `<p>`, `<li>`, `<span>`, `<strong>`, `<em>`, `<td>`, `<th>`, `<h2>`, `<h3>`, `<h4>`, `<blockquote>`, `<code>`, `<pre>`, `<figcaption>`. Anything containing reader-facing text.

**What does survive both modes:** inline `background-color`, `border`, `padding`, `font-size` (on non-heading elements), `text-align`, `text-transform`, `letter-spacing`. None of these are swapped by themes.

**The trap that breaks callouts — and row-header cells, accent rows, panels, anything with a coloured bg:** an inline `background-color: #fffaf0` (or `#f8fafc`, `#fafafa`, `white`, any hardcoded light hex) survives unchanged into dark mode. The theme's `!important` then paints the inner text near-white. Result: near-white text on light background = invisible. **This failure is element-agnostic** — it hits `<div>` callouts, `<td>` row-headers in the first column of a table, `<th>` header cells, accent `<tr>` rows, `<section>` banners, all identically. The fix is structural and the same for every shape: switch to a translucent `rgba()` background so the element tints the page surface in whichever mode is active, and remove every inline `color` so the theme paints the text. For callouts use the patterns in [references/callout-patterns.md](callout-patterns.md); for table headers, row-header cells, and subtle accents use `rgba(0, 0, 0, 0.04)`.

**Muted text (footnotes, captions) is the one exception** where you do set an inline colour, because most themes don't apply muted text styling automatically to body paragraphs. Use `color: #999` — a neutral mid-grey that reads acceptably in both light and dark modes. Don't use any other hex for muted body text.

Full theme-behaviour reference and the principles that motivate these rules are in [references/theme-notes.md](theme-notes.md).

### Inline styles vs CSS classes

Zendesk officially recommends CSS classes defined in the help centre theme. For ad-hoc articles authored without theme coordination, inline styles are more reliable: they survive theme changes, don't require coordination, and don't depend on classes the author can't define.

**Use inline styles when**:

- Authoring a one-off article
- The author doesn't control the help centre theme
- Layout requirements are specific to this article

**Use classes when**:

- The pattern repeats across many articles
- The help centre theme is owned by the same team
- An admin has already defined the classes

Many Zendesk help centre themes define no article-body utility classes (no `.callout`, `.note`, `.alert`, `.warning`, etc.). If yours does, prefer them. If not, inline styles are mandatory for callouts and tables — if a pattern recurs often, extend the theme first rather than continuing to inline-style every instance.

This skill defaults to inline styles unless the user says otherwise.

---
