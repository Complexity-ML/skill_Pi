# Research landing-page refactor and source-of-truth QA

Use this reference when improving or refactoring a local research/project landing page whose claims are tied to a paper, PDF, OpenReview entry, benchmark, or model artifact.

## Source-of-truth sequence
1. Extract/read the current paper/PDF/URL before editing copy.
2. Convert the paper into a short claims map: current title, current contribution names, removed/deprecated concepts, benchmark setup, scaling caveats, and official paper URL.
3. Search the codebase for stale URLs and old terms before and after edits.
4. If the user says a concept was deleted or “doesn’t exist anymore,” remove it completely from hero copy, metadata, dashboards, captions, decorative equations, and citations; do not keep it as an optional/secondary feature unless the current source explicitly says so.

## Hero/design QA
- Decorative equations/tickers should never sit behind the hero title, CTA row, badges, or metric cards. Put them in a bounded band/card below the primary content, or remove them.
- CTA hierarchy should be obvious: one primary action, then secondary/tertiary actions. Avoid three equally weighted buttons in the hero.
- Verify visual layout with `browser_vision`, not just accessibility snapshots. Snapshots can hide overlap such as decorative text crossing a title.
- When the user complains about legibility/layout (“tout est cassé”, “les équations sont écrasées”, “les boutons c’est mal organisé”), stop broad refactoring and fix that exact visual issue before pushing more design changes.

## Research-site copy principles
- Lead with the current claim and evidence, not old branding or spectacle.
- Keep caveats visible: e.g. matched-budget vs speed benchmark, single-seed scaling, or older proxy-scale ablations.
- Rename decorative components when the concept changes; stale component names are a warning sign that old claims may still leak into UI copy.
