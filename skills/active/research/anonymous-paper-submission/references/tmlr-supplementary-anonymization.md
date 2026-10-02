# TMLR supplementary anonymization notes

TMLR Author Guidelines state that supplementary material may include source code/data/videos in PDF or ZIP format and that, like submissions, supplementary material must be anonymized.

## Practical submission artifact

Prefer a supplement-only ZIP when OpenReview separately asks for the paper PDF:

- Include: `supplementary_code/`, license, reproduction README, small config/tokenizer stubs, tests, scripts.
- Exclude: `.git/`, paper PDF/LaTeX unless explicitly requested in the supplement, logs, aux/out files, caches, checkpoints, weights, local run outputs.
- Do not submit a GitHub link if repo owner/history/remotes/commit authors are identifying.

## Revision-form alignment checklist

For OpenReview/TMLR revisions, the web form is part of the submission narrative. After changing the PDF/supplement, update the form fields before writing reviewer replies:

- Title: match the PDF title and the narrowed contribution.
- Abstract: remove stale components/old ablations/future work that the current PDF no longer claims.
- Changes since last submission: explicitly list the major reviewer-driven changes and use the same scope as the revised paper.
- Supplementary material: re-upload the latest scanned ZIP, not an older attachment with the same display name.
- Reviewer reply: answer only after the revision metadata and artifacts are aligned, so the response can point to the revised evidence.

## Dropped-component cleanup checklist

When a reviewer or user says a component is no longer part of the paper, remove it from the review artifact completely, not just from the abstract:

- Paper: title, abstract, contributions, theory/propositions, captions, limitations/future work, and OpenReview abstract/changes fields.
- Supplement docs: root README, reproduction README, package docstrings.
- Code: CLI flags, config fields, model branches, compatibility aliases, tests, examples, filenames.
- Assets: figures named after the component, generated HTML, result CSV labels.
- Final ZIP: scan extracted artifact for both prose terms and implementation identifiers.

Example scan pattern to adapt:

```bash
grep -RInEi 'ComponentName|component_flag|component_to_|component_prev|component_context' /tmp/submission_scan \
  --exclude-dir=.git --exclude-dir=figures --exclude='*.pdf' --exclude='*.pyc'
```

## Final-gate commands

```bash
rm -rf /tmp/submission_scan && mkdir -p /tmp/submission_scan
unzip -q dist/supplement_only.zip -d /tmp/submission_scan

# Identity scan
grep -RInE 'AuthorName|OrgName|email@example|/Users/name|/root/|github.com/org|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' /tmp/submission_scan \
  --exclude-dir=.git --exclude-dir=figures --exclude='*.pdf' --exclude='*.pyc'

# Dropped-component scan
grep -RInEi 'DroppedComponent|dropped_component_flag|dropped_component_identifier' /tmp/submission_scan \
  --exclude-dir=.git --exclude-dir=figures --exclude='*.pdf' --exclude='*.pyc'

# Artifact scan
find /tmp/submission_scan \
  -name '.git' -o -name '*.log' -o -name '*.aux' -o -name '*.out' -o -name '.DS_Store' -o \
  -name '__pycache__' -o -name '.pytest_cache' -o -name '*.pyc' -o -name '*.pt' -o -name '*.ckpt'

# Ensure supplement-only archive has no paper PDF unless intentionally combined
find /tmp/submission_scan -iname '*.pdf' -print
```
