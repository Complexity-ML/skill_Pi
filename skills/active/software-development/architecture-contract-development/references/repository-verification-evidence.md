# Repository Verification Evidence

Use this procedure when architecture or integration verification runs in a repository that already contains user edits, untracked artifacts, multiple runtimes, or hardware-dependent tests.

## Preserve the worktree

Inventory branch, `HEAD`, tracked modifications, staged changes, and untracked paths. Classify requested-change files separately from pre-existing user state. Do not blanket-stash, reset, clean, stage, or rewrite unrelated work to simplify verification.

When a clean baseline is necessary, prefer a separate temporary worktree at the same `HEAD`, using the same dependencies and test command. An exact CI result for that revision is also valid. If neither exists, report current-tree observations without claiming failures are pre-existing or newly introduced.

## Select the runtime deliberately

Read the repository manifest and documented verification command. Resolve the intended executable and confirm it can import the required test/lint modules before starting the main run. The agent host interpreter may differ from the project runtime. Do not install or modify dependencies unless setup changes are authorized.

## Verify in layers

1. Run tests that directly cover the changed symbols and call paths.
2. Run lint/type checks over changed files and their tests.
3. Run the repository-declared broader suite when practical.

Keep each result separate. A targeted pass validates that surface only; it neither cancels nor hides failures in the broader suite.

## Triage hardware-sensitive failures

Rerun each failure alone with the same runtime and environment. Establish whether it exercises the changed path and whether the error demonstrates a host/backend capability boundary, such as an unsupported accelerator operator or dtype. A fallback can expose the next failure boundary, but it does not make the original suite green. Do not suppress or skip the failure unless the repository contract explicitly permits it.

## Evidence-accurate report

Report exact targeted and broader-suite pass/fail/skip counts, lint/type findings with file and line, demonstrated platform constraints, whether a safe baseline existed, and whether verification itself changed files.

Use `clean`, `passed`, or `verified` only when every required gate is green. Otherwise state which surface passed and which gate remains non-green. Never infer architectural correctness, executed kernel selection, or completed experiment status from configuration alone.
