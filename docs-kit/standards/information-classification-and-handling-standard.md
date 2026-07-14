---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Information classification and handling standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard defines how information is classified according to its sensitivity, and how documents and records are governed across their lifecycle, from creation and approval through to retention and disposal. Classifying information consistently lets a small team apply proportionate protection instead of guessing case by case, while clear document and record governance keeps decisions traceable and defensible when it matters most, such as during an audit, dispute, or incident. Together, these practices turn ad hoc judgement calls about sensitive information into a repeatable, low-overhead habit.

### Risks

- Data breaches and information leakage
- Regulatory or contractual non-compliance
- Loss of customer trust and confidence
- Intellectual property theft
- Insider misuse of sensitive information
- Operational disruption from lost, destroyed, or unrecoverable records
- Reputational damage

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| ICH-100 | Maintain a single, centralised inventory of information assets (data, documents, systems, and key third-party services), recording at minimum each asset's name, purpose, owner, and classification. |
| ICH-101 | Classify every information asset into one of four levels (Public, Limited Distribution, Confidential, or Highly Confidential) based on the likely impact of unauthorised disclosure. |
| ICH-102 | Treat any document or asset that hasn't been explicitly classified as Confidential by default. |
| ICH-103 | Classify a document, email, or dataset that mixes multiple sensitivity levels at the level of its most sensitive component. |
| ICH-104 | Label or mark documents according to their classification, including a visible watermark for material that warrants it. |
| ICH-105 | Apply handling controls that scale with classification: for example, restricting Confidential and Highly Confidential material to password-protected storage with multi-factor authentication, and requiring a signed confidentiality agreement before any external party receives Confidential material. |
| ICH-106 | Avoid printing Confidential or Highly Confidential material where possible; when printing is unavoidable, collect the output immediately and never leave it unattended. |
| ICH-107 | Encrypt removable media carrying Confidential or Highly Confidential information, and label it externally with its classification and creation date. |
| ICH-108 | Transport physical documents or storage media containing Confidential or Highly Confidential information only via authorised personnel or a tracked courier, packaged to show evidence of tampering. |
| ICH-109 | Render data unreadable before disposing of or reusing any device or media (by clearing, cryptographic erasure, physical destruction, or degaussing) and physically destroy (via an approved destruction service) any device that can't be rendered unreadable. |
| ICH-110 | Notify the person or role accountable for information security before onboarding a new information asset, materially changing one, or decommissioning one, so the inventory stays current. |
| ICH-111 | Categorise governed documents by type (for example: policy, plan, standard, process, procedure, register) and route each type through a defined author, reviewer, and approver appropriate to its content and sensitivity. |
| ICH-112 | Apply version control to every document that forms part of your management system, and record approval whenever a governed document changes materially. |
| ICH-113 | Use a consistent naming convention for core and template documentation so it can be reliably identified and retrieved. |
| ICH-114 | Define and document a retention period for each category of record, driven by the legal, regulatory, or contractual obligations that apply to it. |
| ICH-115 | Delete or destroy records containing personal or otherwise sensitive information once their retention period expires, unless there's a documented business reason to keep them longer. |
| ICH-116 | Back up records held in databases or applications on a regular schedule, and keep records available in a way proportionate to how critical they are to the business. |
| ICH-117 | Dispose of superseded hard copies of governed documents through your secure-disposal controls, not general waste. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| ICH-200 | Re-assess classified information at least annually and declassify it once there's no remaining business reason for the higher classification. |
| ICH-201 | Add an acknowledgement prompt before users can view, print, or save restricted information, where your systems support it. |
| ICH-202 | Name and file records so their content is obvious and they're easy to find later. |
| ICH-203 | Store records electronically by default, keeping a physical backup only where there's a genuine legal or practical reason to (for example, some financial records). |
| ICH-204 | Map each governed document to the compliance frameworks or regulations it supports, so coverage gaps are easy to spot. |
| ICH-205 | Periodically audit your information asset inventory and document/record retention practices against this standard. |
| ICH-206 | Weigh the confidentiality, integrity, and availability needs of an asset independently: a document can be low-risk to leak but high-impact if it becomes unavailable, and vice versa. |
| ICH-207 | Consider the business impact of a document or record becoming unavailable, not just of it leaking, when deciding how much redundancy and monitoring it needs. |
| ICH-208 | Where a third party's own retention or logging period is shorter than what you need, document the gap and the compensating control: for example, exporting logs before they age out. |
| ICH-209 | Review higher-risk records or logs (those tied to critical systems or suppliers) more frequently than the general annual cycle. |

## Adapt this to your context

- A solo operator can run the information asset inventory as a single spreadsheet; formal document review/approval matrices only need extra rigour once more than one person touches governed documents.
- Scale classification labels and handling controls to what you actually hold: a service with no customer personal data needs a much lighter Confidential/Highly Confidential tier than one handling financial or health data.
- Set retention periods against your own jurisdiction's legal and tax requirements, rather than a schedule copied from another organisation.
- Physical handling controls (courier, shredding, watermarking) only apply if you actually handle physical documents or removable media: a fully cloud-based operation can scope those out.

**Frameworks referenced**: ISO/IEC 27001 Annex A
