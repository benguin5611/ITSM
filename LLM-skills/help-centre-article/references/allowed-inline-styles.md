# Zendesk Allowed Inline Styles

This is the full list of inline CSS properties Zendesk accepts on HTML elements in help center articles. **Anything not on this list is stripped from the HTTP response** with no editor warning.

Source: https://support.zendesk.com/hc/en-us/articles/6644509092378-Supported-HTML-for-help-center-articles

## The single biggest gotcha

**`margin` and all `margin-*` properties are only allowed on `<table>` elements.** On every other element (`<div>`, `<h1>`–`<h6>`, `<p>`, `<ul>`, `<ol>`, `<section>`, etc.) they are silently stripped, and the element falls back to whatever spacing the help centre theme provides.

To add space around non-table elements, use `padding-top` or `padding-bottom` instead — `padding` is globally allowed on every element. To indent a list, use `padding-left: 20px` on the `<ul>`/`<ol>`, not `margin-left`.

## Globally allowed on every element

```
aspect-ratio
background
background-color
background-image
border
border-bottom
border-bottom-color
border-bottom-style
border-bottom-width
border-collapse
border-color
border-left
border-left-color
border-left-style
border-left-width
border-radius
border-right
border-right-color
border-right-style
border-right-width
border-spacing
border-style
border-top
border-top-color
border-top-style
border-top-width
border-width
box-sizing
color
display
font
font-family
font-size
font-style
font-variant
font-variant-caps
font-variant-ligatures
font-weight
height
letter-spacing
line-height
max-height
max-width
min-height
min-width
orphans
outline
padding
padding-bottom
padding-left
padding-right
padding-top
text-align
text-decoration
text-decoration-color
text-decoration-line
text-decoration-style
text-indent
text-transform
vertical-align
white-space
widows
width
word-spacing
```

## Element-specific allowed inline styles

These are allowed only on the specific element listed.

| Element | Additional allowed inline styles |
|---|---|
| `figure` | `float` |
| `li`, `ol`, `ul` | `list-style`, `list-style-image`, `list-style-position`, `list-style-type` |
| `table` | `margin`, `margin-bottom`, `margin-left`, `margin-right`, `margin-top` |

## Notably **not** allowed (don't use these inline)

These are common in modern CSS but **are stripped** from inline styles:

- `margin`, `margin-top`, `margin-bottom`, `margin-left`, `margin-right` (on any element except `<table>`)
- `cursor`
- `transition`, `transition-*`
- `transform`, `transform-*`
- `animation`, `animation-*`, `@keyframes`
- `filter`, `backdrop-filter`
- `box-shadow`
- `pointer-events`
- `position`, `top`, `left`, `right`, `bottom`
- `z-index`
- `opacity`
- `gap`, `row-gap`, `column-gap`
- `flex`, `flex-direction`, `flex-wrap`, `flex-grow`, `flex-shrink`, `flex-basis`
- `justify-content`, `justify-items`, `justify-self`
- `align-items`, `align-content`, `align-self`
- `grid`, `grid-*`
- `order`
- `place-items`, `place-content`, `place-self`
- `inset`, `inset-*`
- `overflow-wrap`, `word-break`
- `clip-path`, `mask`
- `mix-blend-mode`, `isolation`
- Any custom property (`--my-var`)
- Any pseudo-class or pseudo-element (`:hover`, `:focus`, `::before`, `::after`)
- Any `@media`, `@supports`, `@keyframes` rule

## Notes on what *is* allowed

`overflow-x` and `overflow-y` are not explicitly listed in the global allowed properties, but `overflow-x: auto` (the property the wide-table scrolling pattern uses) appears to work in practice on `<div>` wrappers. If a future Zendesk update strips it, the table simply collapses (graceful degradation).

`display: flex` and `display: grid` are technically allowed (because `display` is in the global list), but **none of the flex/grid alignment properties are** — so these are largely useless for layout. Use tables, block layout, or `inline-block` instead.

`background-image: url(...)` is technically allowed, but the URL must point to one of the allowed `src` protocols (`blob`, `data`, `http`, `https`).

## Common substitutions

| What you'd reach for | What works in Zendesk |
|---|---|
| `margin-top` on a heading | `padding-top` on the heading |
| `margin-bottom` on a paragraph or list | `padding-bottom` on the element, or trust the theme |
| `margin-left: 20px` on `<ul>` (list indent) | `padding-left: 20px` on `<ul>` |
| `margin: 0 auto` to centre a block | Not possible without `margin` on non-tables. Use a `<table>` with `margin: 0 auto` — `margin` is allowed on tables — or accept default left alignment |
| Flex/grid layout | `<table>` |
| `gap` between flex children | `padding` on each child |
| `box-shadow` | `border` |
| `cursor: pointer` on hoverable elements | Not expressible inline. Define a class in the help centre theme |
| `:hover` styling | Not expressible inline. Define a class in the help centre theme |
