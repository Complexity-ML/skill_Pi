# Published email audit checkpoint

This checkpoint publishes only the Himalaya and AgentMail guide/reference changes,
their two standalone test files, and `audit-sources-lot2q.json` / `audit-sources-lot2r.json`.
It does not publish the rest of the ongoing local audit, its aggregate ledger,
`GOAL.md`, `SKILLS_AUDIT.md`, scanner, other tests or README/catalogue changes.

Both reviews remain **partial**, with `runtime_verified: false`. No live mail,
account, credential, signup, receiver, deployment, CLI installation or provider
qualification is included. Original authors/licenses remain attributed.

## Reproducible checkpoint checks

From a checkout containing this checkpoint:

```bash
python3 -B -m unittest discover -s scripts -p 'test_himalaya_contracts.py' -v
python3 -B -m unittest discover -s scripts -p 'test_agentmail_contracts.py' -v
```

These are **20 documentation/owned JSON/TOML/AST methods**, not mail/security tests.
TOML parsing requires Python3.11+; that one method explicitly skips when unavailable.
The checkpoint was also tested from a clean index-exported snapshot, not just the
dirty working tree. Loading all227 skills remains a catalogue/loading check, not
semantic or runtime qualification.

## Evidence scope

The source reports record historical audit-time **local workspace** results:
213/225 aggregate tests and 71/72 partial reviews with zero closed reviews.
Those other corrections/tests/ledger entries are not all present in this published
checkpoint. Do not interpret those numbers as reproducible checkpoint coverage.
Reports' statements of no commit/push describe the original audit execution;
publication was separately authorized afterwards. Temporary `/tmp` raw-source
paths are not bundled durable evidence. Source hashes establish integrity, not
complete reading, authenticity, approval or operational qualification.

Publication does not synchronize installed packages, modify badlogic/Nano, deploy
services or close the full227-skill audit. Box's guide and10 references have now
been read locally; its source validation/corrections remain pending and it is not
part of this checkpoint.
