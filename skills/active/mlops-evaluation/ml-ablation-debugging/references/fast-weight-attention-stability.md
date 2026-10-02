# Fast-weight attention stability and scale validation

## Trigger

Use when a fixed-state associative/linear attention has good synthetic recall or miniature-LM loss but fails to improve the full language model.

## Diagnostic pattern

Inspect the trained checkpoint rather than guessing from architecture labels:

- effective write rate: `sigmoid(write_logit)`
- effective retention: `sigmoid(decay_logit)`
- approximate horizon: `1 / (1 - decay)`
- learned output gate or residual scale
- learned contextual-address mix
- memory-state and read norms by sequence position
- BF16 versus FP32 recurrence drift

A high write rate plus decay near one, paired with a very low learned output gate, is evidence that additive writes may be accumulating interference and the model is suppressing the noisy branch. It is not proof that the address mechanism lacks capacity.

## Stable replacement candidate

Replace additive fast-weight writes

`M <- decay * M + beta * k v^T`

with residual delta writes

`prediction = k^T M`

`M <- decay * M + beta * k (v - prediction)^T`.

This overwrites/corrects an association instead of repeatedly accumulating it.

Before an LM run, test:

1. repeated identical writes remain norm-bounded over at least 8k updates;
2. a later value replaces an earlier value for the same key;
3. all state/read tensors remain finite;
4. full-sequence and token-incremental outputs/states agree;
5. recurrence state uses FP32 or demonstrates acceptable BF16 drift;
6. H100 throughput is measured for the attention primitive and integrated model.

## Scale lesson

Do not treat synthetic recall, a 500-step miniature LM, or even a long miniature LM as sufficient evidence that a 98M full-budget model will beat GQA. In this architecture class, miniature proxies repeatedly preserved an advantage that disappeared or reversed at 100M tokens. They are debugging screens only. The decisive gate is a matched full-scale FineWeb held-out loss curve under the production optimizer/scheduler/runtime. Report train loss and held-out loss separately; the final progress-bar loss is usually the latest training batch, not evaluation.

## Run hygiene

- Preserve each failed full run as a real ablation with raw metrics/config.
- If Python aborts during dataset-thread teardown after metrics/checkpoint writes, verify files, byte sizes, and evaluation rows before classifying the run; do not infer corruption from service status alone.
- Throughput comparisons require the same H100, PyTorch, compile mode, warm-up, batch, sequence length, and measurement window.
