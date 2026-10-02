# Reviewer-Driven Architecture Paper Cleanup

Session lesson from a TMLR-style review: when reviewers point out that a paper's headline mechanism is unsupported or no longer in the evaluated model, cleanly pivot the paper instead of defending the old framing.

## When to use

Use this note when revising an ML architecture paper after review, especially when:

- the title/abstract emphasize a component that is not present in the strongest experiment,
- a theorem analyzes a mechanism different from the implemented architecture,
- ablations are confounded or described inconsistently,
- the user says a component has been removed and asks to “clean” the paper.

## Cleanup workflow

1. Switch/open the exact paper repo the user names before searching or editing.
2. Search all paper sources for the removed mechanism and related theorem labels/figures, not just the main English `.tex` file. Include translations if present.
3. Read the structural zones before editing: title/abstract, introduction contributions, architecture section, theory section, experiment tables/captions, limitations, conclusion.
4. Remove the unsupported mechanism from the claim surface:
   - title,
   - abstract,
   - contribution list,
   - architecture overview/captions,
   - comparison tables,
   - limitations/future-work unless explicitly retained as future work.
5. Remove or demote mismatched theory. If a theorem/corollary analyzes a different mechanism than the implemented model, delete it from the main paper unless the user explicitly wants an intuition-only appendix.
6. Remove matching error terms and complexity terms; do not leave symbolic remnants such as `E_mu`, `mu-update`, or stale labels/captions.
7. Reframe experiments around what was actually evaluated. For Complexity/Token-Routed papers, if Mu is removed, present the core as Zipf-balanced deterministic lexical routing plus Shared Lexical Expert / residual routed branch.
8. Add caveats where reviewers were right: single-seed, proxy ablation not strict iso-parameter, matched-token vs compute/wall-clock evidence.
9. If a proxy/component ablation is confounded enough to distract reviewers (parameter mismatch, token-count inconsistency, average-loss-only reporting, caption/plot conflict), remove it as evidence rather than trying to save it with caveats. Recenter the paper on the cleanest validated experiment.
10. Preserve useful ancillary engineering measurements only with explicit scope labels. For example, inference throughput from an earlier/smaller checkpoint may remain as an "inference sanity check" or deployment compatibility check, but must not be framed as evidence for the main scaling/quality claim.
11. Compile the paper after edits. Run at least one extra LaTeX pass if references changed.
12. Search again for stale mechanism names, removed-ablation labels, and figure labels before finalizing.

## Complexity/TMLR-specific pattern

If Mu-Guided Attention is removed, the defensible framing becomes:

```text
COMPLEXITY-DEEP: Zipf-Balanced Deterministic Lexical Routing for Language Model MLPs
```

Core claim:

```text
Deterministic token-id routing with Zipf-balanced greedy bin-packing balances expected corpus load and can improve matched-token loss when used as a residual routed branch with a shared MLP path.
```

Avoid claims that the removed mechanism explains 300M results. Replace `TR + Shared + Mu` language with `TR + Shared + Zipf`, and explicitly say the 300M model is a residual Token-Routed variant with a large shared branch and small Zipf-routed residual branch.

## Verification checklist

- [ ] No stale mechanism name in `.tex` sources (`Mu`, `Guided`, mechanism-specific labels/figures).
- [ ] No stale confounded-ablation evidence remains if the decision was to remove it (`187M`, `171M`, `500M tokens`, old loss-curve figures, `Run 2`/`Run 3`, etc.).
- [ ] Title/abstract/conclusion align with the evaluated model.
- [ ] Mismatched theorem/corollary/proposition terms are removed or demoted.
- [ ] Tables no longer contain columns/rows for removed mechanisms or removed ablations.
- [ ] Figure captions no longer reference removed mechanisms or removed evidence.
- [ ] Ancillary benchmarks are explicitly scoped as sanity checks if they do not evaluate the main model.
- [ ] LaTeX builds successfully for every maintained language/version of the paper.
- [ ] Generated PDFs are updated if they are tracked in the repo.
