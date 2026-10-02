# Token-Routing Ablation Controls: Lessons

This reference captures reusable details from a token-routed MLP ablation session.

## Scenario

The goal was to create 100M ablation launchers for variants such as:

- Zipf-balanced token routing + global shared expert
- Zipf no-shared matched-param control
- Modulo/random/round-robin routing controls with the same shared expert
- Shared-only and dense residual controls

Short local Mac/MPS runs initially showed surprising results: random/shared and dense controls appeared to beat Zipf/shared. This prompted an invariant audit before trusting the numbers.

## Durable Lessons

### 1. Test top-k route purity

Bug found: with `top_k=2`, the primary route used the requested routing strategy, but the auxiliary route was always Zipf-balanced. That meant `random_shared` was actually:

```text
random primary + Zipf-balanced auxiliary
```

and modulo/round-robin controls were also contaminated. The fix was to make auxiliary routes preserve the control strategy:

```text
zipf        -> Zipf-balanced auxiliary, distinct from primary
random      -> deterministic random auxiliary, distinct from primary
modulo      -> shifted primary, e.g. (primary + k) % num_experts
round_robin -> shifted primary, e.g. (primary + k) % num_experts
```

Add a test that inspects `topk_token_to_expert`, not just `token_to_expert`.

### 2. Verify parameter matching after config edits

For shared/no-shared ablations, removing the shared expert can shrink the model substantially. Instantiate on `torch.device('meta')` and print/count params for every variant before launching.

Example target shape from the session:

```text
zipf_shared             ~98.2M token_routed shared=True  inter=768  shared_inter=768
zipf_no_shared          ~98.2M token_routed shared=False inter=1536 shared_inter=768
dense_residual          ~98.2M swiglu       shared=False inter=1536
shared_only             smaller by design; isolates shared branch only
```

### 3. Recompute token budget for actual world size

A step count calibrated for 8 GPUs is wrong on 1 GPU.

Example:

```text
954 steps x 8 x batch 256 x seq 2048 = ~4.001B tokens
954 steps x 1 x batch 256 x seq 2048 = ~0.500B tokens
```

For 1×H200 at 4B tokens/run:

```text
3815 steps x batch 512 x seq 2048 = 4.00031744B tokens
7 runs = 28.00222208B tokens
```

But always smoke the intended batch/sequence on the real hardware. In this session, `batch=512, seq=2048` OOMed on a 143GB H200 because activation memory dominated. `batch=256, seq=2048` passed.

For 1×H200 at a more iterative 1B tokens/run:

```text
1908 steps x batch 256 x seq 2048 = 1.000341504B tokens
7 runs = 7.002390528B tokens
```

This is a useful budget for ranking ablations before spending on larger 4B+ runs.

### 4. Treat 200-step runs as diagnostics only

Short 200-step local runs are useful to catch broken configs, schedules, and obvious regressions. They are not final evidence for dense vs routed claims. If a surprising result appears, audit control invariants before revising the scientific conclusion.

### 5. Avoid schedule confounds when testing routing tables

If the ablation axis is the routing table, keep top-k blending fixed unless schedule is the explicit axis. In this session, fixed top-k 0.5 made the routing-control diagnostic clearer than a schedule moving toward 0.75.

## Recommended pre-launch checks

- Parse each YAML through the real runner parser.
- Build each model config and count params.
- Inspect primary and auxiliary routes for each routing strategy.
- Compute token budget with actual `world_size`.
- Run a 1–2 step smoke on the target device at the intended `batch_size × seq_len`.
- If the target batch OOMs, reduce batch and recompute steps/token budget; do not only lower batch while leaving an old step count.
- Ensure the launcher writes per-run logs plus a final summary CSV.
