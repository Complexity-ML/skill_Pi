# Chat/demo component refactor QA

Use this when a local web app has an interactive chat/demo page that feels like an internal prototype rather than a polished product.

## Durable lessons

- Prefer a thin route page plus a `DemoShell`/workspace component over putting mode switching, conversations, scroll, compare mode, input refs, and rendering all in `page.tsx`.
- Keep hooks (`useChat`, `useCompare`, `useConversations`) stable while refactoring visible components; this lowers risk and lets visual work ship independently from networking changes.
- Align demo copy with the current source of truth. If the landing page was updated from a new paper, also update chat config, welcome screens, model labels, mode descriptions, disclaimers, and footers. Do not leave old parameter counts or deleted concepts in the demo UI.
- For chat apps, refactor by product surfaces: header/model switcher, sidebar, welcome/empty state, message bubble, composer, compare panel, params/monitor panels.
- Message bubbles should support copy, model/user labels, loading/error states, and code/text rendering. A raw `whitespace-pre-wrap` paragraph is acceptable for a prototype but weak for a public demo.
- Composer polish matters: use a contained card, clear placeholder per mode, visible send/stop affordance, and keyboard hint (`Enter` send, `Shift+Enter` newline).
- Compare mode should be visually framed as qualitative inspection unless it is actually a benchmark. Use side-by-side cards with token/latency badges and a caveat header.
- For full-height app shells, avoid mixing document scroll with sticky headers inside nested flex layouts. Use `h-screen overflow-hidden` on the shell, a non-sticky/shrink-0 header, and put scrolling only on the main timeline. Browser QA should verify `document.body.scrollHeight === innerHeight` or otherwise check that the header does not drift/overlay content.

## Verification checklist

1. Run lint and build.
2. Start the dev server and check the chat route plus each query-param mode (`/demo`, `/demo?mode=compare`, invalid mode if supported).
3. Use browser console for JS errors.
4. Use visual inspection, not snapshots only: verify header position, sidebar, welcome card, composer, prompt chips, compare cards, and mobile/small-viewport overlap.
5. If a header/composer overlaps content, fix shell layout before pushing more styling changes.
