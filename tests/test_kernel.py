from rocm_doctor.checks.base import Status
from rocm_doctor.checks.kernel import check_kernel_version
from rocm_doctor.system import FakeSystemContext


def test_ga_kernel_warns():
    ctx = FakeSystemContext(commands={("uname", "-r"): "6.8.0-45-generic\n"})
    result = check_kernel_version(ctx)
    assert result.status == Status.WARN
    assert result.fix is not None


def test_hwe_kernel_passes():
    ctx = FakeSystemContext(commands={("uname", "-r"): "6.14.0-27-generic\n"})
    result = check_kernel_version(ctx)
    assert result.status == Status.PASS


def test_missing_uname_skips():
    ctx = FakeSystemContext(commands={})
    result = check_kernel_version(ctx)
    assert result.status == Status.SKIP
