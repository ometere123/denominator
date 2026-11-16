# Test report (authoring environment)

- Verified: `python -m compileall -q contracts tests scripts examples` — PASS.
- Verified: `python -m pytest -q tests/unit` — **35 passed**, dependency-free simulation of the actual contract source (fake GenLayer runtime).
- Verified: `python scripts/preflight.py` — PASS after documentation and config creation.
- Not verified: `genlayer-test` real Direct Mode — Python GenLayer testing package and GenVM unavailable in authoring environment.
- Not verified: `genvm-linter` binary — dependency unavailable in authoring environment.
- Not verified: `npm install` / repo-local CLI invocation — outbound npm registry lookup returned `EAI_AGAIN`.
- Not verified: StudioNet deployment, finalized receipts, live validator consensus, on-chain source parity — no configured signing wallet and requested repo returned GitHub 404.

The offline tests deliberately mock `gl.nondet` and `gl.vm` but import and exercise the actual `contracts/denominator.py`; they **must not be represented as Direct Mode or finalized network proofs**. Complete the gates in `DEPLOYMENT.md` before submission. Failure to install tools is a blocker, not a passing test.
