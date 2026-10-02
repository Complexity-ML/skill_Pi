# Controlled multi-seed artifact freeze

Use this checklist before shutting down or deleting a paid training instance that produced paper evidence.

## Freeze before shutdown

1. Enumerate every run that may appear in the paper, including:
   - primary matched seeds;
   - component ablations (for example lexical-on/off or normalization on/off);
   - negative controls and failed-but-interpreted runs;
   - any historical run still quoted numerically.
2. For every run, mirror before shutdown:
   - per-step metrics CSV/JSON;
   - realized configuration, not only the intended YAML;
   - final checkpoint when claims involve learned gates/state/weights;
   - source commit and, when dirty, a source diff or immutable source snapshot;
   - logs needed to explain exclusions or numerical failures.
3. Freeze the exact evaluation data identity: repository/config, revision, shard path, size, and SHA-256. Mirror the shard if license and storage permit.
4. Generate one machine-readable summary containing per-seed values and aggregate statistics. Keep raw values at full precision; round only in rendered tables.
5. Produce a manifest that hashes checkpoints, data, summary, configs, and metrics. Verify hashes after transfer on the destination machine.
6. Only after destination verification should the paid instance be stopped or terminated.

If an ablation was not mirrored, do not reconstruct its raw artifact from chat, prose, or remembered output. Exclude its quantitative row from the final reviewer package and narrow the claim. Restarting the instance to recover evidence is optional and cost-sensitive, not something to hide with fabricated provenance.

## Deterministic bilingual tables

Prefer a script that reads the frozen summary and emits both EN and FR LaTeX fragments. The manuscripts should `\input{}` those generated files. Run the generator in the review staging directory and compare SHA-256 values against the source-tree outputs; identical hashes prove the package regenerates the submitted tables.

## Clean package verification order

1. Build the anonymous staging tree and ZIP with an idempotent script.
2. Scan staged and extracted contents for identity strings, secrets, local paths, caches, checkpoints, and large datasets.
3. Run focused tests from the staging tree in a fresh isolated environment (for example `uv run --isolated ...`).
4. Regenerate tables inside staging and compare hashes.
5. Re-run the package builder after testing, because pytest/build commands may create `.pytest_cache`, `__pycache__`, or package metadata in staging.
6. Validate the rebuilt ZIP, compare embedded PDFs byte-for-byte with the final PDFs, and publish final SHA-256 values.
