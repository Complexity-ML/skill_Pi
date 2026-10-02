# Complexity Electron MVP — implementation reference

This reference records a reusable concrete pattern, not a requirement to preserve this exact project state.

## Product correction that shaped the workflow

The initial interpretation of “private npm client” as an importable SDK was wrong. The desired product was a standalone client application built with npm/Electron and delivered as a macOS DMG. For similar requests, distinguish the artifact before writing SDK scaffolding and default to the standalone app for this user.

## Minimal project shape

```text
app/
  main.js
  preload.js
  renderer.js
  index.html
  styles.css
  services/complexity-api.js
test/
  complexity-api.test.js
build/
  icon.icns
package.json
PROPRIETARY.md
```

The renderer used no Node.js integration and communicated through a narrow preload bridge. Main-process `fetch` handled streaming requests and emitted typed renderer events.

## API boundary

The application accepted only:

- private endpoint URL;
- model identifier;
- optional API key.

It called an OpenAI-compatible `/v1/chat/completions` streaming endpoint. It deliberately omitted a vLLM/SGLang selector because serving implementation details belonged behind the private API.

## Useful TDD units

1. Normalize trailing slashes on endpoint URLs.
2. Ensure request bodies contain the selected model, messages, and `stream: true`.
3. Parse multiple complete SSE frames in one chunk.
4. Preserve incomplete trailing SSE data.
5. Recognize `[DONE]`.

Node's built-in `node:test` was sufficient, avoiding an additional runtime test framework.

## Security pattern

- `contextIsolation: true`
- `nodeIntegration: false`
- `sandbox: true`
- restrictive CSP
- settings persisted under Electron `userData`
- API key encrypted with `safeStorage` when encryption was available
- main-process network execution
- cancellation with `AbortController`

## Visual verification workaround

Native screenshot automation may require macOS Accessibility and Screen Recording permissions. A safe fallback is:

1. launch the real Electron app and verify its renderer process exists;
2. temporarily serve the renderer directory on localhost;
3. inspect the same HTML/CSS in browser tooling;
4. repair clipping/overlap issues;
5. stop the preview server;
6. rebuild and relaunch Electron.

This does not make the product a web application. Explain that distinction immediately if the user asks why “web” is involved.

## Cyberpunk redesign lessons

The successful composition treated the client as **Command / Inspect**:

- sidebar as thread navigator;
- top bar as secure-channel status;
- central command area;
- angular composer as directive input;
- cyan for system state and yellow for primary action.

One concrete clipping defect occurred when a composer label was positioned above a `clip-path` boundary. The durable fix was to place the label inside the panel and increase top padding.

## Original mecha icon fallback

When configured image generation was unavailable, an original symmetric mecha/Valkyrie icon was rendered locally with AppKit geometry. The process was:

1. draw at high resolution with large shapes and a limited palette;
2. inspect the full-resolution PNG;
3. downsample to 128×128 and inspect recognizability;
4. generate every macOS iconset size with `sips`;
5. convert the iconset with `iconutil -c icns`;
6. package the app;
7. compare SHA-256 hashes of source and packaged ICNS files.

A Gundam search was useful only as visual research. Official Gundam imagery was not embedded because the target was a commercial proprietary client.

## Release checks used

- full unit test run;
- `node --check` on main, preload, and renderer scripts;
- `npm audit` with zero unresolved vulnerabilities;
- `electron-builder --mac dmg`;
- `file` on the packaged executable to confirm arm64 Mach-O;
- SHA-256 of the final DMG;
- explicit warning that the build was unsigned and unnotarized.
