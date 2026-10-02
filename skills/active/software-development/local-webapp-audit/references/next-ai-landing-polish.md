# Next.js AI/Research Landing Polish Checklist

Session pattern from a Next 16 + React 19 technical research site. Use when the user asks to make a local website more robust, pleasant, or attractive after the basic build/lint issues are solved.

## High-impact visual improvements

- Make the hero answer three questions immediately: what it is, why it matters, and what to click next.
- Promote one primary CTA (for example, `Try the live demo`) and demote secondary links (`GitHub`, `Paper`) to outline/ghost buttons.
- Put proof metrics close to the hero, not buried later: throughput, latency, expert count, model size, etc.
- Add a compact trust/signal strip below the hero with 3–4 cards: measured benchmark, efficient activation, deterministic routing, open inspection.
- Replace generic section headings (`What We're Building`) with stronger product/research framing (`Production-grade research artifacts`) plus a short explanatory paragraph.
- Improve cards with subtle elevation only: border shift, tiny top gradient, hover lift, controlled shadow. Avoid flashy effects that fight the technical tone.

## Robustness improvements that pair well with polish

- Add app-level `src/app/loading.tsx` for branded route loading.
- Add app-level `src/app/error.tsx` with `reset()` and a home link so runtime failures do not produce a blank screen.
- Parse URL query params defensively:

```ts
const MODES: Mode[] = ["TR-MoE", "compare", "dense"];

function parseMode(mode: string | null): Mode {
  return MODES.includes(mode as Mode) ? (mode as Mode) : "TR-MoE";
}
```

- Make all internal links use valid modes. Do not link to unsupported aliases like `?mode=python` or `?mode=chat` unless the parser explicitly supports them.
- For decorative motion/3D/tickers, respect reduced motion:

```ts
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (prefersReducedMotion) return;
```

- Add global focus-visible styling and selection colors in `globals.css` so keyboard users get clear affordances.

## Verification loop

1. Run `npm run lint` and `npm run build` after changes.
2. Start the dev server as a tracked background process.
3. Check key route headers with `curl -I`.
4. Browser-test `/`, the demo route, and at least one malformed demo URL (for example `/demo?mode=python`) to verify graceful fallback.
5. Use browser console inspection plus a visual screenshot pass to catch overlays, unreadable text, or excessive whitespace.

## Pitfalls

- Do not add heavy 3D first. Start with content hierarchy, CTAs, metrics, and resilience; then add 3D if it explains the product.
- Do not trust TypeScript casts for URL state. Casts hide invalid external input.
- Do not let decorative ticker text overlap important CTAs; lower opacity, move it behind content, mask edges, and test while scrolled.
