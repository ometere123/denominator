# Consensus design and equivalence rules

The two nondeterministic operations are isolated in `_agreed_manifest` and `_agreed_case`. No external read or model invocation can mutate contract storage directly. The production source uses the stable GenVM `run_nondet_unsafe` boundary; deterministic storage writes happen only after its validator callback returns true.

## Census binding

A study author chooses a public census URL **before** the observation start. `seal_census` is the only operation that can enumerate members. The leader fetches its HTTP body, parses a strict `denominator-census/v1` JSON document, rejects duplicate/malformed identifiers and disallowed URLs, normalizes entries by `id`, and returns the canonical JSON string and Keccak digest. Each validator independently fetches the **same URL** and verifies the entire canonical string and digest. Only after accepted consensus does the deterministic contract create members. No caller-provided subset can replace this set. The index must remain byte-structure-equivalent at finalization; any changed URL/ID/count produces `CENSUS_DRIFTED` with no certificate. Raw duplicate JSON object keys are rejected before normalization, so parser “last key wins” behavior cannot silently redefine `closed`, `declared_total`, or a member URL. A failed final census fetch is an availability/consensus failure and is not relabelled as drift.

## Case classification

`observe_case` takes a case ID from the on-chain sealed cohort. A validator is not allowed to trust the leader's class. Each independently fetches the case URL, requires a page containing the member's exact ID, runs the frozen semantic rubric, and compares the class and source digest.

| Code | Meaning | Counting effect |
| --- | --- | --- |
| `EXCLUDED` | positive source proof that case violates frozen eligibility | excluded, never denominator |
| `SUCCESS` | positive source proof of eligibility and success | numerator + denominator |
| `FAILURE` | positive source proof of eligibility and explicit failure | denominator only |
| `UNKNOWN` | positive eligibility evidence; outcome undetermined | denominator + upper-bound uncertainty |
| `AMBIGUOUS` | scope/identity/outcome not safely resolved | certification impossible |
| `UNAVAILABLE` | source did not provide readable evidence | certification impossible |
| `UNOBSERVED` | census member never checked | certification impossible |

Positive statuses must carry a contiguous verbatim excerpt of the fetched page. The validator checks it exists and is materially supportive, using a separate semantic quote check if independent extractors produce different excerpts. The source digest must match the validator's own independent fetch, including on quote revalidation. Model results are strict objects with exactly `status`, `evidence`, and `reason` string fields; duplicate keys, extra fields, malformed JSON and wrong primitive types are rejected. Unsupported text or malformed LLM output becomes `AMBIGUOUS`, not a success, failure, or exclusion. Rechecks are allowed only for `UNKNOWN`, `AMBIGUOUS`, `UNAVAILABLE` and are limited to three attempts in the same observation window. Conclusive cases are immutable within the study.

## Deterministic certificate logic

At finalization, everyone can recompute:

```
N_eligible = success + failure + unknown
N_unresolved = unobserved + ambiguous + unavailable
lower_bps = floor(10000 * success / N_eligible)
upper_bps = ceil(10000 * (success + unknown) / N_eligible)
```

The undefined denominator-zero case never returns a percentage certificate. An exact-rate certificate is available only with unchanged census, `N_unresolved = 0`, `N_eligible > 0`, `unknown = 0`. A bounded certificate requires unchanged census, zero unresolved eligibility, at least one eligible member, and positive unknown count. The source index is re-observed at finalization. Any failure to independently fetch/revalidate it blocks finalization rather than producing a misleading certificate.

## Binding and replay

- Definition hash covers title/scope, eligibility and outcome rules, index URL, census digest, and prospective time window.
- Certificate hash covers definition, source digests, case statuses, evidence excerpts, numerator/denominator and certified bounds.
- Consumer predicates are false for invalid, incomplete, drifted, aborted or zero-population studies.
- Changing the study ID, definition or contents cannot be smuggled into a consumer without changing the pinned `definition_hash` or certificate binding.

## Residual consensus risks

This protocol does not make untrusted web data truthful, authenticate the index publisher, solve DNS rebinding in the execution environment, or establish completeness beyond the closed manifest. Independent validators can disagree due to transient source changes or inconsistent semantic decisions. That should cause no transaction finalization instead of silent majority-by-format acceptance. Real GenVM Direct Mode and live StudioNet proof are required before any security claims about deployed behaviour.
