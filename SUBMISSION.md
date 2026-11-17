# Denominator — standalone Intelligent Contract submission

**Denominator makes a reported success rate accountable to its frozen declared population, not to a cherry-picked list of successful examples.**

## Submission description (644 characters including spaces)

Denominator is a GenLayer Intelligent Contract that prevents a reported success rate from being certified over a cherry-picked subset of a frozen public population. Independent leader and validator executions fetch and validate the complete closed census and case evidence; deterministic settlement accounts for every member, preserves failures and unknowns, detects census drift, and exposes exact-rate or conservative-floor predicates. A typed RateGate demonstrates one-shot IC-to-IC consumption. The contract proves scoped accounting over the declared public census—not universal real-world completeness, publisher identity, or source truth.

Most statistical verification tools validate the formula (`19/20 = 95%`); Denominator first verifies the *membership of the denominator*. Its contract freezes an explicit public closed index before outcomes may be evaluated, requires independently observed source-grounded status for every member, and rechecks the index at finalization. The final result either has an exact, traceable eligible denominator, conservative bounds for pending eligible outcomes, or **no certificate**.

## Why consensus is essential

Eligibility, exclusions and real-world success often require interpreting text in independently maintained public records. A deterministic contract cannot safely derive those classes from arbitrary prose without a trusted off-chain decision-maker. Denominator uses GenLayer's independent leader/validator execution to interpret a frozen member against a frozen rubric. Validators fetch the same source independently, compare actual semantic classes, verify a source digest, and require contiguous quoted evidence for positive outcomes. An unsupported LLM guess has no settlement authority.

## Why this is a primitive rather than an application

There is no frontend, no user account flow, no private database, no token custody and no central API. The sole output is on-chain member status, population completeness and exact/bounded rate evidence. Any downstream contract may consume the frozen definition hash and deterministic certification predicates. Examples include research reporting, SLA performance, grant outcome metrics, agent marketplace fulfillment and verified operational statistics. See `examples/rate_gate.py` for the typed contract interface.

## Defensible guarantees

- No caller-selected subset can replace the **already-published index** at sealing.
- Every member frozen at sealing remains accounted for during finalization.
- Source-unavailable, ambiguous or unobserved cases do not silently vanish from the cohort or become presumed failures.
- Only affirmative quoted evidence can remove a member as ineligible.
- In-scope pending outcomes widen the reported interval and prevent a point-estimate certificate.
- A changed public source index invalidates certification.
- Hash-pinned consumer checks cannot be silently pointed at a new definition.

## Trust assumptions

The closed index's completeness is only as good as its independent publisher. The contract cannot discover records the authoritative index never disclosed. It is a **scoped completeness certificate**, not proof that every event in the world has been enumerated. It does not guarantee physical or social truth of the source documents. See `docs/THREAT_MODEL.md`.

## Reproducible review material

- `contracts/denominator.py`: standalone deployable source, custom validator consensus and deterministic accounting.
- `tests/unit`: 40 dependency-free adversarial and lifecycle tests, including strict duplicate-key and Keccak regressions.
- `tests/direct`: 11 native Direct Mode tests using the pinned `genlayer-test` 0.29.2 harness, including validator disagreement paths.
- `scripts/mutation_check.py`: three focused security mutants killed by the unit regressions.
- `docs/CONSENSUS.md`: precisely what validators independently check.
- `docs/THREAT_MODEL.md`: hostile and honest-failure cases and non-goals.
- `fixtures/`: public synthetic cohort examples for exact, bounded, incomplete, zero-population and drift controls.
- `DEPLOYMENT.md`: Windows/Ubuntu acceptance, stable 61999 network guard and live-evidence requirements.

## Submission status

The normalized-LF final primary and consumer are deployed on stable StudioNet 61999 with exact deployed-source byte parity. Current-source live proofs include exact certification, bounded-rate accounting, incomplete-member rejection, zero-population handling, census-drift invalidation, and one-shot consumer unlock/replay protection. All fixtures are repository-controlled synthetic evidence, so they do not prove independent publisher identity or universal population completeness. The exact score is a reviewer decision; this package does not claim a score or guaranteed acceptance.
