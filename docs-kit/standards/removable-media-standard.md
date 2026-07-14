---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Removable media standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, rather than a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard governs how removable media (USB drives, external hard drives, memory cards, and similar portable storage) is requested, issued, transported, and eventually disposed of. Removable media is a well-known channel for both data loss (an unencrypted drive going missing) and malware introduction, so the default posture is to keep it switched off until there's a specific, approved need.

### Risks

Failing to implement this standard can expose the organisation to:

- Data loss or exposure from a lost or stolen unencrypted drive
- Malware introduced onto the network via an untrusted device
- Untracked data leaving the organisation with no record of what, when, or why
- Sensitive data recovered from media that was disposed of without being wiped or destroyed
- No way to reconstruct events during an incident because nothing was logged

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| RMM-100 | Disable removable media by default on every company-owned endpoint. |
| RMM-101 | Require removable media use to be explicitly requested and approved before it's enabled for a specific user or device. |
| RMM-102 | Record, for every approved request: the requester, the media/device involved, the sensitivity of the data involved (if known), the business reason, and an expiry date if the need is temporary. |
| RMM-103 | Encrypt approved removable media, with the password generated and stored through an approved password manager, never written down or kept with the media itself. |
| RMM-104 | Report loss or theft of removable media immediately and treat it as a security incident. |
| RMM-105 | Use only approved couriers/carriers to physically transfer media containing company data between locations. |
| RMM-106 | Keep a chain-of-custody record (dispatch confirmation, tracking reference, receipt confirmation) for every physical transfer. |
| RMM-107 | Securely erase all data from a device or media, using an approved method, before disposal, reassignment, resale, or return. |
| RMM-108 | Physically destroy media that cannot be reliably wiped, or that held highly sensitive data, instead of reusing it. |
| RMM-109 | Update the asset register whenever removable media is issued, transferred, wiped, or destroyed. |
| RMM-110 | Obtain documented approval before gifting, selling, or donating a device or media to staff, charities, or resellers. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| RMM-200 | Time-box access with an explicit expiry date whenever the need for removable media is temporary, rather than granting indefinite access. |
| RMM-201 | Prefer secure electronic transfer over physical media whenever practical, reserving removable media for cases where it's genuinely necessary. |
| RMM-202 | Loosen the default media-control policy only for the duration of an approved transfer, then restore the default-deny posture immediately afterwards. |
| RMM-203 | Use a third-party destruction service for end-of-life media rather than improvised destruction methods. |
| RMM-204 | Keep a record of the destruction method, date, and time for later audit purposes. |

## Adapt this to your context

- If your organisation rarely uses physical media at all, this control can be even simpler: default-deny plus a single manual approval step, with no dedicated encrypted-media stock to manage.
- Match physical destruction requirements (RMM-108) to the actual sensitivity of data your organisation handles. Not every organisation needs certified destruction for every drive.
- Courier/carrier approval (RMM-105) should reflect who you already trust for other sensitive shipments, rather than standing up a new vetted-courier list from scratch.
- If you operate under jurisdiction- or industry-specific media-sanitisation requirements, fold those directly into your wipe/destroy steps rather than treating them as a separate control.

**Frameworks referenced**: ISO/IEC 27001 Annex A, CIS Controls
