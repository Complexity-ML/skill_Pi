---
name: impeccable
description: Frontend design guidance, upstream-maintained (impeccable).
license: Apache-2.0
metadata:
  hermes:
    tags:
    - design
    - frontend
    - ui
    - ux
    - web-design
    - anti-slop
    category: creative
    related_skills:
    - claude-design
    - popular-web-designs
    upstream:
      repo: pbakaus/impeccable
      path: .hermes/skills/impeccable
  hermes_frontmatter:
    version: 4.1.2
    author: Paul Bakaus (pbakaus)
    platforms:
    - linux
    - macos
    - windows
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Impeccable (upstream-maintained)

> **Catalog stub.** This entry is maintained upstream at
> [pbakaus/impeccable](https://github.com/pbakaus/impeccable): the project
> ships and verifies a Hermes-native skill bundle under `.hermes/skills/`.
> `hermes skills install impeccable` pulls the current bundle live from that
> repo (quarantined and scanned like any hub install) — this directory holds
> only the catalog metadata, so the vendored copy can never go stale.

Impeccable is a design language for AI coding agents: one skill exposing 23
sub-commands (`/impeccable init`, `craft`, `shape`, `critique`, `audit`,
`polish`, `bolder`, `quieter`, `distill`, `harden`, `onboard`, `animate`,
`colorize`, `typeset`, `layout`, `delight`, `overdrive`, `clarify`, `adapt`,
`optimize`, `extract`, `document`, `live`), explicit anti-pattern guidance
(overused fonts, purple gradients, nested cards, bounce easing), and a
61-rule deterministic detector CLI (`npx impeccable detect`) that needs no
LLM or API key.

After install, start with:

```
/impeccable init
```

Full documentation: https://impeccable.style
