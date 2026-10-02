# Learned-router ablations on memory-constrained multi-GPU hosts

Use this checklist when comparing fixed token routing against contextual learned routers while preserving a shared-plus-residual architecture.

## Scientific contract

Hold fixed across variants:

- attention backbone, tokenizer, data order, optimizer and schedule;
- shared dense branch width;
- number and width of residual experts;
- top-k and branch-gate initialization;
- number of optimizer updates and effective global batch;
- total token budget.

A learned router adds a small projection. Instantiate full models and report the exact parameter delta rather than calling capacities identical without measurement.

## Learned top-k implementation invariants

1. **Variable-load dispatch**
   - Never reshape routed tokens as `[num_experts, equal_chunk, hidden]` unless equal assignment is guaranteed by construction.
   - Learned top-k loads are data-dependent. Dispatch by assignment indices, grouped GEMM, or per-expert index selection.
   - Assert distinct top-k expert IDs, finite outputs, correct output shape, and a deliberately unbalanced assignment case.

2. **Auxiliary load-balancing baseline**
   - Keep the balancing term as a differentiable tensor; never call `.item()` before backward.
   - Aggregate the term across router layers and add its weighted value to the language-model objective.
   - Test that backward on the auxiliary term produces a nonzero router gradient.
   - Log language loss, weighted router loss, and total loss separately.

3. **Loss-free bias balancing**
   - The balancing bias is a non-trainable buffer used for expert selection only.
   - Compute mixture weights from the unbiased router scores.
   - Aggregate expert counts across micro-batches and distributed ranks.
   - Update the bias once per optimizer step, then reset pending counts.
   - Add no auxiliary term to the training objective; test that underloaded experts receive a positive correction and overloaded experts a negative correction.

## Effective-batch preservation after OOM

When reducing the per-GPU micro-batch, preserve the scientific contract with:

`effective_global_batch = micro_batch_per_gpu * world_size * gradient_accumulation_steps`

`tokens_per_optimizer_step = effective_global_batch * sequence_length`

`total_tokens = optimizer_steps * tokens_per_optimizer_step`

Use DDP `no_sync()` on all but the final micro-batch. Keep schedules indexed by optimizer step, not micro-step. Record micro-batch and accumulation separately in `run_config.json`.

## Paid-GPU smoke ladder

A tiny random-data smoke is necessary but insufficient. Before the full run:

1. run parser/unit tests on the deployed commit;
2. run 1-2 tiny DDP steps for every structural variant;
3. run one optimizer step at the exact sequence length, vocabulary size, effective batch and loss backend;
4. verify finite language/router/total losses and inspect peak VRAM;
5. only then cross into the long paid run.

For very large vocabularies, the exact output projection and cross-entropy can dominate memory after the backbone forward succeeds. Exercise the production loss backend in the full-shape smoke. If the framework supports fused linear cross-entropy, require it explicitly in the launcher rather than silently falling back to a graph-retaining chunked implementation.

## Harden the data path before a long sweep

Remote streaming is useful for a preflight batch but can leave network/background workers alive during interpreter teardown, turning a completed run into a nonzero process exit and aborting a sequential launcher. For long matched sweeps, prefer one verified local token shard when disk permits:

1. resolve and record the immutable dataset revision;
2. download/process one source file at a time so temporary data cannot fill the host;
3. tokenize once with the exact tokenizer and append document boundaries consistently;
4. write a mmap-friendly integer stream plus an atomic index containing token count, vocabulary, source files, source revision, and SHA-256;
5. verify the checksum and read a real batch through the production dataset class;
6. give every variant the same shard and document-disjoint train/eval split;
7. make the full-run launcher fail loudly when either shard data or its index is absent.

Keep shard creation and the sweep under a durable remote supervisor. The GPUs may remain idle during preprocessing; report that phase explicitly so expected idle utilization is not mistaken for a stalled paid job.

## Stop conditions

- Stop before long training on any OOM, detached router loss, unequal-budget manifest, missing tokenizer, or absent metric column.
- Do not silently change global batch, optimizer updates, sequence length, or total tokens to make a run fit.
- Do not describe toy-smoke throughput as stabilized training throughput.
