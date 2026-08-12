# Changelog

## 0.4.1

- Apply pairing, control, cooldown, retry, and stream-renewal options at runtime
  after Supervisor saves them, without requiring a manual add-on restart.

## 0.4.0

- Harden provider communication with host/scheme validation, malformed-response
  handling, thread-safe state, and atomic session persistence.
- Verify the bundled go2rtc binary, bind its control API to loopback, and wait
  for readiness before starting the bridge.
- Persist the bounded secret-safe barrier audit across add-on restarts.
- Harden the local API with request limits, constant-time token checks, no-store
  responses, proper method handling, and richer secret-safe health data.
- Allow automatic local-token recovery only while the explicit pairing window
  is enabled.
- Add a shared asynchronous bridge client, concurrent coordinator polling,
  dynamic entity discovery, integration diagnostics, and a connectivity entity.
- Cache still previews while retaining full-frame-rate native streaming for
  opened camera cards.
- Replace broken Cyrillic UI strings and group each camera with its matching
  guarded button on the generated dashboard.
- Remove obsolete research-only profile code and workstation documentation from
  the distributable project.

## 0.3.2

- Advertise Home Assistant's native camera `STREAM` feature and use RTSP over
  TCP, enabling full-frame-rate video when a camera card is opened.
- Keep the closed dashboard cards on lightweight still previews.

## 0.3.1

- Use the broadly supported Lovelace `call-service` action for barrier buttons.
- Migrate the generated v0.3.0 dashboard action without overwriting other cards.

## 0.3.0

- Generate real camera preview JPEGs through Home Assistant's bundled ffmpeg.
- Add isolated barrier buttons backed by the confirmed access operation.
- Require frontend and bridge confirmation, provide a configurable kill switch,
  enforce per-barrier cooldown, and keep a secret-safe in-memory audit trail.
- Add the barrier buttons to the generated MD Parking dashboard.

## 0.2.9

- Initialize Home Assistant's Camera base explicitly when combined with a
  coordinator entity, fixing unavailable cameras on current HA releases.

## 0.2.8

- Retry config-entry setup instead of orphaning camera entities when the bridge
  is temporarily unavailable during Home Assistant startup.
- Add coordinator-backed camera availability and group cameras under one
  MD Parking device.
- Create a sidebar MD Parking dashboard with live camera cards on first setup.

## 0.2.7

- Replace obsolete foundation notes with the current Git/HACS installation,
  automatic pairing, SMS sign-in, camera, update, and dashboard instructions.

## 0.2.6

- Send the current Bearer access token with provider session refresh requests.
- Refresh provider sessions in the background before access-token expiry.
- Retry camera source rotation independently and recover diagnostics after a
  successful cycle.

## 0.2.5

- Support the confirmed nested `stream.hiRes`/`stream.lowRes` provider response.
- Continue with a still-valid access token when an immediate refresh is rejected.
- Refresh one-minute stream capabilities 15 seconds before expiry.

## 0.2.4

- Treat the provider's `object required` response as the expected transition
  from phone entry to object-number entry.
- Match the official client's compact JSON encoding and public request headers.

## 0.2.3

- Added secret-safe provider error codes for HTTP, network, timeout, JSON, and RPC failures.

## 0.2.2

- Ignore the obsolete persisted `/v2/base` auth URL from pre-0.2 add-on options.

## 0.2.1

- Added config-entry migration from the paired 0.1.x integration.
- Normalized Russian phone formats and matched the confirmed API user agent.

## 0.2.0

- Added complete phone, object, and SMS authentication flow.
- Persisted and refreshed provider sessions inside the add-on data volume.
- Published go2rtc port 8554 and fixed Home Assistant camera stream URLs.

## 0.1.8

- Distinguish unavailable pairing from bridge connectivity failures in config flow.

## 0.1.7

- Added safe health endpoint and pairing diagnostics.

## 0.1.6

- Fixed add-on Python package path during container startup.

## 0.1.5

- Fixed empty auto-pairing token configuration in Home Assistant Supervisor.

## 0.1.4

- Added one-time automatic bridge pairing; integration can obtain its token without manual entry.

## 0.1.3

- Fixed empty bridge runtime options so initial add-on configuration can be saved.

## 0.1.2

- Published the authenticated bridge API on port 8099 for the HA integration.

## 0.1.1

- Added bridge lifecycle wiring, stable go2rtc source rotation, and camera discovery.
- Added public installation and update documentation.

## 0.1.0

- Initial add-on and custom integration foundation.
