# Standalone iteration for shared attention mechanisms

Use this workflow when an attention/context mechanism inside a larger language model is underperforming and the user wants architectural iteration rather than objective engineering or repeated full-model retraining.

## Scope discipline

1. **Externalize the mechanism, not the product architecture.** Keep an experimental implementation outside the production model path behind the intended final contract: `(hidden_states, token_ids, fixed_state) -> (context_residual, new_fixed_state)`.
2. **Preserve canonical framing.** If the intended result is one shared mechanism, do not call a learned extension “hybrid,” “second model,” or “second branch.” Name it by its function, such as shared associative attention.
3. **Change one mechanism axis at a time.** Start with the smallest extension (for example, one tied/shared contextual address projection) before separate query/key projections, multiple heads, delta rules, or multiple timescales.
4. **Use structural TDD.** First prove neutral initialization exactly reproduces the baseline; then prove the new parameters receive gradients; then add causality, full-vs-incremental, fixed-state, and collision/rank tests.
5. **Benchmark standalone before integration.** Compare against a positive GQA control and the previous mechanism with matched parameters/budget on associative recall, induction, an autoregressive language proxy, generalization distances, throughput, and state size.
6. **Integrate only the winner.** Share one winning module instance in the main model only after it clears explicit standalone gates. Then run a bounded real-data pilot before any headline token-budget run.

## Cost and transfer guardrails

- Do not reproduce a known-losing full model merely to regain a checkpoint for architecture exploration.
- On a fresh accelerator, compare estimated checkpoint-transfer time with a bounded new-candidate run. If transfer bandwidth is poor, avoid uploading optimizer state; use a model-only runtime-precision artifact when the exact checkpoint is genuinely required.
- Never spend a full training budget on the old condition when the scientific task is to improve the mechanism. Run the new bounded candidate and retain the old raw metrics as its baseline.
- Stop and correct course immediately when the user asks for a model that beats the baseline; do not substitute auxiliary objectives, grafts, or reproduction work unless explicitly requested.

## Primary-metric-first execution and communication

- Start from the failure that motivated the iteration. If the full model lost on held-out language loss, the first standalone discriminator must include a matched real-language or credible causal-language loss. Retrieval/induction reruns are secondary sanity checks, not the headline result.
- Do not make the user watch a long replay of capabilities already established. Run known retrieval checks quietly or in parallel, and lead status updates with the requested loss comparison.
- A tiny mechanism win is only a promotion signal. After it wins, integrate it into the real-size model and run a bounded matched pilot before claiming the model beats the baseline.
- Re-run the baseline on the same host, framework build, precision, compile mode, data stream, total scheduled steps, evaluation cadence, and LR-selection protocol. Historical losses remain context, but are not a runtime-matched control.
- Remember that changing `--steps` changes cosine schedules: comparing step 500 from a 500-step schedule with step 500 from a 3,052-step schedule is not matched. Match total schedule length or label the comparison explicitly.
- Report quality and throughput separately. A candidate that wins loss but loses throughput is a quality winner with an optimization task remaining, not a global winner.
- Before moving large checkpoints, estimate transfer time from observed bandwidth. If a fresh candidate can be trained faster than the transfer, train the *new candidate* rather than reproducing or uploading a known loser; never retrain the known loser merely to recover state.

## Scale-transfer guardrail

A small-model language proxy can preserve the ordering for thousands of updates and still fail to predict the ordering at the target parameter scale. Matching update count, tokens, optimizer, and schedule inside the proxy does **not** establish scale transfer.

- Treat a long miniature win as evidence that the mechanism is trainable, not evidence that the target-scale model will win.
- Before a headline run, use a target-width bounded pilot with the same total schedule horizon. Evaluate at several points and compare against a baseline produced on the same host/runtime.
- If prior candidates won at 500 miniature steps and 3,052 miniature steps but lost at 98M/100M tokens, retire that proxy as a promotion gate. Do not keep relaunching headline runs from the same discriminator.
- Inspect scale-dependent structural constraints directly: realized receptive field versus sequence length, memory rank versus hidden width, fusion bottleneck width, and whether a residual is suppressed by a global scalar.
- A target-scale run that loses is a valid negative ablation. Preserve its CSV/config and change the structural hypothesis rather than tuning the proxy until it predicts the desired answer.

## Compile-path verification

For compiled attention/state experiments, tensor-dependent Python control flow can invalidate throughput conclusions:

- Do not call `float(tensor)`, `.item()`, or branch in Python on a trainable tensor inside `forward`; these cause graph breaks or repeated specialization.
- If a feature is fixed by configuration, store a plain Python boolean at initialization and branch on that static flag.
- Verify the optimized path with stabilized target-shape throughput after compilation, not only functional equivalence.
- A mathematically unchanged static-control refactor can recover substantial throughput; rerun the same-runtime baseline before claiming a win.

## Promotion gates

A standalone candidate is promotable only when:

- baseline-equivalent at neutral initialization;
- causal and full/incremental consistent;
- fixed state independent of context length;
- learns recall and induction beyond the convolution receptive field;
- includes a causal language proxy, not retrieval tasks alone;
- parameter count and update/token budgets are matched and recorded;
- raw JSON/CSV and plots are generated from measured data;
- it improves the intended baseline without relying on a naming or protocol confound.
