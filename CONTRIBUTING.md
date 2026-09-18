# Contributing to rocm-doctor

The main way this project grows is other people's failure modes becoming
new checks. If `rocm-doctor` gave you a clean bill of health but your
AMD/ROCm setup was actually broken (or vice versa — a false positive),
that's exactly the kind of report that's useful.

## Reporting a new failure mode

Open an issue using the "New failure mode" template and include:

- `uname -r`
- `dmesg | grep -i amdgpu` (or the full `dmesg` if the amdgpu lines alone
  don't show the problem)
- `lspci -vvv` (at least the GPU device's section)
- `rocminfo` output if it runs at all
- `ollama ps` output if relevant
- What you expected vs. what actually happened

You don't need to know the fix — just the symptom and the raw command
output. Fixture data from your report may get turned directly into a
test fixture under `tests/fixtures/`.

## Adding a check yourself

Every check in `src/rocm_doctor/checks/` follows the same shape:

```python
def check_something(ctx: SystemContext) -> CheckResult:
    output = ctx.run(["some", "command"])
    if output is None:
        return CheckResult(NAME, Status.SKIP, "why it couldn't run")
    if <failure signature present>:
        return CheckResult(NAME, Status.FAIL, "what's wrong", fix="the exact fix command")
    return CheckResult(NAME, Status.PASS, "what's fine")
```

Rules that keep this tool trustworthy:

1. **Never call `subprocess`/`open()` directly in a check** — always go
   through `ctx.run()` / `ctx.read_file()` / `ctx.file_exists()`. That's
   what makes every check testable with `FakeSystemContext` and fixture
   text instead of requiring a real GPU.
2. **A check must never raise.** Missing commands/files are a normal,
   expected case — return `Status.SKIP` with a clear reason, don't let an
   exception propagate (the CLI catches broken checks defensively, but a
   check shouldn't rely on that).
3. **`fix` should be a real, copy-pasteable command**, not a vague
   suggestion — the whole point of this tool is turning "something's
   wrong" into "run this."
4. **Ground new checks in a real, reproducible failure**, not a
   theoretical one. If you're not sure a failure signature is stable
   across driver versions, say so in the check's docstring — false
   positives erode trust in every other check.
5. Add the check to `ALL_CHECKS` in `src/rocm_doctor/checks/__init__.py`
   and write tests in `tests/test_<check>.py` using fixture files under
   `tests/fixtures/` (see existing tests for the pattern).

## Running the test suite locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ruff check src tests
pytest -v
```

CI runs the same two commands on Python 3.10/3.11/3.12 — a PR won't be
mergeable if either fails.
