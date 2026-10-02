# Attention-free contextual-retrieval diagnostics

Use this when a convolutional or recurrent LM obtains good language-model loss but fails recall, induction, needle, or ICL probes.

## Interpret the result correctly

Language modeling and content-addressable retrieval are separate capabilities. Compare LM loss against the uniform-vocabulary floor (`ln(vocab_size)`), but do not infer contextual retrieval from a good LM loss. A finite convolutional receptive field means prior tokens influence the output; it does not imply the model can select an old value based on a repeated key.

A zero-shot random-token probe is only a warning until it has a positive control. Run a matched, supervised synthetic control:

- small controlled vocabulary;
- online-generated key/value examples, not a repeated corpus;
- matched parameter counts;
- GQA positive control;
- distances inside and outside the convolutional receptive field;
- exact accuracy, rank, margin, and NLL;
- raw JSON/CSV before plots.

If GQA learns and the convolution remains at `1/vocab_size` accuracy and `ln(vocab_size)` NLL even inside its receptive field, the limitation is content addressing, not merely insufficient context length.

## Correction ladder

1. Do not blindly rerun the same expensive architecture.
2. Test an existing persistent diagonal-state variant locally or on an idle accelerator. A vector state may extend temporal reach but still lack content addressability.
3. If needed, prototype a fixed-size associative/fast-weight state:
   - state size independent of sequence length;
   - read before write for autoregressive causality;
   - normalized content key/query;
   - delta-rule write to reduce overwrite;
   - no sequence-growing KV cache.
4. Require tests for future perturbation, full-vs-incremental behavior, fixed cache shapes, and stable pointers.
5. Run a tiny supervised retrieval benchmark before any 100M/1B-token language pretraining.
6. Promote only variants that beat chance clearly and approach the matched GQA control at trained distances.

## Paid-GPU sequencing

When a long sweep is active, do not run diagnostics concurrently because that corrupts throughput. If a nearly complete condition is running, let it finish, install a guard to stop before redundant later conditions, then reuse the accelerator for short architecture iterations. Existing completed headline checkpoints should prevent redundant retraining.

## Reporting

State the narrow conclusion:

- “learns language statistics” when LM loss beats the uniform floor;
- “fails supervised content-addressable retrieval” only when a matched positive control learns under the same protocol;
- never generalize one failed convolutional mixer into “all QKV-free models have no context.”
