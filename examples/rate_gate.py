# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""OPTIONAL consumer demonstrating contract composition; not part of Denominator deployment."""
from genlayer import *


@gl.contract_interface
class IDenominator:
    class View:
        def is_rate_certified(self, study_id: u256, expected_definition_hash: str, min_bps: u32) -> bool: ...
        def is_floor_proven(self, study_id: u256, expected_definition_hash: str, min_bps: u32) -> bool: ...

    class Write:
        pass


class RateGate(gl.Contract):
    denominator_address: Address
    study_id: u256
    pinned_definition_hash: str
    threshold_bps: u32
    unlocked: bool

    def __init__(self, address: Address, study_id: u256, definition_hash: str, threshold_bps: u32):
        self.denominator_address = address
        self.study_id = study_id
        self.pinned_definition_hash = definition_hash
        self.threshold_bps = threshold_bps
        self.unlocked = False

    @gl.public.write
    def unlock(self) -> None:
        if self.unlocked:
            raise gl.vm.UserError("gate already unlocked")
        provider = IDenominator(self.denominator_address)
        if not provider.view().is_rate_certified(self.study_id, self.pinned_definition_hash, self.threshold_bps):
            raise gl.vm.UserError("exact cohort rate is not independently certified at pinned definition")
        self.unlocked = True

    @gl.public.view
    def is_unlocked(self) -> bool:
        return self.unlocked
