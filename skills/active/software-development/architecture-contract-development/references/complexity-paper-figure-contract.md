# Complexity paper architecture-figure contract

Use this note when correcting Complexity-ML paper diagrams or manuscript architecture descriptions.

## Contract learned from session

- Remove obsolete architecture concepts everywhere, not only in prose. If the user says "virer tout Mu", search manuscript sources, translated variants, figure assets, captions, and visible generated artifacts for `Mu`, `mu`, `MU`, `mu_init`, and guidance wording.
- For the TMLR Complexity-Deep paper, the current story is the 300M shared+routed architecture: shared dense backbone plus Zipf-routed lexical residual. Do not reintroduce Mu-Guidance or frame routed as replacing dense MLP computation.
- The architecture figure is a user-facing claim. A generated PNG that compiles or writes successfully is still a failure if text/arrows overlap, residual paths are unclear, or the 300M configuration is not visually represented.
- If the existing diagram came from an external app/exported PNG, do not silently replace the workflow with a TeX/TikZ source file. Regenerate or edit the requested PNG, and only introduce a new canonical source after explicit user agreement.

## Verification checklist

1. Search for stale terms in the relevant paper tree: `Mu`, `mu`, `MU`, `mu_init`, `guidance`, translated equivalents when applicable.
2. Inspect the actual PNG visually before claiming completion.
3. Confirm the diagram shows: 18 decoder layers, `d_model=1024`, GQA 16/4, RMSNorm/QK-Norm/RoPE, shared dense SwiGLU (`d_ff=3840`), 4 routed experts with top-k=2 and routed total `d_ff=256`, final RMSNorm, tied LM head, and 306.5M iso-parameter comparison if space permits.
4. Ensure no obsolete Mu-guided attention, Mu-Guidance block, `mu_init`, or inter-layer guidance appears in either the figure or caption/manuscript.
