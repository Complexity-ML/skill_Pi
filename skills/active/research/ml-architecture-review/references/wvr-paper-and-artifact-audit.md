# WVR paper and artifact audit

Use this reference when auditing a paper that presents a fixed-state associative mechanism as Write/Value/Read (WVR), especially when prose, translations, configs, and raw artifacts have diverged.

## Canonical mechanism contract

Define the three roles and the state before comparing against attention:

- write address: `w_t ∈ R^r`
- contextual value: `v_t = W_V h_t` (unless an explicit lexical-value ablation replaces it)
- read address: `r_t ∈ R^r`
- associative state: `M_t ∈ R^{r×r}`

A stable delta form is:

```text
y_t     = r_t^T M_{t-1}
hat_v_t = w_t^T M_{t-1}
e_t     = v_t - hat_v_t
M_t     = λ M_{t-1} + η w_t e_t^T
c_t     = γ W_O y_t
```

Audit the implementation's causal alignment. Some implementations read at the current token but pair `v_t` with the previous write address. State this explicitly. If training uses a chunkwise triangular solve, verify and describe it as a parallel evaluation of the recurrence rather than a separate architecture.

## Distinguishing WVR from QKV safely

Compare computational contracts, not letters:

- QKV attention forms token-to-token scores and normalizes across positions.
- WVR contracts read/write addresses through a recurrent matrix state.
- Defensible distinctions include: no attention score matrix, no softmax over positions, and fixed-shape recurrent state.
- Do not call WVR “renamed QKV”: write and read roles have different update/read semantics.
- Do not make KV-cache claims when the requested scope excludes them or when serving evidence is incomplete. “Fixed-shape recurrent state” is usually sufficient.
- The symbol `V` or a projection named `value_proj` does not make the mechanism attention. Conversely, “no QKV parameter names” is only a parameter-name audit, not proof of runtime behavior.

## Raw-artifact result extraction

1. Enumerate every result-bearing JSON/CSV and its run config.
2. For each CSV, report the **last finite evaluation**, not the last row (training-only rows often contain `eval_loss=nan`).
3. Record evaluation step, loss, perplexity, throughput on that same row, parameter count, registered tokens, seed, sequence length, device, and precision.
4. Keep distinct:
   - last finite evaluation throughput;
   - final training-row throughput;
   - median post-warmup throughput;
   - any headline macro copied into TeX.
5. Do not silently attach a parameter count to a copied baseline CSV when no colocated config or checkpoint establishes it.
6. Separate completed runs with different token budgets rather than placing them in one matched-budget table.
7. Treat single-seed differences among close variants as descriptive, not statistical superiority.

## Contradiction checks

Audit every paper claim against raw artifacts:

- “pending” versus archived metrics;
- intended budget versus serialized `total_tokens`;
- headline macro versus exact CSV value;
- claimed incremental tolerance versus measured max/mean logit differences;
- compact theoretical state count versus checkpoint/runtime state shapes;
- fixed addresses versus exact full/incremental equivalence (separate claims);
- claimed associative capability versus synthetic recall/induction accuracy;
- claimed held-out partition semantics versus what configs and data construction actually establish;
- inference/CUDA Graph tables versus raw machine-readable logs.

A stable address is not exact incremental equivalence. If artifacts show nonzero differences above the claimed tolerance, retract the equivalence claim even when cache pointers remain stable.

## Variant naming

Name variants by realized behavior, not run-directory marketing names. For example:

- stable delta;
- collision-normalized delta;
- separate forged read/write addresses;
- collision-normalized forged addresses;
- multi-timescale value channels;
- deterministic lexical-value ablation.

Define each variant's changed address, value, update, and extra state. Do not describe deterministic lexical values as semantic values.

## Translation audit

Diff canonical and translated sources by claim surface, not sentence count. Check especially:

- experimental diagnostics present in only one language;
- differing interpretation of failed ablations;
- stale pending/future-run language;
- equations and variant definitions;
- negative results and limitations;
- identical numeric tables with locale-appropriate separators.

Apply evidence corrections independently to every language; do not assume translation symmetry.

## Read-only deliverable format

For no-edit audits, return:

1. audit outcome;
2. exact method/reframing updates;
3. raw-artifact result table with provenance caveats;
4. stale or unsupported claims;
5. language mismatches;
6. explicit confirmation that no files were changed.
