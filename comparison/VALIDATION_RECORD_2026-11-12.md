# Official HL7 FHIR R4 validation record — 12 November 2026

**Status: Six synthetic Bundles examined with official HL7 FHIR Java validator v7.0.5, against R4 core package `hl7.fhir.r4.core#4.0.1`. Zero errors/fatals; warnings remain.**

## Verifiable execution evidence

- [GitHub Actions run #43212857975](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/actions/runs/43212857975) — completed successfully on 12 Nov 2026.
- [Validator logs, machine-readable OperationOutcome outputs and comparison results (run artifact)](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/actions/runs/43212857975/artifacts/13941682993). Artifacts can expire; the run/commit is the evidence locator.
- HL7 FHIR Java CLI release: `7.0.5` ([upstream release](https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/7.0.5)).
- Pinned JAR digest: `sha256:9dfe9f305b0f9389eceade2a4a1c9a2740d7b0e614066fdf07a78b571c76d92f`.
- Core version: `-version 4.0.1`; terminology server disabled via `-tx n/a`. Neither a full terminology validation nor any named NHS/IHE IG profile was assessed.
- Both original v0.2 and proposed parent/child Task alternatives validated as core FHIR R4-shaped resources, not as clinically deployed or conformant to a health-system workflow profile.

| Fixture | Errors/fatal | Warnings | Information |
| --- | ---: | ---: | ---: |
| Original A: B not seen | 0 | 7 | 1 |
| Original B: A/B seen | 0 | 8 | 2 |
| Original C: outer scope unknown | 0 | 6 | 1 |
| Parent/child A | 0 | 9 | 1 |
| Parent/child B | 0 | 10 | 2 |
| Parent/child C | 0 | 7 | 1 |
| **Total** | **0** | **47** | **8** |

**All 47 warnings are the FHIR `dom-6` best-practice recommendation that resources should have a human-readable narrative.** The warnings remain open; zero-error core validation should not be represented as a zero-warning or full conformance result.

## Local regression and comparison (same CI run)

- 10 existing behavioural/structural tests passed.
- 8 new parent/child comparison tests passed.
- All three source-bounded receiver result states matched the original v0.2 result **when using exactly the same external receiver-policy assumption**.
- Negative controls showed that a completed parent Task does not establish an absent report or child, and the presence of grouping identifiers does not itself prove the exhaustive expected set.

## Supported conclusion and limitations

FHIR R4 **already provides** request grouping, individual Task focus, Task parent-child references and report-to-request linking. A second system can interpret observed statuses and linked resources according to agreed rules. These local fixtures also demonstrate why a receiver should not treat `Task.status=completed` as proof that every expected report was received.

This experiment **does not prove a gap** in FHIR or IHE, nor a need for a new standard: the external policy supplies an exhaustiveness assertion by design; whether an actual FHIR/IHE implementation guide, query contract, authoritative exchange manifest or other implementation agreement can establish that boundary has not yet been resolved.

Not demonstrated: a separate independent implementation, a real FHIR REST/message exchange, search completeness, identity and delegated-authority proof, authenticated provenance, report clinical adequacy, IHE LAB-3/RAD-128 conformance, NHS UK Core conformance or institutional endorsement.

**Open next review:** have an unrelated implementer inspect the R4 modelling and attempt a separate receiver implementation; record corrections and any alternative that does not require the external synthetic policy. See [Issue #1](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1).
