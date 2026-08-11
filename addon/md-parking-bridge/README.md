# MD Parking Bridge add-on

This is the read-only bridge foundation. It exposes an authenticated status API
on port 8099 and deliberately contains no barrier-control routes, client code,
or configuration.

The add-on loads its provider exchange description from
`/data/md_parking_read_only_profile.json`. That file is a local secret: it may
contain provider endpoint details and must be created only after a passive,
authorised observation confirms the exact read-only request and response
schema. It is not part of this repository.

The profile accepts only `GET` and `POST` HTTPS requests to an explicit
allow-list and rejects control-like paths. This is defence in depth, not proof
that an unreviewed profile is safe. Review every profile change against
[the security boundary](../../docs/SECURITY.md) before installing it.

The next implementation increment is the profile executor plus go2rtc source
rotation. It must be tested against the confirmed source-refresh contract in
[the architecture](../../docs/ARCHITECTURE.md), with no provider URL in logs,
diagnostics, or HA configuration.

Set a long random `api_token` in the add-on configuration before starting it.
The bridge rejects status requests without `Authorization: Bearer <api_token>`.
