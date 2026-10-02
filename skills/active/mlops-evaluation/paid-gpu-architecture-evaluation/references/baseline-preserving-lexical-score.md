# Baseline-preserving lexical score case study

## Failed replacement family

On a matched 100M-token FineWeb-Edu seed-42 comparison on RTX PRO 6000 Blackwell:

- GQA eval loss: `4.664001`
- full lexical-contextual W/R/V: `4.680514` (`+0.016513`)
- W/R/V in bottom 4 layers: `4.687049` (`+0.023048`)
- W/R/V in bottom 2 layers: `4.732087` (`+0.068086`)

The full hybrid led through roughly step 1000, crossed the control around step 1250, then lost. Upper-layer lexical gates collapsed near zero, but restricting W/R/V to lower layers made the endpoint worse. Lesson: gate trajectories can identify rejection, but do not prove a sparse replacement will recover the baseline.

## Better candidate contract

Preserve GQA's contextual score and values exactly, then add a gated lexical score channel:

`score(i,j) = Qctx(i) Kctx(j)^T / sqrt(d) + tanh(g_h) Qlex(h_i) Klex(x_j)^T / sqrt(d)`

Implementation properties:

- `Qctx`, `Kctx`, `Vctx`, QK normalization, RoPE, cache, and output projection remain the GQA path.
- `Qlex` is context-derived; `Klex` is token/object-derived; values receive no lexical residual.
- Concatenate lexical channels onto Q/K and pass the original explicit `1/sqrt(d_context)` scale to SDPA. This keeps FlashAttention compatibility and avoids rescaling the baseline score when Q/K width increases.
- A zero gate makes the lexical dot product zero, giving mathematical GQA equivalence at initialization.
- If the learned lexical object table also initializes at zero, there are two distinct bootstraps:
  - a deterministic token-ID code gives the zero gate an immediate gradient;
  - a small nonzero gate gives the zero table an immediate gradient, while the lexical score remains exactly zero at initialization because the key is zero.
- Verify gate/table movement after several optimizer/warmup steps, not only a synthetic backward or the first step (which may have zero LR).
- Treat the deterministic token code as an ablation. In the concrete RTX experiment it produced an early advantage that reversed late:
  - gate 0 lexical-score GQA: `4.698518` versus GQA `4.664001` (`+0.034517`);
  - gate 0.05 lexical-score GQA: `4.688437` (`+0.024436`);
  - both were ahead around step 500 but behind at full budget.
  This pattern motivates a learned-only lexical key control rather than declaring all lexical scores ineffective.
- Match parameter count by reallocating another width rather than granting the candidate free parameters, but treat the compensation as a tested architectural change. In the concrete 100M setup, reducing MLP intermediate width from 1118 to 1075 left only +1360 parameters (+0.0014%) but ended at `4.701946`, well behind GQA `4.664001`. The learned-only arm with the intact 1118 MLP reached `4.658752` (`-0.005249`) and therefore established a positive lexical mechanism control, while also proving that MLP narrowing destroyed the matched arm. This does **not** license an unmatched final claim; it directs the next iteration toward a lower-overhead lexical path rather than further MLP reduction.

## Near-zero-overhead lexical key residual

After an intact-MLP learned-only score arm beats GQA but wider Q/K costs throughput and projections cost parameters, fold the lexical object into the existing K head:

`K'_j = K_ctx(h_j) + tanh(g_h) pad(RMSNorm(L(x_j)))`

then run ordinary GQA `softmax(Q_ctx K'^T / sqrt(d)) V_ctx`.

Contract:

- keep Q, V, QK normalization, RoPE, head dimension, cache, and output projection unchanged;
- use the already-tied lexical object table; add no lexical Q/K/V projections;
- use one gate per KV head (only tens of parameters for a small model);
- inject before the normal RoPE application so cache semantics remain unchanged;
- when the lexical table initializes at zero, a small nonzero gate still gives exact GQA output at initialization and nonzero gradient to the table;
- verify full/incremental equivalence and production FlashAttention throughput because the intended advantage is preserving the baseline head width.

This is preferable to blindly reducing the baseline MLP to pay for a wide lexical channel. Compare two small gate initializations on the first controlled seed; if one beats the full-budget GQA endpoint at baseline-like throughput, replicate that fixed setting rather than continuing seed-42 gate search.

## Required tests before paid GPU

1. Copy GQA weights into the candidate and assert output equivalence at gate zero using the non-SDPA fallback for tight numerical comparison.
2. Assert nonzero gate changes output while no lexical value projection exists.
3. Assert the chosen bootstrap is live under realistic initialization: zero gate + deterministic code must move the gate, or nonzero gate + zero learned table must move the table while preserving the baseline output.
4. Assert full-sequence and token-by-token cached outputs match.
5. Run a full-model CE backward and inspect the relevant gate/table after at least five optimizer steps.
6. Confirm production SDPA/Flash accepts different Q/K and V feature widths and preserves the explicit contextual scale.
