# Epson push scan on macOS

## Component roles

For Epson multifunction devices, distinguish:

- **AirPrint/CUPS**: printing from the Mac.
- **AirScan / Image Capture / Epson Scan 2**: scanning initiated from the Mac.
- **Epson Event Manager**: receives scanner/printer control-panel events and makes the Mac available for device-initiated “Scan to Computer” workflows.

If the Mac can print and Epson Scan 2 can see the scanner, but the printer says it cannot find the computer, check Event Manager before reinstalling the printer queue.

## Verified WF-3725/WF-3720-family example

A WF-3725DWF can advertise itself to macOS as **EPSON WF-3720 Series**. In the observed case:

- CUPS had a DNS-SD IPPS URI and AirPrint PPD;
- `system_profiler` reported scanner support through AirScan;
- `ippfind` discovered the WF-3720 service over both `_ipp._tcp` and `_ipps._tcp`;
- macOS firewall and block-all mode were disabled;
- Epson Scan 2 was installed;
- Epson Event Manager was absent.

This proves network reachability and Mac-initiated scanning support, but not push-scan registration. The missing event receiver explains why the printer control panel could not list the Mac.

## Official Epson workflow

On Epson’s per-model support page, manually select the current macOS version. For the WF-3725DWF on macOS Tahoe 26, Epson listed Event Manager 2.51.94 alongside Epson Scan 2. Event Manager’s stated role is communication between scanner/multifunction buttons and the computer.

After installing Event Manager:

1. Open `Applications/Epson Software/Launch Event Manager` or the current Event Manager launcher.
2. Select the correct Epson scanner/model family.
3. Open Network Scan Settings.
4. Enable network scan.
5. Assign a short, recognizable network scan name such as `Mac-Boris`.
6. Allow Local Network access if macOS prompts.
7. Keep Event Manager running, then check the printer’s `Scan > Computer` destination list.
8. Perform an actual device-initiated scan before declaring the fix complete.

Epson’s guidance states that push scan requires the scanner driver/application plus the event/workflow software appropriate to the OS and model. Package availability changes, so always re-check the live official support page rather than preserving a direct download URL as timeless.
