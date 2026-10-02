# Reviewer evidence package for a new autoregressive architecture

Use this structure when the core claim replaces attention or another canonical sequence mixer.

## Minimum matched controls

1. Standard attention + dense FFN baseline.
2. New sequence mixer + dense FFN (isolates the mixer).
3. New mixer + shared/object mechanism without routed residual (isolates sharing/object contribution).
4. Complete architecture (isolates routed/micro-expert residual).
5. If sharing is a headline claim, add untied or detached-object control while keeping capacity as close as practical.

Match realized parameter count, tokenizer, corpus/split, sequence length, optimizer/schedule, seed, update count, and token count. Report intentional mismatches.

## Checkpoint-level structural evidence

Audit the realized export, not just a toy model or YAML:
- no forbidden Q/K/V or fused QKV parameters/modules;
- expected mixer tensor families only;
- shared objects are actually identical/tied;
- realized parameter count and config hash;
- compatibility names such as `self_attn` are explained if they remain in ABI paths without implementing attention.

Make the audit fail closed and emit JSON.

## Functional evidence

- Future-token perturbation leaves prefix outputs unchanged.
- Full-sequence logits match cached token-by-token logits within a declared tolerance.
- Cache/state shape and addresses stay fixed across decode steps.
- Compare eager and CUDA Graph token sequences over enough steps to wrap every ring/state buffer.
- Sweep associative recall, induction, synthetic ICL, and needle distance before, near, and beyond the finite receptive field. Save accuracy, NLL, rank, and margin.

## Deployment evidence

Save raw official benchmark JSON and realized command/version. Sweep batch/concurrency and separate:
- long-prompt prefill;
- time to first token;
- batch-one decode latency;
- saturated decode throughput;
- memory versus context length.

Dataset-specific CLI flags can differ from generic length flags. Confirm realized input/output token counts from logs before accepting a run.

## Artifact layout

```text
results/
  raw/*.csv
  raw/*.json
  consolidated/results.json
figures/*.png
scripts/plot_results.py
scripts/audit_checkpoint.py
configs/*.yaml
tests/
MANIFEST.md
```

`MANIFEST.md` maps every claim/table/figure to config, raw input, regeneration command, and output. PNGs must be deterministic derivatives of CSV/JSON; do not replace requested result figures with conceptual diagrams.
