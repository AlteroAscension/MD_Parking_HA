# Installation from Git

## 1. Install the add-on

In Home Assistant open **Settings > Add-ons > Add-on store > Repositories** and
add:

```text
https://github.com/AlteroAscension/MD_Parking_HA
```

Install **MD Parking Bridge**. Enable `pairing_enabled`, start or restart the
add-on, and confirm that its log says the local API is listening on port 8099.
No API token, provider password, object number, or SMS code is entered in add-on
options.

## 2. Install the custom integration

In HACS add the repository URL above as a custom repository with category
**Integration**, install **MD Parking**, and restart Home Assistant.

For manual installation, copy `custom_components/md_parking` from this
repository to `/config/custom_components/md_parking`, then restart Home
Assistant.

## 3. Pair and sign in

Open **Settings > Devices & services > Add integration > MD Parking**.

- Bridge URL: `http://<HOME_ASSISTANT_LAN_IP>:8099`
- API token: leave blank

Use the Home Assistant machine's LAN address, not `localhost`: Core and the
add-on run in separate containers. If the add-on already has a valid provider
session, setup completes immediately. Otherwise, enter the phone number, object
number, and SMS code in the guided forms.

Disable `pairing_enabled` after setup and restart the add-on. Re-enable it only
while pairing a replacement integration entry; restart the add-on so it can
return its existing local token automatically.

Enable `control_enabled` only when barrier buttons are required. Every dashboard
press is confirmed, checked again by the bridge, rate-limited, and written to a
secret-safe persistent audit. Camera refresh never calls control.

Supervisor options are read when the add-on starts. Restart it after changing
pairing, control, cooldown, or refresh settings.

## 4. Use the generated dashboard

Open **MD Parking** in the sidebar. Each generated block keeps a camera and its
matching guarded button together. Closed cards use still previews; click a
camera to open the full-rate native stream. The same entities can be used in
your own dashboards.

For a landscape vehicle display, open `https://<HOME_ASSISTANT_URL>/md-parking/car`.
This compact view uses a two-column grid of camera previews and places each
camera's confirmed barrier control below it. It contains no connection-status
or recorder-information cards.

Use **Подключение к видеорегистратору** on this page to open a subview containing
one stable local RTSP address per camera. Copy the required address into an NVR,
VLC, Frigate, Blue Iris, or other RTSP-compatible application and select RTSP
over TCP. The streams contain H.264 video without audio.

For local recording, use the tested [Frigate setup](RECORDING.md). Start with a
six-hour archive and object detection disabled, then increase retention only
after checking disk use.

The generated dashboard is migrated only while it still matches a layout made
by an older release. Version 0.5.1 adds the vehicle view to an unedited 0.5.0
layout. Once edited, it is left untouched.

## Reauthentication

Use **Settings > Devices & services > MD Parking > Configure** if the provider
session is revoked. This repeats the phone, object-number, and SMS steps without
changing the local bridge token or entities.

## Updating

Use the Add-on Store update action for the bridge and HACS for the integration.
After a manual integration update, restart Home Assistant. Compare versions
with [CHANGELOG.md](../CHANGELOG.md).

Do not expose ports 8099 or 8554 through router forwarding or a public reverse
proxy. Do not put provider tokens, stream URLs, account identifiers, or SMS
codes in YAML or Git. See [RECORDING.md](RECORDING.md) and
[SECURITY.md](SECURITY.md).
