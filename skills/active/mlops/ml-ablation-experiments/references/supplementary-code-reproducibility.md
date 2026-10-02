# Supplementary Code Reproducibility Checks

Use this when auditing paper supplementary code that is supposed to reproduce a headline training result, especially when the main repository has moved ahead of the released snapshot.

## Core lesson

A supplementary implementation can match the model architecture/parameter count while still failing to reproduce the claimed experiment because a data-dependent control silently falls back to a default. Verify the *run path*, not just the class definitions.

If the user clarifies that the headline result did **not** come from the legacy supplementary code, stop trying to make that legacy code authoritative. The reproducibility target becomes the actual harness/commit/configs that produced the result.

## Checks that caught issues

### 1. Match the headline configuration exactly

For a paper claim such as "300M Zipf-routed TR beats dense", verify:

- Hidden size, depth, attention heads/GQA.
- Routed/intermediate/shared widths.
- Shared/routed gates and their initial values.
- `top_k` and top-k blend weight.
- Mu or other optional mechanisms disabled/enabled exactly as claimed.
- Parameter counts for TR and dense are actually iso-param.

Example verified shape for a legacy 32k 300M snapshot:

```text
TR:    hidden=1024 layers=18 heads=16 kv=4 routed_inter=256 shared_inter=3840 top_k=2 primary_w=0.5 gates=1.0/0.1 Mu=False 306.486564M
Dense: hidden=1024 layers=18 heads=16 kv=4 dense_inter=4096 Mu=False 306.486528M
```

This only proves that snapshot's parameter matching; it does not prove the snapshot is the code path used for the reported run.

### 2. Detect silent fallback from Zipf to modulo

In token-routed code, `token_frequencies=None` often means "fallback to token_id % num_experts". That is fine for a debug fallback, but not for a Zipf headline run.

Audit every dataset mode:

```text
--dataset text    -> does it compute token frequencies from the text?
--dataset fineweb -> does it load/precompute token frequencies, or does it silently leave None?
```

If the paper result is Zipf-balanced, the FineWeb path should either:

- require `--token-frequency-file` / equivalent, or
- precompute/load frequencies explicitly, or
- fail loudly.

It must not silently run modulo routing while logs/comments claim Zipf.

### 3. Verify packaged tokenizer paths and vocabulary regime

Supplementary scripts are often run from the paper directory, not the source-tree root. If the packaged tokenizer is under `supplementary_code/tokenizer`, defaulting to `./tokenizer` can make examples fail or push users to use a different tokenizer.

Prefer script-relative defaults, e.g.:

```python
SUPPLEMENTARY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TOKENIZER_PATH = SUPPLEMENTARY_ROOT / "tokenizer"
```

Then verify the vocab size matches the model config.

Important: swapping from a 32k tokenizer to `tiktoken`/`o200k_base` changes parameter count dramatically because embeddings scale with `vocab_size × hidden_size`. Do not call an o200k run the same 300M setup unless the profile was resized for o200k.

### 4. If the real result used another harness, snapshot the real harness

When the actual reported result came from a separate training repo/framework, align the supplement by adding a clearly named snapshot directory instead of overfitting the old reference code.

Recommended shape:

```text
supplementary_code/o200k_framework/
  README.md                         # source commit, scope, install, commands
  complexity/                       # actual package snapshot
  configs/run_configs/...           # actual configs used
  scripts/...                       # actual launchers/trainers used
  tests/...                         # invariant tests for routing/config behavior
  tokenizer-o200k/tiktoken_config.json
```

The top-level supplementary README should say which code path reproduces reported results and which code path is legacy/reference. This prevents reviewers from testing a readable but non-authoritative snapshot and concluding the claims are unreproducible.

### 5. Add a token-frequency loader rather than inventing frequencies

If keeping a Zipf-capable legacy path, a durable loader should support at least:

- `.pt` / `.pth`: tensor or dict key `token_frequencies` / `frequencies` / `freqs`.
- `.csv` / `.txt`: one frequency per line or `token_id,frequency` rows.

Validate:

```text
len(freqs) == vocab_size
sum(freqs) > 0
freqs are non-negative
```

### 6. Smoke the reproduction guards

Minimal checks:

```bash
python -m compileall -q supplementary_code
python supplementary_code/training/train_300m_tr_local.py --dataset fineweb --steps 0 --save-steps 0
# should fail with a clear Zipf-frequency error if no --token-frequency-file is supplied
```

Also instantiate TR and dense to compare parameter counts after any fix.

For a framework snapshot, run its invariant test suite and a one-step smoke from the snapshot directory:

```bash
cd supplementary_code/o200k_framework
PYTHONPATH=. pytest tests/test_100m_ablation_configs.py -q
PYTHONPATH=. python scripts/train_100m_o200k_tr_local.py \
  --config configs/run_configs/ablations_100m/100m_zipf_shared.yaml \
  --dataset random --steps 1 --batch-size 1 --seq-len 16 \
  --eval-steps 0 --save-steps 0
```

## Pitfall wording for papers/reviews

Be explicit about scope:

```text
The reported o200k ablations use `supplementary_code/o200k_framework`, a snapshot of the training harness at commit <sha>. The older 32k implementation is retained only as a compact architecture reference.
```

For a legacy Zipf path:

```text
FineWeb runs require precomputed token frequencies; without them the script fails rather than falling back to modulo routing.
```
