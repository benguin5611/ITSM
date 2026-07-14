---
Artefact type: Reference
Owner role: IT operator
Review cadence: Annual
Version: 1.0 (template)
---

# Vendor due diligence questionnaire

> Part of the [docs-kit](../README.md#before-you-rely-on-anything-here): a Department-of-One starting point, not a certified or audit-ready control out of the box. Read that disclaimer and this artefact's own "Adapt this to your context" section before relying on it.

The question set to send a prospective vendor before they touch your systems or data, grouped so you can send the whole thing to a Tier 1 supplier or lift out just the sections that matter for a lower-risk one. Companion to the [Software Onboarding & Vendor Due Diligence](../procedures/software-onboarding-and-vendor-due-diligence-procedure.md) procedure, which this questionnaire feeds into.

## Questionnaire

### 1. Company and security program overview
1. Legal company name, headquarters location, and any other jurisdictions in which you operate, store data, or employ staff who could access our data.
2. Give an overview of your information security program, including whether it aligns to a recognised standard or framework (e.g. ISO/IEC 27001, SOC 2, NIST CSF).
3. Is there a named individual or team responsible for information security?
4. Do you run regular (at least annual) risk assessments of your own environment?
5. Do you provide security awareness training to staff, and how often?

### 2. Data handling
6. What categories of our data will you access, process, or store (e.g. personal information, financial data, credentials, health data)?
7. Where is that data stored and processed? List the countries or regions involved, including any subprocessors' locations.
8. Is data encrypted at rest and in transit? Which standards or algorithms?
9. What is your data retention period, and how is data securely deleted at the end of it?
10. Do you operate a documented data classification scheme?

### 3. Access and authentication
11. Is access to systems containing our data restricted on a least-privilege basis?
12. Is multi-factor authentication enforced for administrative and remote access?
13. How often are user access rights reviewed, and by whom?
14. Do you maintain audit logs of access to sensitive systems and data? How long are they retained?

### 4. Subprocessors and supply chain
15. Do you use subprocessors or subcontractors who will have access to our data? If so, list them and their function.
16. How do you assess and monitor the security posture of your own subprocessors?
17. Will we be notified before a new subprocessor is introduced, and what is the notice period?

### 5. Incident history and response
18. Do you maintain a documented incident response plan?
19. Have you experienced a data breach or security incident in the past three years that resulted in unauthorised access to, loss of, or disclosure of customer data? If so, describe the incident, its impact, and the remediation.
20. What is your process and timeframe for notifying us if a security incident affects our data?

### 6. Business continuity and resilience
21. Do you maintain a documented business continuity / disaster recovery plan?
22. What are your target Recovery Time Objective (RTO) and Recovery Point Objective (RPO)?
23. When was this plan last tested, and what were the results?

### 7. Certifications and independent assurance
24. Do you hold any of the following, and can you provide the current certificate or report: ISO/IEC 27001, SOC 2 (Type I or II), PCI DSS, or an equivalent?
25. If you don't hold a formal certification, would you be able to provide compensating evidence instead: a penetration test summary, relevant policy extracts, or a completed version of this questionnaire?
26. Do you carry cyber insurance, and if so, at what level of coverage?

## Adapt this to your context

- **Scale depth to risk tier.** A vendor handling regulated or high-sensitivity data warrants every section above, in full, before onboarding. A low-risk vendor with no access to your data or systems may only need sections 1 and 7. Don't run the full set identically for every vendor regardless of what they actually touch.
- **Layer on sector-specific questions.** Regulated industries (financial services, health, government) commonly carry additional mandatory vendor-assessment obligations (prudential rules on material service providers, health-data handling requirements, payment-card scope) that this generic list doesn't cover. Add to it, don't assume it's complete.
- **Treat "no certification" as an opening for compensating evidence.** Plenty of legitimate smaller vendors haven't yet invested in a formal certification. Ask for compensating evidence before declining to work with them on that basis alone.

**Frameworks referenced**: ISO/IEC 27001, SOC 2, PCI DSS, NIST Cybersecurity Framework
