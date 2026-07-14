---
Artefact type: Standard
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Network and cloud security standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard defines the minimum network and cloud security controls needed to protect the confidentiality, integrity, and availability of your network resources, data, and communications, whether that network is a production cloud environment, an office LAN, or a home office setup. It matters because a lean team typically has no dedicated network security function, so consistent baseline controls (segmentation, encryption, access control, patching) have to substitute for continuous manual oversight. This standard sets the guardrails any network design should satisfy, rather than prescribing how to design a specific network.

### Risks

- Unauthorised access to systems and data
- Loss of data confidentiality or integrity
- Service disruption and downtime
- Regulatory or contractual non-compliance
- Intellectual property theft
- Reputational and brand damage
- Costly operational and financial fallout from a network compromise

## Requirements

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| NCS-100 | Only use cloud and network service providers that meet your defined security requirements and hold appropriate independent certifications. |
| NCS-101 | Encrypt sensitive data at rest and in transit using approved, current encryption algorithms and key management practices. |
| NCS-102 | Base network design decisions on the classification of the data the network carries, a risk assessment of likely threats, and the resilience and availability the network needs to provide. |
| NCS-103 | Apply a defence-in-depth approach: layer controls (for example, network and host-based firewalls) so the failure of any single control doesn't expose the whole network. |
| NCS-104 | Segregate networks, including tenant or customer isolation in shared cloud environments, so a compromise in one segment cannot move freely into another. |
| NCS-105 | Encrypt all data transmitted over public networks such as the internet, using current TLS. |
| NCS-106 | Enforce multi-factor authentication for access to all cloud services and administrative network interfaces. |
| NCS-107 | Restrict network and cloud access to the minimum ports, protocols, and privileges needed for the job, following least privilege. |
| NCS-108 | Maintain current network documentation, including diagrams, and update it whenever a material change is made. |
| NCS-109 | Define and follow an incident response procedure for network and cloud security events, covering detection, escalation, and reporting. |
| NCS-110 | Change all default credentials on routers, access points, and other network equipment before putting them into use. |
| NCS-111 | Use a strong, unique password and at least WPA2-equivalent (or better) encryption on every Wi-Fi network you operate. |
| NCS-112 | Provide a physically and logically separate guest network wherever guest Wi-Fi access is offered. |
| NCS-113 | Keep firmware and software on network devices current with vendor security patches. |

## Guidelines

**Responsible party should/may:**

| Ref | Statement |
| --- | --- |
| NCS-200 | Deploy intrusion detection at the network perimeter and on critical systems where feasible. |
| NCS-201 | Run a network vulnerability scan at least annually. |
| NCS-202 | Use a DMZ or equivalent pattern to limit direct internet exposure of internal services. |
| NCS-203 | Review network documentation and access control lists at least annually. |
| NCS-204 | Conduct periodic due-diligence reviews of your cloud and network service providers. |
| NCS-205 | Know where your data resides with each provider, and confirm it's fully removed once a contract ends. |
| NCS-206 | Give anyone working from a home or remote network basic guidance on phishing awareness and secure disposal of old routers and devices. |
| NCS-207 | Consider network access control (for example, certificate- or credential-based authentication before devices join the network) for office wireless networks. |
| NCS-208 | Site wireless access points out of easy public reach, and keep an eye out for unusual network activity. |

## Adapt this to your context

- Solo operators without dedicated network engineering should lean on managed, provider-native security controls (managed firewalls, built-in segmentation) rather than building bespoke on-prem infrastructure.
- If most work happens remotely, weight your effort toward home/remote network guidance rather than office network controls you may not need.
- Scale segmentation and perimeter controls to the number and sensitivity of systems actually exposed to the internet: a single low-risk marketing site doesn't need the same architecture as a multi-tenant platform.
- Match certification expectations for providers to your own compliance obligations: a regulated business may need formal audit evidence from every provider, while others can rely on a vendor security questionnaire.

**Frameworks referenced**: ISO/IEC 27001 Annex A, NIST Cybersecurity Framework, CIS Controls
