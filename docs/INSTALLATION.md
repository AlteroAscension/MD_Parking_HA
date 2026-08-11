# Installation from Git

## Add-on repository

In Home Assistant, open **Settings → Add-ons → Add-on store → ⋮ → Repositories**
and add this repository's Git URL. The store discovers
`addon/md-parking-bridge` through the root [`repository.yaml`](../repository.yaml).

Install **MD Parking Bridge**, configure a long random `api_token`, and keep the
port internal to Home Assistant. Provider credentials and the verified local
profile belong to the add-on data volume, never Git or the custom integration.

## Custom integration

Until this repository is packaged for HACS, copy `custom_components/md_parking`
to Home Assistant's `config/custom_components/md_parking`, restart Home
Assistant, and add **MD Parking** through **Settings → Devices & services**.
The config flow accepts only the bridge URL and its API token.

Do not configure a provider RTSP URL, provider credentials, camera ID, or
barrier ID in Home Assistant. See [SECURITY.md](SECURITY.md) and
[BRIDGE_PROFILE.md](BRIDGE_PROFILE.md).
