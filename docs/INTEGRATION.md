# Developer integration

Denominator is one independently deployable Intelligent Contract. The optional `examples/rate_gate.py` shows consumer composition; it is not a frontend.

## Read functions

- `get_study(study_id)` returns immutable definition hash, population size, exact counts, conservative rate bounds, status and certificate hash.
- `get_case(case_id)` exposes the individual indexed source, semantic status, source hash and supporting excerpt.
- `is_rate_certified(study_id, expected_definition_hash, min_bps)` is true **only** for a complete exact-rate result meeting the threshold.
- `is_floor_proven(study_id, expected_definition_hash, min_bps)` can be true for a `BOUNDED` certificate when its conservative lower bound meets the threshold. It cannot silently promote a bound into a point estimate.

Rate values are integer **basis points** (`10000 = 100%`). Example: 1 success, 1 failure, 1 proven exclusion produces an eligible denominator of 2 and 5000 bps exact. With 1 additional eligible unknown outcome the interval is 3333–6667 bps. Never compare an unknown outcome as a known failure or remove it from the denominator.

## Public source contract

The author declares a study `scope`, explicit eligibility rule, explicit success rule, public machine-readable `index_url`, and a prospective observation window. The source index itself uses `denominator-census/v1` and must be closed, internally consistent and 1–24 members. Each entry includes an `id` and public record URL. Source pages must visibly contain their exact member identifier; positive decisions must be supported by a contiguous excerpt. `seal_census` independently retrieves and seals the set before outcomes are evaluated. No entry may be added later by the author.

## Operational lifecycle

1. Publish an externally controlled/independently inspectable source manifest. For a demonstration only, fixture files become accessible when this repository exists publicly at its intended GitHub path.
2. Create study with `evaluate_after >= chain_now + 60s`; select deadline after start and within 30 days.
3. Before start, study author calls `seal_census`; verify `get_study` is `SEALED` and inspect all case IDs.
4. At/after start and before deadline, independent observer calls `observe_case(case_id)` for each index member. Retry only `UNKNOWN`, `AMBIGUOUS`, `UNAVAILABLE` when new evidence warrants it (maximum 3 observations per member).
5. After deadline, any caller calls `finalize`. If the census changed, fails safe. Otherwise it outputs `CERTIFIED`, `BOUNDED`, `INCOMPLETE` or `ZERO_POPULATION`.
6. A consumer pins the exact study definition hash and decides whether the certified exact rate or proven lower bound satisfies its own deterministic policy.

**No finalization shortcut:** It is acceptable for an unresolved source to prevent a certificate. Do not force a model to guess simply to complete a demo.

## Integration cautions

- The cohort scope is not automatically all real-world cases. Verify source provenance separately.
- The certificate reflects independently observed published evidence during the frozen window, not hidden private records or an omniscient outcome.
- A population manifest's `closed:true` is the index publisher's declaration; GenLayer can verify the index's structure and stability, not the honesty of the publisher.
- A successful write/decision does not equal finalized consensus success. Verify `FINALIZED` and successful execution via receipt before consuming.
- For a mutable source, a change may prevent certification. Prefer source URLs pinned to immutable commits and stable public snapshots.

## Optional on-chain consumption

See `examples/rate_gate.py`, which refuses to unlock unless the exact pinned study meets a fixed exact-rate threshold. This consumer is not a required part of Denominator and has no privileged external effect. It should be deployed/tested on stable Studionet only if doing so adds evidence and does not distract from the main single-contract submission.
