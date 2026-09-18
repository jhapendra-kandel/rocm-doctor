from rocm_doctor.checks.base import Status
from rocm_doctor.checks.ollama_host import OVERRIDE_PATH, check_ollama_host_binding
from rocm_doctor.system import FakeSystemContext


def test_bound_to_all_interfaces_passes():
    ctx = FakeSystemContext(
        files={OVERRIDE_PATH: '[Service]\nEnvironment="OLLAMA_HOST=0.0.0.0:11434"\n'}
    )
    result = check_ollama_host_binding(ctx)
    assert result.status == Status.PASS


def test_override_without_host_warns():
    ctx = FakeSystemContext(files={OVERRIDE_PATH: "[Service]\nEnvironment=\"FOO=bar\"\n"})
    result = check_ollama_host_binding(ctx)
    assert result.status == Status.WARN
    assert result.fix is not None


def test_no_override_skips():
    ctx = FakeSystemContext()
    result = check_ollama_host_binding(ctx)
    assert result.status == Status.SKIP
