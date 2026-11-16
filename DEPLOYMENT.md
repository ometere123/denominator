# Stable StudioNet deployment and acceptance

## Hard constraints

| Property | Pinned value |
| --- | --- |
| Network alias | `studionet` |
| Chain | **61999** |
| RPC | **`https://studio.genlayer.com/api`** |
| CLI | **repo-local `genlayer@0.39.1`** |
| User's global CLI | may remain `0.40.0rc2`; do not alter/use it |
| Contract | `contracts/denominator.py` |
| Secondary contract | optional `examples/rate_gate.py`, not required |

## Windows PowerShell from an extracted repository

```powershell
cd "$HOME\Downloads\denominator"
py -3 -m pip install pytest==8.3.5
py -3 scripts/preflight.py
py -3 -m pytest -q tests/unit
npm install
py -3 scripts/network_guard.py --check-only
# Only once all checks pass and the correct selected CLI wallet is funded:
py -3 scripts/network_guard.py --deploy
```

The guarded deployment invokes only `node_modules/.bin/genlayer.cmd`, verifies **exact CLI 0.39.1**, sets stable `studionet`, checks the printed chain ID and RPC against `network.json`, then passes an explicit stable RPC to the deploy command. If network info lacks either required field it *refuses to deploy*. Never fall back to the globally installed CLI or a preview network.

`npm install` uses the exact package pin and creates a package-lock file. Commit `package-lock.json` once generated. Do **not** do `npm install -g`, do **not** upgrade to an RC because of a local installer warning.

## Real test gates before live submission

The authoring environment lacked network access to npm and to the GenLayer testing-suite source, so the local 35-case simulator pass has **not** validated real GenVM behaviour. The release operator must:

1. Install a known-stable `genlayer-test` matching CLI/Studionet, initially from `requirements-test.txt`.
2. Run `python -m pytest -q tests/direct` on Windows and Ubuntu. Investigate harness compatibility rather than weakening tests. If the dependency/GenVM cannot be installed, disclose the blocker.
3. Run `genvm-lint` via pinned stable linter if available, without substituting unreleased artifacts. If the pin cannot be fetched, do not report lint as passing.
4. Prove the on-chain transaction lifecycle and independently reproduced semantic observation on stable 61999.
5. Commit final source hash before deployment and compare deployed source with committed source exactly.

## Live proof plan using published fixtures

Fixture manifests in `fixtures/census_complete.json` and `fixtures/census_bounded.json` point at the intended public GitHub repo. They will not work until that repository exists at `ometere123/denominator` and the files are visible. After importing the ZIP, commit fixtures before beginning the experiment; preferably host them from immutable Git commit URLs or a separately versioned evidence repository to avoid accidental drift.

Demo protocol:

- **Exact case:** closed census A/B/C. Create a prospective study with the scope `October 2026 synthetic public case population; active cases eligible`, eligibility rule `active in October 2026`, success rule `explicitly fully resolved successfully during October 2026`, and index URL referencing `fixtures/census_complete.json` at a stable public revision. Seal before start. Observe all 3 cases during window. Finalize strictly after deadline. Expect `SUCCESS, FAILURE, EXCLUDED` and `CERTIFIED`, numerator 1, eligible denominator 2, lower/upper both 5000 bps.
- **Bounded case:** closed census A/B/C/D. Same rules, with D's outcome unknown. Expect `BOUNDED`, numerator 1, denominator 3, unknown 1, lower 3333 and upper 6667 bps; `is_rate_certified` false and `is_floor_proven(...,3333)` true.
- **Census drift case:** use a separately hosted/isolated mutable test index, not the production fixture, and change its declared membership between seal and finalize; expect `CENSUS_DRIFTED`, zero certificate hash. Do not mutate the canonical fixture used by any other demo.
- **Adversarial case:** independently validator-rejected forged `SUCCESS` against a source that says the case is pending. Reproduce via Direct Mode; do not claim on-chain malicious-leader injection if it cannot be executed in a controlled environment.

## Evidence that must actually be recorded

For every real on-chain transaction: protocol transaction ID, explorer URL, `FINALIZED`, successful GenVM execution result, persisted state readback, consensus result, and complete source parity. For the exact-rate demonstration, provide the index URL and content digest, all case sources, every `CaseRecord` and the final `Study`. Readbacks must match the final hash-pinned definition. Store this in `docs/live-evidence.json` only when it is **real**. The supplied `docs/live-evidence.template.json` is intentionally blank.

## Important conditions

The ZIP is not deployed. No wallet/private keys are provided and no fabricated transaction hashes are included. Source files have been published to `https://github.com/ometere123/denominator` through the connected GitHub integration. Install the local toolchain, pass real Direct Mode, and verify the live deployment before claiming readiness.
