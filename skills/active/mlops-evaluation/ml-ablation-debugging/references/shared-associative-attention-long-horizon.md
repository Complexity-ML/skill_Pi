# Shared associative attention: session-derived ablation lessons

## Why this reference exists

A fixed-state associative attention upgrade was evaluated against GQA. The session exposed workflow failures that generalize to architecture research.

## Correct experimental sequence

1. Keep the candidate mechanism outside the production model behind the same causal fixed-state interface.
2. Test exact equivalence at the neutral setting.
3. Iterate one delta at a time; here, a single tied/shared learned contextual-address projection was preferable to immediately adding separate Q/K projections or multi-head state.
4. If production lost on held-out LM loss, compare matched LM loss first. Synthetic recall/induction remains a sanity check, not the selection criterion.
5. Integrate the standalone winner into the full model only after it wins the relevant proxy.
6. Match parameters by reallocating capacity rather than silently increasing model size.
7. Run the full-size pilot with the eventual long-run scheduler horizon.

## Scalar-gate bottleneck and stronger shared fusion

Checkpoint inspection separated address learning from context usage:

- the contextual-address mix grew substantially, proving that the addressing path was being optimized;
- the single global context output gate remained very small, so the retrieved signal was globally throttled.

The next useful intervention was therefore not another gate sweep. Replace the one-scalar residual with a shared token-and-dimension-dependent fusion such as:

```text
retrieved = associative_memory(hidden, token_ids, fixed_state)
fused = W_out(silu(W_gate(hidden)) * W_value(retrieved))
```

Keep this fusion shared across selected layers, keep the recurrent state fixed-size, and remove the old scalar output gate. Validate that all fusion projections receive gradients and that no deleted/unused inherited projection remains in `named_parameters()`.

A 3052-step miniature FineWeb comparison was materially more reliable than the earlier 500-step pilot: the shared fusion retained a held-out-loss advantage over iso-parameter GQA at every measured checkpoint through step 3052, while paying a modest throughput cost. This authorizes full-model integration, not an immediate victory claim; the full-size matched run remains the final gate.

## Critical scheduler-horizon failure

A 500-step full-size pilot appeared to beat GQA strongly:

- candidate held-out loss: 6.068409
- GQA held-out loss: 6.329749

But both pilots used schedules terminating at step 500. The subsequent 3052-step / 100M-token run used a schedule terminating at step 3052 and finished at:

- candidate held-out loss: 4.921405
- GQA historical matched-budget loss: 4.820476

Thus, the pilot was not a valid prefix predictor. A short pilot must retain the full training horizon in its LR scheduler, or it cannot authorize an expensive complete run.

## Compilation pitfall

Do not convert a trainable GPU tensor to a Python scalar in `forward` to choose a path. This caused graph breaks and an apparent ~8% throughput loss. Replace configuration-time decisions with a static Python boolean set in `__init__`; keep trainable tensor arithmetic inside the graph. In this case throughput recovered from ~115.9k to ~126.1k tok/s without changing the attention mathematics.

## Teardown crashes

Streaming dataset/PyArrow threads may abort during Python finalization after training. Treat the run as valid only after verifying all of:

- target step/token count reached;
- non-empty metrics CSV exists;
- expected checkpoint exists with plausible byte size;
- final or latest scheduled evaluation row is present.

Do not infer training failure solely from systemd's failed status when the traceback occurs after artifact writes.

## Communication/workflow corrections

- When the user asks to upgrade an existing attention, do not divert into checkpoint transfer, frozen grafting, auxiliary curricula, or retraining an already-losing baseline.
- Lead with the exact run, budget, active state, usefulness, and decisive metric.
- Do not foreground already-known synthetic successes when the unresolved blocker is final LM loss.
- Never claim the architecture has passed the long-run gate from an unmatched short-horizon pilot.
