# Callout patterns (dark-mode-safe)

Most modern Zendesk help centre themes support dark mode. The naive callout pattern (hardcoded light background, no inline `color`) renders fine in light mode and unreadable in dark mode: the theme paints body text near-white inside `.article-body`, but the inline `background-color` survives, so you end up with near-white text on a cream background.

You can't reach for `@media (prefers-color-scheme: dark)` or CSS classes — inline styles can't express either, and many Zendesk themes define no `.callout` / `.note` / `.alert` utilities for article body content. So callouts must be inline, but the inline pattern has to survive both modes.

## The rule

**Every callout uses a translucent `rgba()` background and sets no inline `color` anywhere — not on the wrapper, not on inner `<p>`/`<li>`/`<strong>`. The theme paints text for you in mode-appropriate colour.**

Why this works:

- A low-alpha `rgba()` background tints the page surface beneath it. In light mode the page is almost white and the callout renders as a pale tinted card. In dark mode the page is almost black and the same rgba tint renders as a warm dark card. Either way the result is legible against theme-painted text.
- Modern Zendesk themes typically apply a rule like `.article-body p, li, span, td, th { color: var(--text-body) !important; }` where `--text-body` resolves to a near-black in light mode and a near-white in dark mode. Both pass legibility against a translucent-tinted surface of either mode.
- Inline `color` on the wrapper inherits down to children, but the theme's `!important` rule on `.article-body p/li/span` wins against the inline cascade. Setting `color` on the wrapper is therefore a no-op that gives the false impression of safety.
- Setting `color` *directly* on the inner `<p>`/`<li>` still loses to the theme `!important` — inline declarations only beat `!important` selectors when the inline value itself carries `!important`, which is fragile under Zendesk's HTML cleanup pass. Don't rely on it.

## Variants

Three semantic callouts cover almost every use case. Pick the one whose meaning matches the content; don't reach for amber warning just because the others feel too plain.

### Info (blue)

Neutral asides, context, "did you know" moments. Blue reads as factual rather than urgent.

```html
<div style="background-color: rgba(83, 146, 184, 0.16); border-left: 3px solid #5392b8; padding: 12px 16px; border-radius: 0 8px 8px 0;">
  <p>Body of the info callout. No inline color anywhere — let the theme paint text in mode-appropriate colour.</p>
</div>
```

### Warning (amber)

Use when the reader could lose data, break a workflow, or make a costly mistake. Amber signals "stop and read this".

```html
<div style="background-color: rgba(238, 171, 68, 0.18); border-left: 3px solid #eeab44; padding: 12px 16px; border-radius: 0 8px 8px 0;">
  <p>Body of the warning callout.</p>
</div>
```

### Tip (green)

Use for shortcuts, pro-tips, optional optimisations. Green reads as helpful rather than required.

```html
<div style="background-color: rgba(25, 195, 134, 0.12); border-left: 3px solid #19c386; padding: 12px 16px; border-radius: 0 8px 8px 0;">
  <p>Body of the tip callout.</p>
</div>
```

If your brand palette differs, swap the hex on the `border-left` (and the corresponding rgba background) to your equivalents. The pattern stays the same: a translucent-tinted background and a 3px solid border-left in the variant's accent colour. Aim for alpha 0.12–0.18 — low enough to remain a tint, high enough to read as a clearly differentiated surface.

## Multiple paragraphs and lists inside a callout

The wrapper's `padding: 12px 16px` provides the breathing room around the content. The first child paragraph touches the top of that padding — don't add `padding-top` to it. Subsequent paragraphs and lists space themselves with `padding-top: 8px` (or `4px` for a tight list).

```html
<div style="background-color: rgba(238, 171, 68, 0.18); border-left: 3px solid #eeab44; padding: 12px 16px; border-radius: 0 8px 8px 0;">
  <p>First paragraph — no padding-top.</p>
  <p style="padding-top: 8px;">Second paragraph — small gap above.</p>
  <ul style="padding-left: 20px; padding-top: 4px;">
    <li>List item one.</li>
    <li>List item two.</li>
  </ul>
</div>
```

## Links inside callouts

If your theme forces `.article-body a` colour with `!important` (most do), inline overrides won't help. On the info and warning callout backgrounds, your theme's link colour may read as low-contrast in light mode against the pale tinted background. Two acceptable options:

1. **Accept the contrast trade-off.** The underline (themes usually provide one) plus context makes the link discoverable even at low chroma contrast.
2. **Move the link out of the callout.** Put the actionable link in the paragraph immediately *after* the callout instead of inside it. Often reads better anyway — the callout warns, the next paragraph offers the action.

There is no inline-style fix for link colour against callout backgrounds — the theme forces link colour with `!important`, inline styles can't express pseudo-classes for hover/focus, and overriding the link colour inline would also break dark-mode legibility.

## What NOT to do

Each of these renders broken in dark mode, even though they may look fine in light mode:

```html
<!-- DON'T: hardcoded light bg + no explicit text colour. Dark-mode theme paints text near-white on cream = unreadable. -->
<div style="background-color: #fffaf0; border-left: 4px solid #b7791f; padding: 16px;">
  <p>Broken in dark mode.</p>
</div>

<!-- DON'T: inline color on the wrapper. Theme's !important on .article-body p wins over the inherited inline color. -->
<div style="background-color: #fffaf0; padding: 16px; color: #1a202c;">
  <p>Still broken in dark mode — the #1a202c never reaches the &lt;p&gt;.</p>
</div>

<!-- DON'T: inline color on the inner <p> without !important. Loses to the theme's !important rule. -->
<div style="background-color: #fffaf0; padding: 16px;">
  <p style="color: #1a202c;">Same problem. The theme override outranks the inline declaration.</p>
</div>

<!-- DON'T: !important inline. Survives Zendesk's HTML cleanup in current testing but is undocumented and fragile. -->
<div style="background-color: #fffaf0; padding: 16px;">
  <p style="color: #1a202c !important;">Works, but brittle — Zendesk has stripped !important from inline styles before.</p>
</div>
```

The fix in every case is the same: switch the background to a translucent `rgba()` value, drop every inline `color` declaration, and let the theme paint the text.
