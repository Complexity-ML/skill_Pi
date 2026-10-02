# GPU smoke and evidence protocol

## Setup gate

Before a paid run, record GPU model/memory, driver, CUDA, PyTorch, Triton, free disk, source revision, and tokenizer checksum. Run focused CPU/GPU invariant tests before training.

Triton JIT needs a working C toolchain and Python development headers. If its helper compilation fails around `cuda_utils.c`, verify `Python.h`, GCC, and `libcuda.so.1`; install the matching Python development package rather than disabling compilation blindly.

## Smoke gate

1. Run one arm at a time.
2. Use the same batch, context, precision, compile mode, kernels, and loss backend.
3. Keep the scientific LR schedule out of a very short smoke unless its warmup horizon is preserved. A 5% warmup over 120 steps reaches peak LR in 6 steps, unlike a 3052-step run with about 152 warmup steps.
4. For throughput-only smoke, use a clearly labeled conservative LR.
5. Parse metrics during execution and terminate on first non-finite loss, gate, gradient, or parameter statistic.
6. Ignore compile/warmup steps; summarize a fixed steady-state window.

## Full evidence gate

Archive:

- raw per-step metrics;
- resolved config;
- exact source revision;
- final checkpoint;
- learned gates/mechanism diagnostics;
- tokenizer checksum;
- software/hardware manifest;
- repeated throughput samples.

A progress-bar value or one evaluation-row throughput is descriptive only. For hardware migration, rerun every arm on the new accelerator and keep prior hardware results in a separate table.
