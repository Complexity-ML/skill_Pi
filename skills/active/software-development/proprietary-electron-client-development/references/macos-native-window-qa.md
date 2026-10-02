# macOS Native Window and Renderer QA

Use this reference when an Electron renderer looks correct in a browser but breaks around native macOS chrome, scrollbars, or after hot reload.

## Hidden titlebar contract

With `titleBarStyle: 'hiddenInset'`, native traffic lights occupy renderer-adjacent space. The renderer must reserve that space explicitly.

Recommended pattern:

- expose a narrow preload/runtime discriminator such as `window.app.runtime === 'electron'`;
- add a renderer class only in Electron (for example `runtime-electron`);
- reserve roughly 78–84 CSS px at the left of the topbar;
- make the topbar draggable with `-webkit-app-region: drag`;
- mark buttons, navigation, inputs, and other controls `-webkit-app-region: no-drag`;
- optionally set `trafficLightPosition` in `BrowserWindow` so vertical alignment is deliberate;
- do not apply the native-titlebar padding to ordinary browser previews.

A hidden titlebar without renderer padding causes the red/yellow/green controls to cover the app logo. Moving only the traffic lights is insufficient if content still starts underneath them.

## Native scrollbar contract

Electron/Chromium may expose a platform scrollbar that is much brighter or wider than the dark UI, especially when macOS is configured to always show scrollbars. Style every intended scroll container explicitly:

- use a thin width (about 7 px);
- use a dark track matching the panel;
- use a visible but restrained thumb and hover state;
- cover sidebars, inspectors, code editors, and training/tokenizer canvases consistently;
- verify that the scrollbar is inside the intended pane rather than caused by document/body overflow.

Do not hide scrollbars entirely when the pane needs a discoverable scroll affordance.

## Restart discipline

Classify the changed layer before verifying:

- renderer CSS/React usually updates through HMR;
- preload, IPC, `BrowserWindow`, titlebar, sandbox, or main-process changes require rebuilding Electron and fully restarting the Electron process;
- HMR may preserve stale React/player/initial-graph state even after source changes. If behavior contradicts tests or served source, reload the renderer or start Electron with a fresh temporary `user-data-dir` before diagnosing a second bug.

Never treat an old running window as proof of the current main/preload build.

## Verification ladder

1. Run targeted UI tests for the Electron-only renderer class.
2. Build both renderer and Electron TypeScript targets.
3. Restart Electron with a fresh temporary profile.
4. Verify the actual preload bridge/runtime discriminator in the renderer.
5. Inspect computed values through CDP when useful: topbar padding, brand left edge, app-region, scrollbar pseudo-element width, and overflow ownership.
6. Capture and inspect the native window when permissions allow. `Page.captureScreenshot` proves renderer layout but does not include native traffic lights; do not claim native control placement from a page-only capture.
7. If native capture is blocked, report that limitation and combine compiled `BrowserWindow` options with renderer computed-style evidence. Do not substitute an ordinary browser screenshot for native-window proof.

## Regression tests

- Electron runtime adds the Electron-only shell class; browser mode does not.
- Interactive controls inside a draggable titlebar remain clickable.
- Renderer brand/content starts after the reserved traffic-light region.
- Scroll containers use the intended thin dark scrollbar.
- Main-process build accepts the titlebar options.
- A complete process restart is part of visual verification after main/preload edits.
