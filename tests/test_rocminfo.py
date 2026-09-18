from rocm_doctor.checks.base import Status
from rocm_doctor.checks.rocminfo import check_rocminfo
from rocm_doctor.system import FakeSystemContext


def test_gpu_agent_found_passes(load_fixture):
    ctx = FakeSystemContext(commands={("rocminfo",): load_fixture("rocminfo_gpu_found.txt")})
    result = check_rocminfo(ctx)
    assert result.status == Status.PASS


def test_no_gpu_agent_warns(load_fixture):
    ctx = FakeSystemContext(commands={("rocminfo",): load_fixture("rocminfo_no_gpu.txt")})
    result = check_rocminfo(ctx)
    assert result.status == Status.WARN


def test_rocminfo_missing_skips():
    ctx = FakeSystemContext()
    result = check_rocminfo(ctx)
    assert result.status == Status.SKIP
