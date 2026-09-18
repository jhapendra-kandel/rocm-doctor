# rocm-doctor — Project Plan

## Problem statement

Running local LLM inference (Ollama, llama.cpp, vLLM) on AMD consumer/
workstation GPUs via ROCm works, but getting there is unreliable:

- AMD's official ROCm support matrix and Ollama's own supported-target list
  disagree — some GPUs (gfx1030, gfx1102, gfx1150/1151, and very new cards
  like RDNA4 parts) work in practice before AMD or the driver docs formally
  say so.
- Headless (no-monitor) boxes hit a distinct driver failure class: Display
  Core init failing while compute/VRAM init succeeds, producing a cryptic
  `Fatal error during GPU init` with no obvious link to "no monitor attached."
- Leftover config from an earlier failed `amdgpu-dkms` install (e.g. a
  `blacklist-amdgpu.conf` someone renamed instead of deleting) can silently
  keep breaking every boot afterward.
- Docker-based LLM tooling defaults (`OLLAMA_HOST=127.0.0.1`) make Ollama
  invisible from inside a container with zero error message — it just looks
  like Ollama isn't running.
- Silent CPU fallback: a model can load and run on CPU instead of GPU with
  no error, only visible via `ollama ps`'s PROCESSOR column — easy to miss,
  and looks like a hang/perf-bug otherwise.
- Host RAM vs. VRAM headroom: on RAM-constrained boxes, model loaders make a
  full private RAM copy before pushing to VRAM — loading a model sized wrong
  for available system RAM causes swap thrash that looks like a crash.

No single existing tool checks all of these. Generic GPU monitoring tools
(nvtop-style, rocm-smi) show current state but don't diagnose *why* the
state is wrong.

## Goal

A single CLI (`rocm-doctor`) that runs a battery of checks against a host's
kernel, driver, modprobe config, and running Ollama service, and reports:
1. Which known failure mode (if any) is present
2. The exact fix command(s)
3. A clean bill of health if nothing's wrong

Non-goals for v1: training-workload diagnostics, multi-GPU topology,
non-Ollama inference servers (llama.cpp/vLLM support is a later phase).

## Architecture (planned)

- Language: Python (fast to iterate, easy `subprocess` calls to `dmesg`,
  `lspci`, `uname`, `rocminfo`, `ollama ps`), packaged as a single-file
  installable CLI (`pipx install rocm-doctor` target).
- Each check is an independent, isolated function returning a structured
  result (pass / fail / warn + human-readable fix). No check's failure
  blocks the others from running.
- No telemetry, no network calls except an optional `--check-updates` flag.
  Everything runs locally against local system state.
- Output: human-readable by default, `--json` for CI/scripting use.

## Phases

### Phase 0 — Scaffolding (current)
- Repo structure, README, PLAN, LICENSE, CI skeleton
- Package layout (`src/rocm_doctor/`), `pyproject.toml`, entry point
- Empty check registry + one working example check (kernel version)

### Phase 1 — Core checks (headless-server class of bugs)
- Kernel version vs. HWE requirement detection
- `dmesg` grep for Display-Core init failure signature
- `blacklist-amdgpu.conf` / modprobe.d leftover detection
- `rocminfo` reachability + GPU agent listing
- Unit tests against captured/fixture `dmesg` and `lspci` output (no real
  GPU required to run the test suite — critical for CI)

### Phase 2 — Ollama-specific checks
- `OLLAMA_HOST` binding check (systemd override.conf parsing)
- `ollama ps` PROCESSOR column parser + CPU-fallback warning
- Host-RAM-vs-model-size headroom heuristic

### Phase 3 — Polish for real adoption
- `--fix` flag that prints (never auto-runs) the exact remediation commands
- GitHub Actions CI: lint, type-check, test matrix
- Publish to PyPI
- README with a real "before/after" demo GIF against a real failure

### Phase 4 — Community
- Contribution guide for adding new checks (this is the actual OSS-growth
  lever — checks should be crowd-sourced as new failure modes get reported)
- Issue templates prompting for `dmesg`/`lspci` output so new failure
  signatures can become new checks

## Success criteria

- v0.1: running `rocm-doctor` on the box this project is modeled after
  (Ryzen 7 9700X + Radeon AI PRO R9700, Ubuntu 24.04 HWE) correctly
  identifies a clean bill of health, and correctly flags each of the 5
  known failure modes above when reproduced/simulated via fixtures.
- v1.0: at least one external contributor has added a check for a failure
  mode this project didn't originally know about.
