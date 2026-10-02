# Standalone Mini-Framework for Anonymous Review

Use this pattern when experiment metrics were produced by a large private/proprietary research framework that cannot be shipped to reviewers.

## Required separation

Keep two evidence layers distinct:

1. **Historical run evidence**: realized configs, raw CSV/JSON metrics, hardware/backend metadata, source commit identifiers if anonymous, dataset revision/path/hash, and deterministic table generation.
2. **Shareable executable artifact**: a small standalone implementation of the claimed equations and realized architecture, with no imports, package dependency, copied registry, plugin system, or runtime path into the private framework.

Do not solve this by copying the whole private package into the supplement. That creates unnecessary disclosure, deanonymization risk, stale dependencies, and a reviewer-hostile install.

## Mini-framework contents

Include only the complete causal path needed to understand and exercise the claim:

- explicit model/config dataclass;
- candidate and matched-control mixers/attention;
- normalization, position encoding, feed-forward/residual path actually used;
- tied/shared parameters that affect parameter counts;
- full-sequence and incremental cache path;
- chunked loss if required by the reported vocabulary/model size;
- deterministic data split/tokenization adapter;
- minimal training/evaluation CLI and paper configs;
- tests and a clean `pyproject.toml`.

No generic registry, unrelated models, serving stack, CLI framework, experiment dashboard, private package import, or repository metadata.

## Tests that make the artifact credible

Test from a clean isolated environment and again from the final extracted ZIP:

- the source contains no private-package imports or directory;
- paper YAMLs instantiate successfully;
- realized trainable parameter counts match exactly;
- candidate/control module types are explicit;
- causality and full/incremental equivalence hold;
- disabled lexical/residual paths are input-invariant as claimed;
- one real optimization step is finite;
- tokenizer vocabulary size and deterministic split match the paper;
- CLI `--help` and a small smoke path execute.

Scan the ZIP bytes/names for private package names, author/org strings, local paths, cloud IPs, `.git`, caches, checkpoints, and datasets.

## Naming the claimed mechanism

Name the paper and artifact after the **controlled experimental axis**, not every shared substrate in the model.

- Hidden states may carry lexical information because embeddings, lexical objects, or token-routed feed-forward experts affected earlier layers. That does not make an attention operator explicitly lexical.
- Call attention explicitly lexical only when its R/W/Q/K/V construction has a direct token-identity/object path (for example $W_t=f_W(h_t)+g(x_t)$). If $R/W/V$ are projected only from contextual hidden states, describe the operator as contextual or content-based; “semantic” is an interpretation, not an experimentally isolated property.
- If lexical objects or micro-experts are identical in candidate and control, they are controlled shared architecture and cannot explain the measured candidate-control delta. Do not put them in the headline as the demonstrated treatment.
- A one-seed lexical-residual ablation may be reported descriptively, but it does not justify renaming a multi-seed contextual comparison. Keep direct lexical attention, lexically routed hidden states, and shared lexical feed-forward paths distinct in title, abstract, method, and supplement README.

## Provenance wording

Be explicit in the README:

> Raw metrics and realized configs come from the archived accelerator runs. The standalone source implements the same equations, dimensions, data split, and parameterization; it is not claimed to be a byte-identical copy of every internal training utility.

Do not present a newly written mini-framework as the literal historical source snapshot. Conversely, do not call it a mere toy if it reconstructs the full claimed model path and exact parameter counts.

## Checkpoint policy

Checkpoints are **not required** for ordinary loss/throughput claims when raw metrics, realized configs, code, dataset identity, and regeneration logic are present. Require a checkpoint only for claims that inspect learned internal state: learned gates, routing assignments, final residual usage, hidden-state probes, or post-training weight structure.

For completed runs, mirror at minimum `metrics.csv` and `run_config.json`. Mirror checkpoints only when a planned claim needs them. Do not block or weaken a loss/throughput table merely because weights were intentionally omitted.

## Recovery before cloud deletion

Before deleting paid compute, enumerate primary seeds and all potentially cited ablations. Copy only the small required artifacts first; verify local finite evaluation values, throughput aggregation, configuration flags, and hashes. A persistent volume can be remounted briefly for recovery without rerunning training. Once the files are verified locally, terminate the compute instance; retain the volume only as optional temporary insurance.

## Final delivery hygiene

Do not leave the user choosing among stale and current extracted supplement directories.

- Keep the mini-framework source in one canonical source directory and generate the ZIP from that source, never from a previously staged/extracted supplement.
- Give the upload archive one canonical filename and verify it after any deletion or rebuild by extracting, testing, scanning, and hashing it again.
- Distinguish source, staging directory, extracted copies, and upload ZIP explicitly. The file picker needs the `.zip`, not an extracted folder.
- If the user works from a different worktree/project than the one used to build the artifact, copy only the verified PDF/ZIP into a clearly named `submission/` directory in the workspace they actually browse. Re-hash the copied files and report that exact path.
- Prefer a submission directory containing only the current upload files; stale `supplement`, `supplement 2`, or old ZIP variants create avoidable last-minute mistakes.
