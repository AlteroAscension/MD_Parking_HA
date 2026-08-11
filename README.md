# MD Parking → Home Assistant

Private engineering project for bringing the user's authorised MD Parking cameras
into Home Assistant and, later, exposing deliberate barrier controls. It is an
independent project: it must not become a dependency of the Belgee/X50 telemetry
stack.

## Current status

- The official Android application **MD Parking 2.0.6** (`ru.mdparking.application`)
  is installed and authenticated on the shared Android emulator.
- A camera card was opened without pressing a barrier-control button. The app uses
  a native VLC player and receives a short-lived signed RTSP URL for the video.
- The protected API is reached through `app.mdparking.ru`; authentication is
  handled via `auth.mdparking.ru/v2` over HTTPS/TLS.
- The current signed RTSP URL, session data, APK, captures and screenshots are
  intentionally not stored in this repository. See [Security boundaries](docs/SECURITY.md).

The next milestone is **read-only video only**: prove reliable, background
renewal of the temporary source and expose a stable local feed to Home Assistant.
Barrier opening comes only after that and stays isolated from camera recording.

## Target architecture

```text
Official MD Parking service
        │ authenticated HTTPS; gets a short-lived RTSP capability URL
        ▼
MD Parking Bridge (Home Assistant add-on)
        │ refreshes source, audits requests, keeps local restream alive
        ▼
go2rtc / Frigate / local RTSP-HLS endpoint
        │ stable local address, never a temporary provider URL
        ▼
MD Parking HA custom integration
        ├─ camera entities
        ├─ barrier state and guarded services
        └─ dedicated HA page
```

Details: [architecture](docs/ARCHITECTURE.md), [provider research](docs/RESEARCH.md),
[shared emulator](docs/EMULATOR.md), [X50 relationship](docs/X50_CONTEXT.md).

## Repository layout

```text
addon/                 # Future HA add-on: bridge, source refresh, restream.
custom_components/     # Future HA integration: entities, config flow, services.
frontend/              # Future dedicated HA page/card, if standard dashboard is insufficient.
docs/                  # Versioned technical and safety documentation.
.local/                # Ignored: APKs, captures, temporary URLs, local notes and secrets.
```

The first implementation may start in `addon/`; do not create a real barrier
service until the read-only video path is verified.

## Non-negotiable rules

1. Do not commit MD Parking credentials, bearer/session tokens, RTSP URLs,
   screenshots containing personal data, APKs or packet captures.
2. Do not send an `open` command during investigation. Camera navigation is
   permitted; barrier-control buttons are not.
3. Never put a provider RTSP URL directly in HA YAML: it is short-lived and is
   a bearer capability.
4. The HA interface must require a confirmation for each future barrier-open
   action and record who/when/which barrier. No automatic opening by default.

## Start here

1. Read [Research findings](docs/RESEARCH.md).
2. Read [Security boundaries](docs/SECURITY.md).
3. When testing the Android client, follow [Shared emulator](docs/EMULATOR.md).
4. Implement and test the add-on's read-only source-refresh contract before
   adding HA entities or UI.
