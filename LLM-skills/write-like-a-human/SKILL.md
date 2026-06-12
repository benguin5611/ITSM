---
name: write-like-a-human
description: >
  Detect and remove signs of AI-generated writing from any text. Use this skill whenever someone asks to
  "clean up AI writing", "make this sound less AI", "remove AI tells", "humanise this", "de-AI this",
  "check for AI writing signs", "does this sound like AI", "make this sound more natural", "rewrite to
  sound human", or any variation. Also trigger when reviewing or editing text that the user suspects was
  AI-generated, when preparing content for publication and wanting to avoid AI detection, or when the user
  pastes text and asks for a style/tone review. If someone says "edit this" or "improve this" and the text
  is clearly AI-generated, suggest using this skill. Covers blog posts, articles, reports, emails,
  documentation, Wikipedia content, marketing copy, academic writing, and any other prose.
---

# Write Like a Human

Detect signs of AI-generated writing in text, flag them, and rewrite to sound natural and human.

## Hard rules (apply to every output)

1. **Zero em-dashes.** Never use `—` (em-dash) or `–` (en-dash) in rewritten output, anywhere, for any reason. Even correct usage now reads as AI. Replace every em-dash with a comma, semicolon, full stop, parentheses, or rephrase. This rule has no exceptions. Scan the final draft for `—` and `–` characters before returning.
2. **Zero negation pivots.** No "not X, but Y", no "It wasn't X. It was Y.", no "X isn't a Y problem; it's a Z problem". State the positive claim directly. See *Negation pivot* below.
3. **Style reference.** Apply the rules in `references/style-reference.md` to every rewrite — Title Case headings, inconsistent spelling conventions, and trailing punctuation on short bullets are AI tells *and* style violations. Read the reference before rewriting; key rules: sentence-case headings, one consistent spelling locale (US/UK/AU), no full stops in acronyms, no trailing punctuation on short bullets, role titles and common nouns lowercase in body text.

These patterns account for most of the AI-feel that survives normal editing. Treat them as bans, not preferences.

## Before you start

Read the full reference catalogue for the detailed pattern descriptions and examples:

```
references/ai-writing-signs.md
```

You don't need to read it every time. The quick-reference below covers the most common patterns. Consult the reference file when you encounter ambiguous cases or want to cite specific examples.

## Workflow

1. **Read the text carefully.** Don't skim. AI tells are cumulative; one or two signs mean nothing, but clusters are diagnostic.
2. **Flag issues.** Identify every instance of an AI writing pattern, categorised by type.
3. **Rewrite the text.** Produce a clean version that preserves the original meaning and structure but removes AI tells. No em-dashes anywhere.
4. **Summarise changes.** After the rewritten text, provide a concise summary of what was changed and why.

## Output format

```
[Rewritten text. Clean, ready to use, no em-dashes.]

***

**What I changed:**
- [Category]: [Brief description of what was flagged and how it was fixed]
- ...

**Confidence:** [How confident you are that the original contained AI writing, on a rough Low/Medium/High scale, with brief reasoning]
```

If the user only asks for a review (not a rewrite), skip the rewritten text and just provide the flagged issues with quotes and explanations.

***

## Quick-reference: AI writing patterns

### Tier 1: strong tells (high diagnostic value, often standalone)

**Em-dashes (any usage)**
The single strongest surface signal of AI prose in 2025. Even one em-dash in short text is suspicious; two or more is diagnostic on its own. This includes both `—` and `–`. The presence of a correctly used em-dash is no defence; readers pattern-match the character itself.

**AI vocabulary overuse**
Words that spiked in frequency post-2022 when used densely together:
- 2023 to mid-2024 (GPT-4 era): delve, tapestry, intricate/intricacies, meticulous/meticulously, testament, interplay, pivotal, crucial, vibrant, enduring, bolstered, garner, underscore, landscape (abstract), Additionally (sentence-opener), boasts (meaning "has"), valuable, key (adj)
- Mid-2024 to mid-2025 (GPT-4o era): align with, fostering, enhance, showcasing, highlighting, emphasizing, vibrant, crucial, pivotal, bolstered, enduring, underscore
- Mid-2025 onwards (GPT-5 era): emphasizing, enhance, highlighting, showcasing, plus attribution and notability language

One or two of these words is coincidence. A paragraph with five or more is a strong signal.

**Undue legacy/significance language**
Puffing up importance with stock phrases: "stands as a testament to", "marking a pivotal moment", "underscores its significance", "reflects broader trends", "setting the stage for", "indelible mark", "deeply rooted", "key turning point", "evolving landscape", "focal point", "enduring legacy".

**Superficial analysis via participle phrases**
Sentences ending with "-ing" phrases that add vague significance: "highlighting its importance", "underscoring the need for", "reflecting broader trends", "contributing to the ongoing discourse", "fostering a sense of community".

**Promotional/puffery tone**
Travel-guide or press-release register applied to neutral subjects: "boasts a vibrant", "nestled in the heart of", "rich cultural heritage", "diverse array", "commitment to excellence", "groundbreaking", "renowned", "showcasing".

**Negation pivot (a.k.a. "not X, but Y" / antithesis / false-contrast)**
A reflexive AI rhetorical move. Dismiss an obvious target, then pivot to the "real" answer with a punchy short clause. Mimics the cadence of hard-won insight without doing the work.

Forms to flag on sight:
- Single-sentence: "It's not X, it's Y." or "Not just X, Y." or "X isn't a Y problem; it's a Z problem."
- Two-sentence punchy variant: "The people doing the work weren't the problem. The job was." or "It wasn't a tooling issue. It was a trust issue."
- Em-dash pivot: "X, Y" with an em-dash where Y undercuts or refines X. (Doubly banned: it combines two Tier 1 patterns.)
- Cross-paragraph version: a paragraph closes with the "real" answer set off as a one-line sentence.

These are Tier 1 even in isolation. A single instance in short prose is suspicious; two is diagnostic. Strip them unless the contrast is doing genuine work the reader couldn't infer, which is rare. When the contrast is real, state the point directly without the rhetorical setup.

**Copula avoidance**
Substituting "is/are/has" with fancier constructions: "serves as" instead of "is", "features" instead of "has", "stands as" instead of "is", "holds the distinction of being" instead of "is".

### Tier 2: moderate tells (useful in combination)

**Other negative parallelisms**
"No X, no Y, just Z" and similar formulaic constructions. (The dominant "not X, but Y" form is Tier 1; see *Negation pivot*.)

**Rule of three**
Overuse of triple constructions: "adjective, adjective, and adjective" or "short phrase, short phrase, and short phrase", especially when they add superficial comprehensiveness.

**Elegant variation**
Avoiding repetition of a word by cycling through synonyms unnaturally: a person's name becomes "the protagonist", then "the key figure", then "the eponymous character".

**Outline-like "challenges and future" sections**
"Despite its [positive words], [subject] faces challenges..." followed by vague optimism. Rigid formula, usually at the end of a piece.

**Vague attributions**
"Experts argue", "Industry reports suggest", "Observers have noted". Weasel wording that attributes claims to unnamed authorities.

### Tier 3: weak tells (context-dependent, corroborative only)

**Title case in headings.** Capitalising all main words in section headings.

**Overuse of boldface.** Mechanical bolding of "key" terms throughout.

**Vertical lists with inline bold headers.** `**Term**: description` formatted as bullet lists.

**Emoji in professional/academic text.** Decorative emoji before headings or bullet points.

**Tables for trivial data.** Small tables that would work better as prose.

**Curly quotation marks.** "curly" instead of "straight" quotes. Most associated with ChatGPT/DeepSeek output, but other models produce them in some contexts — and so do Word, Google Docs, and macOS autocorrect on human-typed text. Never diagnostic alone; treat as corroborative only when clustered with stronger tells.

### Not AI tells (avoid false positives)

- Perfect grammar alone
- Formal or academic tone alone
- Transition words in isolation
- "Bland" or "robotic" prose
- Unsourced content
- Correct formatting

***

## Rewriting guidelines

When rewriting to remove AI tells:

1. **Preserve meaning.** Don't change what the text says, just how it says it.
2. **Use plain language.** Prefer "is" over "serves as", "has" over "features", "important" over "pivotal".
3. **Cut empty significance claims.** If a sentence only says something is important/significant/notable without adding information, remove it entirely.
4. **Flatten superficial analyses.** Remove participle phrases that add vague commentary. Let facts speak for themselves.
5. **Break the rule of three.** Where triples are used for padding, keep only the most specific or relevant item, or restructure.
6. **Vary sentence structure naturally.** AI text often falls into repetitive patterns. Mix short and long sentences. Start some with the subject, not always with a transition.
7. **Prefer specific over generic.** Replace "rich cultural heritage" with the actual cultural detail. If none exists, cut the phrase.
8. **Use "is" and "are" freely.** Don't avoid copulas. "The building is a hospital" beats "The building serves as a healthcare facility".
9. **Eliminate every em-dash.** Hard rule. Replace `—` and `–` with comma, semicolon, full stop, parentheses, or rephrase the sentence. Never use them in output, even when grammatically correct. If the text would lose meaning without one, restructure.
10. **Don't overcorrect.** Some AI-flagged words are perfectly fine in context. "Crucial" in a sentence about life-or-death medical decisions is fine. "Crucial" describing a town's local park is not.
11. **Kill negation pivots aggressively.** Before producing the rewrite, scan it for "not X, but Y", "It wasn't X. It was Y.", "X isn't a Y problem; it's a Z problem", and any pivot construction. Default action: delete the negated half and state the positive claim directly. Only keep the contrast if a reader would genuinely assume X without the correction. Re-scan the final draft once more for this pattern; it is the most common reason this skill's output still reads as AI.

## Self-check before returning output

Run this checklist on the rewritten text before returning it. **Search the literal characters `—` and `–` in your output.** If either appears even once, you have failed this check.

- [ ] Zero `—` (em-dash) characters anywhere in the output
- [ ] Zero `–` (en-dash) characters anywhere in the output
- [ ] Zero "not X, but Y" / "It wasn't X. It was Y." constructions (unless contrast is load-bearing)
- [ ] No closing one-liner sentence that "lands" a contrast set up earlier
- [ ] Copulas ("is", "are", "has") used freely; no "serves as" / "stands as"
- [ ] No participle-phrase tails ("...highlighting X", "...underscoring Y")
- [ ] No Tier 1 vocabulary clusters
- [ ] Style reference applied (`references/style-reference.md`): sentence-case headings, consistent spelling locale, no full stops in acronyms, no trailing punctuation on short bullets, common nouns and job titles lowercase

If any box fails, rewrite that passage before returning.

## Edge cases

- **Mixed human/AI text.** Flag only the AI-sounding passages. Don't rewrite sections that already sound natural. The em-dash and negation-pivot bans still apply to anything you produce.
- **Technical writing.** Some AI vocabulary ("key", "enhance", "critical") is normal in technical contexts. Weight other signals more heavily.
- **Non-English text.** These patterns are calibrated for English. Be cautious with translated text.
- **Pre-2023 text.** If you know the text predates November 2022, AI writing can be safely ruled out. The patterns may still exist (AI was trained on human writing that uses them) but they aren't diagnostic.
- **User explicitly requests em-dashes.** Comply, but warn them once that em-dashes are now the strongest single AI signal in modern prose.
