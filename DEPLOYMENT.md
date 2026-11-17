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
consensus result and state readback. The exact-rate, bounded-rate,
census-drift, incomplete, zero-population and consumer demonstrations are not
claimed until they have actually been finalized on chain. Store only real
values in `docs/live-evidence.json`; the template remains blank until then.

The public fixtures are synthetic and controlled. Their use can demonstrate
protocol mechanics, but not publisher independence, universal population
completeness or real-world truth. A census outage at finalization must remain
an availability/consensus failure, not be relabelled as `CENSUS_DRIFTED`.
