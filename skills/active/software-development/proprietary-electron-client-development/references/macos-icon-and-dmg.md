# macOS Icon and DMG Recipe

Use this reference when a proprietary Electron desktop client needs a custom macOS icon and a verifiable local DMG.

## Source preparation

- Start from a square high-resolution PNG (1024px minimum).
- Inspect both the full-size source and a 128×128 downsample.
- Favor a centered head/symbol, high contrast, broad silhouette, and generous safe margins.
- Keep original and previous candidates under `build/` for rollback.

For online artwork used in a private prototype, save the original separately and record that it is not cleared for public distribution. Check for obvious text, watermarks, bad crops, and insufficient resolution before use.

## Build an iconset

Expected filenames:

```text
icon_16x16.png
icon_16x16@2x.png
icon_32x32.png
icon_32x32@2x.png
icon_128x128.png
icon_128x128@2x.png
icon_256x256.png
icon_256x256@2x.png
icon_512x512.png
icon_512x512@2x.png
```

Generate each from the same master with `sips`, then compile:

```bash
iconutil -c icns build/icon.iconset -o build/icon.icns
```

Configure electron-builder:

```json
{
  "build": {
    "mac": {
      "icon": "build/icon.icns",
      "target": ["dmg"]
    }
  }
}
```

## Build and verify

```bash
npm test
npm run check
npm audit
npm run pack:mac
```

Confirm architecture and artifact identity:

```bash
file dist/mac-arm64/YourApp.app/Contents/MacOS/YourApp
shasum -a 256 dist/YourApp-*.dmg
```

Find the embedded ICNS under:

```text
dist/mac-arm64/YourApp.app/Contents/Resources/
```

Then hash both files:

```bash
shasum -a 256 build/icon.icns \
  dist/mac-arm64/YourApp.app/Contents/Resources/icon.icns
```

The hashes should match. If they do not, inspect electron-builder configuration, stale output directories, and actual resource naming before claiming the icon was integrated.

## Local versus public release

A locally functional DMG may be unsigned. Public distribution normally needs:

- Apple Developer ID Application certificate
- hardened runtime/entitlements as applicable
- code signing
- Apple notarization
- stapling and post-build verification

State explicitly when those steps were skipped.
