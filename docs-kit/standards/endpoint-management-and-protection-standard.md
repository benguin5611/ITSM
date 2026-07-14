---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Endpoint management and protection standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard sets the baseline for protecting endpoints (laptops and other user devices) against malware, unauthorised network access, and malicious web content. For a lean IT function, endpoint protection is usually the single highest-leverage control: a small number of consistently-applied settings prevent the large majority of everyday compromise attempts, without requiring ongoing per-device effort.

### Risks

Failing to implement this standard can expose the organisation to:

- Malware or ransomware infections spreading across the network
- Data exposure or theft via malicious websites or command-and-control channels
- Extended downtime and recovery cost following a compromise
- Regulatory or contractual non-compliance following a preventable incident
- Loss of customer trust after a public security event

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| EMP-100 | Run antivirus/anti-malware software with real-time (on-access) scanning enabled on every company-owned endpoint. |
| EMP-101 | Enable host-based firewalls by default on every endpoint, denying inbound connections unless a specific exception is approved. |
| EMP-102 | Apply anti-malware signature and engine updates automatically on a recurring schedule, not as a manual step. |
| EMP-103 | Run a full system malware scan on a recurring schedule, at minimum monthly. |
| EMP-104 | Prevent users from disabling or altering anti-malware or firewall controls without documented, time-limited authorisation. |
| EMP-105 | Log and raise malware detections as a security event; never silently clean and close them out. |
| EMP-106 | Block known-malicious destinations, including command-and-control infrastructure, via web or DNS filtering. |
| EMP-107 | Retain antivirus and endpoint protection logs for a minimum period sufficient to support later investigation (e.g. 12 months). |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| EMP-200 | Consider an EDR/XDR solution once alert volume or endpoint count outgrows what a small team can triage manually. |
| EMP-201 | Filter web access by category (e.g. adult content, streaming, file-sharing) rather than maintaining a blocklist of individual sites. |
| EMP-202 | Maintain an allowlist for business-critical destinations to reduce false positives from category filtering. |
| EMP-203 | Review firewall and web-filtering rules on a recurring basis (e.g. every 6-12 months) so exceptions don't accumulate unchecked. |
| EMP-204 | Use sandboxing or behavioural analysis to evaluate suspicious files before they're allowed to run. |
| EMP-205 | Enable command-line/script execution logging (e.g. shell or scripting-host auditing) to support later investigation. |
| EMP-206 | Integrate threat-intelligence feeds so filtering blocks newly identified malicious destinations, not just a static list. |

## Adapt this to your context

- Web/DNS filtering (EMP-106) can be as simple as a filtering DNS resolver for a small fleet; you don't need an enterprise secure web gateway until your workforce is large or distributed.
- EDR/XDR (EMP-200) earns its cost once alert volume outgrows manual triage; below that, built-in antivirus plus logging is usually enough.
- Log retention periods should match whatever your compliance program or cyber insurance policy actually requires, rather than an arbitrary default.
- Sandboxing and threat-intel integration (EMP-204, EMP-206) are maturity upgrades that become more relevant once you handle regulated or high-value data, rather than a day-one requirement for every organisation.

**Frameworks referenced**: ISO/IEC 27001 Annex A, CIS Controls
