# Causal sequence-model review checklist

## Causality probes

- Compare two inputs sharing a prefix but differing only in future states; prefix outputs must match.
- Repeat with `attention_mask=None`, an all-valid 2D bool mask, and an additive mask if supported.
- A common bug is `is_causal = attention_mask is None`: any padding mask then silently enables bidirectional attention.

## Cache probes

- Compare full execution to one-token cached decoding.
- Compare full execution to cached chunks of 2–4 new tokens.
- With a cached prefix of length `p`, query `i` in the new chunk may attend only through key `p+i`.
- A common bug is disabling `is_causal` whenever query length differs from key length; that is safe for one new token but leaks within multi-token chunks.

## Mask composition

Build the causal allowance from absolute query and key positions, then combine it with the user mask. Validate batch and key dimensions. For current-chunk masks used with a cache, document whether past positions are implicitly valid or require a full key-length mask.

## Initialization/configuration

- Generic initializers often recognize conventional names such as `o_proj` but miss aliases such as `output_proj`.
- Verify empirical weight standard deviation against the intended residual scaling.
- Reject unsupported flags rather than silently ignoring them.
- Exercise non-default RoPE theta and positional offsets.

## Evidence consequence

If any fix changes a path used by the historical run, label current source as audit-corrected and rerun before making the metric canonical.
