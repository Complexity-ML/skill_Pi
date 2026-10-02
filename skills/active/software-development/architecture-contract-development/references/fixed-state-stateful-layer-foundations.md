# Fixed-State Stateful Layer Foundations

Use this pattern when introducing a standalone stateful sequence mixer before scheduler or cache-manager integration.

## Contract decomposition

Encode each architectural requirement as an observable test:

- **Numerical contract:** compare full-sequence output directly with the framework reference operation, including causal padding and dilation.
- **Incremental contract:** stack token-by-token decode outputs and compare them with the full-sequence path.
- **State ownership contract:** pass caller-preallocated storage, record `data_ptr()` before decode, and assert it is unchanged afterward.
- **Batching contract:** use noncontiguous state slots and reorder requests between decode steps; outputs must still map to the correct request.
- **Position contract:** pass explicit zero-based absolute positions rather than relying on loop-local counters hidden inside the layer.
- **Public/checkpoint contract:** assert exact parameter names and shapes, including the absence of rejected abstractions such as QKV.
- **Scope contract:** keep the change to the new layer module and focused tests; do not add scheduler/cache-manager wiring until explicitly requested.

## Ring-buffer reference design

For kernel size `K` and dilation `D`, a sufficient fixed ring length is:

```text
state_size = D * (K - 1) + 1
```

At absolute position `p`:

1. Write the current token to `p % state_size` in the request's selected slot.
2. Gather positions `p - D*(K-1), ..., p-D, p` modulo `state_size`.
3. Mask negative source positions to preserve causal zero-padding at sequence start.
4. Apply the Conv1d weights in their native correlation order (oldest sample to current sample).

The caller owns slot uniqueness and monotonically increasing positions for each active slot. Document those assumptions instead of introducing scheduler policy into the standalone layer.

## Gated mixer surface

When checkpoint compatibility is part of the contract, make names structural rather than documenting aliases. A compact gated mixer can expose:

```text
depthwise.weight
gate_proj.weight
up_proj.weight
o_proj.weight
```

A representative path is `o_proj(silu(gate_proj(x)) * depthwise(up_proj(x)))`. Test the full/decode equivalence of the wrapper as well as the convolution primitive. Assert the exact parameter-name set so QKV cannot appear accidentally.

## Verification notes

A focused pure-module run may use pytest collection boundaries to avoid unrelated repository-wide fixtures, but this is only a local isolation aid. Report it accurately and still run the repository's normal targeted command when its declared development environment is available. Never turn a transient missing dependency into a permanent rule about the project or test runner.
