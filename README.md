# rocm-doctor

A diagnostic CLI for AMD GPU (ROCm) local LLM serving setups — the "why is my
GPU not being used" and "why did my driver just die" checks that currently
take hours of manual `dmesg`/`lspci`/`modprobe.d` spelunking to figure out.

**Status: pre-alpha, planning stage.** See [PLAN.md](PLAN.md) for scope and
roadmap.

## Why this exists

AMD's official ROCm hardware-support list and Ollama's supported-target list
don't agree with each other, several failure modes only show up on headless
(no-monitor) boxes, and the fixes for them live scattered across forum posts,
not one place. Multiple independent 2026 writeups describe ROCm setup/debug
sessions eating 10+ hours. `rocm-doctor` exists to collapse that into a single
command that tells you *which* known failure mode you're hitting and what to
run to fix it.

## Planned checks (v0.1)

- Kernel version vs. the HWE/GPU-generation requirement for your card
- `lspci` GPU detection vs. `rocminfo` agreement (driver bound vs. not)
- Headless Display-Core init failure signature in `dmesg`
  (`Fatal error during GPU init`, `error -22`)
- Leftover `blacklist-amdgpu.conf` from an abandoned `amdgpu-dkms` install
- Ollama's `OLLAMA_HOST` binding (127.0.0.1 vs 0.0.0.0 — invisible from
  Docker otherwise)
- `ollama ps` PROCESSOR column check — silent CPU fallback despite VRAM
  being free
- Host-RAM-vs-VRAM headroom check (predicts thrash/swap before you `ollama
  pull` a model too big for available system RAM)

## Install

Not published yet — pre-alpha.

## License

MIT
