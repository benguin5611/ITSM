# AI Writing Signs — Full Reference Catalogue

Source: adapted for general use from Wikipedia's ["Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup).

Licence: as a derivative of that page, this file is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) rather than the MIT licence that covers the rest of this collection.

## Table of Contents

1. [Content patterns](#content-patterns)
2. [Language and grammar](#language-and-grammar)
3. [Style and formatting](#style-and-formatting)
4. [Structural tells](#structural-tells)
5. [Communication artefacts](#communication-artefacts)
6. [Historical patterns (older models)](#historical-patterns)
7. [False positives to avoid](#false-positives)

---

## Content patterns

### Undue emphasis on significance, legacy, and broader trends

LLMs puff up importance by connecting mundane details to "broader" themes. Stock phrases:

- stands/serves as
- is a testament/reminder
- a vital/significant/crucial/pivotal/key role/moment
- underscores/highlights its importance/significance
- reflects broader [trends/movements/shifts]
- symbolizing its ongoing/enduring/lasting [legacy/influence]
- contributing to the [development/evolution/growth of]
- setting the stage for
- marking/shaping the [future/direction of]
- represents/marks a shift
- key turning point
- evolving landscape
- focal point
- indelible mark
- deeply rooted

This happens even for mundane subjects. Population data, etymology, or minor infrastructure may get treated as historically significant.

**Biology-specific variant**: When describing species, LLMs over-emphasise ecosystem connections, conservation status, and "research and preservation efforts" — even when the species' conservation status is unknown and no serious efforts exist.

### Undue emphasis on notability and media coverage

LLMs try to prove a subject's importance by listing media outlets that covered it, often without summarising what those sources actually said. Watch for:

- "independent coverage"
- "local/regional/national/[country] media outlets"
- "profiled in [publication]"
- "active social media presence"
- "maintains a strong digital presence"

Newer models (2025+) are especially prone to this — creating entire sections that just catalogue which publications mentioned the subject.

### Superficial analyses

Vague commentary attached to facts, often via present participle phrases. The analysis adds no information and could apply to almost anything. Watch for:

- highlighting/underscoring/emphasizing ...
- ensuring ...
- reflecting/symbolizing ...
- contributing to ...
- cultivating/fostering ...
- encompassing ...
- valuable insights
- align/resonate with

**Example pattern**: "[Factual statement], highlighting its significance in [vague domain]."

These are often synthesis or unattributed opinions. Newer chatbots with web search may attribute these analyses to named sources regardless of whether those sources actually say anything similar.

### Promotional and advertisement-like language

Even when prompted for neutral tone, LLMs drift toward travel-guide or press-release register:

- boasts a [vibrant/rich/diverse]
- vibrant [community/culture/scene]
- rich [history/heritage/tradition]
- profound [impact/influence]
- enhancing/showcasing/exemplifies
- commitment to [excellence/innovation/sustainability]
- natural beauty
- nestled [in/among]
- in the heart of
- groundbreaking
- renowned
- featuring a diverse array

**Cultural heritage variant**: Anything that could be loosely considered cultural heritage gets constant reminders of its importance.

**People/company variant**: Biographical or corporate text adopts PR tone — emphasising "vision", "commitment", and "goals".

### Vague attributions and overgeneralisation

Weasel wording that attributes claims to unnamed authorities:

- "Industry reports suggest..."
- "Observers have cited..."
- "Experts argue..."
- "Some critics argue..."
- "several sources/publications" (when only one or two are cited)
- "such as" before what appears to be an exhaustive list

LLMs also exaggerate how widely held a view is — presenting one source's opinion as a consensus.

### Outline-like "challenges and future" sections

Formula: "Despite its [positive words], [subject] faces challenges, including [list]..." followed by either:
- Vague optimism: "With ongoing initiatives, [subject] continues to thrive..."
- Speculation: "Future investments in [technology] could enhance..."

Usually appears as the final section. The issue is the rigid formula, not the mention of challenges per se.

### Leads treating article titles as proper nouns

For topics that aren't proper names, AI may introduce the title as if it were a standalone entity: "The 'List of songs about Mexico' is a curated compilation of musical works..."

---

## Language and grammar

### AI vocabulary — detailed breakdown

Words that spiked in frequency post-2022 when co-occurring in text:

**2023–mid 2024 (GPT-4 era):**
Additionally (sentence-opener), boasts (meaning "has"), bolstered, crucial, delve, emphasizing, enduring, garner, intricate/intricacies, interplay, key (as adj), landscape (abstract noun), meticulous/meticulously, pivotal, underscore (as verb), tapestry (abstract noun), testament, valuable, vibrant

**Mid 2024–mid 2025 (GPT-4o era):**
align with, bolstered, crucial, emphasizing, enhance, enduring, fostering, highlighting, pivotal, showcasing, underscore, vibrant

**Mid 2025+ (GPT-5 era):**
emphasizing, enhance, highlighting, showcasing (plus attribution/notability language from the section above)

**Key insight**: These words co-occur. Where there is one, there are likely others. A single "crucial" is nothing; a paragraph with "crucial", "pivotal", "underscoring", and "tapestry" is diagnostic.

Context matters: "underscore" can mean a literal underline character. "Landscape" can refer to actual terrain. "Key" in "key to the lock" is fine.

### Copula avoidance

LLMs substitute "is/are/has" with fancier constructions:

| AI version | Natural version |
|---|---|
| serves as | is |
| stands as | is |
| marks/represents [a] | is |
| boasts/features/offers [a] | has |
| holds the distinction of being | is |
| ventured into politics as a candidate | was a candidate |

A study documented a >10% decrease in "is" and "are" usage in academic writing in 2023. This is particularly visible in AI copyedits — the LLM "improves" text by replacing simple copulas.

### Negation pivot (Tier 1 — strong tell on its own)

Also called *antithesis*, *negation-affirmation*, or *contrastive parallelism*. Rhetorically: dismiss an obvious or sympathetic target, then pivot to the "real" answer with a punchy short clause. It feels insightful because it mimics the cadence of a hard-won realisation — but LLMs reach for it reflexively as a way to manufacture depth, often where no real contrast exists.

This is the single most common rhetorical tic in modern AI prose. A single instance in short text is already suspicious; two is diagnostic.

Forms:

**"Not just X, but also Y"**: "It is not just a work of self-representation, but a visual document of her obsessions."

**"Not X, but Y"**: "not a mirror but a portal: not a representation of self, but a mechanism for its constant reinvention."

**Two-sentence punchy variant**: "The people doing the work weren't the problem. The job was." / "It wasn't a tooling issue. It was a trust issue." The second sentence is short, declarative, and "lands" the contrast.

**Em-dash pivot**: "X — Y" where Y undercuts or refines X. Frequently combined with the patterns above.

**X isn't a Y problem. It's a Z problem.** Variant that reframes the category rather than the specific.

**Cross-paragraph version**: a paragraph closes with the "real" answer set off as a one-line sentence on its own.

**Cross-sentence drift**: "He hailed from the esteemed Duse family. His life, however, took a path that intertwined both personal ambition and familial complexities." — the "however" pivot is a softer relative.

**How to fix.** Default: delete the negated half and state the positive claim directly. The negation rarely adds information; it adds rhythm. If the contrast is genuinely load-bearing (a reader really would assume X), keep it but flatten the cadence — drop the punchy one-liner form, fold it into a longer sentence, and avoid the em-dash setup.

### Rule of three

Overuse of triple constructions for superficial comprehensiveness:
- "adjective, adjective, and adjective"
- "short phrase, short phrase, and short phrase"
- Three bullet points where one or two would suffice

### Elegant variation

Repetition-penalty code causes LLMs to cycle through synonyms unnaturally. A person's name might become "the protagonist", "the key player", "the eponymous character" in successive references.

This tell doesn't apply if content was generated in separate sessions, since each piece may have been generated independently.

---

## Style and formatting

### Title case in headings
AI capitalises all main words: "Global Context: Critical Mineral Demand" instead of "Global context: critical mineral demand".

### Overuse of boldface
Mechanical emphasis of "key" terms throughout, often in a "key takeaways" fashion. Every instance of a chosen word or phrase gets bolded.

### Inline-header vertical lists
Formatted as: **Bold header**: descriptive text — in ordered or unordered lists. The specific pattern of bold-colon-description is characteristic.

Variants: bullet characters (•), hyphens (-), en dashes (–), explicit numbers (1.) instead of proper list markup.

### Emoji
Decorative emoji before headings or bullet points, especially in professional or academic contexts.

### Em-dash usage (Tier 1: hard ban in output)

The em-dash (`—`) and en-dash (`–`) are now the strongest single surface signal of AI writing. Even one in short text is suspicious; two or more is diagnostic on its own. Readers and detection tools pattern-match the character itself, not the construction around it. Correct usage offers no protection.

**Rule for this skill's output: never produce an em-dash or en-dash, ever.** Replace with comma, semicolon, full stop, parentheses, or rephrase. If a sentence would lose its meaning without one, restructure the sentence.

This is partly a calibration problem: human writers do use em-dashes, and good ones use them well. But LLMs use them at roughly 5 to 10 times the rate of literary prose, and the public association is now strong enough that even appropriate usage triggers AI suspicion. With GPT-5.1 (November 2025), OpenAI improved instruction-following so that a "no em-dashes" custom instruction is finally respected, though default output can still overuse them; that the fix was worth announcing at all confirms the signal is now widely recognised.

When auditing existing text, treat any em-dash as a strong tell unless the surrounding prose is clearly literary or pre-2023.

### Unnecessary tables
Small tables for data that would work better as prose.

### Curly quotation marks
"Curly" instead of "straight" quotes — specific to ChatGPT and DeepSeek. Claude and Gemini typically use straight quotes. Also produced by macOS/iOS, Microsoft Word smart quotes, and professional typesetting, so not diagnostic on its own.

---

## Structural tells

### Markdown artefacts in non-Markdown contexts
Asterisks for bold/italic (**bold**, *italic*), hash symbols for headings (##), parenthetical links [text](url), fenced code blocks (```), and triple-symbol thematic breaks (---, ***, ___).

### Skipped heading levels
Starting at heading level 3 (=== in wikitext, ### in Markdown) instead of level 2.

### Thematic breaks before headings
Horizontal rules (---- or ---) inserted before every section heading.

### Knowledge-cutoff disclaimers
"As of my last knowledge update...", "While specific details are limited...", "based on available information...", "not widely documented...". Also: speculation about what unknown information "likely" contains.

### Placeholder text and templates
Fill-in-the-blank text: [Your Name], [Describe the specific section], INSERT_SOURCE_URL, 2025-XX-XX.

### Phrasal templates
Mad Libs-style text with blanks the user was meant to fill in but didn't.

---

## Communication artefacts

These appear when someone pastes AI chat output directly:

- "I hope this helps" / "Would you like..." / "Let me know if..."
- "Certainly!" / "Of course!" / "You're absolutely right!"
- "Here is a [detailed/comprehensive] [breakdown/overview/analysis]..."
- Subject lines ("Subject: Request for...")
- Offers to receive feedback ("I am happy to address any concerns...")
- Canned emphasis on good faith and policy adherence
- Collaborative language ("Let's work together to ensure...")

---

## Historical patterns

These were common in older models but are less frequent now. Still useful for detecting older unreviewed AI content.

### Didactic disclaimers (2022–2024)
"It's important to note/remember/consider..." — safety or disambiguation advice to an imagined reader.

### Section summaries (2022–2024)
"In summary..." / "In conclusion..." / "Overall..." — restating the section's point at the end.

### Prompt refusal artefacts
"As an AI language model, I cannot..." — increasingly rare in newer models.

### Abrupt cutoffs
Text that stops mid-sentence or mid-paragraph, from hitting token limits.

### Outdated access dates in citations
Citations with access dates significantly older than the edit date (e.g., article created December 2025 with access dates from December 2024).

---

## False positives to avoid

These do NOT reliably indicate AI writing:

1. **Perfect grammar** — many humans write grammatically.
2. **Formal or academic tone** — not inherently AI-like.
3. **"Bland" or "robotic" prose** — AI actually skews verbose and positive, not robotic.
4. **"Fancy" vocabulary** — only specific overused words are diagnostic, not formality in general.
5. **Transition words in isolation** — "Additionally" alone isn't a tell; "Additionally" + "Furthermore" + "Moreover" in consecutive paragraphs is.
6. **Letter-like formatting** — salutations and valedictions predate AI.
7. **Unsourced content** — most unsourced content predates LLMs.
8. **Mixed registers** — casual + formal in the same text can indicate a technical person writing casually, youth, neurodivergence, or multiple authors.
9. **Correct formatting** — knowing how to format correctly is a human skill too.
10. **Pre-November 2022 text** — ChatGPT launched November 30, 2022, but GPT-3-era tools were publishing text from 2020. Text verifiably from before November 2022 is very unlikely to be chatbot-generated; these patterns are calibrated to post-ChatGPT models.
