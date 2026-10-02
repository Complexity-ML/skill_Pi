# Apple MPS lexical-object and attention-free ablations

Use this recipe when testing shared lexical objects, micro-experts, attention-free sequence mixers, or fixed-state decoding on a local Apple device before scaling to CUDA.

## Experimental discipline

1. Inspect saved `run_config.json`, not just run names. Confirm `backend=mps`, tokenizer/vocab, parameter count, batch, sequence length, seed, dataset, optimizer, and token budget. Do not compare with similarly named NVIDIA runs.
2. If the main repository is dirty, create an isolated worktree and branch before adding experimental modules.
3. Reuse an existing dense Apple baseline only when its full configuration matches. Label throughput as comparison to a saved run rather than a contemporaneous benchmark unless dense is rerun in the same sweep.
4. Write architecture tests first: output shape, gradients, token dependence, parameter matching, and config plumbing.
5. For a replacement sequence mixer, add a strict causality test: changing future inputs must not change any prefix outputs. Verify the realized `run_config.json` contains the intended mixer type so a hard-coded default cannot silently restore attention.
6. Run a 2-step target-device smoke, then a 20-step throughput screen. Run 200+ steps only if throughput remains competitive. Keep short-run results diagnostic.
7. If the user corrects an irrelevant comparison target (for example, a throughput number from another harness), drop it immediately and return to the matched saved/live baseline; do not keep defending or optimizing against it.

## o200k parameter matching

A per-layer lexical table of shape `vocab_size × rank` is expensive with a 200,019-token vocabulary. Prefer one table tied across layers, with layer-local projections. Verify Python module identity across layers and count deduplicated parameters from the instantiated model.

For a shared dense path plus four tensorized micro-experts, reducing shared width by `4 × expert_width` approximately finances the stored expert matrices at matched parameters. Always instantiate nearby integer widths and select the closest actual count.

## Dispatch-free micro-experts

For small expert banks on MPS, stacked projections can outperform Python loops, sorting, and scatter:

- project to `num_experts × expert_width` in one operation;
- reshape to an expert axis;
- compute expert outputs tensorially;
- select deterministic top-1 output;
- gate it as a narrow residual.

This computes more than sparse top-1 but avoids irregular dispatch overhead. Benchmark rather than assuming it wins. Interpret width-16/32 experts as narrow conditional residual adapters, not full standalone MoE experts.

## Attention-free causal convolution

A causal depthwise convolution mixer can replace Q/K/V attention while preserving the training harness:

- left-pad only by `(kernel_size - 1) × dilation`;
- use depthwise `Conv1d` for causal sequence mixing;
- follow with pointwise gated projections and an output projection;
- use a dilation cycle such as `1,2,4,...`;
- compute and report the resulting receptive field;
- verify no `q_proj`, `k_proj`, or `v_proj` exists.

When the runner historically calls the component `attention`, distinguish interface compatibility from architecture: an attention-free mixer can satisfy the same module signature without being self-attention.

## Fixed-state incremental inference

Training causality is not sufficient evidence for usable autoregressive inference. Before claiming an inference-ready mixer:

1. Implement a parallel prefill and a `[batch, 1, hidden]` decode path.
2. Cache exactly the `(kernel_size - 1) × dilation` normalized mixer inputs per layer; left-pad short prefills so cache shapes are fixed from the first decode token.
3. Under `no_grad`, update cache tensors in place and return the same tensors. Assert `data_ptr()` stability across multiple decode steps.
4. Compare logits from full-sequence forward against token-by-token cached decode at tight tolerances.
5. Benchmark cached decode against full-prefix recomputation with the real vocabulary head.
6. Describe the result as CUDA-Graph-friendly until capture and replay have actually succeeded on CUDA.

CUDA Graph readiness requires static shapes/control flow, long-lived input/state buffers, no `.item()` or CPU synchronization in the captured path, and stable memory addresses. A Mac can validate these structural invariants but cannot verify CUDA capture.

## Persistent-state ablations and numerical stability

A diagonal state can extend memory beyond a finite convolutional receptive field:

`state_t = decay * state_(t-1) + (1 - decay) * write_t * local_t`.

Use content-dependent low-rank write gates and keep persistent decode state in FP32. A global closed-form cumsum involving division by `decay**t` may have a finite forward but unstable gradients at long sequence lengths. Validate finite gradients at the target length, not only short unit tests.

A robust fallback is a statically chunked parallel recurrence:

- evaluate the closed form inside fixed chunks (for example 128 tokens);
- pass only the carry between chunks;
- clamp decay to a justified stable range;
- keep the chunk loop shape-dependent and data-independent so it can be unrolled/captured;
- retain a direct O(1) one-token decode transition.

Do not promote persistent state merely because it is theoretically longer-context. Compare it against convolution-only at a sequence length beyond the convolutional receptive field. If it loses both loss and throughput, keep convolution-only canonical and label state as an experimental long-context ablation.

## Matched-token long-sequence comparisons

When increasing sequence length while holding total tokens fixed, recompute steps as:

`steps = target_tokens / (batch × sequence_length × world_size)`.

This yields a valid within-length architecture comparison, but it changes the number of optimizer updates. Do not compare absolute loss across sequence lengths as if only context changed. Compare variants within the same length, batch, steps, and token budget.

For long runs, the local sample corpus must not be repeated hundreds of times. Move to a deduplicated streaming/sharded corpus and a genuinely held-out validation split before 1B-token claims.

## Routed vocabulary-head spikes

After removing QKV/KV-cache costs, the full vocabulary projection can become the decode bandwidth bottleneck—especially with o200k. Before claiming extreme token rates, calculate the ideal weight-streaming bound from `memory_bandwidth / bytes_read_per_token`; include the LM head separately because it may dominate total parameters.

A useful disposable spike partitions vocabulary rows into static blocks and evaluates:

`hidden → block router → top-k blocks → gathered local logits`.

Measure synchronized batch-1 latency against the dense head and verify that every selected local logit exactly equals the corresponding dense logit. Report candidate count, approximate weight fraction, p50/p95 latency, and speedup. Interpret the result carefully:

- fewer selected weights do not imply proportional speedup because TopK, Gather, dispatch, and small matmuls can dominate;
- random routing validates mechanics only, not language-model quality;
- train/evaluate target-block Recall@K before replacing the dense head;
- prefer learned lexical/embedding clusters over arbitrary contiguous token-ID blocks;
- preserve exact dense training loss or use a mathematically corrected sampled/hierarchical objective—do not silently switch to locally normalized training;
- treat ONNX compatibility as provisional until the target runtime supports and efficiently executes TopK/Gather/static local matmul;
- expect a fused route+gather+matmul kernel to be necessary for large deployment gains.

Keep this as a separate spike until quality, calibration, and target-device performance are all validated; do not contaminate the canonical architecture or headline ablation prematurely.

## Scaling to H100/H200/B200

Do not guess throughput from Apple results or theoretical FLOPs. Prepare hardware-specific launchers that:

- smoke the exact target batch and sequence length;
- verify finite loss and realized config;
- calculate steps using actual world size;
- print ETA from measured stabilized throughput;
- run the dense/live baseline first;
- disable checkpoints for exploratory sweeps unless requested;
- preserve metrics immediately and tolerate post-success teardown failures only when the final metrics step is complete.

A useful paper-stage suite isolates: matched dense QKV, convolutional dense, convolution + lexical object, and convolution + object + micro-experts. Run cheaper screening budgets before 1B-token finalists.

## Interpretation safeguards

- “Lexically conditioned” means token identity modulates or selects a residual at each layer. It does not mean the whole model is purely lexical; the shared path and sequence mixer remain contextual.
- Small experts are defensible as residual adapters, not as standalone replacements for the shared transformation.
- A 200-step local result is evidence for ranking prototypes only, not a scaling or generalization claim.
- Preserve failed numerical runs under distinct names for provenance; rerun corrected implementations under new names rather than overwriting evidence.
- Preserve raw CSVs immediately and report train loss, eval loss, last throughput, and mean throughput excluding warm-up/evaluation-disturbed intervals.
