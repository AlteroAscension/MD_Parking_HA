# MD Parking for Home Assistant

Private Home Assistant integration for MD Parking cameras. The project provides
a local bridge add-on that maintains temporary camera sources and exposes stable
local streams to Home Assistant.

## Features

- authorised camera discovery;
- automatic renewal of temporary stream sources;
- stable local go2rtc stream names;
- Home Assistant camera entities discovered from the bridge;
- local authenticated diagnostics without credentials or source URLs.

Barrier control is intentionally not included in this release.

## Install

1. In Home Assistant open **Settings → Add-ons → Add-on store → ⋮ → Repositories**.
2. Add `https://github.com/AlteroAscension/MD_Parking_HA`.
3. Install **MD Parking Bridge**, configure its runtime options and start it.
4. Install `custom_components/md_parking` with HACS as a custom repository, or
   copy it to `config/custom_components/md_parking`.
5. Restart Home Assistant and add **MD Parking** under **Settings → Devices & services**.

The integration connects only to the bridge. Provider credentials and temporary
stream sources must never be entered in Home Assistant YAML.

When adding the integration, use `http://<HA-LAN-IP>:8099` as the bridge URL
(for example, `http://192.168.1.50:8099`). To pair without entering a token,
temporarily enable `pairing_enabled` in the add-on and leave the integration
token field empty. Pairing closes after the first successful connection.
The integration then guides you through phone number, object number, and SMS
verification. Provider tokens are stored only in the add-on data volume.

## Updates

The add-on version is declared in `addon/md-parking-bridge/config.yaml` and the
custom integration version in `custom_components/md_parking/manifest.json`.
Update through the Add-on Store/HACS, then restart the add-on and reload the
integration.

## Security

Keep the bridge API token and provider credentials in Home Assistant secrets or
add-on options. Do not publish diagnostics, stream URLs, captures, or logs.

See [installation details](docs/INSTALLATION.md) and
[security boundaries](docs/SECURITY.md).
