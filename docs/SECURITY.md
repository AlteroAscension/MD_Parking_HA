# Security boundaries

## Secrets and local data

The following stay exclusively in `.local/` or the Home Assistant add-on data
volume, never in Git, issues, screenshots, release assets, or diagnostics:

- provider login data and session tokens;
- signed RTSP URLs and their query strings;
- APK files, network captures, and camera screenshots;
- address, phone number, and raw provider object identifiers.

Bridge errors use fixed safe codes. URLs, authorization headers, response
bodies, and provider identifiers are not logged.

## Functional boundary

Video and barrier control are separate trust domains.

- Video source acquisition is read-only and may run automatically.
- Opening a barrier is never triggered by video refresh, availability retries,
  or a free-form URL parameter.
- The generated UI confirms the target action immediately before sending it.
- The global `control_enabled` kill switch is disabled by default.
- Only barriers from the authenticated inventory have valid hashed local IDs.
- A per-target cooldown limits repeats.
- The bounded persistent audit contains only a timestamp, hashed ID, and result.

Pairing is possible only while `pairing_enabled` is explicitly enabled. Close
that window immediately after connecting an integration entry.

## Network boundary

The external provider API and RTSP origin are untrusted dependencies. Provider
HTTPS endpoints and media URL schemes/hosts are allow-listed. The go2rtc control
API binds only to loopback inside the add-on container.

Ports 8099 and 8554 must remain on the trusted LAN and must not be exposed by a
router or public reverse proxy. Remote viewing should pass through Home
Assistant authentication rather than publish the bridge directly.
