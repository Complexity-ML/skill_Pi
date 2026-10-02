# Hybrid threshold search and archived-throughput reproduction

## Source-first identification

When a user refers to “the 126k model” or another remembered result, read the paper table and archived `run_config.json` before naming the mechanism. Do not infer which row they mean from memory. Record separately:

- best quality control;
- fastest control;
- dense-attention control;
- exact loss and throughput of each.

A remembered throughput can belong to an attention-free additive control rather than GQA. Misattribution sends the entire ablation in the wrong direction.

## Reproduce the archived execution path

Before diagnosing an architectural throughput regression, diff the live and archived configs. High-impact fields include:

- `grad_ckpt` / `--no-grad-ckpt`;
- custom kernels (`auto` versus forced `false`);
- active Triton backend reported in `run_config.json`;
- compile mode;
- BF16, batch size, sequence length, loss backend/chunk size;
- parameter-matching width.

A run with checkpointing enabled and Triton disabled can look tens of percent slower while the architecture is unchanged. Verify backend telemetry and GPU utilization, then compare stabilized windows (for example step 50+) rather than warm-up steps 1–20.

## Minimal-attention threshold protocol

When a fixed-state or convolutional model remains behind dense attention:

1. Preserve the validated substrate and name the new operation honestly.
2. If the mechanism computes `softmax(R W^T) V`, describe it as W/R/V attention even if the FlashAttention API calls its arguments `q`, `k`, and `v`.
3. Test one layer to measure marginal effect and overhead.
4. If the user wants the threshold quickly, test the maximum compatible attention count next, preserving any protected context layers.
5. If the maximum beats the dense control, descend by binary search to the minimum count. If it does not, redesign the attention mechanism rather than spending on all intermediate counts.
6. Parameter-match every arm and pre-register layer positions. For widths whose parameter count is affine, instantiate only two adjacent widths on `meta`, derive the per-width slope, solve for the nearest width, then instantiate that candidate once for verification. Do not rebuild hundreds of ~100M models in a brute-force sweep.
7. If one lexical W/R/V head yields only a marginal full-budget gain, increase retrieval capacity before adding surrounding mechanisms: use multiple contextual read heads with fewer shared lexical write/value heads (for example 8R/2W), preserve lexical W anchoring and contextual V, and test causal/full-incremental cache equivalence. This is a redesign gate, not evidence that more copies of the weak single-head mechanism will work.
8. Audit attention-logit magnitude before any expensive run. L2-normalizing both R and W and then retaining SDPA's default `1/sqrt(d_h)` scale bounds logits to roughly `[-1/sqrt(d_h), +1/sqrt(d_h)]`; at long sequence lengths this makes softmax nearly uniform and turns retrieval into averaging. Use an explicit learned cosine temperature (with a justified selective initialization), or RMS-style normalization that preserves vector norm, and add a failing test for the intended initial scale.
9. Compare occurrence identity with the dense control. A mostly token-ID-derived W needs an explicit contextual gate per write head and positional separation (for example RoPE applied consistently to current/cached W and R). Test full-sequence versus incremental equivalence with the correct cache position offset.
10. If the architecture claims tied lexical objects, verify object identity, not merely equal values: every W/R/V layer should reference the exact shared rank-r `nn.Embedding`, then project it through a small lexical forge. Ensure the builder performs this attachment after MLP table tying and verify it with an identity assertion.
11. Distinguish the **maximum compatible with protected substrate layers** from the **true global maximum**. An 8/10 arm that preserves two WVR/conv layers answers whether attention can augment that substrate; it does not answer whether the attention formulation itself matches the 10/10 dense control. If 8/10 improves substantially but remains behind, run a parameter-matched 10/10 arm before redesigning again. Only then descend to find the minimum.
12. Treat lexical anchoring as a hypothesis, not an identity requirement. If many layers of lexically centered attention regress held-out loss, invert the composition: start from a complete contextual W/R/V path with standard RoPE and `1/sqrt(d_h)` scaling, then add the tied lexical projection as a per-write-head residual initialized at exactly zero: `W = W_context + tanh(g_head) * W_lex`. This preserves dense-attention capacity at initialization and forces the lexical branch to earn nonzero influence. Test the zero gate and shared-table object identity before training.
13. Do not infer success from final training loss shown in the progress bar. Extract the last finite held-out evaluation row mechanically; scheduled rows between evaluations legitimately contain `eval=nan`. A lower train loss with worse held-out loss is a negative result, not evidence that more training or more heads necessarily helps.
14. Before declaring a residual gap architectural, diff the *normalization path* against the dense control. Standard scaling and matching head counts are not enough: a control may apply learned RMSNorm independently to each contextual read/write head before RoPE. Add the same operation under architecture-native names (`read_norm`, `write_norm`), test its presence and full/incremental equivalence, then re-run at matched parameters. In the reference 98.2M/100M-token case, contextual 10/10 W/R/V with zero-initialized lexical residual scored 4.826292 versus GQA 4.820476; adding per-head RMSNorm moved held-out loss to 4.706118 at 118,416 tok/s versus GQA's 4.820476 at 111,355 tok/s. This large reversal means QK/RW normalization is a first-class ablation, not an implementation footnote.
15. When a zero-initialized lexical residual is attached to a dense-equivalent contextual path, the aggregate result does **not** prove that the lexical residual contributed. Without a saved checkpoint or explicit gate telemetry plus ON/OFF evaluation, attribute the win to the complete W/R/V configuration and isolate lexical credit in a separate gate-off control.

Do not place generic Flash attention at the center and demote the original mechanism to an unmeasured residual while claiming the original architecture still won. When a mathematical audit reveals that an expensive active run cannot test the intended mechanism (for example near-uniform logits), stop it promptly, fix under RED-GREEN tests, re-match parameters, smoke throughput/stability, and only then relaunch.

## Runtime and artifact handling

- A `PyGILState_Release` or similar interpreter-finalization abort after `Metrics saved` is a teardown failure, not automatically a failed experiment.
- Verify the CSV is non-empty, extract the last finite evaluation row, inspect the service/GPU state, and archive `metrics.csv` plus `run_config.json` before deciding validity.
- Progress rows may show `eval=nan` between scheduled evaluations; use the last finite eval mechanically.
- If no checkpoint was requested, do not imply that a final checkpoint exists.
