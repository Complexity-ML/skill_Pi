# Multimodal Any-to-Any Routing Checklist

Use this as a concrete reference when reviewing or designing Complexity-style multimodal routing models.

## Claims to verify in code

- **Shared expert:** check for an explicit parallel path such as `routed_expert(x, route_id) + shared_expert(x)` in each block. A `general_mlp` run before/after modality MLPs is a different design and should be named as a shared/general MLP path, not the paper-style shared expert.
- **Any-to-any:** check whether the model can request target modalities absent from the input. If outputs are only produced for modalities present in `sources`, it is reconstruction/joint encoding, not true any-to-any generation.
- **Target queries:** true any-to-any needs target query tokens or target latent slots, e.g. `[source tokens] + [target_text_queries]` for image→text or `[source tokens] + [target_image_queries]` for text→image.
- **Output tokens:** prefer modality token/codebook outputs for image/audio/video first; direct pixel/mel/video decoding makes the problem much harder and muddies the architecture claim.

## Clean architecture definition

For token `i`:

```text
y_i = E_route(r(i), x_i) + E_shared(x_i)
r(i) = deterministic_route(modality_i, structure_i)
```

Routing keys can be:

- text: lexical/token-id bucket, ideally Zipf-balanced
- image: spatial patch bucket or space-filling-curve bucket
- audio: temporal or time-frequency bucket
- video: spatiotemporal tubelet bucket
- target queries: target modality + target position bucket

## Any-to-any contract

A clean API separates sources and targets:

```python
model(
    sources={"image": image},
    targets=["text"],
)
# returns text logits even though text was not an input

model(
    sources={"text": prompt},
    targets=["image"],
)
# returns image token logits/latents even though image was not an input
```

## Baseline framing

If the claim mirrors deterministic token-routed language-model work, compare against the model's own matched base architecture, not vaguely against external systems:

- Dense Any2Any base: same source/target interface, tokenizer, data, optimizer, training budget; standard dense MLP.
- Routed-only Any2Any: deterministic routed experts without shared expert.
- Shared-only: shared expert/dense shared path without routed specialization.
- Routed + shared: proposed model.

Claim wording should be precise:

```text
At matched architecture, data, optimizer, and training budget, the routed+shared Any2Any model outperforms its dense Any2Any base model.
```

Avoid claiming to beat frontier any-to-any systems unless evaluation is genuinely comparable.

## Minimal validation path

Start with text↔image only:

1. implement source encoders for text and image tokens/latents
2. implement target query tokens for text and image targets
3. implement routed+shared block
4. implement dense matched baseline
5. train/evaluate image→text and text→image under identical budget
6. only then add audio/video

Keep multimodal claims marked experimental until this controlled base-model comparison exists.
