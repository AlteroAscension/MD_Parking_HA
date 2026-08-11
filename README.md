# MD Parking for Home Assistant

MD Parking cameras in Home Assistant through a local add-on and custom
integration. The add-on performs account authentication, keeps the provider
session alive, renews short-lived camera sources, and restreams them under
stable local addresses. The integration creates native Home Assistant camera
entities.

## Features

- guided phone, object-number, and SMS authentication;
- automatic discovery of cameras available to the account;
- automatic provider-session and video-source renewal;
- stable local H.264 streams through bundled go2rtc;
- Home Assistant camera entities and secret-safe diagnostics;
- installation and updates from this Git repository.

Barrier control is intentionally not included in the current camera release.
It will be a separate, explicitly enabled feature with audit and rate limiting;
camera refresh will never invoke a barrier action.

## Installation

1. In Home Assistant open **Settings > Add-ons > Add-on store > Repositories**.
2. Add `https://github.com/AlteroAscension/MD_Parking_HA`.
3. Install and start **MD Parking Bridge**. Enable `pairing_enabled` for initial
   setup; no manual token or provider credentials are required.
4. In HACS add the same URL as a custom **Integration** repository and install
   **MD Parking**. Alternatively copy `custom_components/md_parking` to
   `/config/custom_components/md_parking`.
5. Restart Home Assistant, then open **Settings > Devices & services > Add
   integration > MD Parking**.
6. Use `http://<HOME_ASSISTANT_IP>:8099` as the bridge URL, leave the token blank,
   and complete the phone, object-number, and SMS steps.
7. Disable `pairing_enabled` after setup.

The cameras then appear as normal `camera` entities and can be added to a
Picture Entity or Picture Glance dashboard card. Keep ports 8099 and 8554 on
the trusted LAN; do not expose them to the internet.

## Updates

Update **MD Parking Bridge** in the Add-on Store and **MD Parking** in HACS.
Release versions are recorded in [CHANGELOG.md](CHANGELOG.md).

Provider tokens and temporary video URLs are stored only in the add-on data
volume. Never publish add-on data, diagnostics containing personal data,
captures, or stream URLs. See the [installation guide](docs/INSTALLATION.md),
[architecture](docs/ARCHITECTURE.md), and [security policy](docs/SECURITY.md).
