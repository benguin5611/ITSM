# Security Policy

## Supported Versions

This is a personal toolkit maintained in my spare time. There are no formal releases or version branches — the latest commit on `main` is the only version that receives security fixes. If you're using an older snapshot, pull the latest before reporting.

| Version       | Supported          |
| ------------- | ------------------ |
| `main` (HEAD) | :white_check_mark: |
| Anything else | :x:                |

## Reporting a Vulnerability

If you've found a security issue, please **do not open a public issue**. Report it privately through one of these channels:

- **Preferred:** GitHub's private vulnerability reporting — use the *Report a vulnerability* button under the **Security** tab of this repo.
- **Backup:** email me directly @ security@infosek.com.au.

Include enough detail for me to reproduce it: affected file or script, steps, expected vs. actual behaviour, and the impact you think it has. A proof-of-concept is great but not required.

### What to expect

This is a side project run by one person, so timelines are best-effort rather than contractual:

- **Acknowledgement:** within about 5 business days.
- **Initial triage:** within about 14 days — I'll let you know whether I'm treating it as a vulnerability, a regular bug, or something I won't fix, and why.
- **Fix or decision:** depends on severity and complexity. Critical issues get prioritised; low-severity issues may sit for a while or end up as documented limitations.
- **Disclosure:** once a fix is merged (or I've decided not to fix), I'm happy to credit you in the commit message if you'd like. Please don't publicly disclose before then.

### Scope

In scope:

- Code and configuration in this repository.
- Documentation that, if followed, would cause a user to do something insecure.

Out of scope:

- Vulnerabilities in third-party tools, APIs, or services that the scripts here call. Report those to the relevant vendor.
- Issues that require already having privileged access to a user's machine, account, or infrastructure (the threat model assumes the operator is trusted).
- Social engineering, physical attacks, or anything against my personal accounts or infrastructure rather than the code itself.

### No bounty

I can't pay for reports — this is unpaid work on unpaid tools. Credit and thanks are what's on offer. Thank you for taking the time anyway.
