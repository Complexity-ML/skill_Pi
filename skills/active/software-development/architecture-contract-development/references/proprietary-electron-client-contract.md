# Proprietary Electron client contract

Use this reference when a user wants a closed desktop AI client rather than a web app or reusable SDK.

## Product boundary

- Classify the artifact before scaffolding: Electron app, VS Code extension, CLI, or SDK.
- If the user pivots, remove the abandoned scaffold so the repository exposes one product surface.
- Keep model serving behind a private Complexity endpoint; do not expose vLLM/SGLang selection in the client.
- A proprietary app can use `license: "UNLICENSED"`, but bundled Electron/dependency notices still apply.
- Do not fork MIT code when the user wants an original implementation without upstream attribution; reproduce ideas, not source.

## Minimal Electron shape

- Main process owns networking, encrypted settings, and cancellation.
- Preload exposes a narrow IPC API.
- Renderer runs with `contextIsolation`, sandboxing, no Node integration, and a restrictive CSP.
- Stream OpenAI-compatible SSE from `/v1/chat/completions`; test request construction and partial-chunk parsing before UI integration.
- Encrypt API keys with `safeStorage` when available; never place secrets in renderer storage.

## Verification gate

1. Run behavioral tests and syntax checks.
2. Run `npm audit`; update Electron when advisories affect the pinned version.
3. Launch the actual Electron renderer.
4. If native capture permission is unavailable, preview the same renderer through a temporary local static server, inspect it visually, then stop the server. This is verification only, not a web product.
5. Inspect for clipping/overlap and preserve existing prompt suggestions/content during redesign.
6. Build the `.app`/DMG, verify architecture, size, and SHA-256.
7. State clearly whether signing/notarization was performed.

## Reference-driven visual redesign

For a cyberpunk-style request, use an original command/inspect composition: dark technical surfaces, angular geometry, sparse yellow/cyan accents, condensed display type, mono status labels, and restrained scanlines. Do not copy proprietary game logos, assets, exact layouts, or branded terminology. Preserve readability and run a slop audit before packaging.
