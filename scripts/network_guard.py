"""Fail-closed deploy guard: use repository-local GenLayer CLI 0.39.1, chain 61999.

Never relies on global npm, a project-wide wallet secret, or a caller override.
The CLI account must be configured interactively by the human/agent on the machine.
"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "network.json").read_text(encoding="utf-8"))
EXPECTED = {"environment": "studionet", "chainId": 61999,
            "rpc": "https://studio.genlayer.com/api", "cliVersion": "0.39.1"}


def guard(condition: bool, message: str):
    if not condition:
        raise SystemExit("DENOMINATOR NETWORK GUARD: " + message)


def rpc_chain_id() -> str:
    request = Request(
        EXPECTED["rpc"],
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "denominator-network-guard/1"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise SystemExit("DENOMINATOR NETWORK GUARD: direct RPC eth_chainId failed: " + str(exc))
    if not isinstance(payload, dict) or payload.get("error") is not None:
        raise SystemExit("DENOMINATOR NETWORK GUARD: direct RPC returned an error")
    result = payload.get("result")
    guard(isinstance(result, str) and result.lower() == "0xf22f",
          "direct RPC chain mismatch: expected 0xf22f, got " + repr(result))
    return result.lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy", action="store_true", help="deploy only after verified local CLI/network checks")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    for key, value in EXPECTED.items():
        guard(CONFIG.get(key) == value, f"invalid pinned network config {key}")
    cli = ROOT / "node_modules" / ".bin" / ("genlayer.cmd" if os.name == "nt" else "genlayer")
    guard(cli.is_file(), "local CLI missing; run npm install IN THIS REPOSITORY (never global)")

    def run(*args_: str):
        result = subprocess.run([str(cli), *args_], cwd=ROOT, text=True,
                                capture_output=True, check=False)
        guard(result.returncode == 0, "CLI command failed: " + " ".join(args_) + "\n" + result.stdout + result.stderr)
        return result.stdout + result.stderr

    version = run("--version")
    guard(re.search(r"(?<![\w.])0\.39\.1(?![\w.-])", version) is not None,
          "wrong CLI version: expected exactly 0.39.1; found " + version.strip())
    run("network", "set", "studionet")
    info = run("network", "info")
    guard(re.search(r"(?<!\d)61999(?!\d)", info) is not None,
          "network info does not explicitly confirm chain 61999; STOP\n" + info)
    guard("https://studio.genlayer.com/api" in info,
          "network info does not confirm exact stable Studionet RPC; STOP\n" + info)
    guard("studio-dev" not in info and "61997" not in info,
          "preview environment detected; STOP")
    chain_id = rpc_chain_id()
    print("PASS: repo-local CLI 0.39.1; studionet; 61999; direct eth_chainId=" + chain_id)
    if args.deploy:
        import sys as _sys
        check = subprocess.run([_sys.executable, "scripts/preflight.py"], cwd=ROOT)
        guard(check.returncode == 0, "preflight failed; deployment refused")
        print("Using selected local GenLayer CLI account; verify the wallet on your machine.")
        account = run("account")
        guard(re.search(r"0x[a-fA-F0-9]{40}", account) is not None,
              "selected account output did not expose a public address")
        print(account)
        # The built-in studionet profile carries the stable RPC and consensus
        # configuration. Do not bypass it with --rpc during deployment.
        result = run("deploy", "--contract", "contracts/denominator.py")
        print(result)
        print("NOTE: this is submission only. Verify FINALIZED + SUCCESS receipt, then source parity.")


if __name__ == "__main__":
    main()
