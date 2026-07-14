# Troubleshooting template

**Diátaxis quadrant:** How-to guide (task-oriented), variant for **symptom-driven diagnosis** — when the reader has hit a problem and needs to find the cause among several possibilities.

**When to use:** the reader has a symptom (sign-in failing, MFA rejected, notification missing) and the cause isn't obvious. A troubleshooting article walks them through the likely causes in order, with each check pointing at a fix or escalating to the next one. These are not how-to guides — a how-to assumes the reader knows what they're trying to do; troubleshooting assumes the reader knows what's broken.

**What earns a troubleshooting article:** a symptom earns its own page when it has **multiple plausible causes** the reader can self-diagnose by working a short checklist, *and* one of the following is true:

- The reader arrives at the symptom **without** having been mid-task (e.g. "I can't sign in" — they were never mid-task to start with).
- The symptom is common across **many tasks** (e.g. "MFA code rejected" applies to every sign-in path, not just one how-to).
- The diagnostic tree has **4+ realistic branches**.

If the symptom has one or two causes and one fix per cause, fold it into the **Troubleshooting** section of the relevant [how-to](how-to.md) instead of writing a whole article. The Diátaxis tag stays `how-to` either way — there is no separate troubleshooting quadrant. The diagnostic shape is a sub-structure of how-to, not a fifth classification.

**Voice and tone:** terse, diagnostic, conditional. The article is a *checklist of yes/no questions* with the resolution baked into each branch. Diátaxis endorses conditional imperatives — "If X, do Y; if not, move to the next check" — and that's the natural voice for troubleshooting. The reader is in a hurry and probably annoyed; respect that. Reassure them at the top that working the list in order is the right approach.

**Structural elements:**

1. **Opening** — one short paragraph naming the symptom and telling the reader the article will walk them through the common causes in order. A "before raising a ticket" framing is appropriate here — it sets expectations and tells the reader where they'll end up if nothing matches.
2. **Quick checks** (or similar heading) — an ordered list of diagnostic questions. Each check is short: the question in **bold**, then one or two sentences with the diagnosis and the fix (inline, or a link to the relevant how-to / reference / status page). Most articles need 5–10 checks; more than that suggests the article is trying to cover too many symptoms and should split.
3. **Still stuck** — escalation path when none of the checks resolved the issue. Tell the reader who to contact and what to include in the ticket (exact error message, time of failure, browser/device, screenshots). This block is the troubleshooting article's equivalent of a how-to's *Result* — it answers "what now?" when the diagnostic tree didn't terminate.

**What to avoid:**

- **Treating it like a how-to.** A how-to walks one known task end to end. A troubleshooting article walks *possible causes*; the reader bails out as soon as one matches. Don't make the reader read all eight checks if check three solves their problem — every check should let them resolve and leave.
- **Walls of prose.** Each check should be skim-able. If a check needs more than two sentences of explanation, the underlying topic probably deserves its own reference or how-to article, linked from the check.
- **Hidden or assumed causes.** If a likely cause is "you typed the URL wrong" or "you used your personal email", say so explicitly. Readers don't always notice the obvious until you name it, and putting the obvious causes first is part of why a troubleshooting article works.
- **Branches inside branches.** A check whose resolution is "see this other troubleshooting article" is fine. A check that opens a three-level decision tree inside one bullet is not — split it.
- **Embedded steps for things that are themselves how-tos.** Link out instead — "Reset your password" is a link to the relevant how-to, not seven inline steps.

---

## Worked example — *Troubleshooting sign-in problems*

> Run through these checks in order before raising a ticket. Most sign-in problems fall into one of the categories below.
>
> ### Quick checks
>
> 1. **Are you using the right URL?** The product is at the URL your administrator gave you. If your company uses single sign-on, the URL usually starts with your company's name (for example, `company.product.com`). Typing a guess won't work.
> 2. **Are you using your work email?** Use the email address you sign in to your other work email and apps with. Don't use a personal email.
> 3. **Have you been redirected to your company's login page?** If yes, that's expected. See [Why am I being redirected to my company's login page?](#) — your work password is the one you need.
> 4. **Are you clicking "Sign in with Google" when your account uses a username, password, and MFA?** "Sign in with Google" only works if your administrator has configured Google as your sign-in method. If they haven't, use the email and password fields on the product's sign-in page instead, then enter your MFA code when prompted.
> 5. **Is your password right?** If you don't use single sign-on, try resetting your password — see [Resetting your password](#).
> 6. **Is your MFA code being rejected?** Check that your phone's clock is set to update automatically. TOTP codes are time-sensitive; if your clock has drifted, typically by more than a minute (exact tolerance varies by provider), codes will be rejected.
> 7. **Have you been deactivated?** If you've changed roles or recently left an organisation, your administrator may have removed your access. Confirm with them.
> 8. **Is the product itself up?** Check the product's status page if it has one. If there's a known issue, you'll see it there.
>
> ### Still stuck
>
> If you've worked through everything above and still can't sign in, contact your administrator. Include:
>
> - The exact error message you saw (a screenshot helps)
> - The time the error occurred, in your local time zone
> - The browser and device you were using
