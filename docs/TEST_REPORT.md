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

- Final primary deployment on stable StudioNet: `0xaCC465d6D8138C1Ca3322318616311c3F741E0Fe`, finalized successful deployment transaction `0xa3024d59bfe73a2d1cf47c387b8fcfaea91cbc254b6b42548eca4d207ef77649`.
- Exact controlled study: `CERTIFIED`, 1/2, 5000 bps; bounded controlled study: `BOUNDED`, 1/3 with 3333–6667 bps; incomplete and zero-population controls finalized as `INCOMPLETE` and `ZERO_POPULATION`.
- Correctly typed RateGate deployed at `0x592794e907166f7ff748E4e8bAc8398f30b8877a`; authorized unlock succeeded and exact replay rolled back.
- `gen_getContractCode` byte readback matches the local primary and consumer files exactly.

The live evidence is controlled synthetic fixture mechanics, not independent publisher evidence or a universal completeness guarantee. The mutable census-drift study was sealed after census version A, changed to valid version B in commit `626cd17`, and finalized after the deadline as `CENSUS_DRIFTED` in transaction `0xf101410d697ad95e79981c29bfb80f37c5ecffec6bb598fbe9180d47dcb4423d`; its certificate predicates read `false`.
