# Verification report

This report records the current verification performed from the Windows
authoring environment. Local simulation, Direct Mode and linter results are
not StudioNet deployment evidence.

## Baseline before hardening

- Commit: `6a10889611e169a80492fc71e96499d30d1b5dd2`.
- Offline simulator: 35 passed with `python -m pytest -q tests/unit`.
- Preflight and Python compilation: passed.
- Direct Mode: the pinned `genlayer-test` 0.29.2 harness initially failed on
  Windows before contract loading because its stdin helper attempted to unlink
  an open temporary file (`PermissionError: [WinError 32]`). This was a test
  harness defect, not a contract result.
- GenVM linter, npm installation and StudioNet deployment were not part of the
  historical baseline.

## Current verification

- Offline simulator: **40 passed** with
  `.venv\Scripts\python.exe -m pytest -q tests/unit`.
- Native Direct Mode: **11 passed** with
  `.venv\Scripts\python.exe -m pytest -q tests/direct` using
  `genlayer-test` 0.29.2. The Windows shim catches only the known temporary
  file cleanup error and leaves native contract/validator execution intact.
- Focused mutation checks: **3 security mutants killed** with
  `.venv\Scripts\python.exe scripts/mutation_check.py`:
  duplicate manifest keys, unresolved finalization, and treating bounded
  results as exact certificates.
- Preflight: passed.
- Python compilation: passed for `contracts`, `tests`, `scripts` and
  `examples`.
- True Keccak-256 vectors: passed for the empty string and `abc`; the tests
  use `Crypto.Hash.keccak`, not NIST SHA3-256.
- Repository-local CLI: `genlayer` 0.39.1.
- Direct stable RPC check: the guard verifies `eth_chainId == 0xf22f`.
- GenVM linter: `genvm-linter` 0.11.0. AST lint passed for both contracts.
  With `GENVM_VERSION=v0.2.12`, semantic ABI validation passed for
  `contracts/denominator.py` (9 methods: 5 writes and 4 views) and
  `examples/rate_gate.py` (2 methods: 1 write and 1 view).

## Security regressions added

The suite now rejects duplicate raw JSON keys in census and model responses,
uses explicit HTTP status/body validation, keeps source outages distinct from
confirmed census drift, exercises native validator disagreement for forged
success and exclusion, and verifies the stable Keccak vectors. The validator
continues to fetch and classify the frozen case independently rather than
accepting leader JSON shape alone.

## Live verification added after local testing

- Final normalized-LF primary deployment on stable StudioNet: `0xf6df5044147859B7A299eDF08eA575b1425D2A5d`, finalized successful deployment transaction `0xcf86d040d45bfed27f09953f21a05868c7c09c2bff92db8fe58d794d39ffa28`.
- Current exact controlled study: `CERTIFIED`, 1/2, 5000 bps.
- Current bounded study: `BOUNDED`, 1/3, excluded=1, unknown=1, bounds 3333–6667 bps; exact predicate false and conservative floor predicates 3333=true/3334=false.
- Current incomplete study: `INCOMPLETE`, unresolved=3, no certificate.
- Current zero-population study: `ZERO_POPULATION`, eligible denominator=0, no certificate.
- Current census-drift study: `CENSUS_DRIFTED`, with sealed and changed census hashes recorded in `docs/live-evidence.json`.
- Correctly typed RateGate bound to the current primary is deployed at `0xF24FA9872cEeF626E43Ba9B4770161d8cFC07d55`; authorized unlock succeeded and exact replay rolled back.
- `gen_getContractCode` byte readback matches the local primary and consumer files exactly.

The live evidence is controlled synthetic fixture mechanics, not independent publisher evidence or a universal completeness guarantee. All five current-primary lifecycle states and the consumer proof are now recorded in the ledger; the older CRLF-byte deployment remains historical only.
