---
name: tr-hash-evaluation
description: Use when evaluating TR-Hash. Enforce native protocols.
metadata:
  hermes_frontmatter:
    version: 1.0.0
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# TR-Hash checkpoint evaluation

## Runtime contract

- Use the TR-Hash-i64 inference engine for inference and benchmark requests; do not substitute Complexity Framework generation scripts.
- Record the exact checkpoint path/hash, TR-Hash-i64 commit, tokenizer source/revision, device, dtype, dataset split, example count, and scoring method.
- Do not treat configuration alone as evidence of a completed run. Report only persisted artifacts or observed execution output.

## Refinement token contract

- Inspect and report the tokenizer's registered special tokens and IDs before generating.
- For refinement and raw causal scoring, encode with `add_special_tokens=False` explicitly.
- Do not prepend BOS, `<|begin|>`, role markers, or other special tokens.
- Do not apply a chat template.
- Do not use a BOS fallback for empty contexts; fail clearly instead.
- Verify the actual input IDs contain no registered special-token IDs and save representative IDs in the report.
- A special token existing in the tokenizer vocabulary does not authorize injecting it into a refinement prompt.

## PIQA

- Evaluate the full 1,838-example validation split unless the run is explicitly labeled a smoke test.
- Score both choices with zero-shot causal continuation log-likelihood via teacher forcing.
- Reproduce the published 200M prompt contract exactly: context is the raw `goal`; continuation is one ASCII space plus `solution.lstrip()`, with trailing solution whitespace preserved; encode both pieces with `add_special_tokens=False`; use no chat template.
- Preserve model-native tokenizers across lineages. The 200M releases use `AETHORIA-AI/TR-HASH-Tokenizer-32K`; the Agentic 100M line uses the separately trained, ID-incompatible `AETHORIA-AI/TR-HASH-Tokenizer-32K-Agentic`. Never pair a checkpoint with the other lineage's tokenizer merely to force identical token IDs.
- Treat `bos_token_id` or `<|begin|>` registration as metadata, not insertion policy. The Agentic tokenizer's empty `TemplateProcessing` special-token map means default/`add_special_tokens=True` encoding inserts no BOS or EOS; keep explicit `False` for benchmark reproducibility.
- Do not manually prepend `<|begin|>` for the canonical benchmark. Controlled full-PIQA tests on Agentic 100M base, 55%, and 65% checkpoints found no consistent gain; the 55% normalized score fell by 18/1,838 answers.
- Report raw accuracy and length-normalized accuracy separately, with correct counts.
- Preserve the dataset source/hash and machine-readable report.
- Do not compare a limited smoke score (for example 16 or 32 examples) to a full validation score as if equivalent.

## Canonical 200M lineage

- The final 200M SFT checkpoint is `AETHORIA-AI/TR-HASH-MoE-200M-160B-SFT`, not a v2/epoch alias.
- Published full PIQA evidence: 200M refinement step 8,156 — 68.66% raw, 68.39% normalized on 1,838 examples; 200M final SFT — 68.01% raw, 69.10% normalized on 1,838 examples.
