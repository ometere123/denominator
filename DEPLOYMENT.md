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

### Current final primary deployment

- Address: `0xf6df5044147859B7A299eDF08eA575b1425D2A5d`
- Deployment transaction: `0xcf86d040d45bfed27f09953f21a05868c7c09c2bff92db8fe58d794d39ffa28`
- Result: `MAJORITY_AGREE`, finalized/accepted, successful execution.
- Local and `gen_getContractCode` SHA-256: `34a770eeb277dd9650ad0f9e68063086fbc4f9f3e35e4059b0641acad8d24e0e`.

The earlier CRLF-byte deployment at `0xaCC465d6D8138C1Ca3322318616311c3F741E0Fe` (transaction `0xa3024d59bfe73a2d1cf47c387b8fcfaea91cbc254b6b42548eca4d207ef77649`, hash `0de2b7049737556ba15647b069dc51b9fbaab919fd2739b6fab778f834d983b5`) is historical. An earlier deployment transaction (`0x668f6c784f4e58616d7a61961b81f7597d905e0fbd436ea327c1d41d462d09a`) finalized consensus but returned `invalid_contract`; it is historical failure evidence, not a deployment proof.

### Current final consumer deployment

- Address: `0xF24FA9872cEeF626E43Ba9B4770161d8cFC07d55`
- Deployment transaction: `0x1853729d7d02ff492647f0f40f1347969b9e4e00f8d2c8f5cb7a767cbcdd8f42`
- Constructor: typed `addr#f6df5044147859b7a299edf08ea575b1425d2a5d`, study `1`, definition hash `07f9c73f3a65816610e5b01a626a32d8750657e4ff86bbc0d45242dbfce6f849`, threshold `5000`.
- Result: `MAJORITY_AGREE`, finalized/accepted, successful execution.
- Local and `gen_getContractCode` SHA-256: `bf561da31c507226dfc0db5cc3b30052ebde987ff8fc02e96f95ec1f57c9506d`.

The earlier consumer at `0x592794e907166f7ff748E4e8bAc8398f30b8877a` was bound to the historical primary and is not current integration proof. The first consumer attempt used the invalid `addr#0x...` marker and finalized with a constructor execution error; it is not used as integration proof. The current deployment uses the repository-local CLI's required `addr#` plus 40-hex encoding.

### Finalized controlled lifecycle results

- Current exact study `1`: finalized `CERTIFIED`, `1/2`, `5000–5000` bps; finalization `0xe32f54b742a1849c394c0bf2d9ea5ead81c7364233b7bc82d7008abff8134d2b`; `is_rate_certified(...,5000)=true`, `is_rate_certified(...,5001)=false`.
- Historical controls on the prior primary: bounded study `3` finalized `BOUNDED`, incomplete study `4` finalized `INCOMPLETE`, zero-population study `5` finalized `ZERO_POPULATION`, and census-drift study `6` finalized `CENSUS_DRIFTED`. These receipts remain historical because the primary source bytes changed.
- Current RateGate unlock: `0x2be07b3a6402b0f4e16ee1a5bcf859d4ee54c5e73fc0906b9fa4ace71d114dad`, successful; replay rollback `0x30fd1af011c28ad922dea422c20fe0af8a71cf9472565d3e120215245bd454f4`; `is_unlocked()` remained `true`.

The public fixtures are synthetic and controlled. Their use can demonstrate
protocol mechanics, but not publisher independence, universal population
completeness or real-world truth. A census outage at finalization must remain
an availability/consensus failure, not be relabelled as `CENSUS_DRIFTED`.
