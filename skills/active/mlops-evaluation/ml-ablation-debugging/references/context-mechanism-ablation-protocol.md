# Context-mechanism ablation protocol

Use this protocol when adding a recurrent, associative, fast-weight, convolutional, or other context path to a language model.

## Separate three different claims

1. **Mechanistic capacity:** after direct supervision on recall/induction, can the mechanism solve the task across distances?
2. **Pretraining emergence:** after ordinary LM pretraining only, does the checkpoint actually use the mechanism on the same diagnostics?
3. **Language-model quality:** at matched data and training budget, does held-out LM loss improve?

Do not use (1) as evidence for (2). A mechanism can reach 100% in a supervised probe while an LM-pretrained checkpoint remains at 0% exact recall because ordinary text training never activated that path. Measure mechanism ON/OFF, learned gate value, accuracy, rank/NLL, and full-vs-incremental equivalence on the final checkpoint.

## Safe residual growth

For a new residual branch `y = base + gate * context`, compare gate initializations explicitly. A gate initialized to 1 can inject an untrained residual at full strength and damage early LM loss. Gate 0 preserves the parent model at initialization and lets the branch grow, but can also leave the branch weakly used; log the learned gate and test ON/OFF behavior. A low learned gate plus zero exact recall is evidence that the LM objective did not meaningfully recruit the branch.

## Matched short pilots

- Keep parameter count, data, tokenizer, seed, batch, sequence length, precision, optimizer, total steps, evaluation batches, and software mode explicit.
- The **total number of pilot steps is part of the LR schedule**. Comparing step 250 from a 250-step cosine run with step 250 from a 3052-step run is not matched even if nominal LR is equal.
- If one architecture gets an LR sweep, either grant the principal baseline the same candidate grid/budget or label the result as recipe-tuned rather than iso-hyperparameter.
- Do not mix eager and `torch.compile` throughput. Benchmark every compared architecture under the same compilation mode and warm-up protocol. Keep eager and compiled tables separate when both matter.
- Teardown failures after metrics were flushed are not training failures: verify CSV completeness and service exit cause before discarding a run.

## Decision gates before a paid full run

Require all of the following:

- targeted causal and fixed-state tests pass;
- supervised recall/induction reaches the target distance;
- matched short-pilot LM loss is competitive;
- matched compiled throughput meets the threshold;
- no unexplained ON/OFF or gate anomaly remains.

If the final LM checkpoint does not recruit a mechanism that succeeds under direct supervision, distinguish two valid next experiments and follow the user's chosen intervention class:

- **Objective question:** test curriculum/auxiliary activation or frozen-path training when the question is whether the existing mechanism can be recruited.
- **Architecture question:** upgrade the existing mechanism itself when the goal is a stronger attention/context design. Do not replace this with a graft or curriculum merely because it is easier to run. Start with one minimal change (for example learned contextual queries/keys blended into an exact lexical address), preserve a neutral initialization, and reject it on matched short pilots before adding multi-head or multi-timescale complexity.

Do not multiply injection points or launch another full-budget run without an explicit hypothesis and a matched short-pilot win.

## Figures and artifact handling

- Generate figures only from archived JSON/CSV, never copied numbers.
- Mark incomplete curves as `live`; regenerate from final CSV before paper insertion.
- Visually inspect title, legend, labels, clipping, and misleading throughput dips. A valid PNG file is not proof of a publication-ready figure.
- Before terminating a rented GPU, copy metrics/config/profile first, then the checkpoint. Verify local byte size and SHA-256. Do not tell the user to shut down until the checkpoint transfer is complete.
- For cross-machine continuation, do not blindly upload a full training checkpoint containing AdamW state. Preserve the original archival checkpoint, then create a separate model-only transfer artifact. If the target runtime loads the model in BF16, converting floating model-state tensors to BF16 before transfer is valid only when this matches the measured runtime path; record that conversion and retain the original hash. This can reduce a 1.3 GB training checkpoint to roughly 200–500 MB without losing the weights needed for inference or adapter-only training.
- Prefer server-to-server transfer while both rented machines are alive. If the source has already been terminated, estimate transfer time from measured first-minute throughput before committing. Compare that ETA with the time and scientific value of training a new candidate locally on the target GPU. Never spend longer transferring or reproducing an already losing checkpoint when the user wants the next architectural contender; transfer only when that exact checkpoint is required for the stated experiment.
- If transfer is still the right choice, use the stripped model-only artifact from the verified local archive.
- Use broadly compatible transfer options for the host OS; if a progress flag fails, retry with a portable command and preserve partial large-file transfers. Check the destination byte count within the first minute: a background process that is still `running` while zero bytes exist remotely is stalled, not merely slow. Stop it and change transport rather than polling repeatedly.
- Avoid concurrent copies to the same destination. When handing a transfer to the user, stop the agent-owned transfer first and provide one absolute-path command plus the exact expected source size and destination.

## Paper-state discipline

- A completed run can be a valid intermediate ablation without being the final architecture. If the user chooses to iterate after seeing final loss or checkpoint diagnostics, pause automatic TeX/PDF finalization rather than silently presenting the intermediate run as definitive.
- In reviewer-facing tables, distinguish `iso-parameters/data/tokens` from `iso-hyperparameters`. Put architecture-specific LR and compile mode in explicit columns or protocol text. A tuned recipe may be reported, but it must not be described as a strict architecture-only ablation.
- Do not claim that a model “beats” a baseline globally when the metrics split: state separately which model wins held-out LM loss, supervised contextual diagnostics, and matched throughput.
