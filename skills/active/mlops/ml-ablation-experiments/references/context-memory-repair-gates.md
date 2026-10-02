# Context-memory repair gates

Use this workflow when an attention-free mixer learns language loss but fails associative recall or induction.

## Interpret the failure correctly

- Separate language modeling from contextual retrieval. A model can be far better than uniform-vocabulary NLL while remaining at chance on content-addressed recall.
- Compare against a parameter-matched positive control trained on the identical synthetic stream. Zero-shot failure alone is not enough; supervised learnability distinguishes missing pretraining behavior from structural incapacity.
- Sweep distances both inside and outside the nominal receptive field. Chance performance inside the field means the defect is not merely insufficient context length.

## Escalation gates

1. **Matched tiny control**
   - Small vocabulary and model, online random examples, identical optimizer/update budget.
   - Report exact accuracy, rank, margin, and NLL; include chance levels.
   - Require the attention control to learn before interpreting the mixer failure.

2. **Primitive memory test before integration**
   - Test the proposed memory operation independently of the Transformer/convolution.
   - Verify a written key/value pair can be retrieved by the repeated key.
   - Verify gradients reach read, write, and output paths.
   - Test collision/capacity as memory rank and number of stored associations vary.
   - Do not keep redesigning the full model if the primitive itself has not passed.

3. **Structural TDD**
   - Before implementation, require registry construction, future-perturbation causality, fixed cache shape, stable pointers, and full/incremental equivalence.
   - For a previous-key/current-value memory, include the previous key in the fixed cache and assert its shape.
   - If repeated keys must address the same slot naturally, assert query/key projection identity when tying is intended.

4. **Bounded accelerator probe**
   - Run 100-step checkpoints with an explicit stop gate, e.g. stop by 500 updates if accuracy remains at chance.
   - Use a durable service, but stop failed candidates early rather than completing an arbitrary budget.
   - Only scale to language pretraining after the synthetic probe is clearly above chance and competitive with the positive control.

## Fast-weight pitfalls

- Writing key and value from the same token does not implement a `key, value, ..., key -> value` association. A minimal sequential binding uses previous-token key and current-token value.
- Constant writes let filler tokens overwrite memory. Add or validate selective writes, delta correction, or sufficient capacity rather than assuming fixed decay solves interference.
- Independent query/key projections make repeated-token lookup an additional alignment problem. Tie them for the first learnability test, then ablate untied projections later.
- A small output gate can make a valid memory effectively invisible. Use an open initial gate in the diagnostic, then tune stability only after learnability is established.
- A fixed vector recurrent state transports information but is not automatically content-addressable. Do not equate persistence with associative retrieval.
- Passing causal/cache tests proves execution correctness, not task learnability. Both structural and behavioral gates are required.

## Paid-GPU sequencing

- Do not run diagnostics concurrently with throughput-sensitive training.
- When a nearly complete condition is running, let it finish and install a guard that stops the sweep before a redundant next condition starts.
- Reuse an archived completed checkpoint instead of retraining it solely because a short matched pilot includes the same architecture; label the pilot and headline evidence separately.
