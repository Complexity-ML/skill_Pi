---
name: proprietary-desktop-ai-clients
description: Build proprietary desktop AI clients distributed as native installers, with secure hosted-model boundaries, streaming chat, packaging, visual identity, and release verification. Use when requests mention a closed/private AI client, Electron app, npm-distributed desktop client, macOS DMG, or a branded assistant UI.
metadata:
  hermes_frontmatter:
    version: 1.0.0
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
  copyright: Copyright (c) 2026 Complexity-ML
  ownership: Owner-confirmed original skill, generated with GPT in Hermes for Complexity-ML
license: MIT
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Proprietary Desktop AI Clients

Build a real installable desktop product, not a generic SDK or web deployment, when the user asks for a private AI client.

## Product interpretation

Distinguish these deliverables before implementation:

1. **Desktop application** — standalone `.app`/`.dmg` or platform installer; default for this user.
2. **Editor extension** — VS Code sidebar/command integration.
3. **Library SDK** — imported by other applications.

When the user says “npm client” in the context of an end-user AI product, do not assume they want an npm library. npm may only be the Electron build toolchain. Prefer a standalone Electron/macOS application unless they explicitly request an SDK.

For this user, a DMG-only client is the preferred product shape. Do not introduce a web frontend or hosted web application unless explicitly requested. A temporary local HTTP preview is only a verification mechanism and must be described as such, then stopped.

## Architecture contract

Use this boundary:

```text
Desktop client
    ↓ HTTPS/SSE
Private proprietary API
    ↓
Agent/model orchestration
    ↓
vLLM or SGLang
    ↓
Private model
```

Keep proprietary logic server-side. The desktop client may contain:

- connection settings;
- authenticated requests;
- streaming event parsing;
- conversation UX;
- cancellation;
- local preferences;
- release metadata.

Do not embed:

- provider or serving credentials;
- internal cluster URLs;
- proprietary routing logic;
- model-selection policy;
- sensitive prompts or skills;
- administrator keys.

Do not expose vLLM/SGLang selection in the end-user interface when the private API owns that boundary.

## Electron security baseline

- Enable `contextIsolation`.
- Disable `nodeIntegration` in renderers.
- Enable the renderer sandbox.
- Use a narrow preload bridge with explicit methods.
- Execute authenticated network requests in the main process.
- Use a restrictive Content Security Policy.
- Encrypt stored API keys with `safeStorage` when available.
- Never type, log, screenshot, or commit real credentials.
- Run `npm audit` and upgrade the direct vulnerable package rather than accepting a known issue.

## Implementation workflow

1. Inspect the existing application files and package manifest.
2. State the product surface: usually **Command / Inspect** for an AI desktop client.
3. Write tests first for non-visual contracts:
   - settings normalization;
   - request construction;
   - SSE parsing and incomplete-frame buffering;
   - cancellation/error events.
4. Implement main-process networking and preload IPC.
5. Build the renderer without unnecessary runtime dependencies.
6. Preserve existing user-facing content and examples unless removal is requested.
7. Launch the real Electron application.
8. If native capture permissions block visual inspection, preview the same renderer through a temporary localhost static server, inspect it in Chromium, and stop the server afterward. Never reframe this preview as a web product.
9. Run tests, syntax/type checks, audit, installer build, architecture inspection, and checksum verification.

## Streaming SSE requirements

A correct parser must:

- normalize CRLF to LF;
- split only complete blank-line-delimited events;
- preserve an incomplete trailing fragment for the next chunk;
- support `data: [DONE]`;
- emit text deltas without losing UTF-8 boundaries;
- surface non-2xx response bodies as errors;
- support cancellation via `AbortController`.

## Visual direction

For this user's proprietary clients, favor readable cyberpunk command-console styling rather than generic SaaS styling:

- near-black technical surfaces;
- restrained cyan and acid-yellow accents;
- angular panel geometry;
- compact monospaced system labels;
- clear state indicators;
- dense but readable hierarchy;
- motion only for real state transitions;
- `prefers-reduced-motion` support.

Do not clone proprietary game screens, logos, characters, or assets. Extract broad principles and produce an original identity.

Run a visual self-audit before shipping:

- no clipping or overlap;
- readable at the primary desktop viewport;
- composer labels remain inside clipped panels;
- no generic violet-gradient SaaS look;
- no decorative fake metrics;
- no centered marketing hero when the surface should be Command / Inspect.

## App icons and intellectual property

For commercial clients, do not download and embed copyrighted characters, franchise art, fan art, or search-result images without an appropriate license. A reference such as Gundam may guide broad qualities—mechanical face, V-shaped crown, strong silhouette—but the delivered character must be original.

Icon requirements:

- recognizable at 32–128 px;
- tight head-and-shoulders crop;
- bold symmetric silhouette;
- limited palette aligned with the application;
- generous safe margins;
- no text;
- no fragile micro-detail.

When image generation is unavailable, create an original vector-style icon locally, render a high-resolution PNG, inspect it at full size and at 128 px, generate the complete `.iconset`, convert with `iconutil`, and verify the packaged `.app` contains the same ICNS checksum.

## Packaging and verification

For macOS Electron builds:

1. Build an arm64 `.app` and `.dmg` when targeting Apple Silicon.
2. Configure a custom `.icns` before packaging.
3. Verify the executable with `file`.
4. Confirm the icon exists under `Contents/Resources`.
5. Compare the source and packaged icon checksums.
6. Calculate and report the DMG SHA-256.
7. State explicitly whether the build is unsigned/unnotarized.
8. Do not claim public-release readiness without Developer ID signing and Apple notarization.

## Proprietary licensing boundary

A proprietary application can use `license: "UNLICENSED"` and an all-rights-reserved notice for its original code. Third-party dependencies such as Electron retain their own licenses and required notices. “Proprietary” does not erase third-party license obligations.

Forking MIT code still requires preserving the MIT notice. If the user wants no Hermes-derived license obligation, do not fork or copy Hermes code; perform an independent implementation based only on general product concepts.

## Session reference

See `references/complexity-electron-mvp.md` for a concrete implementation and verification pattern from a completed Electron/DMG build.
