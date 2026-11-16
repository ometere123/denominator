"""Dependency-free preflight with explicit distinction from GenVM and network verification."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "contracts/denominator.py").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
config = json.loads((ROOT / "network.json").read_text(encoding="utf-8"))
pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

assert config["chainId"] == 61999
assert config["rpc"] == "https://studio.genlayer.com/api"
assert config["environment"] == "studionet"
assert config["cliVersion"] == "0.39.1"
assert pkg["devDependencies"]["genlayer"] == "0.39.1"
assert "class Denominator(gl.Contract)" in source
assert "run_nondet_unsafe" in source
assert "def validator_fn" in source
assert "def decode_manifest" in source
assert "def rate_bounds" in source
assert "def is_rate_certified" in source
assert "def is_floor_proven" in source
assert "CENSUS_DRIFTED" in source and "ZERO_POPULATION" in source
assert "no frontend" in readme.lower()

for py in list((ROOT / "contracts").rglob("*.py")) + list((ROOT / "tests").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py")):
    ast.parse(py.read_text(encoding="utf-8"), filename=str(py))

print("PASS: static preflight, exact Studionet/CLI config, syntax and expected safety paths")
print("NOTE: static preflight does NOT establish GenVM Direct Mode, linter or live consensus status")
