# Node-Graph Editor and Electron QA

Use this checklist when auditing or changing a visual node/block editor, especially one embedded in Electron.

## Establish semantic contracts before editing

Distinguish graph operations explicitly and encode each as a test:

- **Delete node**: remove the node's generated declaration/code and its incident edges.
- **Delete edge/cable**: keep both node declarations; remove only the corresponding dataflow. If a required port becomes unavailable, omit or fail that execution call at the exact atom rather than replacing the entire generated program with a generic invalid stub.
- **Reconnect the same edge**: generated node/code order must remain stable. Topological sorting must use a deterministic node-order tie-breaker, not edge insertion order.
- **Parallel branches**: derive execution levels from dependencies. Nodes in one level should transition pending/running/passed together; invalid graphs should still report the first broken atom in a stable user-readable order.

Do not infer a new product behavior from a user's analogy. Restate the block-vs-edge contract briefly and test it before implementation.

## Robust card dragging

Prefer Pointer Events over native HTML5 `draggable` for dense or overlapping cards:

1. Start from a dedicated card surface; ports and form controls must stop propagation.
2. Capture the pointer and convert screen coordinates to graph-world coordinates using the current pan/zoom transform.
3. Keep a local preview position during movement; commit semantic graph state only on pointer-up so code generation and runtimes are not rebuilt every pixel.
4. Raise the active card with a temporary `dragging` z-index/class.
5. Recompute cable endpoints from preview layout while dragging.
6. Handle pointer cancel and release capture.
7. Test preview movement, committed position, zoom conversion, canvas panning, and cable dragging together.

Watch for threshold-based display offsets that cause cards to jump when crossing a coordinate. Apply group-expansion offsets only when that group actually exists.

## Stable card geometry and connector integrity

Treat card geometry as an interaction contract, not incidental CSS:

1. **Selection must not resize movable cards.** Expanding an inline editor inside a selected card can overlap neighboring cards, cover their ports, and move cable endpoints. Keep graph cards at stable dimensions and put editable attributes in a persistent inspector/sidebar. If a composite/group has settings, expose those in the same inspector rather than preserving a second inline-editor path.
2. Keep dimensions used by collision logic synchronized with rendered CSS. Prefer exported width/height constants or a single geometry source; remove responsive rules that silently shrink cards without updating collision calculations.
3. Bound long titles and summaries with line clamping or ellipsis. Verify every registry/card variant, not only the default preset.
4. Disable accidental selection and native drag on card surfaces (`user-select: none`, `-webkit-user-drag: none`, `touch-action: none` on drag handles). Re-enable text selection explicitly for inputs and text editors.
5. Ports must remain outside card clipping: use `overflow: visible`, an adequate hit target, and a clear layer above card bodies. A high child `z-index` cannot escape a parent stacking context, so do not rely on z-index alone when selected cards overlap.
6. Prevent persistent overlaps on pointer-up with deterministic collision resolution. Resolve vertically only among cards whose horizontal bounds intersect, preserve movement direction when possible, and calculate an opposite-direction fallback when the preferred slot would place the card above the canvas.
7. Apply the same Pointer Events implementation to special composites and expanded groups. Leaving one legacy HTML5 `draggable` variant creates inconsistent behavior and missed edge cases.

Regression tests should assert:

- selecting a card preserves its dimensions and cable path;
- settings remain editable from the inspector and still regenerate code;
- a drop into a dense column resolves to a non-overlapping position;
- upward collision resolution cannot produce a negative/off-canvas position;
- ports remain fully visible and cables terminate at their centers;
- standard cards, composites, expanded groups, tokenizer cards, and training cards all respect the interaction invariants.

For browser/Electron QA, measure every card rectangle and report intersecting pairs programmatically, then inspect the same state visually. Exercise a real pointer drop directly onto an occupied card and reload the renderer afterward. Do not claim full validation after a final code change until the complete canonical test/lint/build sequence has been rerun.

## Electron runtime boundary

The Vite browser renderer and Electron renderer may show the same UI at the same URL, but only Electron has the preload bridge:

- Probe the actual Electron page through CDP and assert the runtime marker, the function type of the IPC method, and a minimal real invocation.
- Do not diagnose an IPC/preload failure from an error produced in a normal browser tab where the bridge is absent by design.
- Disable native-only execution controls in browser mode and label them clearly (for example, `desktop only`) instead of letting a click fail with a generic “runtime unavailable” message.
- After validating the bridge, exercise one real atom through the UI and wait for a concrete player state (`paused`, `completed`, or `failed`). Distinguish “IPC exists” from “the real runtime executed.”
- Check for duplicate/stale Electron instances when observed UI state disagrees with the CDP probe, and restart the main process after preload changes because renderer HMR cannot reload the bridge.

## Cross-studio card parity

When one studio establishes hardened card behavior, apply the same interaction class to sibling studios rather than leaving a visually similar but structurally weaker list:

- Tokenizer cards should use stable geometry, Pointer Events, collision handling, Inspector settings, and typed ports/cables just like Model cards.
- Persist visual positions separately from semantic order. Tokenizer compilation/execution order must come from typed links/topology, never card coordinates or incidental array order.
- Preserve delete-card versus delete-link semantics across studios, and verify that moving cards cannot change generated Python/Rust/PyTorch.
- Training cards that are intentionally singular/non-movable may keep inline controls, but still need bounded content, selectable form fields only, visible focus, and overflow checks.

## Electron/macOS chrome

With `titleBarStyle: hiddenInset`:

- Add an Electron-only renderer class; do not shift the browser version.
- Reserve roughly 80–90 CSS px at the left of the titlebar for macOS traffic lights.
- Mark the titlebar as `-webkit-app-region: drag` and interactive controls as `no-drag`.
- Optionally set `trafficLightPosition` in `BrowserWindow` for deterministic vertical alignment.
- Style WebKit scrollbars explicitly; an unstyled native scrollbar can appear as a thick bright divider.
- Restart the Electron main process after BrowserWindow/preload changes; HMR is insufficient.

## Verification

- Unit/integration tests: node deletion, cable deletion, reconnect stability, parallel levels, direct pointer drag.
- Real renderer: invoke Electron through CDP and inspect `window.labo`, computed padding/drag region/scrollbar width, and runtime status.
- Use `Page.captureScreenshot` for renderer visual QA. Native traffic lights are outside the renderer screenshot; if native capture permissions are unavailable, verify the BrowserWindow option plus computed reserved space and state that limitation precisely.
- Exercise real pointer movement with CDP `Input.dispatchMouseEvent`, then read position/class before, during, and after release.
- Reload the test renderer afterward so the user is not left with QA-induced layout state.
