# Attention-Free Object-Model Ablations

Use this checklist when evaluating a causal language model built from a shared convolutional/state substrate plus narrow lexical residuals.

## Separate diagnostics from headline evidence

- Small Apple/MPS runs are useful for causality, numerical equivalence, memory, and early ranking. Do not turn 200-step losses into headline claims.
- For paid NVIDIA runs, smoke the exact `batch × sequence × vocab` shape first. Large-vocabulary cross-entropy can OOM even when the backbone is small.
- Increase batch progressively and sample peak accelerator memory. The output head/loss may be the real memory bottleneck rather than the sequence mixer.
- Compute ETA and cost from stabilized real-data throughput, not synthetic throughput, and obtain explicit approval before crossing from smoke to the long run.

## Data integrity

- Streaming train and eval iterators over the same source split are not automatically disjoint. Partition at document identity/index before tokenization and test that no document can enter both streams.
- Make the held-out fraction large enough that evaluation does not need to scan an impractical number of streamed documents.
- A tiny local text sample must never wrap repeatedly for a headline billion-token run. Fail loud or use a non-wrapping corpus manifest.

## Attention-free evidence

Loss alone is insufficient. Add controlled associative-memory probes:

- key→value recall at increasing gaps;
- induction/repeated-prefix continuation;
- needle retrieval or controlled ICL;
- accuracy, target rank, target-vs-best margin, and target NLL by distance and seed.

Compute only final-position logits for large vocabularies (`h_last @ E.T`), not `[B,T,V]`, so 4–8k diagnostics remain feasible.

For convolutional models, report the exact receptive field. Do not reject a persistent state using only sequences inside that field; test it beyond the field (for example 4–8k) and compare associative recall, not only average LM loss.

## Fixed-state inference

- Verify full-sequence logits against token-by-token cached decode.
- Assert cache shape and pointer stability across decode steps.
- Distinguish “CUDA-Graph-friendly by design” from an actual successful capture/replay on CUDA.
- Keep prefill and single-token decode benchmarks separate.

## Routed vocabulary heads

A block-routed output head must beat appropriate controls, not only the dense head:

1. dense exact softmax;
2. frequency-clustered adaptive softmax;
3. learned lexical/block routing.

Report target-block Recall@K before quality or speed claims. Keep a mandatory always-active block for EOS/control/safety pivot tokens. During training, do not silently replace globally normalized likelihood with an uncorrected local softmax objective.

## Durable paid-run pattern

- Run long jobs under a remote service manager (for example systemd) so SSH loss does not kill them.
- Write logs and metrics continuously.
- Treat a post-success streaming-library teardown crash as non-fatal only when final-step metrics and required artifacts are complete.
- Preserve one final checkpoint when downstream evaluation requires it, even if exploratory ablations otherwise disable checkpoints.
