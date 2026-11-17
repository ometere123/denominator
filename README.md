# Denominator

**Proof that a reported rate was calculated over its complete *declared, sealed, public* population—not just its convenient successes.**

A standalone GenLayer Intelligent Contract primitive. **No frontend, backend, database, or privileged server.** The deliverable is one deployable Python contract, a small optional consumer example, adversarial tests, and reviewer evidence tooling.

**Target is exclusively stable GenLayer Studionet, chain ID `61999`, RPC `https://studio.genlayer.com/api`, using a repository-local `genlayer` CLI `0.39.1`.** The installed global CLI does not matter. No source in this project should ever target Studio's development-preview environment.

## The gap

Suppose a provider reports `19/20 = 95%` success. Its public, frozen case index contains 100 cases. The 19 successful outcomes might be real, but a certificate based on 20 selected cases must not pass for that 100-case cohort. Ordinary string or JSON validation cannot tell whether a page identifies a case as eligible, excluded, successful, failed, or unresolved; GenLayer consensus supplies that bounded semantic interpretation. Deterministic code owns the population cardinality, counting, rate bounds, and certificate state.

**Important limitation:** Denominator proves completeness *relative to a declared externally supplied census index*. It does **not** prove that this index includes every event in the world, or that its publisher is intrinsically authoritative. Callers must independently trust/verify who controls that source and what universe it represents. This limitation is integral to the API, not a footnote to be ignored.

## Mechanism

```text
PUBLIC CLOSED CENSUS INDEX (machine-readable JSON)
   │  independent leader + validator fetch, strict parsing,
   │  exact member list, digest, committed before observation
   ▼
SEALED COHORT: IDs and evidence URLs immutable on-chain
   │
   ├── permissionless observation of every indexed case
   │       └── independently re-fetch + semantic outcome judgement
   │
   ├── missing case        → UNOBSERVED / UNAVAILABLE (never excluded)
   ├── uncertain scope     → AMBIGUOUS (blocks certificate)
   ├── eligible pending    → UNKNOWN (stays in denominator)
   └── excluded by proof  → EXCLUDED (removed from denominator)
   │
   ▼
POST-DEADLINE RE-FETCH OF CENSUS
   ├── changed             → CENSUS_DRIFTED (no certificate)
   ├── incomplete evidence → INCOMPLETE (no certificate)
   ├── zero eligible       → ZERO_POPULATION (no percentage)
   ├── pending outcomes    → BOUNDED (lower/upper rate only)
   └── all resolved        → CERTIFIED (exact scoped rate)
```

**Only direct source-grounded proof can exclude a case.** A missing record does not silently shrink the denominator. An unresolved eligible case remains in the denominator, yielding a lower and upper bound rather than a fabricated exact percentage.

## Example

The included synthetic complete cohort has three indexed cases:

| Case | Public evidence | Classification |
| --- | --- | --- |
| A | active and fully resolved | SUCCESS |
| B | active and explicitly failed | FAILURE |
| C | explicitly outside frozen active-case eligibility | EXCLUDED |

The correct scoped rate is `1 / 2 = 50%`, not `1 / 1 = 100%` and not `1 / 3` if C was truly ineligible. A separate bounded example adds eligible case D with unresolved outcome: `1 / 3 ≤ rate ≤ 2 / 3`, displayed conservatively as **3333–6667 basis points**. `is_rate_certified` returns false for bounded claims; `is_floor_proven` permits only the independently established conservative minimum.

## ABI (stable v0.1)

**Writes:**

| Function | Who | Purpose |
| --- | --- | --- |
| `create_study(title, scope, eligibility_rule, success_rule, index_url, evaluate_after, deadline_at)` | anyone | Freeze rule text, census URL and prospective time window |
| `seal_census(study_id)` | study author only, before start | Independently fetch and bind exact closed population |
| `abort_draft(study_id)` | author only, while draft | Abandon an unfinished study |
| `observe_case(case_id)` | anyone, during window | Independently classify one case; retry only unknown/ambiguous/unavailable up to 3 attempts |
| `finalize(study_id)` | anyone, after deadline | Re-fetch original census and deterministically compute counts and certificate |

**Views:** `get_study`, `get_case`, `is_rate_certified(study_id, expected_definition_hash, min_bps)`, `is_floor_proven(study_id, expected_definition_hash, min_bps)`.

Both consumer gates require an exact **pinned definition hash**. The example `examples/rate_gate.py` is optional documentation of composition, not a claimed live deployment.

## Census input format

A public UTF-8 JSON source with exactly these keys:

```json
{
  "schema": "denominator-census/v1",
  "closed": true,
  "declared_total": 2,
  "cases": [
    {"id": "case_A", "url": "https://example.org/a.txt"},
    {"id": "case_B", "url": "https://example.org/b.txt"}
  ]
}
```

The case set is bounded to 24 entries per study. IDs must be ASCII alphanumeric plus `_` or `-`; duplicate raw JSON keys and duplicate member IDs are rejected; records require public HTTPS; declared count must equal actual entries; any extra field or malformed data rejects the manifest. The source is checked again after the observation deadline before a certificate can be issued. Use stable/commit-pinned source URLs rather than mutable dashboards for production applications.

## Architecture and trust boundaries

1. **Census consensus:** `gl.vm.run_nondet_unsafe` leader fetches/normalises the public index; validators independently fetch and require exact normalized member list and hash. An unverified leader-selected subset is rejected.
2. **Case consensus:** each validator independently fetches the case source and derives the bounded semantic status. Classification and source digest must agree. Evidence must be a verbatim excerpt present in the fetched source; differing supporting excerpts require another validator-side semantic check against the same source digest.
3. **Deterministic settlement:** statuses, attempt limits, study immutability, integer arithmetic, exact/interval certificates, and consumer predicates are all deterministic. The LLM cannot set counts, percentages, payouts, or source members.

Read [Consensus](docs/CONSENSUS.md), [Threat model](docs/THREAT_MODEL.md) and [Integration](docs/INTEGRATION.md) before using these certificates in another protocol.

## Local validation and build

Python 3.12+ and Node.js 22 LTS are suitable. On **Windows PowerShell**:

```powershell
cd <your\denominator\folder>
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest==8.3.5 pycryptodome==3.24.1
npm ci --ignore-scripts
.\.venv\Scripts\python.exe scripts/preflight.py
.\.venv\Scripts\python.exe -m pytest -q tests/unit
.\.venv\Scripts\python.exe scripts/mutation_check.py
.\.venv\Scripts\python.exe -m compileall -q contracts tests scripts examples
.\.venv\Scripts\python.exe scripts/network_guard.py --check-only
```

On **Linux/macOS**:

```bash
python3 -m pip install pytest==8.3.5 pycryptodome==3.24.1
python3 scripts/preflight.py
python3 -m pytest -q tests/unit
npm ci --ignore-scripts
python3 scripts/network_guard.py --check-only
```

The network guard refuses to run if the local CLI is missing/wrong, the alias is wrong, the reported chain ID is not 61999, or the direct `eth_chainId` RPC result is not `0xf22f`. It never selects your global CLI 0.40 RC. The committed lockfile pins the repository-local CLI; use `npm ci` for reproducible installs.

**Real GenLayer Direct Mode is a separate step:** install `requirements-test.txt` and run `pytest -q tests/direct` on an environment with the compatible stable GenVM testing stack. The current verification is 40 unit/adversarial simulator tests and 11 native Direct Mode tests. The Direct Mode tests are local GenVM execution, not StudioNet finality. See [Deployment](DEPLOYMENT.md).

## Current provenance / delivery status

The current source is published at [`ometere123/denominator`](https://github.com/ometere123/denominator). Local verification currently records 40 unit tests, 11 native Direct Mode tests, three focused mutation checks, preflight, Python compilation, and GenVM 0.11.0 AST/semantic ABI validation against the pinned stable `v0.2.12` artifact. It has **not yet been deployed or demonstrated through finalized transactions on StudioNet** in this work. There is deliberately no invented contract address, explorer link, transaction hash, finality receipt, or verified on-chain source parity.

## Security & scope

- Public sources only. No private customer data is required or stored.
- No custodial functions, arbitrary token transfers, proxy governance, frontend, or off-chain authority.
- Contract input rules and retrieved web pages are treated as inert data, not instructions.
- Source completeness and source authenticity are outside the contract unless independently proved by the publishing system. A malicious publisher can omit cases before closure; no intelligent contract can infer unknown hidden cases from a chosen public manifest.
- The exact basis-point representation is integer floor for the lower bound and ceiling for the upper bound.
- Consumers must check the *definition hash*, certificate state, and scope; an unbounded population claim is never implied.

MIT licensed. See [Submission](SUBMISSION.md) for reviewer-facing explanation.
