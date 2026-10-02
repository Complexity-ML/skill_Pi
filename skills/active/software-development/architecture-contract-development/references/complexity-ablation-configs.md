# Complexity ablation config pattern

Use this reference when the user asks for ML architecture ablations in Complexity-style repos.

## Lessons

- Inspect the actual module wiring before inventing new controls. In the TokenRoutedMLP case, the shared expert is a global/free branch computed for all tokens and summed/gated with routed output:
  - `shared_out = SharedSwiGLU(x)` for every token
  - `routed_out = Expert[token_id](x)` or top-k routed blend
  - `out = shared_gate * shared_out + routed_gate * routed_out`
- Do not invent a `shared_by_pair` variant unless explicitly requested after inspecting this wiring. The global shared branch can already learn common or group-correlated structure; ablations should first test global shared vs no-shared vs dense controls.
- For reviewer-facing ablations, prefer explicit controls:
  - Zipf + global shared baseline
  - Zipf no-shared, matched parameter count when possible
  - Modulo + global shared
  - Random + global shared
  - Round-robin + global shared
  - Shared-only dense control
  - Same-size non-routed dense residual control
- Short local runs are smoke tests and setting diagnostics, not evidence. If dense wins early, compare against known-good settings before concluding: routed/shared width balance, routed gate, top-k schedule, batch/seq, and data split can dominate 200-step behavior.

## Known-good diagnostic pattern from session

A previous local signal where TR beat dense used a more balanced routed/shared setting than the large-shared tiny-routed 300M profile:

```text
routed intermediate ~= shared intermediate
routed_gate_init ~= 0.5
top_k_primary_weight ~= 0.5
top_k_primary_weight_final ~= 0.75
seq_len ~= 256 for local smoke
```

For a 100M o200k ablation family, verify parameter counts with a meta-device model build before launching long runs. In the session, a first no-shared config accidentally dropped to ~82M parameters; increasing routed width made it matched to the ~98M shared baseline.

## Verification checklist

- Tests assert routing strategies and parser/config flags before writing long-run scripts.
- Configs include explicit run names/save dirs and token budget math.
- Parameter counts are printed for all variants before launch.
- Local diagnostic scripts override dataset/steps/batch/seq/save settings without changing the long-run configs.
- Summaries report train loss, last eval loss, best eval loss, and throughput; interpret early results cautiously.
