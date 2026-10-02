# Supplement Startup-Equivalence Audit

Use this checklist when a paper's supplement is intended to reproduce an evaluated ML checkpoint.

## Canonical evidence order

1. Saved checkpoint config, launch args, tensor shapes, and persistent routing tables.
2. Raw metric CSVs/logs and exact tokenizer asset.
3. Historical launch command or serialized run config.
4. Current scripts and YAML.
5. Run names, comments, README prose, and figure labels.

Never rewrite checkpoint evidence to match an intended config. If current code is hardened after the run, call it an **audit-corrected reproduction**, not the exact historical snapshot.

## Startup audit

- Enumerate every entrypoint, launcher, YAML, profile, tokenizer, and default.
- Remove unrelated legacy profiles carrying the same nominal model size.
- Load YAML through the production parser/config-merging path; CLI overrides must be included.
- Construct the resulting model config and assert dimensions, vocabulary, routing strategy, top-k, blend weights, branch gates, dataset, seed, precision, steps, per-device batch, sequence length, and world size.
- Keep weighting concepts separate:
  - **top-k blend weights** combine selected expert outputs and may be fixed;
  - **branch-gate initialization** configures shared versus routed residual scaling at step zero;
  - **checkpoint gate values** are learned terminal tensors and need not equal initialization.
  Attach provenance to each value. A CSV note or figure label can document launch intent but cannot substitute for saved config/args; a terminal tensor can establish the learned value but not, by itself, prove its initialization.
- Interpret token budgets explicitly: `steps × world_size × batch_per_device × sequence_length`.
- Add a canonical launcher for the reported run; keep smoke-test defaults separate and visibly named.
- Load-test the exact tokenizer from the packaged path and guard against a mismatched vocabulary. Compare provenance/checksums rather than relying on directory names.
- For intended frequency-aware routing, fail loudly when frequencies are absent. Give any historically realized fallback an explicit strategy name and test its full primary and secondary top-k tables.

## Artifact audit

- Include every raw CSV/log needed by plotting scripts.
- Include throughput source logs or document aggregation windows and deduplication.
- A plot generator without inputs is not reproducibility.
- Do not promise weights or checkpoints unless they are actually attached or have a concrete release plan compatible with review anonymity.
- Exclude caches, credentials, machine-specific paths, and unrelated checkpoints from the archive.
- Test ZIP integrity and inspect its top-level layout.
- Treat verification outputs as dependency-bound. If a late correction changes a canonical value (tokenizer provenance, gate initialization, routing rule, metric label, or launcher argument), regenerate every dependent test fixture, figure, PDF, archive, and checksum before reporting completion. Do not reuse a passing result produced before the correction.

## Evaluation naming

Inspect dataset construction. Two fresh iterators over the same training split are not a held-out validation set. Report them as an evaluation stream/subset drawn from the training split unless a disjoint partition is implemented and documented.

## Translation audit

Run the architecture and claim ledger independently on every language version. Search for removed mechanisms, obsolete scales, stale theorems, unsupported causal explanations, malformed tables, and conclusions that diverge from the canonical source.
