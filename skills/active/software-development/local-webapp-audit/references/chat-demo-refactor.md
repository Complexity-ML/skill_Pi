# Chat/demo UI refactor QA lessons

Use this reference when polishing an AI demo chat inside a local web app.

## Preserve demo affordances
- Do not remove prompt suggestion groups while cleaning the welcome screen. If there are many suggestions, keep all of them and put them in a bounded, scrollable panel instead of slicing the arrays.
- Verify each mode (`TR-MoE`, `compare`, `dense`, etc.) because suggestion counts and groups can differ by mode.

## Code/text rendering
- Never guess that text is code from keywords like `for`, `if`, `class`, or `import`; model prose often contains those words.
- Render code only when the assistant output contains explicit fenced Markdown blocks such as ```python ... ```.
- Plain text should render as readable prose: comfortable line-height, paragraph spacing, lists when the text uses bullets/numbering, and visual chunking for very long single-paragraph outputs.

## Layout shell
- Chat pages should use a fixed viewport shell (`h-screen overflow-hidden`) with one internal scrolling region. Avoid sticky headers inside nested scroll containers; they can appear mid-screen after page scroll/restore.
- Keep the composer anchored and make suggestion panels/timelines scroll above it, not underneath it.

## Verification
- Run lint/build, then open the demo route and visually inspect at least the default chat mode and compare mode.
- Use browser console checks plus visual inspection; accessibility snapshots can confirm suggestion counts, but screenshots catch overlap and composer/header issues.
