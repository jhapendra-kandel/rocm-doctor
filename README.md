# rocm-doctor

[![CI](https://github.com/jhapendra-kandel/rocm-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/jhapendra-kandel/rocm-doctor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](pyproject.toml)
[![Release](https://img.shields.io/github/v/release/jhapendra-kandel/rocm-doctor?include_prereleases)](https://github.com/jhapendra-kandel/rocm-doctor/releases)

A diagnostic CLI for AMD GPU (ROCm) local LLM serving setups — the "why is my
GPU not being used" and "why did my driver just die" checks that currently
take hours of manual `dmesg`/`lspci`/`modprobe.d` spelunking to figure out.

**Status: pre-alpha, working v0.1.** All 7 checks below are implemented and
unit-tested (fixture-driven, no real GPU/root needed to run the suite). Not
yet published to PyPI. See [PLAN.md](PLAN.md) for scope and roadmap.

## Why this exists

AMD's official ROCm hardware-support list and Ollama's supported-target list
don't agree with each other, several failure modes only show up on headless
(no-monitor) boxes, and the fixes for them live scattered across forum posts,
not one place. Multiple independent 2026 writeups describe ROCm setup/debug
sessions eating 10+ hours. `rocm-doctor` exists to collapse that into a single
command that tells you *which* known failure mode you're hitting and what to
run to fix it.

## Checks implemented (v0.1)

- **kernel-version** — flags the Ubuntu 24.04 GA kernel (6.8.x) as risky for
  very new GPU generations; recommends `linux-generic-hwe-24.04`
- **display-core-init-failure** — detects the headless (no-monitor) amdgpu
  Display-Core init failure signature in `dmesg` (`Fatal error during GPU
  init`) and gives the `dc=0` modprobe fix
- **blacklist-amdgpu-leftover** — catches a leftover `blacklist-amdgpu.conf`
  from an abandoned `amdgpu-dkms` install that silently breaks every boot
- **rocminfo-gpu-agent** — confirms `rocminfo` sees a bound GPU agent
- **ollama-host-binding** — flags `OLLAMA_HOST` still bound to 127.0.0.1
  (invisible from inside Docker) and gives the systemd override fix
- **ollama-processor-fallback** — parses `ollama ps` for the `100% CPU`
  silent-fallback tell instead of `100% GPU`
- **ram-vram-headroom** — compares system RAM vs. GPU VRAM and warns when a
  full-RAM-copy model load is likely to thrash

## Install

```bash
git clone https://github.com/jhapendra-kandel/rocm-doctor.git
cd rocm-doctor
pip install -e .
rocm-doctor
```

Not published to PyPI yet — pre-alpha. Run `rocm-doctor --json` for
machine-readable output, `rocm-doctor --no-color` for plain text.

## Contributing

Hit a failure mode this tool doesn't catch yet? That's the actual
growth path for this project — see [CONTRIBUTING.md](CONTRIBUTING.md) for
how to turn it into a new check, and please include your `dmesg`/`lspci
-vvv`/`uname -r` output when opening an issue (there's an issue template
for it).

## License

MIT
