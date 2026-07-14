---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Data privacy and record protection standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard sets requirements for protecting personal and sensitive data as it moves through email, endpoints, backups, logs, and cryptographic systems, and for meeting your obligations to the people whose data you hold. It matters because even a small operation processes data other people have trusted to it, and a single mishandled backup, leaked log, or unlawful disclosure can create legal, financial, and reputational damage well out of proportion to the size of the business. Document and record governance is addressed in a separate standard; this one focuses on keeping data itself safe, private, and recoverable.

### Risks

- Data breaches and privacy violations
- Regulatory non-compliance and financial penalties
- Loss of customer trust
- Operational disruption from unrecoverable or compromised data
- Legal liability, including from cross-border data handling

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| DPR-100 | Restrict company devices from installing unauthorised browser or email plugins and add-ons, and limit which websites they can reach. |
| DPR-101 | Implement email authentication (SPF, DKIM, and DMARC) to reduce spoofing and phishing risk, and quarantine suspicious inbound email and attachments. |
| DPR-102 | Disable end-user access to automatic external email forwarding. |
| DPR-103 | Restrict company data to company-owned devices, or personal devices that have gone through a formal bring-your-own-device approval process. |
| DPR-104 | Encrypt sensitive data at rest and in transit, and use approved cryptographic protection for enterprise data held on mobile devices. |
| DPR-105 | Configure data loss prevention controls appropriate to your tools (for example, cloud storage sharing rules or mobile device management policies) to detect and block unauthorised sharing or exfiltration of sensitive data, scaled to its classification. |
| DPR-106 | Lock screens automatically when unattended, and position screens to avoid casual viewing of sensitive information by passers-by. |
| DPR-107 | Process personal data lawfully, fairly, and transparently: collect only what's needed for a specific stated purpose, keep it accurate, and don't retain it longer than necessary. |
| DPR-108 | Give individuals a working way to exercise their data rights (for example, access, correction, or deletion), and respond within the timeframe your applicable privacy law requires. |
| DPR-109 | Assess suspected data breaches for notifiable harm promptly, and notify affected individuals and the relevant regulator within the timeframe your applicable law requires. |
| DPR-110 | Conduct a privacy risk assessment before launching any new system or process that will handle personal data in a materially new way. |
| DPR-111 | Back up data held by or on behalf of your organisation on a regular, defined schedule, with the scope, method, retention period, and encryption of backups documented and agreed. |
| DPR-112 | Test backup restoration at least annually to confirm backups are reliable, accurate, and complete. |
| DPR-113 | Never use real production data for testing or development purposes. |
| DPR-114 | Enable logging on company-owned systems and devices, capturing enough detail (event, source, user, timestamp) to support an investigation, and retain security logs long enough to meet legal or investigation needs. |
| DPR-115 | Review security logs and alerts regularly for anomalies, and restrict who can access, alter, or delete log data. |
| DPR-116 | Use only current, well-vetted encryption algorithms, and manage encryption keys through a documented lifecycle: generation, storage, rotation, revocation, and destruction. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| DPR-200 | Keep only fully supported, current browser and email client versions in use. |
| DPR-201 | Take a cloud-first approach to storage rather than saving sensitive files locally, and wipe local storage media before any device is decommissioned. |
| DPR-202 | Review cross-border transfers of personal data before they happen, confirming the receiving party will handle the data to a comparable standard, including any extra requirements that apply when the data relates to individuals in another jurisdiction. |
| DPR-203 | Set up alerting rules for security events, and review those rules at least annually or after any significant change to your systems or threat landscape. |
| DPR-204 | Apply data masking, pseudonymisation, or anonymisation to reduce exposure of sensitive data in non-production or reporting contexts. |
| DPR-205 | Scan source code for accidentally committed secrets as part of your build and release process. |
| DPR-206 | Protect backups from accidental overwrite. |
| DPR-207 | Where you rely on a third-party identity verification service, use it only for its intended lawful purpose, obtain informed consent first, and never disclose more of the result than the recipient genuinely needs. |

## Adapt this to your context

- Solo operators without a formal log management platform can meet the spirit of the logging requirements using the audit and activity logs your existing cloud provider already gives you: the goal is visibility and retention, rather than a dedicated tool.
- Scale data loss prevention and access-control investment to what you actually hold; a business with no customer personal data has a much lighter obligation here than one processing financial or health data.
- Breach notification timeframes and data-subject rights are set by whichever privacy law actually applies to you; confirm the specific deadlines and thresholds for your jurisdiction rather than assuming one global standard.
- If you don't handle third-party identity verification at all, that requirement can be dropped entirely.

**Frameworks referenced**: ISO/IEC 27001 Annex A, NIST Cybersecurity Framework, privacy-by-design principles in the style of the GDPR
