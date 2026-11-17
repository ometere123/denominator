"""Run focused mutation checks against the deterministic contract regressions.

Each mutation changes one security-critical branch in a temporary copy of the
contract.  The selected regression must then fail; a passing mutation means
the regression is not actually protecting that invariant.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "denominator.py"


MUTATIONS = (
    (
        "duplicate-manifest-keys",
        'json.loads(body, object_pairs_hook=reject_duplicate_json_keys)',
        "json.loads(body)",
        "test_duplicate_nested_manifest_keys_fail_closed",
    ),
    (
        "unresolved-finalization",
        "elif unresolved:",
        "elif False and unresolved:",
        "test_incomplete_study_cannot_issue_rate_certificate",
    ),
    (
        "bounded-exact-certificate",
        "int(s.status) == CERTIFIED and bool(s.certificate_hash)",
        "int(s.status) in (CERTIFIED, BOUNDED) and bool(s.certificate_hash)",
        "test_unknown_in_scope_is_bounded_not_a_fake_failure",
    ),
)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="denominator-mutant-") as temp:
        mutant_path = Path(temp) / "denominator.py"
        for name, needle, replacement, test_name in MUTATIONS:
            original = SOURCE.read_text(encoding="utf-8")
            if original.count(needle) != 1:
                failures.append(f"{name}: mutation anchor count was not exactly one")
                continue
            mutant_path.write_text(original.replace(needle, replacement), encoding="utf-8")
            env = os.environ.copy()
            env["DENOMINATOR_CONTRACT_PATH"] = str(mutant_path)
            command = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_denominator.py",
                "-k",
                test_name,
            ]
            result = subprocess.run(command, cwd=ROOT, env=env, text=True)
            if result.returncode == 0:
                failures.append(f"{name}: regression did not kill the mutant")
            else:
                print(f"KILLED {name}")
            mutant_path.unlink(missing_ok=True)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"Mutation checks passed: {len(MUTATIONS)} focused mutants killed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
