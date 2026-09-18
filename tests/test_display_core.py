from rocm_doctor.checks.base import Status
from rocm_doctor.checks.display_core import check_display_core_failure
from rocm_doctor.system import FakeSystemContext


def test_failure_signature_detected(load_fixture):
    ctx = FakeSystemContext(
        commands={("dmesg",): load_fixture("dmesg_display_core_failure.txt")}
    )
    result = check_display_core_failure(ctx)
    assert result.status == Status.FAIL
    assert "dc=0" in result.fix


def test_clean_dmesg_passes(load_fixture):
    ctx = FakeSystemContext(commands={("dmesg",): load_fixture("dmesg_clean.txt")})
    result = check_display_core_failure(ctx)
    assert result.status == Status.PASS


def test_unreadable_dmesg_skips():
    ctx = FakeSystemContext(commands={})
    result = check_display_core_failure(ctx)
    assert result.status == Status.SKIP
