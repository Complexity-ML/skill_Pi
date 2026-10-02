# Single-scan routed WVR: preserving throughput while adding occurrence capacity

## Trigger

Use this pattern when a fixed-state WVR/Stable-Delta mechanism needs token- or context-specific capacity but a bank of independently recurrent matrices destroys training throughput.

## Failed decomposition

A seemingly natural design is

\[
Y = Y_{\mathrm{common}} + \alpha Y_{\mathrm{routed}},
\]

where the routed branch owns one recurrent matrix per slot. Even when all W/R/V projections and route logits are computed for the full sequence, this design still performs one causal triangular solve for the common state plus one solve per routed slot. The dominant cost scales with the number of scans, not merely the routed rank.

A real H100 example at batch 16, sequence 2048, approximately 98.2M parameters:

- sequential four-slot routed state: 4,688 train tok/s with exact-vocabulary loss;
- tensorized common plus four independently scanned routed slots: approximately 83.8k tok/s;
- matched Stable-Delta parent in the same runtime: approximately 94.4k tok/s.

Do not compare a candidate's live throughput to a historical number from a different compiler/runtime state. Rerun the parent under the same runner and report the paired overhead.

## Preferred construction

Use one rectangular recurrent matrix and one Stable-Delta scan. Augment the W/R address space with orthogonal routed subspaces while keeping the contextual value width fixed:

\[
R_t = [R_t^{\mathrm{common}};\;g_{t,1}u_t;\ldots;g_{t,S}u_t],
\]
\[
W_t = [W_t^{\mathrm{common}};\;\alpha g_{t,1}u_t;\ldots;\alpha g_{t,S}u_t],
\]
\[
V_t = W_v h_t,
\qquad
M_t\in\mathbb{R}^{R_W\times R_V}.
\]

Here `g` is a straight-through top-1 route, `u` is a small contextual/lexical address, and `alpha` starts at zero. R sees routed rows immediately while W's routed contribution is zero initially. Since routed rows of M start at zero, the forward pass exactly reproduces the common parent at initialization, but `alpha` receives gradient through later routed reads.

This is still WVR, not disguised QKV:

- no position-wise QK score matrix;
- no softmax over prior tokens;
- no growing token-indexed state;
- one fixed recurrent matrix per active invocation;
- one chunkwise Stable-Delta triangular solve;
- contextual values remain `V = W_v h`.

## TDD contracts

Before integration, assert:

1. State is rectangular `[batch, common_rank + slots*slot_rank, value_rank]`.
2. At `alpha=0`, outputs exactly match the Stable-Delta parent.
3. `alpha` receives a finite non-zero gradient.
4. Full-sequence and token-by-token incremental outputs/states match.
5. The integrated model stores exactly one context matrix plus one previous-write address per active layer cache.
6. Parameters may be shared across active layers, but runtime state tensors are independent unless cross-layer state sharing is explicitly intended and tested.
7. H100 forward+backward gradients are finite in BF16 at target batch and sequence length.

## Throughput gate

1. First test uncompiled target-shape forward+backward for memory and finite gradients.
2. Then test the actual compiled FineWeb/exact-vocabulary-loss/optimizer path for at least 20 steps.
3. Use a 100-step no-eval smoke if 20-step throughput may still include warm-up.
4. Run a matched parent control in the same runtime.
5. Promote based on paired overhead, not an absolute historical tok/s threshold.
6. Stop and delete a run immediately if the implementation accidentally retains a Python token loop or multiplies scans by the slot count.

## Operational note

The streaming data worker may abort during Python teardown after complete metrics have been saved. Treat the run as mechanically complete only when the expected final metrics row exists; preserve the metrics, but distinguish teardown failure from training failure.