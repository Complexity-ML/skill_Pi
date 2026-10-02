# Architecture-aware runner pattern

## Minimal module contract

```python
class TrainableBlock(nn.Module):
    def training_control_capabilities(self) -> frozenset[str]:
        return frozenset()

    def training_telemetry(self) -> dict[str, float]:
        return {}
```

Specialized modules declare only their own controls:

```python
class LexicalResidual(TrainableBlock):
    def training_control_capabilities(self):
        return frozenset({"lexical_object_gate"})

    def training_telemetry(self):
        return {"object_gate": float(self.output_gate.detach().float().item())}
```

## Collector behavior

The collector scans the built model tree, calls only the explicit contract methods, unions capability names, and averages same-named scalar values across layers. It must not infer behavior from class names, YAML labels, or generic CLI defaults.

## Trainer behavior

- Apply a top-K curriculum only if `topk_primary_weight` is declared.
- Apply shared/routed gates only if `shared_routed_gates` is declared.
- Add diversity loss only if `expert_diversity` is declared.
- Populate the progress bar from the current generic telemetry snapshot.
- Refresh learned scalar telemetry at each logging interval.

## Required smoke assertions

Lexical residual:

- contains `object_gate` and, when applicable, `micro_gate`;
- excludes `topk_w`, `shared_gate`, and `routed_gate`.

Token-routed:

- contains `topk_w` and applicable shared/routed gates;
- excludes lexical object/micro gates.

Dense:

- contains no expert or lexical control fields.

## Logging hygiene

If a third-party library emits the same warning through its handler and the root logger, configure its level and propagation deliberately. Hide recoverable retry chatter only when exhausted retries still surface as a real exception.

## Scope language

Say “all model types supported by the migrated runner” only after smoke-testing each family. Do not say “all framework runs” unless every independent runner has been audited.
