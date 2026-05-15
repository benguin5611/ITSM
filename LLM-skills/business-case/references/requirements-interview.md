# Requirements Interview Guide

Run these questions BEFORE any research. The goal is to surface every requirement — especially the ones the user hasn't thought to mention — before you invest time in vendor analysis.

---

## Universal Questions (Always Ask)

### Current State
1. What tools, services, or processes are in place today for this function?
2. What plan/tier/version of each? What does it cost annually?
3. How many people use each tool? Who specifically? (roles, not just headcount)
4. Are there external users (contractors, partners, customers) who access any of these?
5. What other systems integrate with or depend on the current setup?
6. Is anything running on a trial, free tier, or legacy plan that could change?

### Problem / Trigger
7. What prompted this decision now? (cost, compliance, incident, growth, contract renewal)
8. What's the consequence of doing nothing for 6 more months?
9. Is there a specific event or deadline driving the timeline?

### Decision Context
10. Who approves this decision? What do they care about most?
11. Is there a budget ceiling or a target cost range?
12. What's the most important factor when choosing between options that all meet requirements? (Rank: cost, simplicity, compliance, single vendor, feature depth, zero migration)
13. Has anyone already tried or evaluated any alternatives? What was the outcome?
14. Are there any options that are already off the table? Why?

### Hard Requirements (Must-Haves)
15. Walk me through the non-negotiable requirements. For each one:
    - What specifically would satisfy this? (Be concrete — not "audit logging" but "12 months of exportable logs showing who accessed what")
    - How would you verify it works?
    - Is this a current gap, or maintaining something that already works?

### Hidden Requirements (Probe For These)
16. Do any third-party services require you to allowlist specific IP addresses? (static egress)
17. Are there data residency or sovereignty requirements? (where data is stored/processed)
18. Do you need to support BYOD or unmanaged devices?
19. Are there compliance frameworks that apply? (ISO 27001, SOC 2, HIPAA, PCI-DSS, GDPR)
20. Is there a preferred deployment model? (SaaS, self-hosted, hybrid)
21. Do you need to integrate with a specific identity provider, MDM, or SIEM?
22. Are there any current tools/contracts that you're NOT willing to change?

### Nice-to-Haves
23. Beyond the must-haves, what would be ideal but not blocking?
24. Are any of these likely to become must-haves in the next 12 months?

---

## Domain-Specific Probes

Use these when the business case falls into a specific category. Don't ask all of them — pick the ones relevant to the domain.

### SaaS / Software Tooling
- How many seats/users at what growth rate?
- SSO requirements? Which protocol — OIDC, SAML, both?
- SCIM provisioning needed?
- API access required? For what?
- Data export / portability?
- What happens to data if you cancel?

### Network Security / Access
- What services need to be privately accessible? To whom?
- Do you need traffic inspection (SWG, DLP) or just encryption?
- VPN client conflicts — are users already running another VPN?
- Exit node / static egress IP requirements?
- DNS filtering — who handles it today?
- Mobile device support requirements? (iOS/Android VPN limitations)

### Infrastructure / Cloud
- Current cloud provider(s) and region(s)?
- IaC requirements? (Terraform, Helm, CloudFormation)
- CI/CD integration needs?
- Monitoring and alerting — what's in place?
- Disaster recovery / failover requirements?
- Expected traffic/load/storage scale?

### Process / Strategy
- Who is affected by the change? How many people?
- What's the current process cost? (labour hours, error rate, cycle time)
- What does success look like? How would you measure it?
- Are there change management considerations? (training, adoption)
- What's the rollback plan if the new approach doesn't work?

---

## After the Interview

Before proceeding to research:
1. Read back the requirements list (must-haves and nice-to-haves) and get explicit confirmation
2. Confirm the decision criteria ranking
3. Flag any requirements that seem under-specified and ask for clarification
4. Note any information you couldn't get and will need to research or estimate

**Never proceed with partial requirements and present the output as complete.** Always state what was confirmed and what was assumed.
