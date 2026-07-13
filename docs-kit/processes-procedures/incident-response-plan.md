---
Artefact type: Plan
Owner role: DRP Coordinator (or equivalent — whoever activates the plan), sponsored by the most senior technical leader
Review cadence: Annual, plus a scenario-based test at least once a year
Version: 1.0 (template)
---

# Cyber security incident response plan (CSIRP)

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here) — a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

What to do at 2am, and how to write it up afterwards. Pairs with the [Post-Incident Report Template](../references/post-incident-report-template.md) for the write-up half.

## Introduction

### Context

This plan draws on established international guidance rather than inventing a framework from scratch:

- **ISO 22301** (Security and Resilience — Business Continuity Management Systems) for the contingency-planning framework.
- **NIST SP 800-34** for contingency planning recommendations, including a Business Impact Analysis process.
- **NIST IR 8286** series for prioritising risk and informing response strategy.

(Named by family, not edition — check the current version of whichever of these you're aligning to; they get revised.)

### Purpose

To provide a structured approach for managing and communicating during a security incident — ensuring stakeholders are informed accurately and promptly, mitigating potential damage, and maintaining the organisation's operations and reputation.

### Scope

Covers all security incidents involving adversarial threats to the confidentiality, integrity, or availability of information, systems, or physical locations — including but not limited to malware, data breaches, unauthorised access, and other malicious activity against the organisation's infrastructure and data. Covers detection, containment, eradication, recovery, and post-incident investigation, across all personnel, systems, and environments in scope, for internal and external threats alike. Integrates with any separate disaster-recovery plan the organisation maintains.

### Objectives

- Rapid recovery of critical systems and data.
- Minimise downtime and service interruption.
- Support a seamless transition between infrastructure or service providers if necessary.
- Maintain data integrity and security throughout recovery.
- Meet applicable regulatory obligations.

## Detection and prioritisation

### Detection

Security is everyone's job, not just IT's. An incident can surface through:

- Alerts from technical monitoring or real-time detection tooling.
- Publicly available information (new exploits, information-sharing groups, vendors, government advisories).
- Reports from staff.
- Reports from third parties, partners, or account managers.
- Industry-wide advisories from a national cyber security agency, industry body, or service provider.
- Findings from assurance reviews or forensic investigation.

Any suspected or confirmed breach must be reported immediately, with enough detail to act on (type of breach, any on-screen messages, details of unusual behaviour).

**Manual detection** typically arrives as a support ticket or a report from an interested party. However it arrives, funnel it into a single reference point — usually an incident ticket — so the response has one common thread to hang off.

**Automated detection**: alerts from your monitoring and alerting stack (a SIEM, cloud-provider security alerts, or an on-call paging tool) should route into the same incident-management process as manually reported issues, not a separate, informal channel.

### Prioritisation

Effective triage needs both an urgency assessment (how fast does this need attention) and an impact assessment (how much does this actually affect the business).

**Urgency levels**

| Level | Criteria |
| --- | --- |
| Low | Minimal impact on confidentiality, integrity, or availability. Addressable during routine maintenance. |
| Medium | Compromises integrity/availability or weakens controls, but workarounds exist and no immediate threat to overall security. |
| High | Severely impacts confidentiality, integrity, or availability and disrupts key operations. Needs an immediate response. |

**Impact levels**

| Level | Criteria | Illustrative examples |
| --- | --- | --- |
| Low | Minimal operational impact; affects a small subset of assets. | Minor endpoint misconfiguration with no exposure; low-privilege role misassigned without security effect; a handful of unsuccessful login attempts on a non-critical tool. |
| Medium | Affects a significant portion of assets or degrades essential functionality; workarounds exist. | Malware on multiple workstations needing isolation and cleanup; contained privilege escalation that didn't reach critical systems; a detected but contained denial-of-service attempt on a secondary service. |
| High | Significantly impairs confidentiality, integrity, or availability of critical assets and operations. | Widespread ransomware across critical systems; compromise of a system holding sensitive customer data; successful privilege escalation to critical systems; a sustained denial-of-service attack on primary services; an insider exfiltrating sensitive data. |

**Priority matrix** — combine urgency and impact into five priority levels, P1 (highest) to P5 (lowest):

| | Low impact | Medium impact | High impact |
| --- | --- | --- | --- |
| **High urgency** | P3 – Medium | P2 – High | P1 – Critical |
| **Medium urgency** | P4 – Low | P3 – Medium | P2 – High |
| **Low urgency** | P5 – Lowest | P4 – Low | P3 – Medium |

**Recommended response by priority**

| Priority | Response |
| --- | --- |
| P1 | Activate this plan. Immediate, sustained effort using all resources that can meaningfully help. On-call procedures activated. |
| P2 | Activate this plan. Immediate response and resource deployment; only people on low/medium-priority work are pulled in. |
| P3 | Immediate response through standard procedures, within normal management structures. |
| P4 | Standard operating procedures; resolution queued behind higher-priority work. |
| P5 | Standard operating procedures; resolution completed when time permits. |

## Plan activation

### Activation procedure

| Step | Description |
| --- | --- |
| Contact the DRP Coordinator | The person who activates this plan and notifies the response team. |
| Assessment | The DRP Coordinator assesses the situation and consults senior leadership. |
| Decision | The DRP Coordinator decides whether to activate, based on severity and impact. |
| Activation | The response team leads the implementation of the plan. |

### Response team roles

Adapt to the size of the organisation — a solo operator may hold several of these at once, but naming the roles (even if one person fills three of them) is what makes handover and escalation possible if that person is unavailable.

| Role | Function |
| --- | --- |
| DRP Coordinator | Activates the plan; overall response coordination. |
| Engineering Recovery | Technical investigation, containment, and remediation of affected systems. |
| Internal IT Recovery | Detection, initial triage, and internal system recovery. |
| Business Recovery | Coordinates the business-facing response and continuity. |
| Communications Lead | Owns internal and external communication during the incident. |

Keep named contacts for each role (phone, email, and a fallback channel) in a document reviewed at least annually — not embedded in this plan, so contact details can be updated without revising the plan itself.

## Response and containment

### Objective identification

Once the response team is activated, define the response objectives by working through:

- Who is the threat actor (if known)?
- What is the scope and extent — which systems, networks, and information are affected?
- When did it occur?
- Was sensitive information accessed, disclosed, stolen, encrypted, or corrupted?
- How did the attacker get in?
- What are the potential impacts?
- Is this targeted, or part of a broader industry-wide attack?

### Investigation and analysis

- Identify which resources — internal and external — are at risk, and what harmful processes are currently running on them.
- Start assembling evidence: logs, artefacts, interview notes.
- Avoid tipping off a suspected threat actor — actions that reveal you're investigating can prompt them to cover their tracks or move further into the network.
- Understand how the incident occurred; review relevant documentation; interview personnel as needed; review any third-party providers in scope.
- Bring in external investigative help if warranted, at management's discretion.
- Record correspondence (emails, tickets, chat messages, call transcripts) as it happens, not reconstructed afterwards.

### Containment

Decide whether at-risk resources need physical or logical removal. Anything posing a significant threat to confidentiality, integrity, or availability should be isolated immediately. Where feasible, back up affected systems onto new media before remediating — this preserves a forensic snapshot even though it isn't a valid production restore point.

## Communication and stakeholder management

### Mandatory reporting obligations (Australia-specific — adapt to your jurisdiction)

If the organisation operates critical infrastructure covered by Australia's *Security of Critical Infrastructure Act*, incidents must be reported to the **Australian Cyber Security Centre (ACSC)**:

- **Critical incidents** (material disruption to essential goods/services): report within **12 hours** of becoming aware.
- **Other reportable incidents** (impact on availability, integrity, reliability, or confidentiality without full disruption): report within **72 hours**.
- Reports can be lodged online, or orally via the ACSC's hotline followed by a written report within 84 hours (critical) or 48 hours (other).
- If unsure whether something is reportable: report it.

If the incident involves personal information, Australia's **Notifiable Data Breach (NDB) scheme** may apply. A notifiable data breach exists where there's unauthorised access, disclosure, or loss of personal information likely to result in serious harm, and the organisation hasn't been able to prevent that harm through remedial action. Where it applies, the organisation must notify affected individuals and the **Office of the Australian Information Commissioner (OAIC)**, including:

- The organisation's name and contact details.
- A description of the breach.
- The kinds of information involved.
- Recommended steps for affected individuals.

If the organisation serves customers regulated by the **Australian Prudential Regulation Authority (APRA)**, a material incident may trigger a customer's own **CPS 234** notification obligation (typically within 72 hours of the customer becoming aware) — even where the organisation itself isn't APRA-regulated, having a process to support a customer's compliance obligation is worth building in.

*(If you operate outside Australia, replace this section with your own jurisdiction's equivalents — a breach-notification law, a sectoral regulator, and a national cyber security agency reporting channel are close to universal requirements; only the specific bodies and timeframes change.)*

### Communication principles

- Avoid proactively phoning stakeholders where a written record is preferable — undocumented verbal commitments are hard to walk back.
- Route calls and written communication through whoever owns the relationship with that stakeholder.
- Avoid absolute commitments in writing; keep updates factual and concise.
- **First contact matters most.** Acknowledge the issue, summarise known impact, promise further updates, and show empathy. Anticipate the obvious questions: what's my exposure, how long has this been going on, how do I know it's fixed, why didn't you catch it sooner.
- **During the incident**, provide regular updates even when there's nothing new — "still investigating, no change" is itself useful information. Keep a status page or equivalent channel current.

### Stakeholder-specific notes

- **Board/senior leadership**: keep informed of potential impact, approach, and timeline throughout the incident lifecycle.
- **Suppliers**: may hold insight into cause or scope; loop them in, but share only the minimum needed for them to help.
- **Customers**: where contractually or statutorily required, notify affected customers with the nature of the incident, the scope of impact to them, any effect on service performance, and an estimated resolution time. Provide regular updates as response progresses.

## Eradication and recovery

1. **Assess residual impact** — a thorough review of what the investigation found, to scope the recovery effort and prioritise restoration.
2. **Identify and remove the threat** — patch vulnerabilities, remove malicious software, reset compromised credentials, or take other remediation steps.
3. **Restore systems and services** — from backup, rebuild, or repair as needed, confirming integrity and functionality.
4. **Test and validate** — functional, performance, and security testing before returning systems to production.

## Post-incident review (PIR)

- Run a PIR for every P1 and P2 incident (unless a customer or regulator specifically requests one for a lower-priority incident).
- Include everyone relevant: response team members, IT/management, and any external parties involved.
- Use the [Post-Incident Report Template](../references/post-incident-report-template.md) to document: description, timeline, actions taken, root cause, impact (technical, operational, business), lessons learned, and recommendations.
- Identify systemic issues behind the incident, not just its immediate cause.
- Turn findings into a corrective action plan with owners and deadlines, prioritised by impact and feasibility.
- Update policies and procedures to reflect what was learned.
- Keep the culture blame-free — an open, honest PIR produces better fixes than one where people are protecting themselves.

## Plan improvement

- Run at least one scenario-based test annually (simulation, fail-over test, or structured walkthrough).
- Update internal and external contact details at least annually.
- Document every test using the template below.

### Appendix A — CSIRP test report template

- **Executive summary** — overview of findings, recommendations, implications.
- **Introduction** — purpose, scope (systems/processes/people involved), scenario tested.
- **Objectives** — verify plan effectiveness; identify gaps; assess readiness.
- **Planning** — schedule, and detailed procedures for conducting the test.
- **Execution** — what happened against the procedures; observations, issues, recovery times.
- **Results and analysis** — outcomes per scenario; strengths and weaknesses of the plan.
- **Conclusion** — root causes of any issues found, and a follow-up action plan.

## Adapt this to your context

- **Size**: the five response-team roles assume a real team. A solo operator will hold several at once — name them anyway (even as "me, wearing the Engineering Recovery hat") so a stand-in or successor knows what each role is actually responsible for.
- **Jurisdiction**: the mandatory-reporting section above is Australia-specific (ACSC, OAIC/NDB scheme, APRA/CPS 234). Replace it with your own jurisdiction's equivalents — a breach-notification law, a sectoral regulator, and a national cyber security agency reporting channel are close to universal; only the specific bodies, thresholds, and timeframes change.
- **Industry**: some sectors carry reporting obligations well beyond a generic national scheme — financial services, healthcare, telecommunications, and critical infrastructure regulators often layer their own mandatory incident-notification rules on top. Check what applies to your sector specifically, not just your jurisdiction generally.
- **Government vs non-government**: government entities are often required to report through a specific mandated channel or to a specific agency (and sometimes on a shorter clock) than private-sector equivalents — confirm the mandated channel for your context rather than assuming the generic one applies.
- **PIR threshold**: this plan runs a PIR for P1/P2 incidents by default. Some regulators or contracts require a formal PIR/root-cause analysis for *any* reportable incident, regardless of your internal priority rating — check your obligations before relying on the priority threshold alone.

**Frameworks referenced** (by family — check the current edition of whichever applies to you): ISO 22301, NIST SP 800-34, NIST IR 8286.
