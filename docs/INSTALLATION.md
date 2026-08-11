# Installation from Git

## Add-on repository

In Home Assistant, open **Settings → Add-ons → Add-on store → ⋮ → Repositories**
and add this repository's Git URL. The store discovers
`addon/md-parking-bridge` through the root [`repository.yaml`](../repository.yaml).

Install **MD Parking Bridge**, configure a long random `api_token`, and keep the
port reachable only on the HA local network. Provider credentials and the verified local
profile belong to the add-on data volume, never Git or the custom integration.

## Custom integration

Until this repository is packaged for HACS, copy `custom_components/md_parking`
to Home Assistant's `config/custom_components/md_parking`, restart Home
Assistant, and add **MD Parking** through **Settings → Devices & services**.
The config flow accepts only the bridge URL and its API token.

Use `http://<HA-LAN-IP>:8099` as bridge URL and exactly the same `api_token`
that was configured in the add-on. Do not expose port 8099 through router port
forwarding or a public reverse proxy.

For automatic pairing, enable `pairing_enabled` in the add-on and leave the
integration token empty. The integration then asks for the MD Parking phone,
object number, and SMS code. For an integration entry created before version
0.2.0, open **Settings → Devices & services → MD Parking → Configure** to run
the same provider login flow. The phone, object number, and SMS code are not
stored in the Home Assistant config entry.

Do not configure a provider RTSP URL, provider credentials, camera ID, or
barrier ID in Home Assistant. See [SECURITY.md](SECURITY.md) and
[BRIDGE_PROFILE.md](BRIDGE_PROFILE.md).

## Updating

Use the Add-on Store update action for the bridge and HACS/manual replacement
for the custom integration. Restart the add-on after every bridge update, then
reload the integration. Check the installed release against
[CHANGELOG.md](../CHANGELOG.md).
