# PCC-57 / Diagnostic Ordering: Independent Receiver Evidence Test

**La Touche Infrastructure Ltd — exploratory research note, 10 November 2026**  
**Status: v0.2 synthetic test pack / preliminary local execution — NOT FHIR or IG conformance validated**

## Executive finding

A `Task.status = completed` is a **reported workflow status**. In a complete, explicitly scoped receiver-visible dataset, separately ordered diagnostic examinations can be compared with linked final `DiagnosticReport` resources. When an expected report is not present, a receiver can state **"insufficient evidence in the examined dataset"** without concluding that care was not performed. This inference requires a defined expectation set, correlation rules, visibility assumptions and a receiver policy. It does **not**, on its own, demonstrate a gap in FHIR/IHE standards.

## What is established in existing work

* **Kevin Mayfield's PatientCareCoordination proof of concept:** PCC-55 distinguishes referral accept/decline (the recipient accepts responsibility for service). PCC-57 models a `completed` referral `Task` and an associated referral outcome document, with order linkage through `Task.output`, `Task.basedOn`, etc. The project explicitly says that it is a proof of concept, not authoritative NHS, IHE or HL7 guidance.
* **FHIR R4:** `DiagnosticReport.basedOn` can reference a `ServiceRequest`; `Task.output.valueReference` can reference results; `Task.basedOn` can reference multiple orders. `ServiceRequest.requisition` links a group of distinct procedure requests. FHIR R4 `ServiceRequest` represents a single procedure per resource; hence this pack uses two requests for A and B.
* **Diagnostic-specific workflow:** Kevin's diagnostics page maps laboratory results to LAB-3 and imaging results to RAD-128. PCC-57 is a *referral outcome* concept; this experiment is a **diagnostic-order/report analogue**, not an assertion that PCC-57 governs all laboratory/imaging tests.
* **Authority/provenance:** FHIR R4 provides `Provenance` and signatures and `ServiceRequest.requester`. The test **does not** attempt to verify actual authority or trustworthiness; it must not be marketed as evidence that FHIR lacks those capabilities.

## Represented synthetic evidence

The test packages each case as a FHIR R4 `Bundle` (`type=collection`) with synthetic Patient, requesting and receiving organizations, ServiceRequest(s), one Task marked `completed`, and DiagnosticReport(s) marked `final`. Each report links to its own order (`DiagnosticReport.basedOn`) and is referenced in `Task.output.valueReference`. The Task links to the ordered requests through `Task.basedOn`. All references use resolvable `urn:uuid` fullUrls. There is **no real patient data**.

**Critical distinction:** The test also supplies `receiver-policy.json`, an explicit **external reliance assumption** stating whether the visible request set is agreed to be exhaustive. This is NOT a claim that FHIR encodes that fact by default. A receiving system cannot presume a globally complete obligation set from a bundle alone.

| Case | Sender claim | Known expectations | Available final, linked reports | Local receiver decision |
|---|---|---|---|---|
| 1 — B not seen | Task `completed` | A, B (agreed exhaustive) | A only | `INSUFFICIENT_REPORT_EVIDENCE`: B not evidenced in the snapshot |
| 2 — A and B present | Task `completed` | A, B (agreed exhaustive) | A and B | `ALL_AGREED_EXPECTED_REPORTS_PRESENT_IN_SNAPSHOT` |
| 3 — only A known | Task `completed` | A (extent unknown) | A | `ALL_KNOWN_REPORTS_PRESENT_SCOPE_UNKNOWN` |

### What the decisions mean — and do not mean

* The receiver can reconcile **linked, locally visible, final report records** with **the known expectation set**.
* `INSUFFICIENT_REPORT_EVIDENCE` is not proof that B was never produced, transmitted, read, performed, clinically authorised, or stored elsewhere.
* `ALL_AGREED_EXPECTED_REPORTS_PRESENT_IN_SNAPSHOT` means the **agreed list** was accounted for in the examined snapshot under the test's linkage rule, not proof of clinical quality, immutable evidence, legal authority, or the absence of other obligations.
* The task completion claim alone neither establishes report delivery nor proves that all contractually required reports have arrived.
* A status `final` is itself an assertion recorded in FHIR, not independent verification of the issuer's clinical credentials or legal authority.
* The local receiver requires both a final `DiagnosticReport.basedOn` match and a corresponding `Task.output` link. This is a **test-specific stricter policy**, not a universal HL7 FHIR R4 requirement.

## Execution and validation record

**Completed locally:**

1. Generated and JSON-parsed 3 deterministic synthetic FHIR R4-shaped bundles.
2. Checked a deliberately limited subset of R4 required fields, known type/status values, bundle UUID identities, uniqueness and internal reference resolution.
3. Ran a dependency-free Python receiver over the three cases and compared outputs to expected states.
4. Ran 10 automated structural/behavioural unit tests in v0.2, including deliberate missing-link, non-final-report, wrong-link, absent-request and omitted Task-order-link mutations — all passed on 10 November 2026. The prior v0.1 pack had 8 local tests.

**Not completed / must not be implied:**

* Official HL7 Java FHIR validator execution against `hl7.fhir.r4.core#4.0.1`.
* Validation against Kevin's project-generated profiles/StructureDefinitions or a published NHS UK Core profile.
* Independent receiver implementation by a second party, FHIR messaging/REST round trip or a real clinical deployment.
* Identity, role/authority, signatures, provenance-chain, authenticity or clinical-safety verification.
* Completeness of the receiver's real-world query/search environment, including pagination, report revisions, non-final and retracted reports, delayed delivery and data sharing restrictions.

**Reason:** official FHIR validation packages / a conformant validator were not available in the execution environment; installing them via package services was unavailable. The pack is **syntactically valid JSON with local consistency checks, not an officially validated FHIR implementation**.

## Remaining research questions for Kevin (no assumption of a gap)

1. For separate diagnostic `ServiceRequest`s linked to one requisition, which existing IHE/HL7 pattern should indicate that the receiving system has the **full, authoritative set of expected results**? Is a shared requisition identifier plus task references sufficient under the applicable workflow profile, or must an exchange agreement establish this independently?
2. Which profile(s) or workflow rules require matching final reports before a consuming system treats the overall examination group as complete? How do LAB-3, RAD-128 and PCC-57 differ?
3. What should a receiver conclude when a `Task` or order indicates completion, but a report is temporarily inaccessible or delayed? Which defined negative/incomplete/unknown states already exist in the profiles?
4. What should be required for relying-party acceptance of authority and sign-off? Compare existing FHIR `Provenance`, `Signature`, audit mechanisms and relevant IHE profiles before proposing any extension.

**Narrowest defensible proposal:** a cross-system **receiver decision procedure / evidence sufficiency test** applied to already-standard resource fields and known obligations. Do not propose new information models unless research identifies a genuine absence.

## Sources inspected (working research links)

* Kevin: https://github.com/KevinMayfield/PatientCareCoordination/blob/main/input/pagecontent/PCC-55.md
* Kevin: https://github.com/KevinMayfield/PatientCareCoordination/blob/main/input/pagecontent/PCC-57.md
* Kevin: https://github.com/KevinMayfield/PatientCareCoordination/blob/main/input/pagecontent/NHSEnglandDiagnostics.md
* Kevin: https://github.com/KevinMayfield/PatientCareCoordination/blob/main/input/pagecontent/Reports.md
* Kevin's issue: https://github.com/KevinMayfield/PatientCareCoordination/issues/1
* HL7 R4 Task: https://www.hl7.org/fhir/R4/task.html
* HL7 R4 ServiceRequest: https://www.hl7.org/fhir/R4/servicerequest.html
* HL7 R4 ServiceRequest requisition: https://hl7.org/fhir/R4/servicerequest-definitions.html
* HL7 R4 DiagnosticReport: https://hl7.org/fhir/R4/diagnosticreport.html
* HL7 R4 Provenance: https://hl7.org/fhir/R4/provenance.html
* HL7 validator information: https://www.hl7.org/fhir/validator/
