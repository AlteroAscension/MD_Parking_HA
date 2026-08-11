# Installation from Git

## 1. Install the add-on

In Home Assistant open **Settings > Add-ons > Add-on store > Repositories** and
add:

```text
https://github.com/AlteroAscension/MD_Parking_HA
```

Install **MD Parking Bridge**. Enable `pairing_enabled`, start the add-on, and
confirm that its log says the local API is listening on port 8099. You do not
need to enter an API token, username, password, object number, or SMS code in
the add-on options.

## 2. Install the custom integration

In HACS add the repository URL above as a custom repository with category
**Integration**, then install **MD Parking** and restart Home Assistant.

For a manual installation, copy `custom_components/md_parking` from this
repository to `/config/custom_components/md_parking`, then restart Home
Assistant.

## 3. Pair and sign in

Open **Settings > Devices & services > Add integration > MD Parking**.

- Bridge URL: `http://<HOME_ASSISTANT_LAN_IP>:8099`
- API token: leave blank during automatic pairing

Use the Home Assistant machine's LAN address, not `localhost`: the integration
runs in the Core container while the bridge runs in a separate add-on
container.

Complete the guided forms for phone number, object number, and SMS code. On
success, Home Assistant creates one camera entity for every camera available to
the account. Return to the add-on options and disable `pairing_enabled`.

Enable `control_enabled` only when barrier buttons are required. Every press is
confirmed in the dashboard, checked again by the bridge, rate-limited, and
recorded in the bridge's secret-safe audit. Camera refresh never calls control.

## 4. Add cameras to a dashboard

Add a **Picture Entity** or **Picture Glance** card and select the generated
`camera` entity. The integration points Home Assistant at port 8554 using a
stable stream name; temporary provider URLs are never placed in dashboard
configuration.

## Updating

Use the Add-on Store update action for the bridge and HACS for the integration.
After a manual integration update, restart Home Assistant. Compare installed
versions with [CHANGELOG.md](../CHANGELOG.md).

Do not expose ports 8099 or 8554 through router forwarding or a public reverse
proxy. Do not put provider tokens, stream URLs, account identifiers, or SMS
codes in YAML or Git. See [SECURITY.md](SECURITY.md).
