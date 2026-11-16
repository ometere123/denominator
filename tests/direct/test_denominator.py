"""GenLayer Direct Mode tests; require genlayer-test / stable GenVM in a real development environment.

These are intentionally separate from the dependency-free simulator. CI should
execute them only when the actual GenLayer testing toolchain is installed.
"""
import json
from datetime import datetime, timezone, timedelta

import pytest

CONTRACT = "contracts/denominator.py"
BASE = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
START = BASE + timedelta(minutes=2)
DEADLINE = BASE + timedelta(minutes=35)
INDEX_URL = "https://example.org/census.json"
CASE_URL = "https://example.org/case-a.txt"
CASE_KEY = "case_A"
PROMPT = r"You are independently classifying ONE member of a sealed statistical population"


def epoch(dt):
    return int(dt.timestamp())


def census(url=CASE_URL):
    return json.dumps({"schema": "denominator-census/v1", "closed": True,
                       "declared_total": 1,
                       "cases": [{"id": CASE_KEY, "url": url}]})


def sealed(vm, deploy):
    vm.warp(BASE.isoformat())
    contract = deploy(CONTRACT)
    vm.mock_web(r".*example\.org/census\.json.*", {"status": 200, "body": census()})
    sid = contract.create_study(
        "Public demo", "Frozen sample cohort", "Active cases count in population",
        "Cases explicitly marked complete count as success", INDEX_URL, epoch(START), epoch(DEADLINE))
    contract.seal_census(sid)
    return contract, sid, contract.get_study(sid)["case_ids"][0]


def test_seal_validates_census_and_exports_definition_hash(direct_vm, direct_deploy):
    contract, sid, cid = sealed(direct_vm, direct_deploy)
    assert contract.get_study(sid)["status_name"] == "SEALED"
    assert contract.get_case(cid)["external_key"] == CASE_KEY
    assert len(contract.get_study(sid)["definition_hash"]) == 64
    assert direct_vm.run_validator() is True


def test_validator_rejects_forged_one_member_census(direct_vm, direct_deploy):
    contract, sid, _ = sealed(direct_vm, direct_deploy)
    assert contract.get_study(sid)["status_name"] == "SEALED"
    # Explicit invalidation on subsequent census changes is tested in the
    # next case; current leader cannot freely choose a new population.
    direct_vm.warp((DEADLINE + timedelta(seconds=1)).isoformat())
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/census\.json.*", {"status": 200, "body": census(url="https://example.org/changed.txt")})
    contract.finalize(sid)
    assert contract.get_study(sid)["status_name"] == "CENSUS_DRIFTED"
    assert contract.get_study(sid)["certificate_hash"] == ""
    assert direct_vm.run_validator() is True


def test_success_uses_independent_reobservation_and_can_be_certified(direct_vm, direct_deploy):
    contract, sid, cid = sealed(direct_vm, direct_deploy)
    text = "Report case_A: case_A is active and explicitly completed successfully."
    evidence = "case_A is active and explicitly completed successfully."
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/case-a\.txt.*", {"status": 200, "body": text})
    direct_vm.mock_llm(PROMPT, {"status": "SUCCESS", "evidence": evidence, "reason": "explicit"})
    direct_vm.warp((START + timedelta(minutes=1)).isoformat())
    contract.observe_case(cid)
    assert contract.get_case(cid)["status_name"] == "SUCCESS"
    assert direct_vm.run_validator() is True
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/census\.json.*", {"status": 200, "body": census()})
    direct_vm.warp((DEADLINE + timedelta(seconds=1)).isoformat())
    contract.finalize(sid)
    claim = contract.get_study(sid)
    assert claim["status_name"] == "CERTIFIED"
    assert claim["denominator"] == 1 and claim["numerator"] == 1
    assert contract.is_rate_certified(sid, claim["definition_hash"], 10000)


def test_forged_success_is_rejected_when_validator_saw_unknown(direct_vm, direct_deploy):
    contract, sid, cid = sealed(direct_vm, direct_deploy)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/case-a\.txt.*", {
        "status": 200, "body": "case_A is active, but outcome is not settled."})
    direct_vm.mock_llm(PROMPT, {
        "status": "UNKNOWN", "evidence": "case_A is active, but outcome is not settled.", "reason": "pending"})
    direct_vm.warp((START + timedelta(minutes=1)).isoformat())
    contract.observe_case(cid)
    own = contract.get_case(cid)
    assert own["status_name"] == "UNKNOWN"
    assert direct_vm.run_validator(leader_result={
        "status": 2, "evidence": "case_A is active, but outcome is not settled.",
        "reason": "forge", "source_hash": own["source_hash"]}) is False


def test_unknown_produces_bounds_not_exact_certificate(direct_vm, direct_deploy):
    contract, sid, cid = sealed(direct_vm, direct_deploy)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/case-a\.txt.*", {
        "status": 200, "body": "case_A is eligible but outcome remains unresolved."})
    direct_vm.mock_llm(PROMPT, {
        "status": "UNKNOWN", "evidence": "case_A is eligible but outcome remains unresolved.",
        "reason": "unresolved"})
    direct_vm.warp((START + timedelta(minutes=1)).isoformat())
    contract.observe_case(cid)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/census\.json.*", {"status": 200, "body": census()})
    direct_vm.warp((DEADLINE + timedelta(seconds=1)).isoformat())
    contract.finalize(sid)
    s = contract.get_study(sid)
    assert s["status_name"] == "BOUNDED"
    assert s["lower_bps"] == 0 and s["upper_bps"] == 10000
    assert not contract.is_rate_certified(sid, s["definition_hash"], 0)
    assert contract.is_floor_proven(sid, s["definition_hash"], 0)


def test_missing_case_source_is_not_a_failure(direct_vm, direct_deploy):
    contract, sid, cid = sealed(direct_vm, direct_deploy)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.org/case-a\.txt.*", {"status": 503, "body": ""})
    direct_vm.warp((START + timedelta(minutes=1)).isoformat())
    contract.observe_case(cid)
    assert contract.get_case(cid)["status_name"] == "UNAVAILABLE"
    assert direct_vm.run_validator() is True


def test_only_author_can_seal_and_draft_cannot_seal_late(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp(BASE.isoformat())
    contract = direct_deploy(CONTRACT)
    sid = contract.create_study("Test", "scope", "eligible", "success", INDEX_URL,
                                epoch(START), epoch(DEADLINE))
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("only author"):
            contract.seal_census(sid)
    direct_vm.warp((START + timedelta(seconds=1)).isoformat())
    with direct_vm.expect_revert("before observations"):
        contract.seal_census(sid)
