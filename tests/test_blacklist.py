from rocm_doctor.checks.base import Status
from rocm_doctor.checks.blacklist import (
    ACTIVE_PATH,
    DISABLED_PATH,
    check_blacklist_leftover,
)
from rocm_doctor.system import FakeSystemContext


def test_active_blacklist_fails():
    ctx = FakeSystemContext(files={ACTIVE_PATH: "blacklist amdgpu\n"})
    result = check_blacklist_leftover(ctx)
    assert result.status == Status.FAIL
    assert DISABLED_PATH in result.fix


def test_commented_out_blacklist_passes():
    ctx = FakeSystemContext(files={ACTIVE_PATH: "# blacklist amdgpu\n"})
    result = check_blacklist_leftover(ctx)
    assert result.status == Status.PASS


def test_already_disabled_passes():
    ctx = FakeSystemContext(files={DISABLED_PATH: "blacklist amdgpu\n"})
    result = check_blacklist_leftover(ctx)
    assert result.status == Status.PASS


def test_no_file_passes():
    ctx = FakeSystemContext()
    result = check_blacklist_leftover(ctx)
    assert result.status == Status.PASS
