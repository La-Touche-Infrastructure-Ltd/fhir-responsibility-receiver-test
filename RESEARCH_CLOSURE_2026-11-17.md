# Research closure record — 17 November 2026

**Disposition:** This bounded synthetic FHIR R4 receiver-evidence investigation is closed as a research exercise. Closure does not establish that the underlying clinical or cross-organisation questions have been solved, and does not certify interoperability.

## Question examined

What can a receiver establish about expected diagnostic reports from the FHIR R4 records visible to it, and what must remain unknown when the expected set or observation scope is incomplete?

## Evidence reviewed

- [Original protocol](TEST_PROTOCOL.md), [findings](FINDINGS.md), [three synthetic fixtures](fixtures), [receiver logic](receiver.py), and [external synthetic expectation assumptions](receiver-policy.json).
- [FHIR-native comparison](comparison/COMPARISON.md), including parent/child Task alternatives and negative controls.
- [Dated validation record](comparison/VALIDATION_RECORD_2026-11-12.md): GitHub Actions [run #43212857975](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/actions/runs/43212857975) reports six synthetic Bundles checked using HL7 FHIR Java validator v7.0.5 against R4 core 4.0.1: zero errors/fatals, 47 narrative warnings and eight informational messages; 10 baseline and eight comparison study-local tests passed. This is a recorded run, not a fresh independent rerun for this closure.
- Public FHIR implementers discussion considered the distinction between filler-side Task completion and placer-side sufficiency decisions, existing FHIR request/report linkage and parent/child Task modelling, and the operational prevalence of HL7 v2 for laboratory order/result exchanges. A participant described established EHR/LIS matching and, in some configurations, analyst workqueues for matching failures; other configurations may process mismatches as unsolicited results. These are participant descriptions, not an independently audited implementation or measured prevalence study.

## Supported findings

1. FHIR R4 offers existing representations for request grouping, Task focus and hierarchy, and report-to-request linkage. The synthetic receiver can compare visible final reports against an explicitly supplied expected-request list.
2. A completed Task does **not**, by itself, establish that every expected report is visible, that a placer has accepted fulfillment as sufficient, or that clinical work was adequate.
3. In the synthetic examples, missing evidence means **not evidenced in the examined snapshot**, not that a report was never produced or care was not performed.
4. Parent/child modelling reproduced the same three bounded receiver classifications **under the same external expectation-policy assumptions**. This does not independently authenticate the policy or demonstrate independent interoperability.
5. Existing clinical integrations already perform substantial order/result reconciliation and can handle matching exceptions. This exercise therefore does not demonstrate an absence of exception detection or operational handling.

## Not established / unresolved

- Whether an applicable clinical implementation guide, exchange agreement, authorised manifest or query/search contract already establishes the exhaustive expected-report boundary in a particular deployment.
- Whether a specific clinical workqueue exposes assignment, corrective action, audit trail, closure authority and supporting evidence to a separately authorised receiver.
- Independent receiver implementation; live LIS–EHR exchange; named clinical implementation-guide conformance; complete terminology validation; authenticated provenance or delegated authority; clinical adequacy or patient-safety outcome.
- A missing HL7, IHE or NHS interoperability requirement, or a need for any new standard.

## Closure rationale and limits

The original question has been examined sufficiently to reach a **bounded negative finding**: this study has **not demonstrated a standards gap**. The available evidence does not justify extending the current synthetic test into a claim about clinical operations or introducing a new protocol. Unresolved questions remain unresolved rather than being treated as absent capabilities.

The existing code, fixtures, policy, test protocol, outputs and validation record are preserved unchanged as a reproducible research record. No further testing or third-party review is represented as completed by this closure. A future investigation would require a separately scoped operational use case, documented baseline mechanisms, agreed evidence access and independent assessment.

**Research issue disposition:** Close [Issue #1](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1) as **not planned / bounded research concluded**, not as acceptance that every issue checklist item was completed. Contributions and corrections remain historically attributable; closure implies no endorsement by named participants or standards organisations.
