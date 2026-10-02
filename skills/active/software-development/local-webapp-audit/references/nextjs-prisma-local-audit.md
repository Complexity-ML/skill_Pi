# Next.js + Prisma Local Audit Notes

Use these notes when auditing a local Next.js repository with Prisma and browser-facing pages.

## Preflight commands

- `npm install` only when dependencies are absent or scripts fail because local binaries are missing.
- `npm run lint`
- `npm run build`
- `npm audit fix` for non-breaking dependency fixes, followed by lint/build again.
- `npm audit --omit=dev --audit-level=high` to distinguish remaining high-severity production risk from moderate/dev-only issues.

## Build script safety

Avoid ordinary build scripts that run DB schema pushes or destructive actions:

```json
{
  "scripts": {
    "build": "prisma generate && next build",
    "db:push": "prisma db push --accept-data-loss"
  }
}
```

Rationale: deploy/build should compile the app; migrations/schema pushes should be explicit and environment-aware.

## Common fixes

- JSX text `// LABEL` can be parsed as a comment-like text node by ESLint. Use `{ "// LABEL" }` or otherwise wrap the text expression.
- Replace `Math.random()` in render/memoized render-time calculations with deterministic noise functions or state initialized outside render purity-sensitive paths.
- Replace public static `<img>` with `next/image` when lint warns about LCP/bandwidth; use measured image dimensions and an appropriate `sizes` attribute.
- For hooks, avoid synchronous state writes in effects when the value can be derived for rendering (e.g. expose `isAuthenticated ? conversations : []`).

## Browser verification checklist

- Start dev server as a tracked background process.
- `curl -I` key routes (`/`, `/demo`, feature/marketing pages) for HTTP 200.
- Browser navigate to representative routes.
- Check console after each route and after important interactions.
- Use visual inspection for hero spacing, sticky nav behavior, CTA visibility, large blank regions, and text spacing/accessibility issues.
