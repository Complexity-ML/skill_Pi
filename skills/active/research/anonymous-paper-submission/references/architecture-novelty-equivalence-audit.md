# Architecture novelty and functional-equivalence audit

Use this before freezing or uploading any paper whose contribution is a new attention, mixer, routing mechanism, memory, or renamed tensor semantics.

## 1. Write both operators algebraically

Reduce the proposed operator and strongest baseline to their executable equations, including normalization, positional encoding, masking, head grouping, cache layout, and residual paths.

Example warning pattern:

- baseline: `Q = h W_Q`, `K = h W_K`, `V = h W_V`, then `softmax(QK^T)V`;
- proposal: `R = h W_R`, `W = h W_W`, `V = h W_V`, then `softmax(RW^T)V`.

If dimensions, head grouping, norms, RoPE, masking, cache semantics, and nonlinearities match, then `R <-> Q` and `W <-> K` is a semantic rename, not a new function class.

## 2. Audit every claimed source of novelty

For each claimed component, answer:

- Does it enter the forward computation in the reported main condition?
- Is it enabled in realized configs, not merely allocated as a module/parameter?
- Does a zero gate or disabled flag make it exactly inert?
- Is it also present in the baseline?
- Does it alter outputs under matched weights and inputs?

Unused parameters, renamed projections, interpretive terminology, and components shared by both conditions do not establish architectural novelty.

## 3. Run fail-closed equivalence tests

Where shapes permit:

1. instantiate baseline and proposal;
2. copy/rename matched weights explicitly;
3. use the same hidden states, token IDs, masks, and cache state;
4. compare full-sequence and incremental outputs;
5. test both default flags and the exact submitted config.

If outputs match within numerical tolerance, the paper must call the mechanisms isomorphic/equivalent under that condition. A small multi-seed loss difference does not override an algebraic equivalence; it may reflect initialization assignment, implementation details, or noise.

## 4. Distinguish indirect substrate from direct operator input

A hidden state influenced by token embeddings, lexical objects, routed experts, or semantic features does not make the attention operator itself lexical/semantic/routed when the direct operator remains `f(h)`.

Reserve explicit labels for direct paths:

- contextual attention: `R/W/V = f(h)`;
- explicitly lexical attention: token/object identity enters `R`, `W`, `Q`, `K`, or `V` directly;
- lexical-contextual attention: combine direct lexical address and contextual projection, e.g. `R = norm(R_ctx(h) + beta L(x))`, `W = norm(W_ctx(h) + alpha L(x))`, while `V` may remain contextual.

If a lexical gate is initialized at zero, verify nonzero finite gradients and state clearly that the model starts at the contextual baseline. If the intended new model must be active from step 1, make gate initialization configurable and test the submitted nonzero value.

## 5. Submission decision gate

Before telling the user to submit, state one of:

- **Novel operator confirmed:** algebra and matched-weight tests show a real functional difference.
- **Equivalent main condition:** reframe as analysis/negative result or change the main condition.
- **Novelty depends on an ablation not adequately controlled:** delay the claim and run matched evidence.

Do not let packaging quality, clean PDFs, successful multi-seed runs, or consistent directional metrics substitute for this gate.

## 6. Minimal evidence for a genuinely new lexical-contextual operator

Require:

- direct lexical/object path into the claimed address tensors;
- contextual values preserved unless lexical values are separately motivated;
- matched parameter budget and training protocol;
- operator-difference test under copied common weights;
- causality and full/incremental-cache equivalence;
- gradients reaching lexical gates/tables at initialization;
- matched multi-seed full-budget comparison before changing the paper claim;
- recall/induction/rare-token diagnostics as mechanism-specific evidence, not merely global loss.
