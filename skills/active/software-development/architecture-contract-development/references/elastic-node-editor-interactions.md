# Elastic 2D Node Editor Interaction Contract

Use this reference when building a block/graph research IDE with draggable semantic atoms.

## Camera and coordinate system

- Treat pan/zoom as camera state `{x, y, zoom}` separate from graph IR positions.
- Put blocks, ports, grid, and SVG cables inside one transformed world container with `transform-origin: 0 0`.
- Convert screen coordinates to world coordinates for drop and cable-drag operations: `(screen - pan) / zoom`.
- Zoom around the pointer, preserving the world point under it.
- Support trackpad X/Y pan, Ctrl/Cmd-wheel pinch zoom, background drag, middle-button drag, Space+drag, zoom buttons, reset, and Fit Graph.
- A fixed-size SVG overlay is invalid once the world can exceed that size; use the same large world dimensions as the block layer.

## Elastic cable behavior

An “elastic” connection must follow the live DOM geometry, not only IR changes.

Recompute cable endpoints when:

- graph positions or edges change;
- camera pan/zoom changes;
- selection changes card width or height;
- inline settings expand/collapse;
- a composite expands/collapses;
- ports or cards resize (`ResizeObserver`);
- the window resizes.

Calculate endpoints from port centers in screen space, then invert the camera transform into world space before generating SVG paths.

## Ports and composites

- Port circles centered on card boundaries require `overflow: visible`; otherwise half the plug is clipped.
- Keep controls, ports, and settings interactive while making the card header/body draggable.
- Store composite position in the group IR. Moving a composite must not mutate its child atom positions.
- Expanded and collapsed representations must share the same group position.
- When several internal edges map to the same visible ports on a collapsed composite, render one bundled cable. Split it into individual cables only when expanded.

## Semantic surface

Expose semantic blocks such as Router, Top-K Routing, Routed Expert Bank, Shared Expert Bank, Expert Merge, and Load-Balancing Loss. Keep dispatch/gather/scatter/all-to-all and kernel plumbing internal to lowerings/runtime.

## Verification

Automate tests for:

1. pointer-centered zoom invariance;
2. independent X/Y pan and zoom clamping;
3. screen-to-world drop coordinates;
4. cable endpoint recalculation after selection resize;
5. fully visible port circles;
6. bundled collapsed links versus expanded child links;
7. draggable composite position without child-position mutation.

Then inspect the rendered canvas at multiple zoom levels and verify every cable terminates at the center of its visible port.