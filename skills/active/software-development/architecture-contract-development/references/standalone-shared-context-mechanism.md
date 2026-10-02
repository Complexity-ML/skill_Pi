# Standalone Shared Context Mechanism: Validation and Reintegration

Use this reference when adding a fixed-state contextual or associative mechanism to an existing sequence model without creating a second model or silently changing top-level cache ownership.

## Boundary contract

Keep these questions separate:

1. **Source boundary:** Is the mechanism implemented in its own file/module?
2. **Composition boundary:** Is it reinserted as a branch of the same model?
3. **Parameter sharing:** Do layers reference one parameter instance or own copies?
4. **Runtime state:** Is state per layer, caller-owned, or global? Never infer a new model-level cache from “shared”.
5. **Terminology:** A shape analogy such as “2D table” is not automatically the canonical class/API name. Prefer capability names such as associative context or fixed-state context unless representation is explicitly contractual.

## Experiment identity and replacement semantics

Before launching an expensive matched pilot, write one unambiguous experiment identity:

- **subject:** the architecture being trained;
- **role:** replacement candidate, baseline, or isolated ablation;
- **budget:** parameters and tokens;
- **existing controls:** runs already available and sufficient for comparison;
- **explicitly excluded runs:** obsolete/broken architectures that must not be retrained.

If the user says “we corrected the model and now run it iso-parameter,” interpret that as a **replacement-candidate run of the corrected architecture**, not permission to create both an old-model rerun and a new fifth ablation. Existing controls remain controls; do not independently queue an obsolete architecture merely to make a table visually complete. A historical long-budget checkpoint may be reported separately without triggering a short-budget rerun unless the user explicitly requests that control.

Communicate the active run by its scientific role and complete architecture, e.g. “corrected full architecture, 98M parameters × 100M tokens,” not by an internal nickname such as “contextual run.” Internal nicknames can make one model sound like two products. If the user corrects the experiment identity, stop any queued unwanted service immediately and verify the intended service remains active.

## Evidence ladder

Do not begin a long language-model run until all earlier gates pass:

1. **Primitive correctness**
   - write known key/value associations
   - read with the same key
   - verify exact/near-exact retrieval without end-to-end learning
2. **Address quality**
   - compute normalized-address Gram matrix
   - report max and p99 absolute off-diagonal similarity
   - test retrieval capacity at several ranks and association counts
3. **Optimization path**
   - verify nonzero finite gradients for address/value projections and read/write gates
   - confirm the context residual changes outputs
4. **Synthetic task**
   - matched positive control (e.g. GQA)
   - random/chance baseline
   - associative recall and induction at trained and held-out distances
5. **Structural invariants**
   - strict causality
   - fixed-size state independent of context length
   - stable state pointers where required
   - full-forward/incremental equivalence
6. **Performance gate**
   - profile realistic sequence length and batch sizes
   - stop before a 100M/1B-token run if a Python token loop dominates
7. **LM pilot**
   - matched parameters, tokens, tokenizer, data order, seed, optimizer, and evaluation cadence
   - produce raw JSON/CSV before plots

## Collision failure pattern

A memory primitive may retrieve perfectly with random normalized keys but plateau end-to-end with deterministic token keys. Before increasing rank, measure key correlations. Near-duplicate addresses can mimic a capacity limit.

A durable regression test should assert:

- repeated token ID produces exactly the same address;
- different IDs are not identical;
- at the intended rank, the tested vocabulary subset stays below a justified maximum cosine threshold.

Do not impose a rank-128 separation threshold on a rank-8 toy fixture; instantiate a dedicated separation probe at the deployment rank.

## Vectorization pattern

For additive decayed fast-weight state

`M_t = decay * M_{t-1} + write_rate * outer(k_{t-1}, v_t)`

and read

`r_t = q_t @ M_{t-1}`,

process full sequences in causal chunks:

- contribution from incoming state uses powers of `decay`;
- within-chunk reads use a lower-triangular address-similarity matrix weighted by temporal decay;
- final state is a weighted batched outer-product reduction;
- incremental length-1 execution remains the recurrent reference.

This reduces Python iterations from sequence length to sequence length/chunk size. After changing from a delta correction to an additive scan, rerun all synthetic probes: numerical equivalence can hold for the new recurrence while behavioral capacity changes.

## Invocation count, compilation, and performance gates

Sharing one context module across layers deduplicates parameters, but it does **not** deduplicate execution. Audit separately:

- number of parameter instances;
- number of context invocations per forward;
- number and shape of runtime states;
- full-sequence training throughput;
- incremental decode cost.

A useful optimization sequence is:

1. establish the all-invocation behavioral upper bound on synthetic recall/induction;
2. reduce invocation points (for example, one early injection, then two spaced injections) while retaining one parameter instance;
3. rerun synthetic probes after every reduction—one injection may be fast but plateau below the positive control;
4. benchmark realistic parameter count, sequence length, and batch size for 20–30 steps;
5. treat the first compiled interval as warm-up and compare only stabilized intervals;
6. stop any paid pilot immediately if it misses the user's efficiency ceiling;
7. restart only when the candidate simultaneously meets the behavioral and throughput gates.

Chunk size, rank, address generation, and invocation count are independent levers. Measure them rather than assuming smaller is faster: reduced chunks can increase launch overhead, and reduced rank may not matter when the causal score matrix dominates. `torch.compile(mode="reduce-overhead")` can fuse enough of the graph to cross an engineering threshold, but a paper claim still requires compiling the GQA/control path under the same policy.

## Measurement support for a short LM pilot

A useful 100M-parameter × 100M-token pilot should save one final checkpoint and automatically emit:

- train/eval loss history;
- median post-warmup throughput;
- recall and induction over distances spanning below and above the convolutional receptive field;
- mechanism ON/OFF intervention by zeroing only its output gate;
- causality and full/incremental checks;
- fixed-state shapes, element count, byte estimate, and pointer stability;
- consolidated JSON/CSV plus SHA-256 hashes.

Keep plots downstream of the consolidated raw JSON. Do not launch the 1B-token rerun until the short pilot shows both useful LM quality and context behavior.

## Publication-grade comparison protocol

For a TMLR-style comparison, keep these evidence axes separate:

1. **Fixed-budget quality:** match parameters, tokens, data order, tokenizer, seed, batch, sequence length, optimizer family, total scheduler horizon, warm-up, decay, and evaluation cadence. If architecture-specific learning rates are selected, disclose them in the main table and give the principal control the same short tuning grid/budget.
2. **Throughput:** benchmark every candidate and control under the same eager/compiled policy, precision, shapes, warm-up exclusion, and measurement window. A compiled candidate beating an old eager CSV passes an engineering gate but is not the final paper comparison.
3. **Context behavior:** report recall/induction, held-out distances beyond the convolutional receptive field, and a mechanism ON/OFF intervention separately from LM loss.
4. **Long-budget evidence:** keep a historical 1B-token result separate from 100M-token ablations. Do not use it to fill a missing short-budget row or trigger an unwanted rerun of an obsolete predecessor.

A run is not “invalid” merely because LR or compile policy differs. Its measurements remain valid; only the scope of the comparison changes. Label the mismatch, retain the artifact, and run the cheapest missing matched control (often a short throughput benchmark or LR pilot) rather than discarding evidence.

Schedulers whose trajectory depends on configured `steps` create a common trap: step 250 of a 250-step run has a different LR than step 250 of a 500- or 3052-step run. Only compare checkpoints from the same configured horizon when selecting architecture or LR.

## Neutral reinsertion gates and LM-quality pilots

A newly inserted context branch can pass synthetic retrieval while damaging language modeling simply because its random output enters the residual at full strength. Treat the residual gate as an architectural preservation device:

- `output = base + gate * context`;
- initialize `gate=0` when exact parent-function preservation matters;
- initialize above zero only when a matched pilot demonstrates that early context gradients outweigh representation disruption;
- expose the gate in config and record its initial/final value in telemetry;
- rerun synthetic retrieval with the **deployment gate initialization**—a gate-1 probe does not prove that a gate-0 training path will learn quickly enough.

At gate zero, the first update reaches the gate while context-internal gradients may initially be suppressed; this is expected, but learning-speed must be measured. Compare gate/LR candidates under the same total scheduler horizon. Never compare the endpoint of a 250-step cosine schedule to step 250 of a 3052-step schedule.

Use short matched LM pilots to select the neutral reinsertion recipe, then require the chosen candidate to beat or match the principal control at multiple checkpoints, not only at the first evaluation. Early gains can reverse late in training.

## Measurement-derived validation figures

Architecture-validation PNGs must represent the current candidate, not merely older checkpoint diagnostics. Build them from identifiable raw JSON/CSV and include, where relevant:

- recall and induction versus dependency distance;
- matched held-out LM-loss curves;
- matched steady-state throughput;
- mechanism ON/OFF behavior after the final checkpoint.

Mark partial-training figures as `live`, preserve their source CSV, and regenerate them after completion. Visually inspect the rendered PNG: title/legend overlap, clipped labels, misleading evaluation-time throughput dips, and mixed training horizons are publication defects even when the plotting script succeeds.

## Communication during rapid iteration

Use one sentence to identify the active experiment: “corrected full architecture, X parameters × Y tokens.” Avoid introducing labels that sound like separate products or models. When the user asks what is running, answer in this order:

1. exact active architecture;
2. exact scientific purpose;
3. current step/status;
4. explicitly state what is not running.

If the user says the explanation is becoming confusing, stop expanding the taxonomy, cancel any accidental queued baseline, verify service state, and return to the single replacement candidate.
