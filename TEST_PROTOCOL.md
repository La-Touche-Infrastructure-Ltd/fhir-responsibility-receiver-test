# Synthetic FHIR R4 Receiver Test — Reproduction Protocol (v0.2)

**La Touche Infrastructure Ltd · 10 November 2026 · Synthetic research only**

This independently inspectable **study-local** exercise compares a sender's completed Task with receiver-visible final diagnostic reports and a *separately agreed* list of expected ServiceRequest identifiers. It does **not** establish a missing requirement in FHIR, HL7, IHE, NHS UK Core or Kevin Mayfield's PatientCareCoordination proof of concept.

## Source and relation to PCC-57

The motivating conversation is [PatientCareCoordination Issue #1](https://github.com/KevinMayfield/PatientCareCoordination/issues/1). Kevin's [PCC-55](https://github.com/KevinMayfield/PatientCareCoordination/blob/main/input/pagecontent/PCC-55.md) addresses referral acceptance; [PCC-57](https://github.com/KevinMayfield/PatientCareCoordination/blob/main/input/pagecontent/PCC-57.md) addresses referral outcomes. The example below is a **diagnostic-order/report analogue**, not an assertion that PCC-57 governs all diagnostic orders. See [FINDINGS.md](FINDINGS.md) for the comparison and limitations.

## Three synthetic cases

| Fixture | Agreed requests | Receiver-visible final reports | Study-local result |
| --- | --- | --- | --- |
| `case1_missing_B` | A, B; exhaustive by external agreement | A | B not evidenced in snapshot |
| `case2_both_received` | A, B; exhaustive by external agreement | A, B | Agreed reports accounted for in snapshot |
| `case3_only_A_known` | A; extent explicitly unknown | A | A evidenced; wider obligations unknown |

An absent report is **not proof that a test was not performed**. A `Task.status=completed` is a recorded assertion, not independent proof of clinical completion or authority.

## Reproduce locally

Requires **Python 3.9+**, standard library only, no network or personal data:

```bash
python build_fixtures.py
python structural_checks.py
python receiver.py
```

For Linux/macOS, you may need `python3` instead of `python`.

The local structural/mutation test suite contains **10 tests**. All passed in the author's local environment on 10 November 2026. The receiver creates `results.json`; compare it with the checked-in output. `SHA256SUMS.txt` lists the checked-in publication files by relative path (use `sha256sum -c SHA256SUMS.txt` on a compatible system). Re-running `receiver.py` should reproduce the committed results.

The **v0.2 correction** makes the receiver use the explicitly declared `expected_service_requests` in `receiver-policy.json`, rather than inferring the complete obligation list from the requests present in a single Bundle. Two new regression tests cover absent request resources and missing Task order linkage. This supersedes the original v0.1 local suite of eight checks without changing the underlying three scenarios.

## Formal validation and interpretation limits

* Files are FHIR R4-shaped JSON and pass **study-local, deliberately incomplete structural/reference checks**. They have **not** been tested with the official HL7 FHIR Java validator against core R4 4.0.1 or relevant profile packages.
* No independent second receiver or FHIR messaging/REST round trip has been run. This is **not** an interoperability conformance report.
* The test requires both a `DiagnosticReport.basedOn` link to the expected request and a matching `Task.output` reference (and now requires that request in `Task.basedOn`). This is a chosen **local rule**, **not** a universal FHIR rule.
* The separate policy declares whether the receiver has an exhaustive expectation set. The FHIR Bundle alone does not establish that fact. Whether an existing relevant workflow profile supplies it is an **open question**.
* No real patient information, authority verification, signatures, provenance-chain validation or clinical safety assurance is included. The synthetic institution names, identifiers and observations are fictional.
* This repository is not affiliated with, approved by or endorsed by NHS England, HL7, IHE or Kevin Mayfield. The cited PatientCareCoordination guide identifies itself as a demonstration only.
* Only this standalone, synthetic test code and data are published. No RIIP gateway implementation, secret, customer record or private research is included. **No open-source licence is granted by this repository unless one is added explicitly.** Third-party rights and trademarks remain with their respective owners.

## Research question

**What existing standards, profiles or inter-organisation agreements define the authoritative *expectation boundary* and the receiving system's evidence-sufficiency decision before relying on a workflow-completion claim?**

Questions or corrections welcome via GitHub issues. Findings are provisional and may be revised after formal validation and external review.
