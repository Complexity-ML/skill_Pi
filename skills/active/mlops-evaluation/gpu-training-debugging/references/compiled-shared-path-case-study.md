# Compiled shared-path case study

## Symptom

A 98M-parameter BF16 training job was numerically stable in eager mode but produced finite loss at step 2 followed by NaN control gates and NaN loss at step 3 under `torch.compile`. The process still exited with code 0, demonstrating why exit status alone is insufficient.

## Efficient isolation sequence

1. Inspected metrics to locate the first logged non-finite step.
2. Ran 12 steps with `lr=0`, eager, custom kernels off: stable. This cleared data and forward-only execution.
3. Ran eager with nonzero LR: stable. This cleared the optimizer in the eager path.
4. Ran compiled with custom kernels off: failed. This cleared custom Triton kernels.
5. Checked a standalone lexical MLP: finite gradients. This cleared the isolated module.
6. Checked the full exact production shape and inspected gradients immediately after backward:
   - step 1: all gradients finite;
   - step 2: loss finite, output gradient finite, but 156 parameter-gradient groups non-finite.
7. Dense GQA compiled for two steps stayed finite.
8. Independent lexical tables stayed finite; the tied/shared lexical path failed.

This localized the fault to compiled backward interaction with the shared lexical path rather than data, SDPA generally, the loss, AdamW generally, or custom kernels.

## Important epistemic correction

Several plausible interventions did not fix the exact reproducer:

- registering the shared embedding only once;
- computing its lookup once at model level;
- cloning the shared values per layer;
- switching Python 3.12 to 3.11.

Therefore these were not valid root-cause fixes. The durable lesson is to require the original reproducer to pass before declaring causality.

## Cost-aware response

The invalid compiled full run was not continued. A valid eager control completed, but a slower eager W/R/V run was stopped early when the user rejected the throughput regression. Optimization then targeted exact redundant work:

- hoist deterministic lexical-address calculation shared by all layers;
- fuse separate R/W/V input projections into one concatenated GEMM while retaining distinct parameters.

Each optimization received equivalence/unit tests and a short throughput smoke before any new full-budget run.

## Measurement lesson

Report medians after warmup, not only final or maximum samples. Keep these labels explicit:

- valid eager measurement;
- invalid compiled measurement (NaNs; diagnostic only);
- prior accelerator historical measurement;
- current accelerator matched measurement.

Do not use an invalid compiled peak as a performance baseline.

## Operational pitfalls

- A broad `pkill -f` pattern can match the SSH command containing the pattern and terminate its own session. Resolve the remote PID first or use a pattern that cannot match the search command itself.
- A whole-file stage in a dirty workspace can capture unrelated local edits. Inspect `git diff -- <file>` against `HEAD` before staging and prefer hunk-level staging or reconstruct the intended patch.
