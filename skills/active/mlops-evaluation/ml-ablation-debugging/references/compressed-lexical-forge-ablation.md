# Compressed lexical-forge ablations

## Architectural contract

A lexical forge is a tiny token-conditioned neural adapter, not a semantic representation. Preserve the fixed-state Delta memory and distinguish:

- lexical read/write addresses, conditioned on `token_id`;
- contextual payload values, derived from hidden activations;
- deterministic fingerprints, which anchor exact token identity.

A compact forge can reuse an already-paid shared lexical table:

```text
token_scale[token_id] (rank 16)
  -> Linear 16→4
  -> SiLU
  -> Linear 4→state_rank
```

Do not add a second vocabulary table when the MLP already has a tied token table. Attach the same `nn.Embedding` object after inter-layer tying and verify parameter identity/deduplication.

## Durable experimental findings

1. **Pure lexical values are a confound.** Replacing `value_proj(hidden)` with a deterministic token code can win a miniature proxy and regress strongly at production scale. Keep contextual hidden values; forge addresses first.
2. **A forge must be a strict baseline extension.** Removing the baseline contextual address path made an apparently lexical forge worse. Preserve the contextual path and test bit-for-bit equality at neutral initialization.
3. **Global diagonal read/write scales are weak.** They can separate read and write globally but cannot individualize directionality by token.
4. **Compressed token-specific modulation is cheap and testable.** A shared 16→4→rank forge adds hundreds of parameters at proxy rank and under 1K at rank 128 while using the existing token table.
5. **Miniature paired wins do not authorize production claims.** A large paired proxy gain can shrink to a marginal production-scale gain. Production held-out loss remains decisive.
6. **Read and write need a shared coordinate system.** Independent token-specific R/W heads can erase the forge gain because reads no longer target the geometry used for writes. Even a gated antisymmetric correction around a common center may regress; causal direction is already represented by writing the current payload under the previous address. Prefer a common token-specific address unless evidence clears a predeclared gate.
7. **Contextual-value modulation may be real but immaterial.** A neutral-gated FiLM modulation of `value_proj(hidden)` can produce a tiny proxy improvement while missing the minimum effect-size gate and reducing throughput. Treat this as a stop signal, not permission to iterate more RWV variants.
8. **Stop the forge branch when successive clean extensions miss the gate.** Retain the simplest forge that survived production scale, archive negative variants, and move loss work to an orthogonal mechanism rather than accumulating heads and gates.

## Clean paired-control design

When the old proxy uses a SwiGLU MLP but the forge depends on a lexical MLP table, create two new arms:

- lexical MLP + shared token table + Stable Delta;
- identical lexical MLP/table + forge.

Do not compare the forge arm directly against the old SwiGLU arm as its only control. Match:

- tokenizer/data stream and seed;
- scheduler horizon and token budget;
- lexical table and tying;
- contextual mix and hidden value path;
- parameter count using meta-device construction.

At initialization with a zero-initialized token table, forge output must reproduce Stable Delta exactly. Test full-sequence/incremental equivalence and ensure different hidden states affect contextual values while token-only forge components remain token-conditioned.

## Combining the retained forge with an orthogonal mechanism

After stopping forge-only iteration, combine the retained forge only with a mechanism that independently improved production-scale loss (for example, diagonal causal collision-load normalization). Use a paired control with the same lexical MLP and shared token table:

- lexical MLP + collision-normalized Delta;
- identical lexical MLP/table + collision-normalized Delta + retained forge.

Do not use an old SwiGLU collision run as the sole control. Match widths and parameter counts, preserve the collision state's extra load vector, and verify full/incremental equivalence for the resulting three-component state. Predeclare a minimum loss gain before authorizing a full run.

## Parallel R/W forge

A more expressive but still compressed variant uses a fused projection:

```text
rank 16 → bottleneck 4 → 2 × state_rank
                         ├─ read delta
                         └─ write delta
```

Compute both deltas in one matmul and split the output. Keep one Delta memory; do not multiply recurrent matrices merely to call the forge “parallel.” Match this variant directly against the shared-head forge and require a predeclared held-out-loss gate before a full-scale run.

## RWV caution

A three-output forge may modulate values, but should not replace hidden payloads with lexical values. If tested, use a separate ablation such as bounded additive or FiLM-like modulation of `value_proj(hidden)`, initialized neutrally. Do not bundle value modulation into the first R/W experiment.

## Verification and telemetry

Record:

- norms of forge down/up weights;
- norm and frequency-binned statistics of the shared token table;
- read/write divergence (e.g. cosine similarity);
- modulation-to-fingerprint norm ratio;
- collision/load statistics before and after forged addressing;
- exact parameter counts and throughput.

A post-training nonzero forge norm proves use, not usefulness; held-out production loss decides usefulness. Archive metrics/configs and hashes even when Python aborts during teardown, provided metrics and checkpoints were written first.

## Occurrence signatures without reverting to QKV

When comparing fixed-state WVR (write/value/read) to QKV, exclude KV-cache arguments from the quality comparison. At matched training conditions, the core representational gap is that QKV can compare against individual past occurrences, while WVR compresses them into one matrix. Diagnose missing occurrence identity before adding more forge heads.

Do not duplicate an occurrence-context mechanism already present in the address path. If `address_proj(hidden)` already contributes a contextual signature, the clean next control is a gated deterministic absolute-position signature:

```text
address = forged_lexical + contextual_signature + tanh(position_gate) * position_signature
```

Requirements:

- initialize `position_gate` to zero so the candidate exactly reproduces the baseline;
- carry one absolute integer position per sequence in recurrent state;
- derive local positions from that counter so full and token-incremental execution match;
- add the same occurrence term to read and write addresses to preserve their shared coordinate system;
- verify gate-off equality, gate-on effect, counter advancement, and full/incremental equality.

This adds fixed-size state rather than a growing positional history. Test it only after the production winner it extends has completed; synchronizing source files must not be confused with changing an already-loaded remote process.

## Orthogonal-combination gate

A retained compressed forge can combine strongly with collision normalization even when each forge-only extension is marginal. Require a paired collision-only control with the same lexical MLP/table. A large, persistent proxy delta across late checkpoints is stronger evidence than an early lead, but still run a production smoke and matched full-scale held-out evaluation before claiming parity with QKV. For QKV-vs-WVR reporting, state the exact production-loss threshold the WVR candidate must cross and discuss cache/state complexity separately from language-model quality.