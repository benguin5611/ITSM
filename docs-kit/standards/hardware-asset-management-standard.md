---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Hardware asset management standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, rather than a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard defines how physical devices (laptops, phones, tablets, and hardware security tokens) are tracked, configured, and retired across their lifecycle. Without it, a lean IT function loses visibility into what devices exist, who holds them, and whether they're still safe to use: the most common root cause of avoidable data loss.

### Risks

Failing to implement this standard can expose the organisation to:

- Devices going missing without anyone noticing
- Data exposure or loss when a lost or stolen device isn't encrypted or wipeable
- Unauthorised or unmanaged software introducing malware
- Wasted spend from over-purchasing or under-utilised hardware
- Inability to reconstruct what happened to a device during an audit or incident

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| HAM-100 | Maintain a single, current asset register recording every company-owned hardware device, its owner, and its status. |
| HAM-101 | Affix a unique asset identifier/label to every issued device. |
| HAM-102 | Enrol every company-owned laptop, tablet, and phone in a device management tool before it's handed to a user, and prevent the user from removing that enrolment. |
| HAM-103 | Require full-disk encryption on every device capable of accessing company data. |
| HAM-104 | Require a passcode/lock screen and an automatic lock after a defined idle period. |
| HAM-105 | Provision standard, non-administrative accounts by default; grant administrative rights only through a documented exception. |
| HAM-106 | Ensure company-owned devices can be remotely wiped; personally-owned (BYOD) devices need either full-disk encryption or device-management enrolment as a minimum before accessing company data. |
| HAM-107 | Securely wipe all data from a device before it is disposed of, resold, returned, reassigned, or sent for external repair. |
| HAM-108 | Require immediate reporting of any lost, stolen, or potentially compromised device. |
| HAM-109 | Prohibit jailbroken or rooted devices from accessing company resources. |
| HAM-110 | Reconcile the asset register against a physical count on a recurring basis. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| HAM-200 | Define an expected lifecycle for each device type and plan replacement ahead of failure, rather than reacting to breakdowns. |
| HAM-201 | Keep shared peripherals (monitors, keyboards, docks) in the office rather than issuing them for offsite use. |
| HAM-202 | Transport devices in a protective case when moving them between locations. |
| HAM-203 | Disable removable media and network printing by default, granting exceptions case by case. |
| HAM-204 | Review the minimum supported OS version for each platform on a recurring basis. |
| HAM-205 | Use configuration-management tooling to automatically reapply baseline settings to devices at regular intervals. |

## Adapt this to your context

- A single spreadsheet or lightweight asset-tracking tool is enough for a small fleet; move to a dedicated asset-management system only once device count or turnover makes a spreadsheet unreliable.
- Your BYOD stance (allowed or not, and under what conditions) should reflect your industry's data sensitivity and your contractual obligations to customers, rather than a default copied from elsewhere.
- Lifecycle length (HAM-200) should reflect your budget cycle and the operational risk of ageing hardware, not a fixed industry number.
- If you're subject to a compliance program with an asset-management control (e.g. SOC 2, ISO 27001), tighten audit frequency (HAM-110) to match its evidence requirements.

**Frameworks referenced**: ISO/IEC 27001 Annex A, CIS Controls
