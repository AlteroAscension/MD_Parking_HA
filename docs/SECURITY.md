# Security boundaries

## Secrets and local data

The following stay exclusively in `.local/` or a Home Assistant add-on secret
store, never in Git, issue text, screenshots, release assets or diagnostics:

- provider login data;
- access/refresh/session tokens;
- signed RTSP URLs and their query strings;
- APK files, PCAP/HAR captures and screenshots with camera content;
- apartment/address, phone number and raw provider object IDs.

Any logs emitted by the future bridge must redact query strings and HTTP
`Authorization`/cookie headers.

## Functional boundary

Video and barrier control are different trust domains.

- Video source acquisition is read-only and may run automatically.
- Opening a barrier is a physical action and must never be triggered by a video
  refresh, an availability retry, an automation, or a free-form URL parameter.
- The future UI uses a confirmation step and names the target barrier.
- The add-on has a global control-disable switch, enabled by default until the
  user explicitly turns it on.

## Network boundary

The external provider API and RTSP origin are untrusted internet dependencies.
The bridge should expose only localhost/add-on-internal ports to Home Assistant;
do not expose its diagnostics, restream input or control endpoint through the
public HA URL.

The restream output should remain LAN/HA-internal. External viewing, if ever
needed, must be handled through Home Assistant authentication rather than by
publishing an RTSP address.
