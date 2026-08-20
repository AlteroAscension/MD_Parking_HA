# MD Parking for Home Assistant

MD Parking cameras and guarded barrier controls in Home Assistant through a
local add-on and custom integration. The add-on authenticates the account,
keeps the provider session alive, renews short-lived camera sources, and
restreams them under stable local addresses. The integration creates native
camera, button, and connectivity entities plus a ready-to-use sidebar page.

## Features

- guided phone, object-number, and SMS authentication;
- automatic pairing without manually copying an API token;
- automatic camera and barrier discovery;
- provider-session and short-lived video-source renewal;
- stable local H.264 streams through bundled go2rtc;
- full-frame-rate video when a camera card is opened;
- guarded barrier buttons with confirmation, kill switch, cooldown, and audit;
- a responsive sidebar dashboard that preserves user edits;
- a dedicated landscape vehicle view at `/md-parking/car` with a compact
  camera-and-barrier layout;
- an information page with stable local RTSP addresses for recording software;
- secret-safe Home Assistant diagnostics;
- installation and updates from this Git repository.

Camera/session refresh and barrier control are separate code paths. Refreshing
a stream can never invoke a barrier action.

## Installation

1. Open **Settings > Add-ons > Add-on store > Repositories** in Home Assistant.
2. Add `https://github.com/AlteroAscension/MD_Parking_HA`.
3. Install **MD Parking Bridge**, enable `pairing_enabled`, then start or restart
   it; no manual token or provider credentials are required.
4. In HACS add the same URL as a custom **Integration** repository and install
   **MD Parking**. Alternatively copy `custom_components/md_parking` to
   `/config/custom_components/md_parking`.
5. Restart Home Assistant, then open **Settings > Devices & services > Add
   integration > MD Parking**.
6. Enter `http://<HOME_ASSISTANT_IP>:8099`, leave the token blank, and complete
   the guided login only if requested.
7. Disable `pairing_enabled` after setup and restart the add-on.

Enable `control_enabled` only if barrier buttons are needed. The bridge applies
`control_cooldown_seconds` independently to each barrier and persists a bounded
audit containing only time, a hashed stable ID, and the outcome. Restart the
add-on after changing its options.

The integration creates **MD Parking** in the sidebar. Closed cards use cached
still previews to keep resource use low; opening a card switches to the native
Home Assistant stream at the source frame rate. The `/md-parking/car` view is
optimized for a landscape vehicle display: cameras are arranged in a two-column
grid with their matching confirmed barrier buttons immediately below. The device page includes a
connectivity diagnostic entity. Use **Подключение к видеорегистратору** on the
dashboard to copy stable local RTSP addresses into NVR software.

## Updates

Update **MD Parking Bridge** in the Add-on Store and **MD Parking** in HACS.
Both components use the same release version; changes are recorded in
[CHANGELOG.md](CHANGELOG.md).

Keep ports 8099 and 8554 on the trusted LAN. Provider sessions and temporary
video URLs remain only in the add-on data volume. Never publish add-on data,
captures, tokens, or stream URLs. See the [installation guide](docs/INSTALLATION.md),
[recording guide](docs/RECORDING.md), [architecture](docs/ARCHITECTURE.md), and
[security policy](docs/SECURITY.md).
