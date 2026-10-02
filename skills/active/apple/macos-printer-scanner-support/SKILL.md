---
name: macos-printer-scanner-support
description: Use when macOS printers or scanners will not connect.
metadata:
  hermes:
    tags:
    - macos
    - printer
    - scanner
    - airprint
    - cups
    - troubleshooting
    category: apple
  hermes_frontmatter:
    version: 1.0.0
    platforms:
    - macos
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
  copyright: Copyright (c) 2026 Complexity-ML
  ownership: Owner-confirmed original skill, generated with GPT in Hermes for Complexity-ML
license: MIT
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# macOS Printer and Scanner Support

Diagnose the exact workflow before reinstalling drivers. Printing, scanning started from the Mac, and scanning started from the device are separate paths with different requirements.

## Classify the failure

Ask or infer which path fails:

1. **Print from Mac**: document goes from macOS/CUPS to the printer.
2. **Pull scan from Mac**: Image Capture, Preview, vendor scan software, or AirScan starts the scan.
3. **Push scan from device**: the printer/scanner control panel must discover the Mac and notify a resident vendor utility.

A printer appearing in macOS does not prove push scan is configured. Avoid saying “connected” without naming the path that was verified.

## Read-only diagnosis first

Use live system checks before changing configuration:

- `sw_vers` for the exact macOS release.
- `lpstat -p -d -v` for configured queues, defaults, and device URIs.
- `lpstat -o` for blocked jobs.
- `system_profiler SPPrintersDataType SPUSBDataType` for driver/PPD, AirPrint, scanner support, firmware, and USB visibility.
- `ippfind -T 8 _ipps._tcp -s` and `ippfind -T 8 _ipp._tcp -s` for current Bonjour/IPP discovery.
- `/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate` and `--getblockall` when network discovery is involved.
- Search Applications and active processes for the vendor’s scanner event/receiver utility.

Interpret `Idle` or localized equivalents such as `inactive, mais activée` as ready/waiting unless jobs or status details show an error. Model-family names may differ from the retail model; confirm through the vendor’s support page rather than assuming a mismatch.

## Push-scan rule

For a scan initiated on the printer/scanner, a normal AirPrint/AirScan registration is often insufficient. Many vendors require a background event receiver that:

- registers the computer on the local network;
- listens for control-panel button events;
- exposes a recognizable computer name;
- maps buttons to save/PDF/email/application actions.

Verify that utility is installed, running, configured for network scan, and permitted to access the local network. Also verify the main scanner driver/application separately.

## Obtain software safely

Use the manufacturer’s official per-model support page and manually select the exact live macOS version; auto-detection can be wrong. Inspect the page before recommending a package. Prefer vendor-hosted downloads over third-party driver sites.

Before installing:

1. Confirm the package is listed for the exact model family and macOS version.
2. Download from the manufacturer’s domain.
3. Mount or inspect the package to confirm its identity.
4. Open the installer only when installation is the requested fix.
5. Let the user handle administrator authentication and OS privacy prompts.

After installation, configure the network-scan name, enable network/push scan, allow Local Network access, keep the receiver running, and then verify that the device control panel lists the Mac. Do not claim success until the device-initiated workflow is tested.

## Safety and side effects

Printing a test page consumes paper and ink; ask before doing it. Installing packages and changing firewall/privacy settings are state changes—keep the scope explicit. Never disable security controls as a blanket workaround.

## Vendor notes

See `references/epson-push-scan.md` for the Epson Event Manager/Scan 2 pattern and a verified WF-37xx diagnostic example.
