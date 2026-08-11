# Architecture and staged plan

## Why a bridge is required

The provider does not offer a permanent camera URL. The mobile client asks its
authorised API for a signed RTSP capability URL; the observed capability contains
a validity of about one minute. A direct HA `generic` camera configuration would
therefore stop working quickly and would expose the temporary URL in HA settings
or logs.

The bridge owns provider authentication and source renewal. Home Assistant only
receives a stable local stream and high-level entities.

## Components

### 1. `md-parking-bridge` HA add-on

Responsibilities:

- retain credentials/session in the add-on secret store;
- call only documented or carefully verified provider read-only endpoints for
  camera/source discovery;
- obtain a new signed source before expiry and recover from a failed connection;
- feed the source to go2rtc (or a bundled compatible restreamer);
- provide a local authenticated status API to the HA integration;
- keep an audit log with identifiers and result codes, never URLs or tokens.

The add-on must expose a health model: provider authentication state, source
age, current restream state, last refresh failure and camera availability.

### 2. `md_parking` custom integration

Responsibilities:

- config flow that connects to the locally installed bridge;
- `camera` entities sourced from the bridge's stable restream;
- read-only availability/state sensors;
- later, explicit barrier `button`/`cover` entities and services;
- diagnostics that redact all credentials and stream URLs.

The integration should not know how provider authentication works.

### 3. HA presentation

Initial version: standard HA Picture Glance/Picture Entity cards generated or
documented by the integration. It avoids frontend complexity while proving video
latency and reliability.

Later version: a dedicated HA panel with two large camera tiles, availability,
last-frame age and a guarded barrier action. The panel must ask for confirmation
immediately before sending the action.

## Video refresh contract

1. Bridge obtains a source capability and records its expiry estimate.
2. go2rtc establishes the RTSP session.
3. Bridge refreshes proactively (target: no later than 15 seconds before expiry)
   or immediately on restream failure.
4. If an established RTSP session remains valid beyond capability expiry, keep it
   alive; renewal is still prepared for reconnects.
5. HA sees a fixed local source. It must never receive provider credentials or
   the signed external URL.

This needs measurement on the real source: the one-minute signature could govern
only session setup or could terminate an active stream too.

## Barrier control: separate later stage

Before adding a write endpoint, implement:

- a named barrier inventory; never accept a free-form provider ID from HA;
- per-action confirmation in UI and service call;
- idempotency/request correlation where the provider supports it;
- rate limit and a short cool-down;
- append-only local audit log with timestamp, HA user, barrier alias and result;
- an emergency disable switch in add-on configuration.

No camera refresh task may be allowed to call a barrier endpoint.

## Delivery order

1. Identify the minimal authorised **read-only** API exchange and source refresh.
2. Build the add-on with one camera and a stable go2rtc output.
3. Validate long-running video and reconnect behaviour.
4. Add custom integration camera and diagnostic entities.
5. Add the dedicated page.
6. Design, review and test guarded barrier control separately.
