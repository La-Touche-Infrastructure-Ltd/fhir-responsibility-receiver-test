# FHIR R4 receiver evidence test

A small, **synthetic and independently inspectable** research exercise examining what a receiving system can establish from FHIR R4 diagnostic workflow records.

**Status:** exploratory. The author reports 10 local structural/behavioural tests passing. The fixtures have **not** passed the official HL7 R4 validator or relevant implementation-guide validation, and **no independent receiver or clinical interoperability test** has been completed. The experiment is not an HL7, IHE or NHS conformance claim or endorsement.

## Official R4 core validation and comparison (12 November 2026)

- The **original three synthetic Bundles** and **three generated parent/child Task alternatives** were run through the official HL7 Java validator **v7.0.5**, against **FHIR R4 core 4.0.1**, with **zero errors/fatals** and **47 documented `dom-6` narrative warnings**. No applicable clinical implementation-guide profiles or terminology server were evaluated.
- The **10 original** and **8 additional comparison** local tests passed. The comparison does not establish independent interoperability or actual clinical completeness.
- Read the [dated validation record](comparison/VALIDATION_RECORD_2026-11-12.md), [FHIR-native comparison](comparison/COMPARISON.md), and [independent reproduction invitation](comparison/INDEPENDENT_RECEIVER_INVITATION.md).
- Existing standards support grouping requests and parent/child Tasks; whether the receiver can establish an **exhaustive expected set** from what is exchanged remains an open, implementation-dependent research question. [Contribute a correction or counterexample in Issue #1](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1).

## The research question

A sender may mark a `Task` completed even when the receiving system cannot establish that it has **every expected diagnostic report**.

Can a receiver use existing FHIR R4 resources, applicable implementation guides and/or a specified inter-organisational agreement to determine:

- What reports it has evidence of receiving?
- Whether the set of expected requests is known to be exhaustive?
- Whether completion is only **reported**, or independently **supported within an agreed scope**?
- What remains unknown when the exchange or search coverage is incomplete?

No conclusion about clinical adequacy, authority, unseen obligations or real-world completion is inferred from a status or an absent record alone.

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
