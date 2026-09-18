from rocm_doctor.checks.base import Status
from rocm_doctor.checks.ollama_processor import check_ollama_processor
from rocm_doctor.system import FakeSystemContext


def test_gpu_processor_passes(load_fixture):
    ctx = FakeSystemContext(commands={("ollama", "ps"): load_fixture("ollama_ps_gpu.txt")})
    result = check_ollama_processor(ctx)
    assert result.status == Status.PASS


def test_cpu_fallback_warns(load_fixture):
    ctx = FakeSystemContext(
        commands={("ollama", "ps"): load_fixture("ollama_ps_cpu_fallback.txt")}
    )
    result = check_ollama_processor(ctx)
    assert result.status == Status.WARN


def test_no_models_loaded_passes(load_fixture):
    ctx = FakeSystemContext(commands={("ollama", "ps"): load_fixture("ollama_ps_empty.txt")})
    result = check_ollama_processor(ctx)
    assert result.status == Status.PASS


def test_ollama_missing_skips():
    ctx = FakeSystemContext()
    result = check_ollama_processor(ctx)
    assert result.status == Status.SKIP
