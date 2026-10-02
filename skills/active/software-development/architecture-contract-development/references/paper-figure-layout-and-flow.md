# Paper figure layout and narrative flow

Use this when replacing an architecture figure in a LaTeX research paper.

## Contract

A technically correct image is not enough. The figure must preserve the surrounding argument and must not split a paragraph from the list, proof, or explanation it introduces.

## Workflow

1. Read the actual compiled pages around the figure, not only the `.tex` source. Extract at least the page before, figure page, and page after with `pdftotext -layout`.
2. Distinguish two independent tasks:
   - image correctness and legibility;
   - document flow and float placement.
3. If the figure deserves a dedicated page, keep it at its semantic source location but use a float page and barrier:

```tex
\begin{figure}[p]
\centering
\includegraphics[width=0.68\textwidth,height=0.78\textheight,keepaspectratio]{figure.png}
\caption{...}
\label{fig:architecture}
\end{figure}
\FloatBarrier
```

4. Compile twice so references and float placement settle.
5. Re-extract pages around the figure and verify:
   - the preceding section ends cleanly;
   - the figure has a real dedicated visual space;
   - the following subsection begins intact;
   - no introductory sentence is separated from its enumeration.
6. If the diagram is intentionally simplified, describe it as a `simplified schematic` or `overview`, never as the `complete architecture`.
7. Apply equivalent wording and float behavior to translated paper sources.

## Pitfalls

- Enlarging `\includegraphics` alone can worsen pagination and split prose.
- A visually good PNG can still make the paper unreadable because LaTeX floats it into the middle of an argument.
- `pdftotext` does not show image pixels; a caption-only extracted page can correctly represent a dedicated figure page. Inspect the rendered page separately when visual confirmation is needed.
- Do not answer a complaint about the paper's prose organization by repeatedly redesigning the image. First identify whether the user means figure pixels, float placement, or the manuscript text itself.
