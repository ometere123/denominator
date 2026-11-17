"""GenLayer Direct Mode harness for stable contract SDK; requires gltest installation."""
import os

import pytest


def pytest_configure():
    """Work around genlayer-test 0.29.2's Windows temp-file cleanup bug.

    The harness dup2s the message file onto stdin, then immediately unlinks the
    still-open file. Windows correctly returns WinError 32. The message has
    already been injected at that point, so only the cleanup exception is
    suppressed; all contract execution and validator behavior remains native.
    """
    if os.name != "nt":
        return
    try:
        from gltest.direct import loader
    except ImportError:
        return
    if getattr(loader, "_denominator_windows_cleanup_patch", False):
        return
    original = loader._inject_message_to_fd0

    def windows_safe_inject(vm):
        try:
            original(vm)
        except PermissionError as exc:
            if getattr(exc, "winerror", None) != 32:
                raise

    loader._inject_message_to_fd0 = windows_safe_inject
    loader._denominator_windows_cleanup_patch = True


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
