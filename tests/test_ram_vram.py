from rocm_doctor.checks.base import Status
from rocm_doctor.checks.ram_vram import check_ram_vram_headroom
from rocm_doctor.system import FakeSystemContext


def test_low_ram_relative_to_vram_warns(load_fixture):
    ctx = FakeSystemContext(
        files={"/proc/meminfo": load_fixture("meminfo_low_ram.txt")},
        commands={("rocm-smi", "--showmeminfo", "vram"): load_fixture("rocm_smi_vram.txt")},
    )
    result = check_ram_vram_headroom(ctx)
    assert result.status == Status.WARN


def test_high_ram_relative_to_vram_passes(load_fixture):
    ctx = FakeSystemContext(
        files={"/proc/meminfo": load_fixture("meminfo_high_ram.txt")},
        commands={("rocm-smi", "--showmeminfo", "vram"): load_fixture("rocm_smi_vram.txt")},
    )
    result = check_ram_vram_headroom(ctx)
    assert result.status == Status.PASS


def test_missing_data_skips():
    ctx = FakeSystemContext()
    result = check_ram_vram_headroom(ctx)
    assert result.status == Status.SKIP
