# How-to guide template

**Diátaxis quadrant:** How-to guide (task-oriented).

**When to use:** the reader knows what they want to do and just needs the recipe for one specific task. How-to guides assume the reader is already oriented — they know what the product is, what a staff member is, why they'd add one. They are not tutorials; they don't teach a concept or take the reader on a journey. They are not reference articles either; they don't list every field or option.

**What earns a how-to:** a how-to earns its shape when the reader knows what they want to do, knows roughly the shape of it, and needs the recipe for **one specific task with one outcome, in one sitting**. If they don't yet know the shape, it's a [tutorial](tutorial.md). If the article is mostly diagnostic checks ("is X happening?", "have you tried Y?") rather than imperative action steps, it's a [troubleshooting article](troubleshooting.md) — still tagged `how-to`, but written to a different structure. If the article would need to compare values or list every field, it's a [reference](reference.md).

**Voice and tone:** terse, imperative, action-first. "Click X." "Open Y." "Enter Z." Second person is implied by the imperative, so explicit "you" can be dropped from steps. Keep prose between steps to a minimum — only what's needed to disambiguate.

**Structural elements:**

- **Opening:** don't write a meta-opener like "This article shows you how to...". The Zendesk-rendered title already names the task. The body should start with the first precondition or, if there are none, the first step. The Diátaxis framework prefers conditional imperatives ("If you want X, do Y") to narrative scaffolding around the task.
- **Before you start** (optional): the small number of preconditions, with sideways links to the reference or explanation articles that fill in the gaps.
- **Steps:** numbered, imperative, one action per step. Steps are short.
- **Result:** one sentence describing what the reader sees when it worked, so they can confirm the task succeeded.
- **Troubleshooting** (optional): three or four common failures, each with a one-sentence cause and a one-sentence fix. If the diagnostic content grows beyond a handful of checks, or the same symptom is common across many how-tos, extract it into a standalone [troubleshooting article](troubleshooting.md) instead and link to it from here.
- **See also** (optional): sideways links to related how-to guides, the relevant reference, and any explanation article that gives the wider context.

**What to avoid:**

- Tutorial-style scene-setting. The reader is here to do the task, not to learn.
- Comprehensive option lists. If a field has six possible values and only one matters for this task, mention only that one and link to the reference.
- "Why" paragraphs. Link out to the explanation article instead.
- Branches mid-steps. If two paths are genuinely different tasks, write two articles. If they share most of the work, branch only at the step that diverges.

---

## Worked example — *How to add a staff member*

> ### Before you start
>
> - You need the **Administrator** role on the workspace. If you don't, ask an existing admin to add the staff member or to grant you the role.
> - Have the staff member's full name, work email address, and the role you intend to assign. The available roles are listed in the [permission roles reference](#).
>
> ### Steps
>
> 1. Open **Settings** from the main navigation.
> 2. Click **Staff** in the settings sidebar.
> 3. Click **Add staff member** in the top-right corner.
> 4. Enter the staff member's full name and work email address.
> 5. Choose a role from the **Role** dropdown.
> 6. Click **Send invite**.
>
> ### Result
>
> The new staff member appears in the staff list with the status **Invited**. They receive an invitation email and become active once they sign in for the first time.
>
> ### Troubleshooting
>
> - **The invite email didn't arrive.** The address may be wrong, or the email may be in a junk folder. Click the staff member's row in the list and choose **Resend invite**.
> - **The *Add staff member* button isn't visible.** Your role doesn't have permission to manage staff. Ask an administrator to add the staff member.
> - **The role you want isn't in the dropdown.** Some roles are restricted to higher-tier accounts and aren't available at workspace level. Check the [permission roles reference](#) for which roles can be assigned where.
>
> ### See also
>
> - [How to change a staff member's role](#)
> - [How to remove a staff member](#)
> - [Permission roles](#) — the full list of roles and what each one can do.
