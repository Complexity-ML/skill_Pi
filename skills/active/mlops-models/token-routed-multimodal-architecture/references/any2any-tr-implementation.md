# Any-to-Any TR implementation reference

Session-derived scaffold for adding a paper-aligned multimodal Any-to-Any TR module without rewriting legacy multimodal prototypes.

## Context learned

The user expects the text TR result as a premise: TR already beats the base dense model. For multimodal work, do not keep explaining base-model comparisons. Build the Any-to-Any extension using the same winning ingredients:

```text
deterministic routed expert + universal shared expert
```

and Zipf-balanced routing for text.

## Minimal module shape

Add a new module instead of rewriting broad legacy code:

```text
complexity/multimodal/any2any_tr.py
```

Recommended public classes:

```text
Any2AnyTRConfig
Any2AnyTRModel
Any2AnyTRBlock
Any2AnyModality
ZipfStructuralRouter
RoutedSharedMLP
TargetQueryBuilder
```

Export them from:

```text
complexity/multimodal/__init__.py
```

## Required behavior tests

Create tests like:

```text
tests/test_any2any_tr.py
```

Cover at least:

1. Zipf router assigns the highest-frequency text tokens across different experts.
2. `sources={"image": image_tokens}, targets={"text": N}` returns `text_logits` even with no source text.
3. `sources={"text": text_tokens}, targets={"image": N}` returns `image_logits` even with no source image.
4. Shared expert sees every source + target token, not only source tokens.
5. Public exports work from `complexity.multimodal`.

## Minimal forward contract

```python
out = model(sources={"image": image_tokens}, targets={"text": 7})
assert out["text_logits"].shape == (batch, 7, text_vocab_size)
assert "image_logits" not in out
```

```python
out = model(sources={"text": text_tokens}, targets={"image": 9})
assert out["image_logits"].shape == (batch, 9, image_vocab_size)
assert "text_logits" not in out
```

## Core block contract

The MLP sublayer should look conceptually like:

```python
shared = shared_expert(x)
routed = routed_experts(x, route_ids)
return routed + shared
```

The target sequence is:

```text
[source modality tokens] + [target query tokens]
```

and route ids are concatenated in the same order.

## Routing policy

- Text source tokens: `token_id -> Zipf-balanced expert id` when frequencies are provided.
- Non-text sources: deterministic structural position route.
- Target queries: deterministic route from `(target_modality, target_position)`.
- Offset modality ids in structural routes so equal positions in different modalities do not trivially collapse to identical expert patterns.

## Verification commands used

When torch is available under Python 3.13 in this repo:

```bash
python3.13 -m pytest tests/test_any2any_tr.py -q
python3.13 -m pytest tests/test_any2any_tr.py tests/test_imports.py -q
python3.13 -m py_compile complexity/multimodal/any2any_tr.py complexity/multimodal/__init__.py tests/test_any2any_tr.py
git diff --check -- complexity/multimodal/any2any_tr.py complexity/multimodal/__init__.py tests/test_any2any_tr.py
```

If unrelated dirty files exist before editing, leave them untouched and mention them in the final report.
