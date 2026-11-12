# Independent reproduction invitation — FHIR R4 synthetic receiver test

The research team welcomes technical corrections and **independent reproduction** of synthetic R4 receiver examples. The aim is to compare what a receiver can establish from Task, ServiceRequest and DiagnosticReport references with the **stated boundary of known expectations**.

**No real patient records, confidential code, commercial agreement or product purchase is required.** This is an open technical exercise, not an invitation to endorse a product, join a standards body or provide free ongoing consultancy.

## Minimum contribution (optional)

1. Inspect the three synthetic input cases and the [method](../TEST_PROTOCOL.md). Validate the resources against core R4 4.0.1 and, if relevant, a specific existing IG; record tools/versions and warnings.
2. Independently interpret the received data: reported Task status, known expected requests, final reports actually evidenced, and missing/unknown states. If producing an independent implementation, use your own code rather than importing the study's receiver function.
3. Explain whether a complete expectation set is established from the FHIR data alone, from a **separately asserted policy/agreement**, or remains unestablished. Include counterexamples and alternative FHIR-native patterns.
4. Share the interpretation or technical correction on [Issue #1](https://github.com/La-Touche-Infrastructure-Ltd/fhir-responsibility-receiver-test/issues/1), stating your own scope, prior exposure to the reference outputs, and any relevant interests.

**Independence wording:** the expected outputs are published in the repository, so this is a **non-blinded public reproduction by default**. Nobody should claim blinded review or independent validation unless a separately controlled test and documented access record establish those conditions.

## What a successful contribution looks like

One corrected FHIR reference, an official validation log, a reproducible counterexample, a separate receiver implementation, or a source-backed relevant IG can be useful. Full legal authority, clinical adequacy and exhaustive obligations must not be inferred from fields that do not establish them.

Contributors retain rights in their materials. Please do **not** upload patient records, proprietary implementations, secrets or unpublished third-party documents; request permission before sharing another party's source material. Participation or technical correction does not imply HL7, IHE, NHS or other institutional approval.
