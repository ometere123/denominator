"""GenLayer Direct Mode harness for stable contract SDK; requires gltest installation."""
import pytest


@pytest.fixture(autouse=True)
def _enable_storage_validation_and_clock(direct_vm):
    direct_vm.check_pickling = True
    original = direct_vm._refresh_gl_message

    def refresh():
        original()
        import sys
        gl = sys.modules.get("genlayer.gl")
        if gl is not None and isinstance(getattr(gl, "message_raw", None), dict):
            gl.message_raw["datetime"] = direct_vm._datetime

    direct_vm._refresh_gl_message = refresh
    direct_vm._refresh_gl_message()
    yield
