# Router-ablation input isolation

Use this when one trainer supports lexical, learned, and dense routing variants.

## Suspicious symptom

A learned-router log reports construction of corpus/Zipf frequency tables before model initialization. Do not immediately claim mathematical contamination: first trace the tensor to its consumer. However, an unused lexical input in a learned control is still an ambiguous manifest and a future leakage risk.

## Audit path

1. Locate where token/corpus frequencies are computed from streaming data or a local shard.
2. Trace assignment into the model config.
3. Trace config conversion into the per-layer MLP config.
4. Inspect each implementation:
   - learned hidden-state router should select experts only from router logits over hidden states;
   - dense control should have no routing inputs;
   - lexical router may consume token IDs and, only for explicitly frequency-aware strategies, corpus counts.
5. Check auxiliary objectives separately: learned load-balancing loss and loss-free selection bias must derive from learned-router probabilities/assignments, not lexical frequency tables.

## Safe gating pattern

Centralize a predicate equivalent to:

- lexical MLP type **and** frequency-aware routing strategy → compute/attach counts;
- learned router, dense MLP, random lexical routing, or frequency-independent modulo routing → do not compute or attach counts.

Keep the allowed MLP aliases and strategies explicit. Avoid a broad condition such as `dataset == tokens`, which leaks preprocessing into every architecture.

## Tests

Add both sides of the contract:

- positive: frequency-aware lexical strategies receive corpus counts;
- negative: learned router and dense control do not;
- negative: random/frequency-independent lexical controls do not unless their declared mechanism says otherwise.

Also verify that the learned router ignores token IDs and that its top-k choices originate from hidden-state router logits.

## Exact counting at billion-token scale

Do not accumulate corpus counts in float32. Above `2**24 = 16,777,216`, adding one is no longer guaranteed to change a float32 value; common tokens can therefore saturate silently while rare-token counts remain apparently reasonable. This can alter greedy load-balanced routing tables.

Safe pattern:

1. count each token chunk with integer `bincount`/`int64` accumulation;
2. assert integer dtype in tests;
3. verify `sum(counts)` equals the indexed source-token count (or the explicitly selected training range);
4. report the maximum token count so precision risk is visible;
5. convert to float64 only for CPU ranking/load calculations;
6. record the count source range and shard checksum in the run manifest.

A mismatched total is a fail-closed condition for frequency-aware lexical controls. Stop before training, fix the counter, rebuild the lookup, and relaunch the affected lexical variants from step zero. It does not invalidate completed learned/dense variants if code tracing and manifests prove those variants neither computed nor consumed the counts.

## Reporting language

For a legitimate lexical control, say “corpus-derived routing frequencies from the fixed shard” and record shard checksum/source revision. Do not call measured counts “hardcoded Zipf.” For learned controls, the resolved config and launch log should contain no lexical-frequency preparation line.

## Architecture-summary audit

Shared CLIs often carry fields that are valid for only some architectures. A dense run can therefore log `shared_intermediate`, router mode, top-k, expert count, or gate values even though its concrete MLP is a plain SwiGLU and ignores every one of them.

Before stopping a paid run for an apparent architecture mismatch:

1. verify the resolved architecture selector (for example `mlp_type`);
2. inspect the registry target/concrete module class;
3. inspect named parameters for shared/router/expert prefixes;
4. reconcile the parameter count against the matched-budget expectation;
5. determine whether suspicious fields are consumed or merely inherited CLI defaults.

If the graph is correct but the summary is misleading, let the valid run continue and patch only the logger. Dense summaries should print dense width and omit routed/shared fields; routed summaries should print only mechanisms they instantiate.

## Telemetry semantics

Missing telemetry must not masquerade as failure. If a fixed lexical path does not collect expert shares, do not emit `NaN` shares plus a derived “all experts dead” count without an explicit `telemetry_collected=false` marker. Prefer `not_collected`/blank values. Analysis code must gate dead-expert conclusions on telemetry availability.

## Paid-run response

If discovered after launch:

1. stop the run if reviewer-facing ambiguity matters;
2. establish whether the tensor affected the forward/loss;
3. patch and test the gating predicate;
4. remove only partial artifacts for the affected run prefix;
5. relaunch from step zero under a clean service/log;
6. verify absence of frequency-related log entries before allowing the run to continue.
