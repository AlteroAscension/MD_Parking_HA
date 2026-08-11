# Shared Android emulator

## Relationship to X50

This project deliberately reuses the existing X50 Android AVD for quicker
investigation. The emulator is **shared test infrastructure**, not part of this
repository and not an MD Parking deliverable.

Current AVD identifier: `emulator-5554` / `x50_navi_api30_magisk`.

The X50 AVD includes Magisk, LSPosed, Yandex Navigator and X50 modules. MD
Parking testing must not uninstall, reconfigure or update those components.
Only `ru.mdparking.application` and local diagnostic files are in scope here.

## Start and verify

On this PC the launcher normally resides at:

```powershell
powershell -ExecutionPolicy Bypass -File C:\X50_local\emulator\Start-Emulator.ps1 `
  -AvdName x50_navi_api30_magisk
```

Verify the shared AVD before any test:

```powershell
adb -s emulator-5554 get-state
adb -s emulator-5554 shell getprop ro.product.cpu.abilist
adb -s emulator-5554 shell pm path ru.mdparking.application
```

The installed MD Parking split package must match the AVD architecture. Version
2.0.6 currently has an x86_64 split and starts on this AVD. An earlier archive
with only `arm64-v8a` native libraries installed but crashed because
`libreactnative.so` was unavailable for x86_64.

## Safe investigation rules

- It is acceptable to launch the app, authenticate the user's own account,
  navigate to a camera and inspect logs/connections.
- Never tap the button labelled `Открыть` during automated investigation.
- Do not copy the whole X50 project or its emulator data into this repository.
- Keep temporary APKs, pulled packages, screenshots and captures under
  `MD_Parking_HA/.local/`.

## Useful diagnostic commands

```powershell
adb -s emulator-5554 shell pidof ru.mdparking.application
adb -s emulator-5554 logcat -d | Select-String 'VLC|rtsp|mdparking'
adb -s emulator-5554 shell ss -tnp
```

These commands may reveal short-lived signed URLs in logs. Treat their output as
secret and do not paste it into versioned files.
