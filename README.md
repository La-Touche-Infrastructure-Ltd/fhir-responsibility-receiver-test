# Expected laboratory report evidence — synthetic FHIR R4 receiver test

A small, **synthetic and independently inspectable** research exercise examining what a receiving system can establish from FHIR R4 diagnostic workflow records.

**Status (13 November 2026):** exploratory, synthetic research. The 12 November comparison run reports **zero errors/fatals in official FHIR R4 core 4.0.1 validation across six synthetic Bundles**, with **47 narrative warnings and eight informational messages**, and **18/18 study-local tests passing** (10 baseline plus 8 comparison). No clinical implementation-guide validation, independent receiver implementation, live LIS–EHR exchange or clinical interoperability test has been completed. These results do **not** establish HL7, IHE or NHS conformance, completeness of real clinical results, or endorsement. See the [dated validation record](comparison/VALIDATION_RECORD_2026-11-12.md).

## The clinical-operational question comes first

**One problem:** A clinician places a laboratory order. At a defined review point, the ordering EHR needs to distinguish an expected **final** result report that is present and linked to that order from a report that is not evidenced in the receiver-visible records. The EHR must also be able to retain **unknown** when the expected-report set or order linkage is incomplete.

**One bounded question:** For one clinician-initiated ordering episode, can the receiving EHR determine, from a defined snapshot and an explicitly stated expected-report list, which expected final reports are present and correctly linked to the clinician's order?

**One measurable synthetic test:** Compare the agreed expected report identifiers with final, order-linked reports visible at a specified observation point. Report (1) expected report not evidenced in the snapshot, (2) all reports on an agreed exhaustive list evidenced in the snapshot, or (3) known reports evidenced but the wider expected set unknown. These are **evidence states**, not claims that a test was never performed, a message was never sent, or care was completed.

**Explicit exclusions:** This first question does not measure turnaround time, whether the clinician viewed or acted on the report, clinical adequacy, placer acceptance of fulfilment, or preliminary-to-final/amended-report transitions. Unsolicited or reflex results are a separate follow-up scenario, not presumed to belong to the original clinician order.

**Technology boundary:** The implementers discussion identified existing laboratory HL7 v2 interfaces as the practical setting for the operational question. This repository does **not** inspect a live HL7 v2 exchange. Its FHIR R4 `ServiceRequest`, `DiagnosticReport` and `Task` examples are **synthetic representations used to compare evidence rules**, not claims that LIS–EHR result delivery currently uses FHIR Task. FHIR modelling is secondary to the operational question.

*Research framing clarified on 13 November 2026 after implementer feedback. The frozen synthetic fixtures, original tests and dated validation results are unchanged.*

## Official R4 core validation and comparison (12 November 2026)

- The **original three synthetic Bundles** and **three generated parent/child Task alternatives** were run through the official HL7 Java validator **v7.0.5**, against **FHIR R4 core 4.0.1**, with **zero errors/fatals** and **47 documented `dom-6` narrative warnings**. No applicable clinical implementation-guide profiles or terminology server were evaluated.
- The **10 original** and **8 additional comparison** local tests passed. The comparison does not establish independent interoperability or actual clinical completeness.
- Read the [dated validation record](comparison/VALIDATION_RECORD_2026-11-12.md), [FHIR-native comparison](comparison/COMPARISON.md), and [independent reproduction invitation](comparison/INDEPENDENT_RECEIVER_INVITATION.md).
- Existing standards support grouping requests and parent/child Tasks; whether the receiver can establish an **exhaustive expected set** from what is exchanged remains an open, implementation-dependent research question. [Contribute a correction or counterexample in Issue #1](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1).

## What the synthetic FHIR comparison tests

The FHIR R4 examples test a **narrower modelling issue**: when a synthetic `Task` records `completed`, can a receiver distinguish that reported workflow state from the evidence of final `DiagnosticReport` resources linked to an **explicitly agreed** set of `ServiceRequest` identifiers?

The receiver's expected-set assumption comes from the synthetic external `receiver-policy.json`. It is **not** a claim that a real EHR, LIS, FHIR resource or implementation guide supplies an authoritative exhaustive list automatically.

A `Task` completion flag is not treated as proof of result delivery, clinical adequacy, clinician acknowledgement or the ordering party's acceptance of fulfilment. Whether a particular real-world interface already provides adequate reconciliation and expectation boundaries remains untested. This exercise does not demonstrate a deficiency in FHIR, HL7 v2, IHE or any deployed system.

## Run the existing v0.2 experiment

Requires Python 3.9+ with the standard library.

```bash
python build_fixtures.py
python structural_checks.py
python receiver.py
```

Three synthetic scenarios are included: one expected report missing from the receiver's snapshot, both expected reports present, and an unknown wider expectation set. The study's `receiver-policy.json` supplies an *external, synthetic assumption* about the scope of expected requests; **FHIR does not automatically attest the completeness of this list**.

See [test protocol](TEST_PROTOCOL.md), [recorded findings](FINDINGS.md), [fixtures](fixtures), [receiver code](receiver.py) and [local results](results.json). A local `Task.output` + `DiagnosticReport.basedOn` matching requirement is a **study choice**, not a universal FHIR rule.

## Open technical challenge

**[Issue #1 — FHIR-native expectation boundaries](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1)** records modelling alternatives suggested during a public FHIR implementers discussion, including parent/child Tasks, request grouping and FHIR-native ways to express expected work. It also asks where an exchange agreement is still needed.

Implementers are invited to **correct resource modelling, point to existing standards/IGs, reproduce the tests or provide counterexamples**. Contributions that demonstrate existing FHIR mechanisms are sufficient are welcome.

The issue records community feedback, **not** independent review, approval, endorsement or participation commitments by the contributors.

## Scope and provenance

All subjects, services and organisations in the fixtures are fictional. The work tests **evidence sufficiency in a receiver-visible snapshot**, not a clinical workflow system. It does not replace FHIR, assert a standards gap or provide a certified interoperability implementation.

See [FINDINGS.md](FINDINGS.md) for specific limits, sources and open validation requirements. No open-source licence is currently granted for reuse outside applicable legal exceptions; opening an issue to discuss a modelling correction does not require an implementation licence.
