# Stable StudioNet deployment and acceptance

This repository is locked to stable GenLayer StudioNet:

| Property | Required value |
| --- | --- |
| Network alias | `studionet` |
| Chain | `61999` / `0xf22f` |
| RPC | `https://studio.genlayer.com/api` |
| Local CLI | `genlayer@0.39.1` |
| Primary source | `contracts/denominator.py` |
| Optional consumer | `examples/rate_gate.py` |

Never use chain 61997, Studio Dev, Studio Next, a preview network, or the
global `genlayer` executable. The deployment wrapper invokes the repository
local `node_modules/.bin/genlayer.cmd` on Windows (or the corresponding local
Unix executable), selects the `studionet` profile, and performs a direct
JSON-RPC `eth_chainId` check before any deploy command. It intentionally does
not pass an ad-hoc `--rpc` flag that could bypass the pinned stable profile.

## Reproducible Windows setup

```powershell
Set-Location "$env:USERPROFILE\Downloads\denominator"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-lint.txt
npm ci --ignore-scripts
cmd /c node_modules\.bin\genlayer.cmd --version
.\.venv\Scripts\python.exe scripts\preflight.py
.\.venv\Scripts\python.exe -m pytest -q tests\unit
.\.venv\Scripts\python.exe -m pytest -q tests\direct
.\.venv\Scripts\python.exe scripts\mutation_check.py
.\.venv\Scripts\python.exe scripts\network_guard.py --check-only
```

The local CLI version must be exactly `0.39.1`, and the guard must print a
direct RPC result of `0xf22f`. If either check fails, stop before signing.
`network_guard.py --check-only` is read-only apart from selecting the local
CLI's named network profile. The deploy mode additionally runs preflight and
checks that the selected CLI account exposes a public address; it never prints
private key material.

## Deployment gate

Before deployment, record the final contract SHA-256 and commit the exact
source. Run the offline suite, native Direct Mode, mutation checks, Python
compilation, preflight, `genvm-lint lint`, and stable `v0.2.12` semantic ABI
validation. The current verified local results are documented in
`docs/TEST_REPORT.md`. Direct Mode is native local GenVM execution, not a live
StudioNet proof.

The stable linter command is:

```powershell
$env:GENVM_VERSION = "v0.2.12"
.\.venv\Scripts\genvm-lint.exe validate contracts\denominator.py --json
.\.venv\Scripts\genvm-lint.exe validate examples\rate_gate.py --json
Remove-Item Env:GENVM_VERSION
```

Expected validation schemas are 5 writes/4 views for `Denominator` and 1
write/1 view for `RateGate`.

## Guarded deployment

```powershell
.\.venv\Scripts\python.exe scripts\network_guard.py --deploy
```

The CLI may request the configured wallet password interactively. Supply it
only to the local terminal; never place it in a file, command line, log or
commit. After the command returns, inspect the actual receipt. A broadcast or
`FINALIZED` status alone is not a successful deployment: require the platform's
successful execution result and a contract-code readback.

Deploy the optional consumer only after the primary address is finalized. Bind
the typed primary address, exact study ID, definition hash and threshold in
the constructor. It is a deliberately permissionless one-shot gate; it proves
the primary predicate and replay protection, not custody or payment.

## Live proof ledger

Record each transaction separately with its hash, finality, execution result,
consensus result and state readback. The exact-rate, bounded-rate, census-drift,
incomplete, zero-population and consumer demonstrations are recorded only after
their finalized transactions and readbacks were observed on stable StudioNet.
The current ledger in `docs/live-evidence.json` contains only observed values
from stable StudioNet.

### Final primary deployment

- Address: `0xaCC465d6D8138C1Ca3322318616311c3F741E0Fe`
- Deployment transaction: `0xa3024d59bfe73a2d1cf47c387b8fcfaea91cbc254b6b42548eca4d207ef77649`
- Result: `MAJORITY_AGREE`, finalized/accepted, successful execution.
- Local and `gen_getContractCode` SHA-256: `0de2b7049737556ba15647b069dc51b9fbaab919fd2739b6fab778f834d983b5`.

An earlier deployment transaction (`0x668f6c784f4e58616d7a61961b81f7597d905e0fbd436ea327c1d41d462d09a`) finalized consensus but returned `invalid_contract`; it is historical failure evidence, not a deployment proof.

### Final consumer deployment

- Address: `0x592794e907166f7ff748E4e8bAc8398f30b8877a`
- Deployment transaction: `0xa4cca14d3105e0172918a55519e7c710fbd1fd2e232f65549db9f9963cd3f517`
- Constructor: typed `addr#acc465d6d8138c1ca3322318616311c3f741e0fe`, study `1`, exact definition hash, threshold `5000`.
- Result: `MAJORITY_AGREE`, finalized/accepted, successful execution.
- Local and `gen_getContractCode` SHA-256: `cf940bf5c13c038be35dc429be9dd4cb33797c048f54792a7306aba04d26d28d`.

The first consumer attempt used the invalid `addr#0x...` marker and finalized with a constructor execution error; it is not used as integration proof. The successful deployment uses the repository-local CLI's required `addr#` plus 40-hex encoding.

### Finalized controlled lifecycle results

- Exact study `1`: finalized `CERTIFIED`, `1/2`, `5000–5000` bps; finalization `0x4e44ab8fa922fe4c2217ec6557c04286726246051bc4973345720afb1760fe3b`.
- Bounded study `3`: finalized `BOUNDED`, numerator `1`, eligible denominator `3`, unknown `1`, `3333–6667` bps; finalization `0x5436cff22bed60816712bdddc40434add2d1ce804ad09dc62ecf43cdd4526be2`.
- Incomplete study `4`: finalized `INCOMPLETE`, unresolved `3`; finalization `0xc24e44edee7d9b2f54960daf20cd2ffe1dadb48ce5832ed05cf2a705a54748a6`.
- Zero-population study `5`: finalized `ZERO_POPULATION`, eligible denominator `0`, no certificate; finalization `0xb42e16ec76434fccf18ba567948528c0a066315edd2e4f52e93145649cd755ad`.
- Census-drift study `6`: sealed against census hash `80feaf62d549c267a3f14b2f6fa33f726b3db19c1a533e354b169942c91a4952`; the valid mutable fixture was then changed and pushed as commit `626cd17`, producing changed hash `a89f01b5eaf3e1e567a1c3b5785c1895e1cb66356c76e28ee0508669c206b951d`. Finalization `0xf101410d697ad95e79981c29bfb80f37c5ecffec6bb598fbe9180d47dcb4423d` reached `MAJORITY_AGREE` with successful execution and stored `CENSUS_DRIFTED`; both certificate predicates read `false`.
- RateGate unlock: `0xa8804488eba63f6dcad0cd08e21c58de3b6b51050eeb865f739b6945523a6f4e`, successful; replay rollback `0x5ee9508c801539cd96f42ac9a7882270e508c2f24fdfec282bea8bade0cb873e`; `is_unlocked()` remained `true`.

The public fixtures are synthetic and controlled. Their use can demonstrate
protocol mechanics, but not publisher independence, universal population
completeness or real-world truth. A census outage at finalization must remain
an availability/consensus failure, not be relabelled as `CENSUS_DRIFTED`.
