---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Domain management standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard sets out how your organisation selects, registers, renews, and manages the domain names that make up its online identity. Domains are cheap to lose and expensive to recover: a lapsed renewal, a hijacked registrar account, or a look-alike domain can disrupt customers, damage trust, and hand part of your brand to someone else. This standard exists to make sure that doesn't happen by accident.

### Risks

- Cybersecurity incidents targeting weakly secured domains or DNS
- Service interruption from an expired or hijacked domain
- Compliance violations tied to naming or registration rules
- Brand and reputational damage
- Domain squatting and typosquatting
- Loss of control over domain assets and everything that depends on them

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| DOM-100 | Choose domain names that reflect your organisation's name, products, or services, and confirm they don't infringe on an existing trademark before registering. |
| DOM-101 | Use your registrar's privacy/protection service to shield registration contact details from public lookup. |
| DOM-102 | Register domains only through an approved registrar, and hold every registration in the organisation's name, never an individual's. |
| DOM-103 | Keep domain registration account details and credentials confidential and access-restricted. |
| DOM-104 | Ensure domain registrations meet the requirements of the relevant naming authority and any industry regulator for that domain space. |
| DOM-105 | Renew domains before they expire: a domain must never lapse because a renewal was missed. |
| DOM-106 | Assign a named owner, and a backup, responsible for tracking and actioning domain renewals, with renewal notifications sent to more than one person. |
| DOM-107 | Turn on automatic renewal wherever your registrar supports it, to reduce reliance on someone remembering to act. |
| DOM-108 | Review all domain registrations, DNS records, contacts, and payment details, across every registrar and provider in use, at least annually. |
| DOM-109 | Restrict access to domain and DNS management tools and accounts to a named, minimal set of authorised people. |
| DOM-110 | Route all changes to domain or DNS configuration through your normal change management process. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| DOM-200 | Avoid hyphens and numbers in domain names unless there's a clear reason to use them. |
| DOM-201 | Register close variations of your domain (common misspellings, alternative top-level domains) to reduce squatting and typosquatting risk. |
| DOM-202 | Use a domain-monitoring service to alert on the registration of similar or potentially infringing domain names. |
| DOM-203 | Avoid country-specific top-level domains unless you have a genuine business presence in that region. |
| DOM-204 | Consider registering internationalised domain names if you serve non-English-speaking audiences. |
| DOM-205 | Prioritise registering domains that closely match your own trademarks or brand names. |
| DOM-206 | Keep a backup payment method on file for renewals in case the primary method fails. |
| DOM-207 | Choose the longest renewal term your registrar allows, to reduce lapse risk and administrative overhead. |
| DOM-208 | Budget for domain renewal costs annually as part of routine financial planning. |
| DOM-209 | Make sure anyone with domain management access understands their responsibilities and the risk of getting this wrong. |

## Adapt this to your context

- A single-domain solo operator may only need one named owner and a calendar reminder; a multi-brand or multi-region organisation needs a proper domain register and delegated ownership per brand.
- If you operate in a regulated industry, factor in any sector-specific naming or registration rules alongside standard trademark checks.
- Scale monitoring for squatting and typosquatting to your brand's public profile: a high-visibility consumer brand warrants more investment here than a low-profile B2B tool.
- Fold domain and DNS account access into your broader identity and access management practices rather than treating it as a separate silo.

**Frameworks referenced**: ISO/IEC 27001 Annex A
