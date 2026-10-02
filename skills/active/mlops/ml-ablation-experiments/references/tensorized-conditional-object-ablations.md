# Dense substrate + tensorized conditional-object ablations

## When to use

Use this recipe when testing a new conditional module intended to improve both matched-token loss and throughput while keeping most computation on regular PyTorch kernels.

## Experimental sequence

1. Identify the exact live/saved baseline by backend, tokenizer, vocabulary size, parameter count, hidden width, layer count, batch, sequence length, dataset, seed, optimizer, and loss implementation. Do not optimize against a throughput number from an unrelated harness.
2. Isolate dirty user work with a dedicated git worktree and experiment branch. Never mix architecture experiments into an already-modified research tree.
3. Build the conditional object without experts first. This establishes the object's standalone loss effect and throughput ceiling.
4. Match total trainable parameters by reducing the shared dense width. Instantiate full models and compare actual counts; analytic formulas are only candidate generators.
5. Run tests before training: shape, token dependence, gradients, config plumbing, table sharing, and parameter-count tolerance.
6. Smoke both forward and backward on the target device.
7. Run a short throughput screen. Only promote variants that remain competitive with the exact baseline.
8. Add experts as a separate axis after the object-only control. This isolates whether experts recover loss and what throughput they cost.
9. Save per-run CSVs immediately and produce a compact comparison CSV.

## Tensorized object patterns

### Shared lexical low-rank residual

A practical dispatch-free object is

\[
\Delta(x,t)=B\left(\operatorname{SiLU}(Ax)\odot(1+m_t)\right),
\]

where a token-indexed modulation table supplies \(m_t\). Use regular dense projections, an embedding lookup, and elementwise multiplication—no sorting or scatter.

For very large vocabularies, a separate table per layer can dominate the parameter budget. Tie one token-modulation table across layers while retaining layer-specific projections. Verify Python module identity across layers and verify that parameter enumeration deduplicates the shared table.

Initialize the table to zero after the model's generic embedding initialization, so \(1+m_t=1\) is neutral at startup. A generic model initializer may otherwise overwrite the module-local zero initialization.

### Lexical channel modulation

A lower-compute alternative directly modulates shared SwiGLU channels:

\[
h=\operatorname{SiLU}(xW_g)\odot xW_u,\qquad y=(h\odot(1+\alpha\,\mathrm{expand}(m_t)))W_d.
\]

This keeps the same three dense GEMMs as the baseline plus lookup/elementwise work. Benchmark it rather than assuming it is faster: tensor expansion operations such as `repeat_interleave` can erase the theoretical gain on MPS.

### Dispatch-free micro-expert residual

After establishing the object-only control, test tiny deterministic experts. One MPS-friendly implementation stores expert projections in stacked tensors, computes a small bank regularly, then gathers the selected top-1 output. This avoids Python expert loops, token sorting, and scatter. It computes more than sparse top-1, so keep expert width very small and measure the trade-off.

A useful matched-parameter construction is to reduce shared width by the total stored micro-expert width. For SwiGLU experts, adding \(E\) experts of width \(w\) costs approximately the same matrix parameters as reducing shared width by \(Ew\).

## Controls

At minimum compare:

- dense baseline;
- object-only;
- object + micro-experts;
- optionally dense low-rank residual without lexical modulation, to separate lexical conditioning from an extra branch.

Keep the tokenizer and exact vocabulary loss identical. Large-vocabulary LM-head cost can dominate training throughput, so do not attribute whole-loop performance changes solely to the MLP.

## Interpretation

Report:

- full trainable parameter counts and percentage mismatch;
- final and checkpointed evaluation losses;
- final throughput and a mean excluding startup/evaluation intervals;
- object-only versus object+expert differences;
- hardware/backend and whether the baseline was contemporaneously rerun.

A short single-seed local run is diagnostic. It can rank designs but does not support a paper-level generalization claim. If using a saved baseline rather than rerunning it, say so explicitly.

## Pitfalls

- **Irrelevant throughput anchors:** A remembered tok/s figure may come from inference, another tokenizer, another model size, or a loop excluding exact vocabulary loss. Find the run artifact before chasing it; if the user says it was unrelated, discard it immediately.
- **Per-layer large-vocabulary tables:** `vocab_size × rank × layers` can consume the entire parameter budget. Tie the table or factorize it.
- **Generic initialization clobbers neutral object init:** Re-zero token modulation after model-wide initialization.
- **Theoretical FLOPs are not device throughput:** MPSGraph may dislike expansion/einsum patterns. Screen on the actual Mac.
- **Adding experts too early:** Without object-only control, loss and throughput effects cannot be attributed.
- **Misleading runner logs:** Generic Token-Routed logging may mention top-k schedules even for a custom MLP that ignores them. Treat model config and executed module type as authoritative, and improve logging before publication.
