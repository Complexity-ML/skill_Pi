# Routing top-k control contamination

## Problem pattern

In top-k routed MoE/lexical-routing ablations, it is not enough to verify the primary route. A bug can make controls look valid while silently using the baseline strategy for auxiliary routes.

Example contamination:

```text
random_shared = random primary route + Zipf-balanced auxiliary route
modulo_shared = modulo primary route + Zipf-balanced auxiliary route
```

With `top_k=2` and primary/auxiliary weights near 0.5, this makes the control neither random nor modulo. Metrics from such runs should be treated as contaminated.

## What to test

For every routing strategy and `top_k > 1`:

- `topk_token_to_expert[0]` follows the selected primary strategy.
- Every auxiliary route preserves the same control family.
- For a token, auxiliary route does not equal any earlier route.
- Random controls are deterministic across model construction.
- Modulo/round-robin auxiliaries use controlled offsets, not Zipf-balanced bin packing.

Minimal PyTorch assertions:

```python
assert torch.equal(modulo[1], (modulo[0] + 1) % num_experts)
assert torch.equal(random_a, random_b)
assert torch.all(random_a[0] != random_a[1])
```

## Diagnostic interpretation

If a short local run shows `random_shared` sharply beating `zipf_shared`, do not immediately call it noise. First check:

1. top-k route construction for all routes
2. parameter counts via meta-device model construction
3. shared/routed gates and top-k schedule
4. expert load/mass distribution for the local corpus
5. run names vs actual `run_config`/CSV output

Zipf load balance can be perfect while performance is still worse; that points to semantic grouping, shared-branch interaction, gate balance, or schedule — not necessarily load imbalance.
