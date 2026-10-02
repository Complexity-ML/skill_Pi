# Contextual W/R/V on H200: case study

## Experimental shape

- One paid H200; BF16; batch 16; sequence 2048; 100,007,936 tokens per run.
- Matched GQA and contextual W/R/V used the same lexical-object micro-expert MLP, optimizer, LR schedule, tokenizer, data stream, evaluation cadence, and seed.
- Historical H100 and new H200 throughput were kept separate.

## Numerical failure isolated

`torch.compile` produced finite forward losses but, on the second backward at production shape, 156 parameter groups became non-finite. Differential probes established:

- eager was finite;
- compiled dense SwiGLU was finite;
- custom kernels were not the cause;
- Python 3.11 vs 3.12 was not the cause;
- failures involved the tied lexical representation across layers;
- changing registration ownership, doing one lookup, and cloning per-layer consumers did not repair AOTAutograd.

After three falsified fixes, compiled training was abandoned for controlled eager runs rather than wasting paid time.

## Exact throughput optimizations

Two transformations preserved the model math:

1. The deterministic float64 sinusoidal lexical address, identical in every W/R/V layer, was computed once per model forward instead of once per layer.
2. Separate R/W/V input projections were concatenated into one `F.linear` GEMM, then split, matching the established GQA projection pattern.

Focused causality/equivalence tests were rerun, then both GQA and W/R/V were rebenchmarked on the same commit.

## Seed-42 ablation interpretation

Observed evaluation losses:

- matched GQA: 4.683425;
- full contextual W/R/V: 4.660939;
- W/R/V with lexical attention gates fixed exactly at zero: 4.662531;
- lexical-off W/R/V with per-head R/W RMSNorm bypassed/frozen: 4.795811.

Interpretation:

- The lexical attention residual explained almost none of the gain (+0.001592 loss when removed) and cost throughput.
- Per-head R/W RMSNorm was essential (+0.133280 loss when removed).
- The defensible candidate became contextual W/R/V + R/W RMSNorm, lexical residual off.
- One seed was insufficient for publication, so matched GQA and the candidate were scheduled on seeds 43 and 44.

## Multi-seed controlled result

Matched H200 evaluation losses for GQA versus contextual W/R/V + R/W RMSNorm with the lexical attention residual fixed off:

| Seed | GQA | W/R/V lexical-off | Paired delta |
|---:|---:|---:|---:|
| 42 | 4.683425 | 4.662531 | -0.020894 |
| 43 | 4.717673 | 4.686053 | -0.031620 |
| 44 | 4.708008 | 4.704711 | -0.003297 |

Aggregates:

- GQA loss: 4.703035 mean, 0.017657 sample SD.
- W/R/V loss: 4.684432 mean, 0.021137 sample SD.
- Paired delta: -0.018604 mean, 0.014300 sample SD; W/R/V won 3/3 seeds.
- The two-sided 95% t interval for the paired delta with only three pairs was approximately [-0.0541, +0.0169], so the defensible claim is a consistent three-seed observation, not established universal superiority.
- Mean throughput was 125,021 tok/s for GQA and 121,448 tok/s for W/R/V, a 2.86% penalty.

## Durable execution and offline recovery

A sequential chain launched through an SSH-owned process died during W/R/V seed 43 at step 2200. Because only the final step was checkpointed, that work was not resumable. The replacement used a remote `systemd-run` service so the chain survived SSH disconnects. Future chains should also save intermediate checkpoints.

FineWeb-Edu streaming then degraded from occasional retryable range-read closures to persistent CAS 403 errors. The successful escape hatch was:

1. Download the exact pinned `sample-10BT` first shard with the native `hf download` CLI, which succeeded even while direct HTTP resolve/CAS reads failed.
2. Verify the local Parquet before training: 2,152,819,114 bytes, 726,000 rows, 726 row groups, expected schema, and SHA-256 `b1ba7b2ce4cb5ea6ef42dca40263eabb85f37700d01693a68e9b30a31d78e871`.
3. Add an explicit local-Parquet override while preserving the remote loader default.
4. Read one train and one eval sample under that override.
5. Relaunch the durable service with the local path in its own environment.

The service log still described the dataset as “streaming,” but the stream source was now the local Parquet file. This distinction should be explicit in future logging.

## Artifact closure

Six primary checkpoints totaled about 7.17 GB. They were copied with resumable `rsync`, then SHA-256 was computed independently on H200 and local storage for every checkpoint. The exact 2.15 GB dataset shard was also copied and verified. On older macOS `rsync`, `--info=progress2` was unsupported; `--progress` was the compatible fallback. Only after source/destination hashes matched, the service was inactive, and no CUDA process remained was the accelerator cleared for provider termination.

## RTX PRO 6000 hybrid lexical-contextual follow-up

A later two-GPU Blackwell rental tested a genuinely lexical-contextual operator in which one lexical address was injected into grouped R and W heads while V remained contextual. The shared gate was active from initialization; the dense core remained $\operatorname{softmax}(RW^\top)V$ and used SDPA/FlashAttention.

Operational lessons:

- Code was committed and pushed first, then the rental cloned/fetched the exact Git commit. Repeated repository `rsync` was rejected; artifact transfer remained appropriate only for metrics/configs/checkpoints.
- The 2.15 GB pinned FineWeb-Edu shard was downloaded directly on the rental with `hf download`, then checked against the known SHA-256, rather than relayed through the laptop.
- On two GPUs, matched single-process arms ran concurrently with one `CUDA_VISIBLE_DEVICES` value each. This preserved batch 16 and the 100,007,936-token budget; DDP would have changed the global batch.
- Vast had no persistent volume, so `supervisor` owned the jobs with automatic restart disabled. A failed local SSH poller did not indicate run failure: direct `supervisorctl`, GPU, and log checks showed both jobs had completed.

Seed-42 RTX PRO results at the last finite evaluation (step 3000):

| Variant | Eval loss | Stable throughput |
|---|---:|---:|
| GQA | 4.664001 | about 94.3k tok/s |
| lexical-contextual W/R/V in all 10 layers | 4.680514 | about 92.4k tok/s |

The hybrid candidate led at every evaluation from steps 250 through 1000 (best delta about -0.0081), crossed behind near step 1250, and ended +0.016513 worse. This pattern forbids selecting the early checkpoint as the claimed result, but it motivates structural diagnosis.

Final per-layer lexical gates supplied that diagnosis: layers 0–3 retained roughly 0.07–0.105, while most upper layers decayed toward zero, with one value slightly negative. The next paid experiments therefore tested hybrid placement only in bottom 4 and bottom 2 layers, reusing the completed GQA control. General rule: use full trajectory plus checkpoint controls to choose bottom-$k$ ablations before paying for extra seeds; do not replicate a full-budget loser merely because it won early.