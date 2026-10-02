---
name: domain-intel
description: Passive recon of subdomains, SSL certs, WHOIS, and DNS.
license: MIT
metadata:
  hermes:
    tags:
    - Domains
    - OSINT
    - DNS
    - Research
    related_skills: []
  hermes_frontmatter:
    version: 1.0.0
    author: FurkanL0, Hermes Agent
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
- Legacy Hermes references used in the source:
  - `web_search` → an installed search skill or tool.
  - `web_extract` → an installed fetch/browser tool or CLI.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Domain Intelligence — Passive OSINT

Passive domain reconnaissance using only Python stdlib.
**Zero dependencies. Zero API keys. Works on Linux, macOS, and Windows.**

## Helper script

This skill includes `scripts/domain_intel.py` — a complete CLI tool for all domain intelligence operations.

```bash
# Subdomain discovery via Certificate Transparency logs
python SKILL_DIR/scripts/domain_intel.py subdomains example.com

# SSL certificate inspection (expiry, cipher, SANs, issuer)
python SKILL_DIR/scripts/domain_intel.py ssl example.com

# WHOIS lookup (registrar, dates, name servers — 100+ TLDs)
python SKILL_DIR/scripts/domain_intel.py whois example.com

# DNS records (A, AAAA, MX, NS, TXT, CNAME)
python SKILL_DIR/scripts/domain_intel.py dns example.com

# Domain availability check (passive: DNS + WHOIS + SSL signals)
python SKILL_DIR/scripts/domain_intel.py available coolstartup.io

# Bulk analysis — multiple domains, multiple checks in parallel
python SKILL_DIR/scripts/domain_intel.py bulk example.com github.com google.com
python SKILL_DIR/scripts/domain_intel.py bulk example.com github.com --checks ssl,dns
```

`SKILL_DIR` is the directory containing this SKILL.md file. All output is structured JSON.

## Available commands

| Command | What it does | Data source |
|---------|-------------|-------------|
| `subdomains` | Find subdomains from certificate logs | crt.sh (HTTPS) |
| `ssl` | Inspect TLS certificate details | Direct TCP:443 to target |
| `whois` | Registration info, registrar, dates | WHOIS servers (TCP:43) |
| `dns` | A, AAAA, MX, NS, TXT, CNAME records | System DNS + Google DoH |
| `available` | Check if domain is registered | DNS + WHOIS + SSL signals |
| `bulk` | Run multiple checks on multiple domains | All of the above |

## When to use this vs built-in tools

- **Use this skill** for infrastructure questions: subdomains, SSL certs, WHOIS, DNS records, availability
- **Use `web_search`** for general research about what a domain/company does
- **Use `web_extract`** to get the actual content of a webpage
- **Use `terminal` with `curl -I`** for a simple "is this URL reachable" check

| Task | Better tool | Why |
|------|-------------|-----|
| "What does example.com do?" | `web_extract` | Gets page content, not DNS/WHOIS data |
| "Find info about a company" | `web_search` | General research, not domain-specific |
| "Is this website safe?" | `web_search` | Reputation checks need web context |
| "Check if a URL is reachable" | `terminal` with `curl -I` | Simple HTTP check |
| "Find subdomains of X" | **This skill** | Only passive source for this |
| "When does the SSL cert expire?" | **This skill** | Built-in tools can't inspect TLS |
| "Who registered this domain?" | **This skill** | WHOIS data not in web search |
| "Is coolstartup.io available?" | **This skill** | Passive availability via DNS+WHOIS+SSL |

## Platform compatibility

Pure Python stdlib (`socket`, `ssl`, `urllib`, `json`, `concurrent.futures`).
Works identically on Linux, macOS, and Windows with no dependencies.

- **crt.sh queries** use HTTPS (port 443) — works behind most firewalls
- **WHOIS queries** use TCP port 43 — may be blocked on restrictive networks
- **DNS queries** use Google DoH (HTTPS) for MX/NS/TXT — firewall-friendly
- **SSL checks** connect to the target on port 443 — the only "active" operation

## Data sources

All queries are **passive** — no port scanning, no vulnerability testing:

- **crt.sh** — Certificate Transparency logs (subdomain discovery, HTTPS only)
- **WHOIS servers** — Direct TCP to 100+ authoritative TLD registrars
- **Google DNS-over-HTTPS** — MX, NS, TXT, CNAME resolution (firewall-friendly)
- **System DNS** — A/AAAA record resolution
- **SSL check** is the only "active" operation (TCP connection to target:443)

## Notes

- WHOIS queries use TCP port 43 — may be blocked on restrictive networks
- Some WHOIS servers redact registrant info (GDPR) — mention this to the user
- crt.sh can be slow for very popular domains (thousands of certs) — set reasonable expectations
- The availability check is heuristic-based (3 passive signals) — not authoritative like a registrar API

---

*Contributed by [@FurkanL0](https://github.com/FurkanL0)*
