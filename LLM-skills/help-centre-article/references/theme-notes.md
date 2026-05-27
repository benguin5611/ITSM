# Zendesk help centre theme notes

A compressed reference for what a modern Zendesk help centre theme typically does inside `.article-body`, so the skill stops fighting it. The specifics vary by theme — the principles below are what *most* current Zendesk themes implement. When in doubt, inspect your live theme's CSS (usually `style.css` in the theme assets) and confirm.

## Palette tokens

Modern themes commonly expose a set of CSS custom properties for palette swapping between light and dark mode. Typical token names (yours may differ — read your theme's CSS to confirm):

| Token (typical) | Light (typical) | Dark (typical) | Used for |
|---|---|---|---|
| `--bg` | near-white (`#f7f7f9`) | near-black (`#1a1a1c`) | Page background |
| `--surface` | white (`#fff`) | dark grey (`#232323`) | Card surfaces, search box, sidebar tiles |
| `--surface-alt` | very pale grey (`#fafafa`) | dark grey (`#1f1f21`) | Code block bg, blockquote bg |
| `--text` | near-black (`#141414`) | near-white (`#f5f5f7`) | Headings, strong text, primary copy |
| `--text-body` | mid-dark grey (`#676767`) | very light grey (`#f0f0f2`) | Body paragraph text |
| `--text-muted` | mid-grey (`#999`) | mid-light grey (`#9a9a9c`) | Footnotes, captions, helper labels |
| `--border` | very pale grey (`#ebebeb`) | dark grey (`#3d3d3d`) | Card borders, table cell borders |
| `--brand` / accent | a brand colour | same | Links, primary buttons, accent borders |

Dark-mode swap is typically driven by either `[data-theme="dark"]` on `<html>` (set from `localStorage`) or `@media (prefers-color-scheme: dark)` first-paint fallback. Many themes use both — the user toggle persists their choice, with `prefers-color-scheme` as the default before the toggle has been touched.

**Zendesk strips `var(--foo)` from inline styles.** Resolve tokens to their hex values when writing inline CSS. The translucent rgba values in [callout-patterns.md](callout-patterns.md) are derived from typical accent hexes at alpha 0.12–0.18.

## What the theme typically paints inside `.article-body`

Stop redundantly setting these inline. Most modern Zendesk themes define them in light/base CSS and force them with `!important` in dark mode.

| Element | Theme style (typical) | What the skill should NOT set inline |
|---|---|---|
| `.article-body` | base font-size (~17px), line-height (~1.7), body text colour | `font-size`, `line-height`, `color` on prose elements |
| `.article-body p` | inherits | `color`, `line-height`, `font-size` |
| `.article-body li, span, td, th, dd, dt` | inherits | `color` |
| `.article-body h2` | larger size + light weight + heading colour | `font-size`, `font-weight`, `color` |
| `.article-body h3` | medium size + light weight + heading colour | `font-size`, `font-weight`, `color` |
| `.article-body h4` | smaller size + medium weight + heading colour | `font-size`, `font-weight`, `color` |
| `.article-body a, a:visited` | brand colour (often with `!important`) | `color` — can't override link colour inline |
| `.article-body :not(pre) > code` | themed background, rounded radius, themed border, body text colour | `background`, `color`, `border`, `padding` on inline code |
| `.article-body pre` | similar code-bg pattern with larger padding | `background`, `color`, `border`, `padding` on `<pre>` |
| `.article-body blockquote` | typically a coloured border-left + soft surface-alt background | the whole block — `<blockquote>` is often already a themed callout |
| `.article-body figcaption` | small centred muted text | the whole block |
| `.article-body img` | `height: auto; max-width: 100%` (responsive) | `width`/`max-width` for fluid sizing — keep them only for fixed-size product screenshots |

**Practical consequence:** redundant inline `font-size`, `line-height`, and `color` on every `<h2>`, `<p>`, and `<ul>` is either no-op (overridden by theme `!important`) or actively breaking dark mode. Omit them. Inspect your theme to confirm exactly which properties it enforces with `!important` — but the safe default is to assume text-related properties are theme-controlled inside `.article-body`.

**Particularly useful:** if your theme styles `<blockquote>` as a soft callout already, just use `<blockquote>` for lightweight emphasis — no inline styles needed, dark-mode safe automatically.

## What the theme typically does NOT style inside `.article-body`

| Element | Theme treatment | Skill responsibility |
|---|---|---|
| `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>`, `<tr>` | Most Zendesk themes apply no default styling here. The browser's `border-style: none` default applies. | Every property must be inline. Use `#999` borders, `rgba(0, 0, 0, 0.04)` for header bg, NO `color` on body cells. See `templates/article-skeleton.html` for the canonical wide-table pattern. |
| `<hr>` | Browser default only | Set inline if you want a visible rule: `<hr style="border: none; border-top: 1px solid #999; padding-top: 16px;">` |
| `<dl>`, `<dt>`, `<dd>` | Browser default only | Set inline if used |
| Callouts / asides / panels / notes | Many themes define no utility class for these inside `.article-body` | Use the inline rgba patterns in [callout-patterns.md](callout-patterns.md) |

## Article container width

Most Zendesk themes render article content at roughly **770–810px effective width** on desktop. The exact value depends on theme variables — a typical layout uses a max container width around 1320px with the article column taking ~66% minus padding.

**Practical consequence:** the skill's "wide table threshold of 700px content width" is approximately correct for typical themes, with a small safety margin against narrower viewports / browser zoom. If your theme uses a substantially different article width, recalibrate the threshold.

## Mode-flip transition

Themes commonly set a transition on `body` and core colour properties, so toggling the theme fades between modes smoothly.

**Practical consequence:** an inline `color` on a body-text element breaks the transition for that element — it never re-animates because the inline value doesn't change. One more reason not to set inline `color` on prose.

## WYSIWYG artefacts that are safe to leave or strip

| Attribute / pattern | Source | What to do |
|---|---|---|
| `data-list-item-id="e..."` on `<li>` | Zendesk WYSIWYG editor | Harmless — not consumed by any theme CSS or JS. Strip during cleanup if doing a tidy pass; leave if not. |
| `<figure class="wysiwyg-table">` wrapping a `<table>` | Zendesk WYSIWYG | Harmless — most themes have no `.wysiwyg-table` rule, but the `figure` element renders fine. Strip the wrapper if you want cleaner source; leave if Zendesk's editor will be used to edit the article later (the wrapper helps the editor identify table blocks). |
| `id="h_01..."` on headings | Zendesk auto-generates these for in-page anchors when an article is saved through the WYSIWYG editor | Strip if you're writing fresh source; leave if you're editing an article that has them — Zendesk's auto-anchors and the article's table-of-contents widget depend on them. |
| `<zd-html-block>` wrapping a snippet | Marker that Zendesk wraps around HTML blocks pasted into the WYSIWYG editor | Strip — it's only there for the editor's benefit and doesn't render anything useful. Some Zendesk environments will re-wrap on save, which is fine. |

## Theme behaviour summary

- Dark mode is common in modern Zendesk themes, default-aware (`prefers-color-scheme`), and often persisted via `localStorage`.
- All text colours inside `.article-body` are typically forced via `!important` in dark mode. Don't fight it.
- Link colour is typically forced via `!important` in both modes. Slime/green/blue brand link colours often fail WCAG against pale callout backgrounds — either accept the trade-off or move the link out of the callout.
- No syntax highlighter is loaded by default. Code blocks render as plain text with theme-styled padding/background.
- The theme's `box-shadow` card patterns are NOT replicable inline — `box-shadow` is not in Zendesk's allowed inline-style list. Articles can't look like the surrounding theme cards.

## Confirming what *your* theme does

The notes above describe typical patterns. Your specific theme may differ. Before relying on a "the theme paints this for me" assumption, verify it:

1. Open the theme's CSS (usually `style.css` in `Customize design → Edit code` in Zendesk Guide admin).
2. Search for `.article-body` selectors and note which properties carry `!important`.
3. Check for a `[data-theme="dark"]` block or a `@media (prefers-color-scheme: dark)` block. Confirm what swaps.
4. Render a test article in both modes and check inline `color` overrides actually behave as documented above.

If your theme is substantially different (e.g. no `!important` overrides; no dark mode; explicit utility classes for callouts), adapt this reference and the rules in SKILL.md to match.
