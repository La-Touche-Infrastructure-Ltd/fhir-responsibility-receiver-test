# FHIR-native receiver comparison — working technical note

**Scope:** synthetic R4 4.0.1 input; test of receiver-visible evidence only. **This is not a healthcare implementation guide, approved standard, or conformance certification.**

## Motivation

The public FHIR implementers discussion highlighted existing mechanisms worth testing: separately ordered `ServiceRequest`s grouped through `requisition`, `Task.partOf` parent/child coordination, the distinction between `Task.focus` and `Task.basedOn`, and conditional use of `Task.restriction.repetitions`.

The research asks what a receiver **can demonstrate from evidence actually received**, rather than whether a status or group identifier proves an entire workflow complete.

## Comparators

| Mechanism | Exists in R4? | What it conveys | What it does not automatically establish |
| --- | --- | --- | --- |
| `ServiceRequest.requisition` | Yes | Association of multiple distinct requests under a shared identifier | That all requests in the group are visible to the receiver |
| `DiagnosticReport.basedOn` | Yes | A report's linkage to request(s) | Complete delivery of all required reports, clinical adequacy, or absence of unseen requests |
| `Task.focus` | Yes | What a Task is actioning (one focus per Task) | An authoritative, exhaustive list of all tasks or requests |
| `Task.partOf` | Yes | Child Task membership in parent Task(s) | That every child exists in the receiving snapshot or that the placer accepted the result |
| `Task.status=completed` | Yes | Recorded completion state for that Task | Evidence that every report arrived or a ServiceRequest was accepted as sufficient |
| `Task.restriction.repetitions` | Yes, conditional | Number of times the **requested action** should occur when the Task seeks fulfillment | Number of DiagnosticReport resources, by itself; excluded as a report-count proxy |
| External `receiver-policy.json` | **No (study-local)** | An explicitly asserted complete/partial expected-set boundary | Real-world authority or truth of the underlying agreement |

## Existing baseline

The v0.2 baseline uses distinct active `ServiceRequest`s with shared `requisition`, a synthetic aggregate Task with `basedOn` links, and report links. The baseline receiver also reads the **separate, fictional** `receiver-policy.json` to learn whether expectations are declared exhaustive.

**Open modelling correction:** R4 describes `Task.focus` as the request being actioned and `Task.basedOn` as the higher-level authorization. That may make the baseline single Task-with-multiple-`basedOn` representation unsuitable for an actual fulfillment Task. The baseline remains frozen so comparisons are traceable; the alternatives use `Task.focus` for each request.

## Parent/child alternative

`comparison/build_parent_child.py` derives a corresponding Bundle per case without changing the original fixtures. It keeps the same requests and reports but places one **synthetic completed child Task per visible ServiceRequest**, where:

- each child Task has `focus` on that request;
- each child references the parent via `partOf`;
- any visible final report is linked through the child's `output` as well as `DiagnosticReport.basedOn`;
- the parent Task remains `completed` as a **reported aggregate status**; this does not prove exhaustive children or placer acceptance.

The alternative does not assert that completed child Tasks prove delivery or adequate care. Task and ServiceRequest are not conflated.

## Three scenarios and source-bounded expected interpretation

| Case | Known expected set (external study assumption) | Reports in snapshot | Receiver's bounded reading |
| --- | --- | --- | --- |
| A: missing B | {A,B}, declared exhaustive | A | B not evidenced in the observed snapshot |
| B: both seen | {A,B}, declared exhaustive | A,B | Both agreed reports evidenced **in snapshot** |
| C: scope unknown | {A}, explicitly non-exhaustive | A | Known A evidenced; wider completeness **unknown** |

Even a perfect set of FHIR-native references cannot prove that there are no requests outside the material the receiver was allowed to see. That may be resolved by query coverage, authoritatively supplied resource scope, suitable profiles/IGs or implementation agreements; the experiment does **not** determine which is required in a real deployment.

## Reproduce

Run from repository root, Python 3.9+, standard library:

~~~bash
python build_fixtures.py
python structural_checks.py
python receiver.py
python comparison/build_parent_child.py
python comparison/compare_receivers.py
python comparison/test_comparison.py
~~~

The comparison script checks that the three study-local receiver states match the original baseline when the **same external policy assumptions** are supplied. Negative controls alter expected-set exhaustiveness, remove a child Task or report, and change a report away from `final`. Results are generated at `comparison/comparison-results.json` and should be treated as **local calculations**, not proof of actual cross-system interoperability.

## Official validation plan and limits

The CI workflow attempts to run the official HL7 FHIR Java CLI validator **v7.0.5** against **R4 core 4.0.1** on original and generated JSON Bundles and saves machine-readable `OperationOutcome` files.

- The FHIR R4 *core* check is not validation against a named clinical implementation guide. IHE LAB-3, RAD-128, applicable NHS/UK Core IGs and business workflow agreements have not been formally evaluated in this synthetic test.
- Any validator warnings/errors must be recorded and addressed or retained explicitly; **passing local unit tests is not an HL7 validator pass**.
- A successful validator run does not establish an independent implementation, real-world transport interoperability, provenance reliability, legal authority, clinical safety or evidence of a standards gap.
- At initial publication of this note, **official validator outcomes were pending**. Later CI artifacts, not this sentence, are the record of what actually ran.

## Contribution request

Technical corrections and existing profile references are welcome, including evidence that **FHIR already solves** a proposed issue. Independent implementers can reproduce the examples without La Touche tooling and provide their own source-bounded readings. See [independent reproduction invitation](INDEPENDENT_RECEIVER_INVITATION.md) and [Issue #1](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1).

Reference definitions: [Task](https://hl7.org/fhir/R4/task-definitions.html), [ServiceRequest](https://hl7.org/fhir/R4/servicerequest-definitions.html), [DiagnosticReport](https://hl7.org/fhir/R4/diagnosticreport-definitions.html), [Provenance](https://hl7.org/fhir/R4/provenance-definitions.html).
