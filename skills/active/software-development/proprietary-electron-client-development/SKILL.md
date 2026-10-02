---
name: proprietary-electron-client-development
description: Build and iterate private, standalone Electron AI clients distributed as macOS apps/DMGs rather than web deployments or generic SDKs. Covers product-boundary clarification, secure Electron architecture, streaming chat UX, proprietary packaging, visual QA, icon pipelines, and artifact verification.
metadata:
  hermes:
    tags:
    - electron
    - desktop
    - macos
    - dmg
    - proprietary
    - ai-client
    - product-development
    related_skills:
    - test-driven-development
    - claude-design
    - popular-web-designs
  hermes_frontmatter:
    version: 1.0.1
    platforms:
    - macos
    - linux
    - windows
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

# Proprietary Electron Client Development

Use this skill when the requested deliverable is a closed/private desktop AI client built with npm/Electron, especially when the user wants a macOS `.dmg` rather than a website, browser app, generic SDK, or editor extension.

## Start by locking the product boundary

Before scaffolding, distinguish these materially different deliverables:

1. **Standalone Electron app** — a desktop product installed from a DMG. This is the default when the user says “client,” “app,” “DMG,” or rejects a web target.
2. **VS Code extension** — UI and agent capabilities hosted inside VS Code.
3. **npm SDK** — a library consumed by developers, not an end-user client.
4. **Web application** — requires hosting/deployment and is not implied by Electron’s use of HTML/CSS.

Do not silently reinterpret “npm client” as “SDK.” Ask once only when the distinction is genuinely unresolved; otherwise prefer the concrete end-user artifact the user emphasized. If the user corrects the boundary, stop the previous direction immediately and remove or isolate abandoned scaffolding before continuing.

For this user, default to a **standalone proprietary Electron/macOS client and DMG** when discussing a Complexity AI client. Do not propose a web deployment unless explicitly requested. A temporary local HTTP server may be used for renderer QA, but it is not part of the shipped product and must be stopped afterward.

## Architecture contract

Use a narrow, secure desktop boundary:

```text
Electron renderer
  -> context-isolated preload API
  -> Electron main process
  -> private hosted AI endpoint
  -> proprietary orchestration/model serving
```

Required defaults:

- `contextIsolation: true`
- `nodeIntegration: false`
- `sandbox: true`
- strict Content Security Policy
- renderer never receives filesystem, process, or arbitrary IPC access
- request execution in the main process
- narrow preload methods with explicit payloads
- secrets stored through `safeStorage` when available
- proprietary model logic, prompts, routing, and serving details remain server-side

If the server is OpenAI-compatible internally, expose it as a Complexity endpoint rather than surfacing vLLM/SGLang selectors in the UI. Backend serving choices should remain replaceable implementation details.

## Minimal useful AI-client surface

A credible first desktop client should include:

- endpoint/model connection settings
- optional API key handling
- streaming chat
- cancellation
- empty, loading, error, and completed states
- clear conversation reset
- readable model/connection status
- keyboard send affordance
- preserved user-visible examples unless removal is requested

Avoid turning the first version into a generic agent SDK, universal provider abstraction, or sprawling plugin framework.

## TDD and verification sequence

1. Write tests around pure modules first: settings normalization, request construction, stream parsing, error mapping.
2. Confirm RED before implementation.
3. Implement the smallest main-process service that passes.
4. Run syntax/static checks on main, preload, and renderer files.
5. Run `npm audit`; upgrade the direct vulnerable dependency rather than accepting a known Electron advisory.
6. Launch the real Electron process and confirm main + renderer processes remain alive. Rebuild and fully restart Electron after preload, IPC, `BrowserWindow`, titlebar, sandbox, or other main-process changes; renderer HMR is not verification for those layers.
7. Inspect the renderer visually. Verify native macOS chrome separately from page content: a CDP/page screenshot excludes traffic lights. With `hiddenInset`, reserve an Electron-only left titlebar region, keep controls `no-drag`, and style native scrollbars for the dark UI. If HMR-preserved state contradicts tests or served source, reload or use a fresh temporary `user-data-dir` before diagnosing another bug. See `references/macos-native-window-qa.md`.
8. If native capture permissions block screenshots, host only the renderer directory on a temporary localhost server for page-level QA, inspect it, and then terminate that server. Do not describe this as a web product.
9. Build the unpacked app, then the DMG.
10. Verify the executable architecture, artifact size, checksum, and that the expected icon is embedded.

Never claim the app is distributable without warnings when code signing/notarization was skipped. Distinguish a functional local DMG from a production-signed public release.

## Visual direction and iteration

Treat a desktop AI client as a **Command / Inspect** surface, not a marketing landing page. The conversation, connection state, model identity, and composer must dominate.

For this user’s Complexity clients:

- favor readable cyberpunk HUD styling rather than generic purple SaaS gradients
- use dark surfaces, restrained cyan/yellow accents, technical status labels, angular geometry, and disciplined scanline/grid texture
- preserve legibility at normal laptop sizes
- avoid copying protected game logos, exact branded UI, or proprietary assets in a public build
- perform a visual pass for clipping, overlaps, tiny labels, and wrong surface composition before rebuilding

When the user supplies a visual correction, implement and re-inspect it rather than defending the previous design.

## Proprietary source versus third-party licenses

A private package may use:

```json
{
  "private": true,
  "license": "UNLICENSED"
}
```

and carry an internal proprietary notice. This does not erase third-party obligations. Electron and build dependencies retain their own license notices. A fork of MIT code remains subject to MIT attribution even after simplification; avoiding that obligation requires an original implementation with no copied code.

Never suggest obfuscation as a substitute for keeping sensitive logic server-side.

## Icon and DMG pipeline

Use a square 1024px source with a silhouette that survives 128px and 32px. Generate a complete `.iconset`, compile it with `iconutil`, configure `build.mac.icon`, rebuild, then compare the source ICNS hash with the ICNS inside the packaged `.app` to rule out stale-cache/default-icon mistakes.

Keep prior icon sources when exploring identity changes so the user can revert. Third-party franchise artwork may be used only when the user explicitly scopes it to a local/private prototype; do not treat that as cleared for public or commercial distribution.

See `references/macos-icon-and-dmg.md` for a concise icon/build/verification recipe.

## Stop conditions

The task is complete only when:

- tests pass
- syntax checks pass
- security audit is clean or any remaining exception is explicitly justified
- the application has actually launched
- the primary renderer viewport has been visually inspected
- the DMG exists and its architecture/checksum are verified
- signing/notarization status is stated accurately

Do not commit, publish, sign, notarize, or distribute unless the user explicitly requests it.

## Pitfalls

- Building an SDK after the user asked for a client application.
- Calling an Electron renderer a “web app” and confusing implementation technology with product delivery.
- Leaving temporary preview servers running.
- Using the default Electron icon in a supposedly polished DMG.
- Rebuilding without checking the icon actually embedded in `Contents/Resources`.
- Storing an API key in plain JSON when `safeStorage` is available.
- Exposing raw vLLM/SGLang choices in the product UI.
- Claiming a local unsigned DMG is ready for public distribution.
- Copying a franchise asset into a commercial build without a separate licensing decision.
- Using `hiddenInset` without reserving renderer space for macOS traffic lights, or making the whole titlebar draggable without restoring `no-drag` on controls.
- Treating a page-only screenshot as proof of native titlebar placement; CDP does not capture traffic lights.
- Trusting an HMR-preserved Electron window after main/preload changes instead of rebuilding and fully restarting with fresh state when needed.
