---
Artefact type: Standard
Owner role: Information Security Manager / IT lead, in conjunction with the control owner
Review cadence: Annual
Version: 1.0 (template)
---

# Identity and access management (IAM) standard

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here), a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

## Introduction

### Purpose

This standard defines Identity and Access Management (IAM) requirements for the information assets, information systems, and technology infrastructure owned and used by the organisation. IAM provides controlled access allowing staff, customers, and vendors to carry out their business while protecting the organisation's information assets from unauthorised and inappropriate access.

IAM defines the life cycle around staff identities and the accounts, permissions, and entitlements tied to those identities. It also sets requirements for managing access on an ongoing basis, including privileged access, according to business need and segregation-of-duties requirements. This standard is a key control in protecting the organisation's information: it ensures users are identified and authenticated, the correct permissions are allocated, and access is authorised according to business requirement, on an ongoing basis.

### Risks

This standard mandates that information system access is governed to ensure only appropriate access is granted. Failure to adopt and implement it may expose the organisation to:

- Unauthorised access
- Data breaches and information leakage
- Insider threats
- Compliance and regulatory violations
- Weakened authentication
- Inefficient provisioning and de-provisioning
- Lack of accountability and auditing
- Operational disruptions

### Format

Standards define directives in support of a Policy, developed by the Information Security Manager (or equivalent) in conjunction with the control owner. Standards split into two sections, **Requirements** and **Guidelines**, mapped to a consistent verb form. Getting this split right, and keeping it explicit, is what separates a Standard that's actually auditable from one that just sounds authoritative.

**Requirements** are the acceptable level of quality or attainment for controls protecting the confidentiality, integrity, and availability of information assets:

- **"must" or "shall"** indicates a requirement.

**Guidelines** are recommended but non-mandatory controls representing best practice within a domain:

- **"should"** indicates a recommendation.
- **"may"** indicates a permission.
- **"can"** indicates a possibility or capability.

Reference numbering starts each control area at the next hundred (e.g. Access and account management IAM-100 to 199, Account inventory and authentication IAM-200 to 299), so a reader can tell which control area a reference belongs to at a glance.

## Control areas

### Access and account management

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| IAM-100 | Implement a defined access control model appropriate to the systems in use, with role-based access control (RBAC) and least privilege as the baseline, to secure system components and data resources. |
| IAM-101 | Restrict user and privileged access based on the principle of least privilege. |
| IAM-102 | Assign access based on each person's job classification and function. |
| IAM-103 | Define the minimum system access each role needs for its job function. |
| IAM-104 | Ensure all access requests are reviewed, with documented approval clearly specifying the reasoning for the necessary privileges. |
| IAM-105 | For internally developed applications, restrict access based on need-to-know. |
| IAM-106 | Obtain approval and authorisation before granting user access to a system, from the System Owner, Information Security Manager, and/or Line Manager as applicable. |
| IAM-107 | Ensure staff with administrative/privileged access understand their responsibilities and accountability. |
| IAM-108 | Where proportionate to the size of the organisation, apply segregation of duties: separation of authorisation and execution; separation of recording and custody; separation of IT roles (system administration, network management, database administration); separation of approvals and payments. |
| IAM-109 | Disable dormant accounts after a defined period of inactivity, no longer than ninety (90) days. |
| IAM-110 | Document and maintain procedures for Joiners (onboarding), Movers (role change), Leavers (offboarding), and password management (verification of identity before modifying authentication credentials). |
| IAM-111 | Delete an account only after it has first been disabled and its deletion has been explicitly authorised. |
| IAM-112 | Log all access requests with the IT help desk (or equivalent). |
| IAM-113 | Promptly revoke access: disabling accounts on the termination date, on a role change that no longer requires the access, or as soon as reasonably possible. |

**Responsible party should:**

| Ref | Statement |
| --- | --- |
| IAM-114 | Where reasonable, require users with administrative privileges to use a dedicated secondary account for elevated activities. |
| IAM-115 | Limit access to scripting tools to administrative or development users who need them. |
| IAM-116 | Restrict production accounts from non-production environments, and non-production accounts from production environments. |
| IAM-117 | Disable any account that cannot be associated with a business process or business owner. |
| IAM-118 | Ensure all temporary access has an expiry date that is monitored and enforced. |
| IAM-119 | Avoid group, shared, or generic accounts for privileged and non-privileged purposes. |
| IAM-120 | Where duties can't be fully segregated, apply compensating controls: audit trails (who, when, what, what activity); supervisory review; independent review. |
| IAM-121 | Layer additional access control models (e.g. mandatory or discretionary access controls) on top of the RBAC baseline where the platform supports them and the data classification warrants it. |

### Account inventory and authentication

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| IAM-200 | Maintain an inventory of all user accounts, including privileged accounts, clearly marking which are administrative. |
| IAM-201 | Maintain an inventory of all authentication systems. |
| IAM-202 | Use multi-factor authentication for all administrative account access, where possible. |
| IAM-203 | Transmit authentication credentials across networks using encrypted channels. |
| IAM-204 | Assign a unique user ID when access is provisioned, and transmit the credential securely. |
| IAM-205 | Meet the following password requirements for user and privileged accounts: **Length**: minimum 15 characters as a single factor, or 12 with multi-factor authentication; systems must accept at least 64 characters and should accept up to 128 to support passphrases. **Permitted characters**: all printing ASCII, the space character, and Unicode where feasible. **No composition rules**: do not impose mixed-case/number/symbol requirements. **Blocklist enforcement**: reject passwords found on a blocklist of known-compromised or commonly used values. **Secure storage**: salt and hash with Argon2id; use scrypt where Argon2id isn't available, and PBKDF2-HMAC-SHA-256 (600,000+ iterations) only where FIPS-140 compliance requires it; salts at least 128 bits, cryptographically random. **User experience**: permit password managers and autofill; never disable paste in password fields. **Algorithm migration**: re-hash on next successful login, or require a new password within a defined transition window, when the hashing scheme changes. |
| IAM-206 | Use unique passwords per system. |
| IAM-207 | Change passwords immediately on any suspicion of compromise. |
| IAM-208 | Provide passwords via out-of-band methods when self-service reset isn't available. |

**Responsible party should:**

| Ref | Statement |
| --- | --- |
| IAM-209 | Configure access through as few centralised authentication points as possible. |
| IAM-210 | Use multi-factor authentication for all user accounts where possible, on-site or third-party managed; prefer phishing-resistant methods (FIDO2/WebAuthn or similar) where supported. |
| IAM-211 | Lock out a user ID after no more than ten (10) failed attempts, for at least thirty (30) minutes or until an administrator intervenes; throttle per-authenticator where feasible; for biometrics, limit to five (5) failures (ten (10) with presentation-attack detection) with a minimum thirty (30) second delay. |
| IAM-212 | Do not mandate periodic password rotation; only change on evidence of compromise; where MFA isn't in use, assess and document the risk of static passwords. |
| IAM-213 | Compare prospective passwords against a blocklist where possible. |
| IAM-214 | Prevent reuse of any of the last four (4) passwords. |

### Audits and logging

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| IAM-300 | Review system access for all systems at least every twelve (12) months, confirming accounts and IDs are documented, only authorised users hold an account, and unnecessary licences are revoked. Retain evidence for audit. |
| IAM-301 | Review privileged access on critical systems at least every three (3) months, confirming only authorised users hold privileged accounts. Retain evidence for audit. |

**Responsible party should:**

| Ref | Statement |
| --- | --- |
| IAM-302 | Log and alert when an account is added to or removed from an administrative-privilege group. |
| IAM-303 | Log and alert on unsuccessful logins to an administrative account. |
| IAM-304 | Monitor attempts to access deactivated accounts. |
| IAM-305 | Continuously monitor user and privileged account activity to detect and respond to suspicious or unauthorised action. |

### Customer authentication and identity federation

Applicable where the organisation offers a product or service with customer-facing authentication.

**Responsible party must:**

| Ref | Statement |
| --- | --- |
| IAM-400 | Authenticate customers through federated identity protocols (OIDC or SAML 2.0) brokered via a centralised identity platform; don't offer direct password authentication where federation is available, unless the customer explicitly requests it. |
| IAM-401 | Prefer asymmetric client authentication (e.g. `private_key_jwt`) over shared secrets where the customer's identity provider supports it. |
| IAM-402 | Run all federated authentication exchanges over encrypted channels (TLS 1.2+). |
| IAM-403 | Validate signatures on SAML assertions and OIDC ID tokens; never disable signature validation. |
| IAM-404 | Monitor credential expiry for federated connections and rotate no later than thirty (30) days before expiry. |
| IAM-405 | Transmit shared credentials to and from customers over out-of-band secure channels; never unencrypted email. |
| IAM-406 | Verify the end-to-end federated login flow before production use, and re-verify after key rotation, certificate update, or configuration change. |
| IAM-407 | Document and follow a key-rotation procedure for the identity platform's signing keys, including per-provider impact assessment and customer coordination. |

**Responsible party should:**

| Ref | Statement |
| --- | --- |
| IAM-408 | Prefer JWKS URL-based key verification over static certificate upload, where supported, to enable automatic rotation. |
| IAM-409 | Ask customers to restrict their identity provider application to single-tenant or organisation-internal access. |
| IAM-410 | Ask customers to assign only authorised users or groups to the federated application, rather than organisation-wide access by default. |
| IAM-411 | Log all federated authentication events and retain per the organisation's logging standard. |
| IAM-412 | Review active customer federation connections at least every twelve (12) months, confirming they're still in use, credentials aren't approaching expiry, and the method still meets current requirements. |

## Breach of this standard

### Misconduct

Failure to define access needs per role; assigning access on incorrect job classification; granting excessive privileges; not reviewing and approving access requests; failing to enforce least privilege; granting access without proper approval; not training staff with privileged access; failing to disable dormant accounts on schedule; missing joiner/mover/leaver/password-management procedures; deleting accounts without confirmation; not logging access requests.

### Serious misconduct

Violating segregation-of-duties controls; violating legal, regulatory, or contractual requirements related to access management.

### Disciplinary actions

Proportionate to severity and impact: verbal or written warning, performance improvement plan, loss of privileges or access rights, suspension, or termination of employment or contract.

## Adapt this to your context

- **Password policy (IAM-205/212)** follows current guidance favouring length over complexity and dropping mandatory periodic rotation. This is a considered, current best-practice position, but some older frameworks, specific auditors, or contractual requirements still expect periodic rotation. Check what actually applies to you before adopting this wholesale; don't assume every assessor has caught up to the same guidance.
- **MFA (IAM-202/210)**: regulated industries or government contexts may mandate phishing-resistant MFA specifically (not just "any MFA") for certain data classes or roles; confirm what your applicable framework actually requires versus what this standard treats as a "should."
- **Dormant accounts (IAM-109)**: the 90-day ceiling is a starting point; common baselines sit in the 45 to 90 day range. A dormant but enabled account is a standing takeover target for the whole window, so document the trade-off explicitly if you extend it.
- **Review cadences (IAM-300/301)**, 12 months for general access and 3 months for privileged access on critical systems, are a common baseline. Some frameworks or regulators mandate shorter cycles for specific data classes or sectors, so confirm what applies to you before relying on these defaults.
- **Customer federation (IAM-400 series)** only applies if you offer customer-facing federated authentication; skip that section entirely if you don't.
- **Size**: a solo operator can't always separate "who requests" from "who approves" from "who provisions" the way IAM-104/106 implies. Where roles can't be separated, document that explicitly and add a compensating control (e.g. a periodic external review of the log of self-approved changes) rather than silently ignoring the requirement.

**Frameworks referenced** (by family; check the current edition of whichever applies to you): NIST's digital identity guidelines (SP 800-63 series), the OWASP Password Storage Cheat Sheet, and ISO/IEC 27001:2022 Annex A's access-related controls.
