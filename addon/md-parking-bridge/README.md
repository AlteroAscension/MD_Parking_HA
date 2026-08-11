# MD Parking Bridge add-on

The bridge signs in to the user's MD Parking account, discovers available
cameras, renews the provider session and short-lived video sources, and serves
each camera under a stable local go2rtc RTSP name.

Authentication is completed from the Home Assistant integration in three
steps: phone number, object number, and SMS code. Provider tokens and temporary
stream URLs remain in the add-on data volume and are not returned by its local
API or diagnostics.

## First setup

1. Start the add-on with `pairing_enabled` enabled.
2. Add the **MD Parking** integration.
3. Enter `http://<HOME_ASSISTANT_IP>:8099` as the bridge URL and leave the API
   token blank.
4. Complete the phone, object-number, and SMS forms.
5. Disable `pairing_enabled` after the integration has been added.

Ports 8099 and 8554 must remain on the trusted local network. Do not forward
them from the router or publish them through a reverse proxy.

This release exposes cameras only. Barrier control is intentionally isolated
from camera source renewal and is not included yet. See the
[installation guide](../../docs/INSTALLATION.md) and
[security policy](../../docs/SECURITY.md).
