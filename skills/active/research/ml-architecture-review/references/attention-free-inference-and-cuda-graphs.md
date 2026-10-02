# Attention-free inference and CUDA Graph review

Use this checklist when reviewing or prototyping a causal LM that replaces QKV attention with convolution, recurrence, retention, or an SSM.

## Separate the claims

Never collapse these into one claim:

1. **Training/full-sequence correctness**: causal outputs, parallel prefill, useful loss.
2. **Incremental inference correctness**: fixed per-layer state, no prefix recomputation, step logits match full-sequence logits.
3. **Graph-friendly design**: static shapes/control flow, preallocated state, stable addresses, no CPU/GPU synchronization in the captured path.
4. **CUDA Graph verification**: actual capture and replay on the target CUDA/PyTorch stack, with numerical and throughput checks.

Say “CUDA-Graph-ready by design” until real CUDA capture succeeds. A successful MPS/eager run is not CUDA Graph evidence.

## QKV replacement contract

QKV attention provides content-addressed global access and mature KV-cache inference. A replacement must define how it carries prefix information and what it sacrifices:

- Causal convolution: parallel and simple, but finite receptive field.
- Fixed recurrent/retention state: constant decode state, but compresses history.
- SSM/associative scan: parallel training plus recurrent decode, often needs fused scan kernels.
- Hybrid local convolution + persistent state: robust default for attention-free local and long-range mixing.

Always calculate the effective receptive field for finite-context mixers and compare it with the evaluated sequence length.

## Required inference tests

Before calling an attention-free LM inference-ready:

1. Assert the target model instantiates no `q_proj`, `k_proj`, or `v_proj` parameters.
2. Test strict causality by changing future tokens and comparing past outputs.
3. Compare full-sequence logits with token-by-token cached logits using tight tolerances.
4. Verify each layer’s state has fixed shape after prefill.
5. Verify cache/state pointers remain stable across decode steps if graph replay depends on fixed addresses.
6. Benchmark cached decode against explicit prefix recomputation.
7. Test prompt prefill followed by generation, not only one-token synthetic mixer calls.

For a dilated convolution of kernel size `k` and dilation `d`, cache the previous `(k - 1) * d` mixer inputs per layer. The total receptive field across residual stacked layers is `1 + sum_l((k_l - 1) * d_l)`.

## CUDA Graph capture checklist

Use static `[batch, 1]` decode inputs and preallocated per-layer states. During capture/replay:

- no `.item()`, CPU-dependent branch, dynamic shape, or data-dependent Python loop;
- no growing cache or `torch.cat` over the entire prefix;
- state updates occur in-place or are copied into stable input buffers inside the graph;
- warm up on a side stream;
- retain long-lived references to static inputs, states, and outputs;
- capture separate graphs or buckets for required batch/prefill shapes;
- verify multiple replays, not capture alone;
- compare replay logits/state against eager decode;
- benchmark eager versus replay on the target GPU.

Ops that look graph-friendly (`Linear`, convolution, embedding, gather, einsum) still require real capture verification on the target software/hardware stack.

## Research framing

Treat short matched-token runs as diagnostics, especially when evaluation comes from a small local corpus. Report exact parameters, token budget, seed, held-out construction, raw metrics, and whether throughput baselines were contemporaneous. Do not generalize a local convolutional win at sequence length 256 to long-context language modeling without longer-context tests and a persistent-state mechanism.
