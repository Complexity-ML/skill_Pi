# Checkpoint-grounded routing audit

Use this procedure when a paper claims static, lexical, frequency-balanced, hash, or top-k routing. Source code and config filenames are not sufficient evidence: the saved routing buffers in the evaluated checkpoint are the closest available record of what actually ran.

## Evidence order

1. Evaluated checkpoint tensors and persistent buffers.
2. Checkpoint `config` and launch `args`.
3. Raw metric CSV/logs from the same run.
4. Training code at the commit used for the run.
5. Paper prose, figure-generation scripts, and filenames.

Resolve contradictions in that order. Never preserve a higher-level claim merely because a plot or run name contains words such as `zipf` or `balanced`.

## Safe inspection

For multi-gigabyte PyTorch checkpoints, use `torch.load(path, map_location="cpu", mmap=True, weights_only=False)` and inspect only metadata and small routing buffers. The bundled `scripts/audit_routing_checkpoint.py` reports metadata, expert counts, and exact permuted-modulo structure.

If PyTorch is unavailable, inspect the zip archive's small `data.pkl` with `zipfile`/`pickletools` to locate metadata keys before choosing an environment that can load the checkpoint. Do not unpickle an untrusted checkpoint.

## Proving or disproving a routing claim

- Check whether token-frequency data is present at construction time. Beware serialization helpers that omit tensors; a missing serialized frequency vector alone is not conclusive.
- Inspect every saved `token_to_expert` table, not only layer 0.
- Test exact structural hypotheses, e.g. whether each table is a layer-specific permutation of `token_id % E` across the entire vocabulary.
- Compare vocabulary assignment counts with corpus traffic. Equal vocabulary counts do not imply equal corpus-frequency load; conversely, a traffic-share curve is not a vocabulary-assignment plot.
- Trace fallback conditions in the exact data path. A frequency-aware branch that runs only for local text or token shards may silently fall back when training uses a streaming dataset.
- For top-k routing, inspect all persistent route tables. If secondary routes are not saved, state that limitation rather than inferring their construction.

## Metrics verification

- Compare candidate and baseline CSVs at identical steps and token budgets.
- Deduplicate resumed logs by step before computing trailing-window means; keep the last row for each step.
- Report exact final train values, the last common validation checkpoint, and the deduplicated trailing mean separately.
- A single matched run pair supports a run-specific result, not a general effect or wall-clock claim.

## Figure audit

Regenerate distribution plots from checkpoint buffers. A paper figure that reports counts inconsistent with the checkpoint is stale, even when the discrepancy is small. Titles must say whether the plot shows vocabulary assignments, corpus token traffic, or measured expert execution shares, and must name the actual routing rule rather than the intended one.

## Router terminology and condition naming

Do not equate a routing fallback with the absence of routed experts. Separate four mechanisms explicitly:

1. **Expert functions**: the MLP experts that process selected tokens.
2. **Selection mechanism**: a learned gating network versus a fixed lookup table.
3. **Top-k combination**: which primary and secondary experts are selected and whether their weights are fixed or learned.
4. **Branch gates**: learned shared/routed scalar gates are not an expert-selection router.

Name an ablation by its realised primary and secondary rules, not with a vague label such as `default fallback`. For example, distinguish `modulo-primary / balanced-secondary top-2` from `modulo-adjacent top-2`, even though neither has a learned router. If two nominal controls produce exactly the same primary and secondary tables, call them equivalent controls and treat score differences as run variance.

## Confounded ablations

If a fallback makes two named routing controls mathematically identical, their difference estimates run nondeterminism/variance, not a routing effect. When reviewers require the ablation evidence, preserve the measured table and curves but:

- rename each condition by verified primary/secondary lookup behavior rather than the intended config label;
- mark the suite exploratory and single-seed;
- state which controls are equivalent and prohibit causal interpretation of their ranking;
- retain qualitative conclusions only when the confound does not invalidate them (for example, a large shared-vs-no-shared gap);
- regenerate the PNG legends and captions so the image cannot reintroduce the obsolete claim.

An intended frequency-aware or bin-packing path that was not activated belongs in Future Work, not Methods or Results. The follow-up protocol should compute frequencies from the exact training stream, serialize the routing table before initialization, store a table hash and frequency provenance in each checkpoint, verify expected and realized traffic, and compare against the audited lookup baseline over multiple seeds.

## Hardening a corrected supplementary artifact

When the audited runtime behavior differs from the intended config, correcting only the paper is insufficient. Repair the released reproduction snapshot without pretending the repaired source is byte-identical to the historical training commit:

1. Describe it as an **audit-corrected reproduction snapshot**, and preserve raw logs/checkpoints as the historical evidence.
2. Introduce an explicit strategy name for the realized lookup, including both primary and secondary rules (for example, `modulo_balanced_secondary`). Do not use ambiguous names such as `default`, `fallback`, or the unexecuted intended strategy.
3. Write failing tests first for both required behaviors: the explicit strategy reproduces the verified fixed top-k table, and an intended frequency-aware strategy without frequencies raises a clear error.
4. Remove silent fallbacks. An explicit `zipf`/frequency-aware request must require frequency data; it must never silently become modulo.
5. Make the audited strategy the default only when that matches the artifact's stated reproduction target. Keep the unevaluated strategy available solely through explicit configuration.
6. Update the strategy allowlists and defaults at every propagation boundary: low-level MLP config, model config deserialization, CLI choices/defaults, profile builders, model blocks, pipeline checks, YAMLs, launch scripts, orchestrators, and tests.
7. Rename config and launcher filenames as well as display labels. Historical metric CSV filenames may remain unchanged as provenance identifiers, but plotting code must map them to truthful labels.
8. Document that fixed token-to-expert lookup is still expert routing, but not a learned expert router; fixed top-k weights and learned shared/routed branch scalars are separate mechanisms.
9. Verify targeted tests, the full included suite, Python compilation, shell syntax, the exact config count, absence of stale experiment strategy values, and ZIP integrity. Remove `__pycache__`, `.pyc`, and test caches before packaging.
10. Rebuild the archive with a stable top-level directory and report its checksum. Re-open or text-extract the final PDF/ZIP rather than trusting an application cache.
