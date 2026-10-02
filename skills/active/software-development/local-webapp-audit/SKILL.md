---
name: local-webapp-audit
description: 'Audit and improve a local web application repository: code health, build safety, browser QA, and verification.'
metadata:
  hermes:
    tags:
    - web
    - qa
    - nextjs
    - lint
    - build
    - audit
    related_skills:
    - dogfood
    - systematic-debugging
  hermes_frontmatter:
    version: 1.0.0
    platforms:
    - linux
    - macos
    - windows
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Local Web App Audit

Use this skill when the user points to a local website/app repository and asks to read it, audit it, improve what is wrong, or test it locally. This complements browser-only dogfooding: start with repository health, then run the site and verify changes in the browser.

## Workflow

1. **Enter the project intentionally**
   - Use a project/workdir rooted at the provided repo path.
   - Inspect `package.json`, README, framework config, and app entry points before changing files.

2. **Run a code-health preflight**
   - Install dependencies only if they are missing (`npm install`, `pnpm install`, etc.); do not record missing `node_modules` as a durable project flaw.
   - Run the app's available lint/typecheck/build scripts.
   - Fix high-signal failures before subjective UX polish.
   - Re-run the same commands after fixes.

3. **Check build-script safety**
   - Watch for ordinary build scripts that mutate infrastructure or data, e.g. `prisma db push --accept-data-loss && next build`.
   - Prefer safe build scripts such as `prisma generate && next build`.
   - Move DB mutation/migration to a separate explicit script such as `db:push` or `db:migrate`, so CI/deploy builds do not unexpectedly alter schema/data.

4. **Fix common Next/React lint failures**
   - JSX text beginning with `//` can trigger `react/jsx-no-comment-textnodes`; wrap as `{ "// LABEL" }` or split text safely.
   - React purity rules can reject impure calls like `Math.random()` during render. Replace with deterministic helpers, memoized data from stable inputs, or state/effect-driven generation.
   - Remove unused imports/parameters rather than suppressing warnings.
   - For local/public static images in Next, prefer `next/image` with real width/height and `sizes` to avoid LCP/layout-shift warnings.

5. **Handle security audit pragmatically**
   - Run non-breaking audit fixes when practical, then re-run lint/build.
   - Do not run `npm audit fix --force` silently; it may downgrade or introduce breaking major changes. Report remaining vulnerabilities and the breaking-change trade-off.

6. **Browser QA after build health**
   - Start the dev server as a tracked background process.
   - Verify key routes with HTTP status checks.
   - Open representative pages in the browser, check console errors, and visually inspect layout/CTA/navigation.
   - For demo/API flows, distinguish local UI readiness from external endpoint availability.
   - For visual node/block editors or Electron graph workspaces, use `references/node-graph-electron-editor-qa.md`: lock node-vs-edge semantics, stable parallel execution levels, fixed card geometry across studios, pointer/collision behavior, native-runtime boundaries, macOS titlebar spacing, and real CDP verification.

7. **Polish for attraction + resilience**
   - For technical AI/research landing pages, improve trust and comprehension before adding heavy effects: clear primary CTA, proof metrics near the hero, a compact trust/signal bar, and more explanatory section headings.
   - When claims are tied to a new paper/PDF/OpenReview page, extract the source first and build a claims map before editing; remove concepts the user says were deleted everywhere, including metadata, dashboards, citations, and decorative copy.
   - Keep decorative equations/tickers out of the hero title/CTA/metric area; put them in a bounded band/card and verify visually with `browser_vision` before pushing.
   - If the user says the site is broadly wrong or asks to “tout reprendre / refonte / en composants”, stop doing micro-copy patches. Rebuild the landing page around a small set of reusable sections (hero, claims/evidence, projects, benchmarks), delete redundant old sections, and make the current paper/source-of-truth the organizing structure.
   - For research/technical landing pages, prefer a bounded explainer card or two-column hero over a huge centered hero when there are several claims/metrics. Put metrics and decorative equations inside that card so they cannot overlap title/CTA text.
   - In browser QA, inspect at the initial viewport and after scrolling. A fixed/sticky nav can cover content mid-scroll; verify the section transition and not just the first screenshot.
   - Make demos defensive: parse query params against an allowed mode list and fall back safely instead of passing invalid modes into hooks/API config.
   - Add app-level `loading.tsx` and `error.tsx` so route transitions and recoverable runtime errors stay branded instead of blank.
   - Respect `prefers-reduced-motion` for decorative tickers/3D/background motion.
   - When refactoring demo/chat UIs, preserve existing prompt/example sets unless the user explicitly asks to prune them. Check git history before assuming the current config is complete; compare prompt counts/groups before and after.
   - Render chat prose as prose by default. Do not heuristically detect code from keywords like `for`, `if`, `class`, or `import`; only render syntax-highlighted code for explicit fenced Markdown blocks.
   - Long model outputs need readable typography: paragraph spacing, comfortable line-height, list rendering, and sentence chunking for single-paragraph walls of text. Verify with an actual generated/fixture message, not just the empty welcome screen.
   - If the user says a UI is “n’importe quoi”, “moche”, “cassé”, or says content disappeared, treat that as a first-class QA failure: inspect visually, compare against history, and fix the specific complaint before broadening scope.
   - Preserve existing user-facing examples/content during UI refactors. Before pruning prompt chips, demo examples, cards, or copy libraries, compare against git history and report what would be removed; default to restoring rather than simplifying away content.
   - If the user says they do not trust you to touch a codebase, switch to audit-only mode: read/inspect and propose exact changes, but do not edit files until explicitly authorized.
   - See `references/next-ai-landing-polish.md` for a compact implementation checklist, and `references/research-landing-page-refactor.md` for source-of-truth/content-refactor QA.
   - Render assistant prose as prose. Do not heuristically classify text as code from keywords; only fenced Markdown code blocks should get code styling/highlighting. Long single-paragraph model outputs should be visually chunked for readability.
   - Chat/demo shells should use a fixed viewport layout (`h-screen overflow-hidden`) with one internal scroll region; avoid sticky headers inside nested scroll containers because they can overlap content after scroll restore.
   - See `references/next-ai-landing-polish.md` for a compact implementation checklist, `references/research-landing-page-refactor.md` for source-of-truth/content-refactor QA, and `references/chat-demo-refactor.md` for chat/demo component pitfalls.
   - For interactive chat/demo pages, align model labels and caveats with the current paper/source of truth, then polish the product surfaces: welcome/empty state, message bubbles, composer, compare view, sidebar, header, params/monitor panels. See `references/chat-demo-component-refactor.md`.
   - See `references/next-ai-landing-polish.md` for a compact implementation checklist, and `references/research-landing-page-refactor.md` for source-of-truth/content-refactor QA.

8. **Final report**
   - Summarize concrete files changed and commands verified.
   - Include remaining risks or decisions for the user, especially breaking dependency upgrades, auth/env setup, or external API testing.

## Pitfalls

- Do not stop at a visual pass if lint/build are broken.
- Do not treat transient setup failures (`command not found` before dependency install, missing env vars in a fresh repo) as durable facts; capture the fix or the safe workflow instead.
- Do not couple production builds to destructive DB operations.
- Avoid promising end-to-end backend success if only the frontend loaded and external services were not exercised.
- Do not push broad visual refactors after the user flags a concrete layout problem; first fix and visually verify the exact complaint (overlap, CTA hierarchy, missing/deleted concept).
- User frustration about legibility or organization (`tout est cassé`, `les équations sont écrasées`, `les boutons c'est mal organisé`) is a workflow signal: stop explaining/defending, make a concrete visual fix, run browser QA, and only then summarize.
- In app-style pages with sidebars/composers, sticky headers inside nested flex layouts can drift when the document itself scrolls. Prefer a fixed-height shell (`h-screen overflow-hidden`) with a shrink-0 header and an internally scrolling main region.
