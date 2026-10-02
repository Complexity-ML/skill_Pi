# Skills for Pi

227 skills for Pi covering coding, research, automation and blockchain engineering. All are grouped under `skills/active/` and discovered by the package manifest. This package contains skills only, not extensions. The eight separately installed badlogic skills are not included. The folder name `active` does not imply tested runtime compatibility.

## Install

```sh
pi install git:github.com/Complexity-ML/skill_Pi
```

Then run `/reload` in Pi and type `/skill:` to discover commands. Private repositories require GitHub authentication.

## Compatibility

Frontmatter is normalized, supported skill references are relocatable, and compatibility notes explain Pi tools and legacy Hermes pseudocode. Bundled scripts and resources are included. Paths in references are relative to the containing skill directory: resolve them to absolute paths before tool calls.

Runtime compatibility is **not verified**. Legacy tool-call examples are not executable Pi calls; follow the compatibility notes. External CLI programs, accounts, API keys, browser integrations and optional subagent extensions are not installed by this package. Fourteen explicitly Hermes-dependent workflows have been excluded; other external dependencies can remain.

Skills can instruct an agent to run commands. Review instructions and scripts before use. Health and biometric skills are research-only and must not be used for diagnosis or treatment.

## Blockchain engineering skills

Ten new, self-contained workflows cover qualification evidence, EVM conformance, distributed finality, validator recovery, asynchronous network admission, immutable releases, durable alerts, contract qualification, bridge trust and RPC behavior.

See [NANO_DOCS_SKILLS.md](NANO_DOCS_SKILLS.md) for the complete tracked project Markdown inventory (excluding vendored dependencies), source-to-skill mapping and pinned provenance. Indexing is not an exhaustive document audit. No Nano runtime, remote network campaign or deployment was executed for this extraction. New skills have passed Pi loading/structural validation only; runtime workflows remain unverified. Their licensing is pending owner review before redistribution.

Example after installing this package and running `/reload`:

```text
/skill:qualification-evidence-gates Audit the coverage and terminal results of this repository.
```

## Catalog and licensing

See [catalog.json](catalog.json) for names, descriptions, locations and declared licenses, and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and redistribution limitations. This collection does not claim a single blanket license over its third-party content.
