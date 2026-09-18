from rocm_doctor.checks.base import Status
from rocm_doctor.cli import run_all
from rocm_doctor.system import FakeSystemContext


def test_run_all_never_raises_on_empty_context():
    # An empty FakeSystemContext simulates a box where every external
    # command/file is unavailable. No check may raise — each must degrade
    # gracefully (SKIP for missing data; the blacklist check is a genuine
    # PASS on "no blacklist file found") so the tool is safe to run on any
    # host, including CI.
    ctx = FakeSystemContext()
    results = run_all(ctx)
    assert len(results) == 7
    assert all(r.status in (Status.SKIP, Status.PASS) for r in results)
    non_skip = [r.name for r in results if r.status != Status.SKIP]
    assert non_skip == ["blacklist-amdgpu-leftover"]
