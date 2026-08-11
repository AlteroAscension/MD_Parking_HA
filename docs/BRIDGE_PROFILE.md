# Read-only bridge profile contract

## Purpose

`md-parking-bridge` separates provider-specific request details from its
long-lived restream and Home Assistant boundary. Its local profile is stored at
`/data/md_parking_read_only_profile.json` inside the add-on data volume, never
in the Git repository. It is a secret operational artefact even if it contains
no token, because endpoint details and request shapes reduce the provider's
attack surface.

The profile may be created only after a passive observation of the official
authorised Android client confirms each request. Do not infer endpoints from
names, try alternatives, or include a barrier operation. This applies the
research constraints in [RESEARCH.md](RESEARCH.md) and the functional boundary
in [SECURITY.md](SECURITY.md).

## Version 1 validation

The current add-on validates a profile before it is usable. A version 1 profile
must declare:

- `allowed_hosts`: explicit HTTPS provider hosts;
- `auth`: a `GET` or `POST` request description;
- `cameras`: a `GET` or `POST` request description;
- response paths for token, camera list, camera alias, and source.

Only declared HTTPS hosts are accepted. Control-like URL paths (`open`, `close`,
`barrier`, `gate`, `control`, `command`, or `action`) are rejected. This is a
guard rail, not permission to use an unreviewed profile.

The add-on's status API reports only readiness and error class. It never
returns a request URL, headers, response body, signed source, camera object ID,
or credentials. URL and header redaction functions are covered by unit tests.

## Delivery boundary

This commit intentionally does not execute the profile, authenticate to the
provider, or start go2rtc. The precise API request/response schema has not yet
been confirmed, and pretending otherwise would violate the read-only research
rule. The next increment is permitted only after that observation and must add:

1. a profile executor that allows only the validated read-only exchange;
2. a refresh scheduler that renews before the observed expiry;
3. a go2rtc update using a stable local stream name;
4. tests with synthetic sources, ensuring URL and token redaction.

That increment implements the [video refresh contract](ARCHITECTURE.md#video-refresh-contract).
It remains separate from every barrier-control design in
[ARCHITECTURE.md](ARCHITECTURE.md#barrier-control-separate-later-stage).
