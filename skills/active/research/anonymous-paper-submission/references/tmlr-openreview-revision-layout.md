# TMLR / OpenReview Revision Layout Checklist

Use this when revising a TMLR submission after changing architecture figures, claims, or supplementary artifacts.

## PDF layout after figure changes

- Inspect the compiled PDF page-by-page around the changed figure, not just the LaTeX source.
- If a figure interrupts a paragraph and its bullet/enumerated evidence, move the float boundary rather than accepting the break.
- For a large architecture schematic, prefer a dedicated float page before the next subsection:
  - `\begin{figure}[p]`
  - large enough `\includegraphics[...]`
  - `\end{figure}`
  - `\FloatBarrier`
  - then start the next subsection.
- Verify the local flow with `pdftotext -f N -l M -layout paper.pdf ...` or by opening pages around the figure.
- A dedicated figure page is acceptable when it preserves the reading flow; avoid leaving a paragraph setup on one page and its numbered points after the figure.

## Figure scope wording

- If the diagram is simplified, never describe it as the “complete architecture.”
- Use wording like:
  - “simplified schematic”
  - “architecture overview”
  - “300M residual Token-Routed schematic”
- Caption should state what is omitted/simplified by implication and match the actual evidence:
  - shared dense MLP backbone
  - small Zipf-routed lexical residual branch
  - no obsolete removed components
- Search for stale phrases such as `complete architecture`, old component names, or removed mechanisms in both paper and submission-form text.

## OpenReview/TMLR form alignment

- Update OpenReview fields after updating the PDF:
  - title
  - abstract
  - changes since last submission
  - submission type
  - PDF upload
  - supplementary ZIP upload
- Do not paste stronger claims into the form than the revised PDF supports.
- For TMLR, use “Long submission” if main content exceeds the regular page limit, even if the PDF compiles cleanly.
- Leave “Beyond PDF” empty unless submitting an interactive webpage package; supplementary ZIPs do not belong there.

## Supplement consistency

- If a figure is inside the supplementary ZIP, replace it there too and hash-check it against the source PNG.
- Scan the extracted ZIP, not only the source directory.
- When a component is removed from the paper, remove it from figure text, captions, OpenReview prose, and supplement artifacts unless explicitly retained as historical/legacy context.
