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

### Phase 0 — Scaffolding — ✅ done (2026-09-18)
- Repo structure, README, PLAN, LICENSE, CI skeleton
- Package layout (`src/rocm_doctor/`), `pyproject.toml`, entry point
- Empty check registry + one working example check (kernel version)

### Phase 1 — Core checks (headless-server class of bugs) — ✅ done (2026-09-18)
- Kernel version vs. HWE requirement detection
- `dmesg` grep for Display-Core init failure signature
- `blacklist-amdgpu.conf` / modprobe.d leftover detection
- `rocminfo` reachability + GPU agent listing
- Unit tests against captured/fixture `dmesg` and `lspci` output (no real
  GPU required to run the test suite — critical for CI)

### Phase 2 — Ollama-specific checks — ✅ done (2026-09-18)
- `OLLAMA_HOST` binding check (systemd override.conf parsing)
- `ollama ps` PROCESSOR column parser + CPU-fallback warning
- Host-RAM-vs-model-size headroom heuristic

### Phase 3 — Polish for real adoption — partially done
- ✅ GitHub Actions CI: lint (ruff), test matrix (3.10/3.11/3.12)
- ✅ README badges (CI/License/Python/Release)
- ✅ Tagged + released v0.1.0 on GitHub (marked prerelease — honest about
  no real-hardware validation yet)
- ⬜ **Real-hardware validation** — every check is fixture-tested only;
  none has run against an actual ROCm/AMD GPU host yet. This is the
  single most important thing left before the prerelease flag can come
  off. Candidate host: the `abc-gpu` box (see root workspace `CLAUDE.md`
  for specs/access).
- ⬜ `--fix` flag that prints (never auto-runs) the exact remediation
  commands as a single copy-pasteable block (checks already carry a
  `fix` field — this is just a CLI flag to print them cleanly together)
- ⬜ Publish to PyPI (`pipx install rocm-doctor`) — hold until real-hardware
  validation, per user's own priority call in the 2026-09-18 session
- ⬜ README "before/after" demo GIF/asciinema against a real failure

### Phase 4 — Community — partially done
- ✅ CONTRIBUTING.md (report-a-failure-mode + add-a-check rules)
- ✅ GitHub issue template for new failure modes (structured uname/dmesg/
  lspci/rocminfo/ollama-ps fields)
- ✅ Repo description + topics set for discoverability
- ⬜ Submit to awesome-rocm / awesome-ollama / awesome-llmops lists
- ⬜ Origin-story write-up (the R9700 headless-Display-Core debugging
  session) — hold for public launch push, after hardware validation
- ⬜ Answer real GitHub issues on Ollama/ROCm repos where relevant,
  linking the tool only where it actually solves the reported problem

## Next session: start here

1. Get access to a real AMD/ROCm host (abc-gpu is the candidate) and run
   `rocm-doctor` against it for real. Confirm each of the 7 checks fires
   (or correctly doesn't fire) against actual system state, not just
   fixtures. Fix anything that misfires — this is the #1 open item.
2. Once validated: remove the "prerelease" flag from the GitHub release
   (or cut a new v0.2.0), consider PyPI publish.
3. Only after that: the public-launch push (origin-story post, r/ROCm /
   r/LocalLLaMA / Show HN, awesome-list PRs) — see the growth-strategy
   discussion in this project's chat history (2026-09-18 session) for
   the full reasoning on why hardware validation gates this.

## Success criteria

- v0.1: running `rocm-doctor` on the box this project is modeled after
  (Ryzen 7 9700X + Radeon AI PRO R9700, Ubuntu 24.04 HWE) correctly
  identifies a clean bill of health, and correctly flags each of the 5
  known failure modes above when reproduced/simulated via fixtures.
- v1.0: at least one external contributor has added a check for a failure
  mode this project didn't originally know about.
