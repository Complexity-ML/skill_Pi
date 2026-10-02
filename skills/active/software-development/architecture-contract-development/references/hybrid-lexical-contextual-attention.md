# Hybrid lexical-contextual attention contract

Use this note when a project wants an attention operator that is genuinely different from renamed Q/K/V while retaining SDPA/FlashAttention execution.

## Novelty gate

A mechanism with

- `R = h W_R`,
- `W = h W_W`,
- `V = h W_V`, and
- `softmax(R W^T) V`

is functionally in the Q/K/V family when dimensions, grouping, norms, RoPE, masking, and cache semantics match. Write/Read terminology alone is not architectural novelty. Before publication or a paid scale-up:

1. align matched baseline/candidate weights;
2. show identical outputs when the proposed lexical path is disabled;
3. show non-identical outputs with the claimed path active;
4. confirm the active config reaches every intended layer;
5. keep parameter/token/data/optimizer budgets matched.

## Minimal genuinely lexical hybrid

Let `L(x)` be one shared lexical address derived directly from token identity or a tied lexical object. Use:

- `R_t = RMSNorm(R_ctx(h_t) + g L_R(x_t))`
- `W_t = RMSNorm(W_ctx(h_t) + g L_W(x_t))`
- `V_t = V_ctx(h_t)`
- output `softmax(R W^T) V`

For grouped read/write heads, a low-parameter contract is to build one lexical address per write head and repeat it to the corresponding read-head group. A shared gate keeps read/write lexical strength coherent. Values remain contextual so repeated lexical identities retrieve occurrence-specific content rather than a static token value.

The gate may default to zero for backward compatibility, but a new-model config should explicitly choose its initialization. If the scientific claim is that the model is hybrid from step one, use a small nonzero initialization and record it in the realized config.

## Required tests

- Lexical address is repeated to exactly the intended grouped read heads.
- Matched write-only and hybrid modules have equal parameter count.
- With identical weights and a nonzero gate, hybrid output differs from write-only output.
- Disabling the lexical residual while requesting hybrid mode fails closed.
- Full-sequence and incremental-cache outputs match.
- Causality and padding-mask behavior remain correct.
- A full-model forward/backward gives finite, nonzero lexical-gate gradients.
- Tied lexical-object embeddings receive finite gradients.
- Real CLI/YAML parsing propagates the flag and gate initialization into every target layer.
- Production batch/sequence smoke confirms CUDA SDPA/Flash dispatch and memory fit before paid full-budget runs.

## Baseline-preserving lexical ladder

When replacing GQA with lexical W/R/V loses, stop renaming or sparsifying the replacement and preserve the proven operator instead. Explore in this order:

1. **Additive lexical score:** keep contextual GQA scores and values unchanged; add a gated context-query / learned-token-key score. Preserve the original explicit contextual scale when Q/K is widened.
2. **Learned-only control:** if a deterministic token-ID code wins early then loses late, remove the hash and let the zero-initialized tied lexical object supply keys. A small nonzero gate keeps the initial score exactly GQA while giving the lexical table gradient.
3. **In-place lexical key residual:** inject the tied lexical object into the existing K head, then apply normal RoPE/FlashAttention. This avoids wider Q/K and preserves throughput. However, do **not** RMS-normalize a near-zero learned lexical object directly into unit magnitude: that can preserve speed yet distort K enough to reverse early gains later in training.
4. **Projected in-place lexical key:** prefer `K' = K_ctx + g A(L(x))`, where `A: r -> n_kv_heads * d_head` is a tiny per-layer projection and `L(x)` is the zero-initialized tied lexical object. Do not widen Q/K, do not add a lexical V path, and initially avoid RMS-normalizing `A(L)`. At rank 16, two KV heads, head dimension 48, and ten layers, this adds only about 15k parameters while retaining the stock FlashAttention shape and near-baseline throughput.

Do not assume strict parameter matching is neutral. If matching a small lexical branch requires narrowing the baseline MLP, run an unadjusted-width diagnostic in parallel. A matched arm that loses while the intact-MLP arm wins indicates compensation damage, not necessarily mechanism failure. The final claim still requires a matched or near-zero-overhead design; the unadjusted arm is diagnostic evidence.

For paid searches, inspect the whole evaluation trajectory. Early lexical gains that reverse after roughly one-third of training are a rejection signal for that representation, not a checkpoint to cherry-pick. After one seed beats the full-budget baseline, retain that checkpoint/config as the positive control and simplify toward a near-zero-overhead mechanism before adding seeds.

## Interpretation discipline

- Hidden states influenced by lexical routing are *lexically informed*, but that does not make the attention operator explicitly lexical.
- Direct token/object injection into R/W or existing GQA K does make the operator lexical-contextual.
- A one-seed write-only residual result does not validate the R/W hybrid; run a fresh matched baseline and candidate on the same commit/hardware.
- Keep throughput and quality claims separate until multi-seed evidence exists.
